const loginView = document.getElementById("loginView");
const adminView = document.getElementById("adminView");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const loginError = document.getElementById("loginError");
const inventoryList = document.getElementById("inventoryList");
const shoppingList = document.getElementById("shoppingList");
const statsGrid = document.getElementById("statsGrid");
const cocktailAdminGrid = document.getElementById("cocktailAdminGrid");
const catalogCocktailGrid = document.getElementById("catalogCocktailGrid");
const cocktailSearchInput = document.getElementById("cocktailSearchInput");

let dashboardData = null;

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "request_failed" }));
    throw new Error(error.error || "request_failed");
  }
  return response.json().catch(() => ({}));
}

function cocktailCard(cocktail) {
  const tags = cocktail.tags.map((tag) => `<span class="tag">${tag}</span>`).join("");
  const requirements = cocktail.requirements
    .map((requirement) => {
      const options = requirement.options.map((option) => option.name).join(" o ");
      return `<span class="tag ${requirement.available ? "available" : "missing"}">${options}</span>`;
    })
    .join("");
  const source = cocktail.source || {};

  return `
    <article class="card">
      <img src="${cocktail.image_url}" alt="${cocktail.name}" />
      <div class="card-body">
        <div class="row-top">
          <div>
            <h3>${cocktail.name}</h3>
            <p>${cocktail.description}</p>
          </div>
          <label class="pill">
            <input data-favorite="${cocktail.id}" type="checkbox" ${cocktail.is_favorite ? "checked" : ""} />
            favorito
          </label>
        </div>
        <div class="meta-row">
          <span class="pill">${cocktail.prep_time_minutes} min</span>
          <span class="pill">${cocktail.difficulty}</span>
          <span class="pill">${cocktail.strength || "equilibrado"}</span>
        </div>
        <div class="tag-row">${tags}</div>
        <div class="details">
          <strong>Compatibilidad con stock</strong>
          <div class="requirements">${requirements}</div>
        </div>
        <div class="details">
          <label>
            Rating
            <input data-rating="${cocktail.id}" type="number" min="0" max="5" step="0.1" value="${cocktail.rating}" />
          </label>
        </div>
        <div class="details">
          <label>
            Importado desde
            <input data-source-provider="${cocktail.id}" value="${source.provider || ""}" placeholder="TheCocktailDB, IBA, manual..." />
          </label>
          <label>
            Link fuente
            <input data-source-url="${cocktail.id}" value="${source.source_url || ""}" placeholder="https://..." />
          </label>
          <button data-save-source="${cocktail.id}" class="secondary">Guardar fuente</button>
        </div>
      </div>
    </article>
  `;
}

function renderStats(data) {
  const available = data.cocktails.filter((cocktail) => cocktail.is_available).length;
  const lowStock = data.ingredients.filter((ingredient) => ingredient.low_stock).length;
  const shoppingPending = data.shopping.filter((item) => !item.done).length;
  statsGrid.innerHTML = `
    <div class="stat"><span>Ingredientes en stock</span><strong>${data.ingredients.filter((item) => item.in_stock).length}</strong></div>
    <div class="stat"><span>Cocteles posibles hoy</span><strong>${available}</strong></div>
    <div class="stat"><span>Cocteles en catalogo</span><strong>${data.cocktails.length}</strong></div>
    <div class="stat"><span>Ingredientes bajos</span><strong>${lowStock}</strong></div>
    <div class="stat"><span>Compras pendientes</span><strong>${shoppingPending}</strong></div>
  `;
}

function renderInventory(data) {
  inventoryList.innerHTML = data.ingredients
    .map((ingredient) => `
      <div class="inventory-row">
        <div class="row-top">
          <div>
            <strong>${ingredient.name}</strong>
            <div class="muted">${ingredient.category || "sin categoria"}</div>
          </div>
          <div class="pill">${ingredient.alcoholic ? "alcoholico" : "no alcoholico"}</div>
        </div>
        <div class="form-grid" style="margin-top:12px">
          <label><input data-stock="${ingredient.id}" type="checkbox" ${ingredient.in_stock ? "checked" : ""} /> Disponible</label>
          <label><input data-low="${ingredient.id}" type="checkbox" ${ingredient.low_stock ? "checked" : ""} /> Queda poco</label>
          <label>Cantidad <input data-qty="${ingredient.id}" value="${ingredient.quantity_label || ""}" placeholder="1 botella, poco, 500 ml..." /></label>
          <button data-save-inventory="${ingredient.id}" class="secondary">Guardar</button>
          <button data-shopping="${ingredient.id}" class="secondary">Agregar a compras</button>
        </div>
      </div>
    `)
    .join("");
}

function renderShopping(data) {
  if (!data.shopping.length) {
    shoppingList.innerHTML = `<div class="empty">No hay compras pendientes.</div>`;
    return;
  }
  shoppingList.innerHTML = data.shopping
    .map((item) => `
      <div class="shopping-row">
        <div class="row-top">
          <div>
            <strong>${item.ingredient_name}</strong>
            <div class="muted">${item.note || "Sin nota"}</div>
          </div>
          <label class="pill"><input data-shopping-done="${item.ingredient_id}" type="checkbox" ${item.done ? "checked" : ""} /> comprado</label>
        </div>
      </div>
    `)
    .join("");
}

