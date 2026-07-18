const loginView = document.getElementById("loginView");
const adminView = document.getElementById("adminView");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const loginError = document.getElementById("loginError");
const inventoryList = document.getElementById("inventoryList");
const shoppingList = document.getElementById("shoppingList");
const statsGrid = document.getElementById("statsGrid");
const catalogCocktailGrid = document.getElementById("catalogCocktailGrid");
const cocktailSearchInput = document.getElementById("cocktailSearchInput");
const ingredientSearchInput = document.getElementById("ingredientSearchInput");
const inventoryCategoryFilters = document.getElementById("inventoryCategoryFilters");
const cocktailStatsFilters = document.getElementById("cocktailStatsFilters");
const cocktailAvailabilityFilter = document.getElementById("cocktailAvailabilityFilter");
const publicListsPanel = document.getElementById("publicListsPanel");

let dashboardData = null;
let inventoryFilter = "all";
let cocktailFilter = "all";

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

function escapeHtml(value) {
  return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

function renderStats(data) {
  const cards = [
    { key: "stock", label: "Ingredientes en stock", value: data.ingredients.filter((item) => item.in_stock).length },
    { key: "available", label: "Cocteles posibles hoy", value: data.cocktails.filter((item) => item.is_available).length },
    { key: "catalog", label: "Cocteles en catalogo", value: data.cocktails.length },
    { key: "low", label: "Ingredientes bajos", value: data.ingredients.filter((item) => item.low_stock).length },
    { key: "shopping", label: "Compras pendientes", value: data.shopping.filter((item) => !item.done).length },
  ];
  statsGrid.innerHTML = cards.map((item) => `<button class="stat stat-button" data-stat-filter="${item.key}"><span>${item.label}</span><strong>${item.value}</strong></button>`).join("");
}

function filteredIngredients(data) {
  const query = (ingredientSearchInput.value || "").trim().toLowerCase();
  return data.ingredients.filter((ingredient) => {
    if (inventoryFilter === "stock" && !ingredient.in_stock) return false;
    if (inventoryFilter === "low" && !ingredient.low_stock) return false;
    if (!["all", "stock", "low", "shopping"].includes(inventoryFilter) && ingredient.normalized_category !== inventoryFilter) return false;
    return !query || `${ingredient.name} ${ingredient.normalized_category}`.toLowerCase().includes(query);
  });
}

function renderInventory(data) {
  const categories = [...new Set(data.ingredients.map((item) => item.normalized_category))];
  inventoryCategoryFilters.innerHTML = `<button class="chip" data-inventory-filter="all">Todos</button>` + categories.map((item) => `<button class="chip" data-inventory-filter="${escapeHtml(item)}">${item}</button>`).join("");
  const groups = filteredIngredients(data).reduce((acc, ingredient) => {
    acc[ingredient.normalized_category] = acc[ingredient.normalized_category] || [];
    acc[ingredient.normalized_category].push(ingredient);
    return acc;
  }, {});
  inventoryList.innerHTML = Object.entries(groups).map(([category, items]) => `
    <section class="inventory-group">
      <h4>${category}</h4>
      ${items.map((ingredient) => `
        <div class="compact-row ingredient-row">
          <div class="compact-main">
            <strong>${ingredient.name}</strong>
            <span class="muted">${ingredient.quantity_label || ingredient.category || "sin nota"}</span>
          </div>
          <label class="quick-check"><input data-stock-toggle="${ingredient.id}" type="checkbox" ${ingredient.in_stock ? "checked" : ""} /> stock</label>
          <label class="quick-check"><input data-low-toggle="${ingredient.id}" type="checkbox" ${ingredient.low_stock ? "checked" : ""} /> bajo</label>
          <button class="secondary mini-button" data-shopping="${ingredient.id}">comprar</button>
        </div>`).join("")}
    </section>`).join("") || `<div class="empty">No hay ingredientes para ese filtro.</div>`;
}

function renderShopping(data) {
  const explicit = data.shopping.filter((item) => !item.done);
  const lowStock = data.low_stock_items || [];
  const suggestions = data.shopping_suggestions || [];
  shoppingList.innerHTML = `
    <div class="shopping-block"><h4>Seleccionados para comprar</h4>${explicit.length ? explicit.map((item) => `<div class="compact-row"><div class="compact-main"><strong>${item.ingredient_name}</strong><span class="muted">${item.note || item.normalized_category}</span></div><label class="quick-check"><input data-shopping-done="${item.ingredient_id}" type="checkbox" /> comprado</label></div>`).join("") : `<div class="empty">No hay ingredientes marcados.</div>`}</div>
    <div class="shopping-block"><h4>Queda poco</h4>${lowStock.length ? lowStock.map((item) => `<div class="compact-row"><div class="compact-main"><strong>${item.ingredient_name}</strong><span class="muted">${item.quantity_label || item.normalized_category}</span></div><button class="secondary mini-button" data-shopping="${item.ingredient_id}">agregar</button></div>`).join("") : `<div class="empty">No hay ingredientes bajos.</div>`}</div>
    <div class="shopping-block"><h4>Sugeridos por impacto</h4>${suggestions.length ? suggestions.slice(0, 12).map((item) => `<div class="compact-row"><div class="compact-main"><strong>${item.ingredient_name}</strong><span class="muted">Habilita ${item.cocktail_count} cocteles</span></div><button class="secondary mini-button" data-shopping="${item.ingredient_id}">agregar</button></div>`).join("") : `<div class="empty">No hay sugerencias de impacto.</div>`}</div>
  `;
}

function requirementEditor(requirement, index) {
  const options = requirement.options.map((option) => option.name).join(" | ");
  return `<div class="requirement-editor"><input data-field="amount" value="${escapeHtml(requirement.amount || "")}" placeholder="cantidad" /><input data-field="unit" value="${escapeHtml(requirement.unit || "")}" placeholder="unidad" /><input data-field="options" value="${escapeHtml(options)}" placeholder="Tequila | Mezcal" /><label class="quick-check"><input data-field="optional" type="checkbox" ${requirement.optional ? "checked" : ""} /> opcional</label><button class="secondary mini-button" type="button" data-remove-requirement="${index}">quitar</button></div>`;
}

function cocktailEditor(cocktail) {
  const source = cocktail.source || {};
  return `
    <article class="editor-card" data-editor-card="${cocktail.id}">
      <button class="editor-summary" type="button" data-toggle-editor="${cocktail.id}">
        <div class="compact-main"><strong>${cocktail.name}</strong><span class="muted">${cocktail.is_available ? "Disponible" : "No disponible"} • ${cocktail.requirements.length} grupos</span></div>
        <span class="pill">${cocktail.rating.toFixed(1)}</span>
      </button>
      <div class="editor-body hidden" data-editor-body="${cocktail.id}">
        <div class="form-grid">
          <label>Nombre <input data-edit-name="${cocktail.id}" value="${escapeHtml(cocktail.name)}" /></label>
          <label>Foto URL <input data-edit-image="${cocktail.id}" value="${escapeHtml(cocktail.image_url || "")}" /></label>
          <label>Minutos <input data-edit-minutes="${cocktail.id}" type="number" value="${cocktail.prep_time_minutes}" /></label>
          <label>Dificultad <input data-edit-difficulty="${cocktail.id}" value="${escapeHtml(cocktail.difficulty || "")}" /></label>
          <label>Fuerza <input data-edit-strength="${cocktail.id}" value="${escapeHtml(cocktail.strength || "")}" /></label>
        </div>
        <label>Descripcion <textarea data-edit-description="${cocktail.id}" rows="2">${escapeHtml(cocktail.description || "")}</textarea></label>
        <div class="form-grid">
          <label>Rating <input data-edit-rating="${cocktail.id}" type="number" min="0" max="5" step="0.1" value="${cocktail.rating}" /></label>
          <label>Tags separados por coma <input data-edit-tags="${cocktail.id}" value="${escapeHtml(cocktail.tags.join(", "))}" /></label>
          <label>Importado desde <input data-edit-source-provider="${cocktail.id}" value="${escapeHtml(source.provider || "")}" /></label>
          <label>Link fuente <input data-edit-source-url="${cocktail.id}" value="${escapeHtml(source.source_url || "")}" /></label>
        </div>
        <div class="compact-toolbar compact-toolbar-2">
          <label><input data-edit-alcoholic="${cocktail.id}" type="checkbox" ${cocktail.is_alcoholic ? "checked" : ""} /> Tiene alcohol</label>
          <label><input data-edit-favorite="${cocktail.id}" type="checkbox" ${cocktail.is_favorite ? "checked" : ""} /> Favorito</label>
          <label><input data-edit-active="${cocktail.id}" type="checkbox" ${cocktail.is_active ? "checked" : ""} /> Activo</label>
        </div>
        <label>Pasos, uno por linea <textarea data-edit-steps="${cocktail.id}" rows="4">${escapeHtml(cocktail.steps.map((item) => item.instruction).join("\n"))}</textarea></label>
        <div class="details">
          <div class="row-top"><strong>Ingredientes / reemplazos</strong><button class="secondary mini-button" type="button" data-add-requirement="${cocktail.id}">agregar fila</button></div>
          <div class="requirement-stack" data-requirements-stack="${cocktail.id}">${cocktail.requirements.map((requirement, index) => requirementEditor(requirement, index)).join("")}</div>
        </div>
        <div class="row-top" style="margin-top:12px"><button data-save-cocktail="${cocktail.id}">Guardar cambios</button><button class="secondary" data-delete-cocktail="${cocktail.id}">Eliminar coctel</button></div>
      </div>
    </article>`;
}

function renderCatalog(data) {
  cocktailStatsFilters.innerHTML = `<button class="chip" data-cocktail-filter="all">Todos</button><button class="chip" data-cocktail-filter="available">Disponibles</button><button class="chip" data-cocktail-filter="unavailable">No disponibles</button><button class="chip" data-cocktail-filter="favorites">Favoritos</button>`;
  const query = (cocktailSearchInput.value || "").trim().toLowerCase();
  const availability = cocktailAvailabilityFilter.value;
  const items = data.cocktails.filter((cocktail) => {
    if (availability === "available" && !cocktail.is_available) return false;
    if (availability === "unavailable" && cocktail.is_available) return false;
    if (cocktailFilter === "available" && !cocktail.is_available) return false;
    if (cocktailFilter === "unavailable" && cocktail.is_available) return false;
    if (cocktailFilter === "favorites" && !cocktail.is_favorite) return false;
    return !query || `${cocktail.name} ${cocktail.tags.join(" ")}`.toLowerCase().includes(query);
  });
  catalogCocktailGrid.innerHTML = items.length ? items.map(cocktailEditor).join("") : `<div class="empty">No encontre cocteles con ese filtro.</div>`;
}

function renderLists(data) {
  publicListsPanel.innerHTML = data.lists.length ? data.lists.map((item) => `<div class="compact-row"><div class="compact-main"><strong>${item.name}</strong><span class="muted">${item.description || "sin descripcion"}</span></div><span class="pill">publica</span></div>`).join("") : `<div class="empty">No hay listas publicas.</div>`;
}

async function loadDashboard() {
  const response = await fetch("/api/admin/dashboard");
  if (response.status === 401) {
    loginView.classList.remove("hidden");
    adminView.classList.add("hidden");
    return;
  }
  dashboardData = await response.json();
  loginView.classList.add("hidden");
  adminView.classList.remove("hidden");
  renderStats(dashboardData);
  renderInventory(dashboardData);
  renderShopping(dashboardData);
  renderCatalog(dashboardData);
  renderLists(dashboardData);
}

function collectRequirementRows(cocktailId) {
  const stack = document.querySelector(`[data-requirements-stack="${cocktailId}"]`);
  return [...stack.querySelectorAll(".requirement-editor")].map((row, index) => ({
    group_key: `group-${index + 1}`,
    amount: row.querySelector('[data-field="amount"]').value,
    unit: row.querySelector('[data-field="unit"]').value,
    options: row.querySelector('[data-field="options"]').value.split("|").map((item) => item.trim()).filter(Boolean),
    optional: row.querySelector('[data-field="optional"]').checked,
  }));
}

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
passwordInput.addEventListener("keydown", (event) => { if (event.key === "Enter") login(); });
cocktailSearchInput.addEventListener("input", () => dashboardData && renderCatalog(dashboardData));
ingredientSearchInput.addEventListener("input", () => dashboardData && renderInventory(dashboardData));
cocktailAvailabilityFilter.addEventListener("change", () => dashboardData && renderCatalog(dashboardData));

document.addEventListener("click", async (event) => {
  const statFilter = event.target.closest("[data-stat-filter]")?.dataset.statFilter;
  const inventoryCat = event.target.closest("[data-inventory-filter]")?.dataset.inventoryFilter;
  const cocktailStat = event.target.closest("[data-cocktail-filter]")?.dataset.cocktailFilter;
  const toggleEditor = event.target.closest("[data-toggle-editor]")?.dataset.toggleEditor;
  const addShopping = event.target.dataset.shopping;
  const addRequirement = event.target.dataset.addRequirement;
  const removeRequirement = event.target.dataset.removeRequirement;
  const saveCocktail = event.target.dataset.saveCocktail;
  const deleteCocktail = event.target.dataset.deleteCocktail;

  if (statFilter) {
    inventoryFilter = statFilter === "stock" || statFilter === "low" || statFilter === "shopping" ? statFilter : inventoryFilter;
    cocktailFilter = statFilter === "available" ? "available" : statFilter === "catalog" ? "all" : cocktailFilter;
    renderStats(dashboardData);
    renderInventory(dashboardData);
    renderCatalog(dashboardData);
    return;
  }
  if (inventoryCat) { inventoryFilter = inventoryCat; renderInventory(dashboardData); return; }
  if (cocktailStat) { cocktailFilter = cocktailStat; renderCatalog(dashboardData); return; }
  if (toggleEditor) {
    const body = document.querySelector(`[data-editor-body="${toggleEditor}"]`);
    const willOpen = body.classList.contains("hidden");
    document.querySelectorAll("[data-editor-body]").forEach((item) => item.classList.add("hidden"));
    if (willOpen) body.classList.remove("hidden");
    return;
  }
  if (addShopping) { await postJson("/api/admin/shopping", { ingredient_id: Number(addShopping), note: "Agregado desde admin", done: false }); await loadDashboard(); return; }
  if (addRequirement) { document.querySelector(`[data-requirements-stack="${addRequirement}"]`).insertAdjacentHTML("beforeend", requirementEditor({ amount: "", unit: "", options: [{ name: "" }], optional: false }, Date.now())); return; }
  if (removeRequirement) { event.target.closest(".requirement-editor").remove(); return; }
  if (saveCocktail) {
    const id = Number(saveCocktail);
    await postJson("/api/admin/cocktail-save", {
      cocktail_id: id,
      name: document.querySelector(`[data-edit-name="${id}"]`).value,
      description: document.querySelector(`[data-edit-description="${id}"]`).value,
      image_url: document.querySelector(`[data-edit-image="${id}"]`).value,
      prep_time_minutes: Number(document.querySelector(`[data-edit-minutes="${id}"]`).value || 5),
      difficulty: document.querySelector(`[data-edit-difficulty="${id}"]`).value,
      strength: document.querySelector(`[data-edit-strength="${id}"]`).value,
      is_alcoholic: document.querySelector(`[data-edit-alcoholic="${id}"]`).checked,
      rating: Number(document.querySelector(`[data-edit-rating="${id}"]`).value || 0),
      is_favorite: document.querySelector(`[data-edit-favorite="${id}"]`).checked,
      is_active: document.querySelector(`[data-edit-active="${id}"]`).checked,
      tags: document.querySelector(`[data-edit-tags="${id}"]`).value.split(",").map((item) => item.trim()),
      steps: document.querySelector(`[data-edit-steps="${id}"]`).value.split("\n"),
      source_provider: document.querySelector(`[data-edit-source-provider="${id}"]`).value,
      source_url: document.querySelector(`[data-edit-source-url="${id}"]`).value,
      requirements: collectRequirementRows(id),
    });
    await loadDashboard();
    return;
  }
  if (deleteCocktail) { await postJson("/api/admin/cocktail-delete", { cocktail_id: Number(deleteCocktail) }); await loadDashboard(); }
});

document.addEventListener("change", async (event) => {
  const stockToggle = event.target.dataset.stockToggle;
  const lowToggle = event.target.dataset.lowToggle;
  const shoppingDoneId = event.target.dataset.shoppingDone;
  if (stockToggle || lowToggle) {
    const ingredientId = Number(stockToggle || lowToggle);
    const ingredient = dashboardData.ingredients.find((item) => item.id === ingredientId);
    await postJson("/api/admin/inventory", {
      ingredient_id: ingredientId,
      in_stock: document.querySelector(`[data-stock-toggle="${ingredientId}"]`).checked,
      low_stock: document.querySelector(`[data-low-toggle="${ingredientId}"]`).checked,
      quantity_label: ingredient.quantity_label || "",
    });
    await loadDashboard();
  }
  if (shoppingDoneId) { await postJson("/api/admin/shopping", { ingredient_id: Number(shoppingDoneId), note: "Marcado desde lista de compras", done: event.target.checked }); await loadDashboard(); }
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
  await postJson("/api/admin/lists", { name: document.getElementById("newListName").value, description: document.getElementById("newListDescription").value, is_public: true });
  await loadDashboard();
});

fetch("/api/session").then((response) => response.json()).then((session) => { if (session.authenticated) loadDashboard(); });