function renderCocktails(data) {
  const available = data.cocktails.filter((cocktail) => cocktail.is_available);
  if (!available.length) {
    cocktailAdminGrid.innerHTML = `<div class="empty">Todavia no hay cocteles armables con el stock actual.</div>`;
  } else {
    cocktailAdminGrid.innerHTML = available.map(cocktailCard).join("");
  }
  renderCatalog(data);
}

function renderCatalog(data) {
  const query = (cocktailSearchInput.value || "").trim().toLowerCase();
  const catalog = data.cocktails.filter((cocktail) => {
    if (!query) return true;
    return cocktail.name.toLowerCase().includes(query) || cocktail.tags.some((tag) => tag.toLowerCase().includes(query));
  });

  if (!catalog.length) {
    catalogCocktailGrid.innerHTML = `<div class="empty">No encontre cocteles con esa busqueda.</div>`;
    return;
  }
  catalogCocktailGrid.innerHTML = catalog.map(cocktailCard).join("");
}

async function loadDashboard() {
  const response = await fetch("/api/admin/dashboard");
  if (response.status === 401) {
    loginView.classList.remove("hidden");
    adminView.classList.add("hidden");
    return;
  }
  const data = await response.json();
  dashboardData = data;
  loginView.classList.add("hidden");
  adminView.classList.remove("hidden");
  renderStats(data);
  renderInventory(data);
  renderShopping(data);
  renderCocktails(data);
}

cocktailSearchInput.addEventListener("input", () => {
  if (dashboardData) renderCatalog(dashboardData);
});

async function login() {
  loginError.classList.add("hidden");
  try {
    await postJson("/api/login", { password: passwordInput.value });
    await loadDashboard();
  } catch (error) {
    loginError.classList.remove("hidden");
  }
}

loginButton.addEventListener("click", login);
passwordInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") login();
});

document.addEventListener("click", async (event) => {
  const saveInventory = event.target.dataset.saveInventory;
  const addShopping = event.target.dataset.shopping;
  const saveSource = event.target.dataset.saveSource;
  if (saveInventory) {
    const ingredientId = Number(saveInventory);
    const inStock = document.querySelector(`[data-stock="${ingredientId}"]`).checked;
    const lowStock = document.querySelector(`[data-low="${ingredientId}"]`).checked;
    const quantityLabel = document.querySelector(`[data-qty="${ingredientId}"]`).value;
    await postJson("/api/admin/inventory", {
      ingredient_id: ingredientId,
      in_stock: inStock,
      low_stock: lowStock,
      quantity_label: quantityLabel,
    });
    await loadDashboard();
  }
  if (addShopping) {
    const ingredientId = Number(addShopping);
    await postJson("/api/admin/shopping", {
      ingredient_id: ingredientId,
      note: "Agregado desde inventario",
      done: false,
    });
    await loadDashboard();
  }
  if (saveSource) {
    const cocktailId = Number(saveSource);
    const provider = document.querySelector(`[data-source-provider="${cocktailId}"]`).value;
    const sourceUrl = document.querySelector(`[data-source-url="${cocktailId}"]`).value;
    await postJson("/api/admin/cocktail-source", {
      cocktail_id: cocktailId,
      provider,
      source_url: sourceUrl,
    });
    await loadDashboard();
  }
});

document.addEventListener("change", async (event) => {
  const favoriteId = event.target.dataset.favorite;
  const ratingId = event.target.dataset.rating;
  const shoppingDoneId = event.target.dataset.shoppingDone;

  if (favoriteId) {
    const ratingInput = document.querySelector(`[data-rating="${favoriteId}"]`);
    await postJson("/api/admin/cocktail-rating", {
      cocktail_id: Number(favoriteId),
      rating: Number(ratingInput.value || 0),
      is_favorite: event.target.checked,
    });
    await loadDashboard();
  }

  if (ratingId) {
    const favoriteInput = document.querySelector(`[data-favorite="${ratingId}"]`);
    await postJson("/api/admin/cocktail-rating", {
      cocktail_id: Number(ratingId),
      rating: Number(event.target.value || 0),
      is_favorite: favoriteInput ? favoriteInput.checked : false,
    });
    await loadDashboard();
  }

  if (shoppingDoneId) {
    await postJson("/api/admin/shopping", {
      ingredient_id: Number(shoppingDoneId),
      note: "Marcado desde lista de compras",
      done: event.target.checked,
    });
    await loadDashboard();
  }
});

document.getElementById("saveCocktailButton").addEventListener("click", async () => {
  await postJson("/api/admin/cocktails", {
    name: document.getElementById("newCocktailName").value,
    description: document.getElementById("newCocktailDescription").value,
    image_url: document.getElementById("newCocktailImage").value,
    prep_time_minutes: Number(document.getElementById("newCocktailMinutes").value || 5),
    difficulty: document.getElementById("newCocktailDifficulty").value,
    strength: document.getElementById("newCocktailStrength").value,
    instructions: document.getElementById("newCocktailInstructions").value,
    is_alcoholic: document.getElementById("newCocktailAlcoholic").checked,
  });
  await loadDashboard();
});

document.getElementById("saveListButton").addEventListener("click", async () => {
  await postJson("/api/admin/lists", {
    name: document.getElementById("newListName").value,
    description: document.getElementById("newListDescription").value,
    is_public: true,
  });
  await loadDashboard();
});

fetch("/api/session")
  .then((response) => response.json())
  .then((session) => {
    if (session.authenticated) loadDashboard();
  });
