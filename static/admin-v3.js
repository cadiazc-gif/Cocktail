const loginView = document.getElementById("loginView");
const adminView = document.getElementById("adminView");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const loginError = document.getElementById("loginError");
const inventoryList = document.getElementById("inventoryList");
const shoppingList = document.getElementById("shoppingList");
const statsGrid = document.getElementById("statsGrid");
const catalogCocktailGrid = document.getElementById("catalogCocktailGrid");
const suggestionsList = document.getElementById("suggestionsList");
const cocktailSearchInput = document.getElementById("cocktailSearchInput");
const ingredientSearchInput = document.getElementById("ingredientSearchInput");
const inventoryCategoryFilters = document.getElementById("inventoryCategoryFilters");
const cocktailStatsFilters = document.getElementById("cocktailStatsFilters");
const cocktailTagFilterButton = document.getElementById("cocktailTagFilterButton");
const cocktailTagFilterPanel = document.getElementById("cocktailTagFilterPanel");
const cocktailTagSearchInput = document.getElementById("cocktailTagSearchInput");
const cocktailTagFilterOptions = document.getElementById("cocktailTagFilterOptions");
const cocktailGlassFilterButton = document.getElementById("cocktailGlassFilterButton");
const cocktailGlassFilterPanel = document.getElementById("cocktailGlassFilterPanel");
const cocktailGlassSearchInput = document.getElementById("cocktailGlassSearchInput");
const cocktailGlassFilterOptions = document.getElementById("cocktailGlassFilterOptions");
const cocktailFavoriteFilter = document.getElementById("cocktailFavoriteFilter");
const cocktailRatingFilter = document.getElementById("cocktailRatingFilter");
const publicListsPanel = document.getElementById("publicListsPanel");
const adminViewModeFilters = document.getElementById("adminViewModeFilters");
const leftPanelModeFilters = document.getElementById("leftPanelModeFilters");
const leftPanelModeFiltersShopping = document.getElementById("leftPanelModeFiltersShopping");
const ingredientsColumn = document.getElementById("ingredientsColumn");
const cocktailsColumn = document.getElementById("cocktailsColumn");
const ingredientOptionsDataList = document.getElementById("ingredientOptionsDataList");
const unitOptionsDataList = document.getElementById("unitOptionsDataList");
const newCocktailRequirements = document.getElementById("newCocktailRequirements");
const newCocktailSteps = document.getElementById("newCocktailSteps");
const addNewRequirementButton = document.getElementById("addNewRequirementButton");

let dashboardData = null;
let inventoryFilter = "all";
let inventoryStockOnly = false;
let cocktailFilter = "all";
let cocktailFavoriteOnly = false;
let cocktailSelectedTag = "";
let cocktailSelectedGlass = "";
let cocktailAvailableTags = [];
let cocktailAvailableGlassware = [];
let adminViewMode = "both";
let leftPanelMode = "ingredients";
let adminNotice = "";
const ingredientReplacementDrafts = {};

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
}

function sortByName(items, getter = (item) => item.name) {
  return [...items].sort((left, right) => getter(left).localeCompare(getter(right), "es", { sensitivity: "base" }));
}

function isIngredientViewVisible() {
  return adminViewMode !== "cocktails" && leftPanelMode !== "shopping";
}

function isShoppingViewVisible() {
  return adminViewMode !== "cocktails" && leftPanelMode !== "ingredients";
}

function isCocktailViewVisible() {
  return adminViewMode !== "ingredients";
}

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

function draftReplacementsForIngredient(ingredient) {
  if (!ingredientReplacementDrafts[ingredient.id]) ingredientReplacementDrafts[ingredient.id] = [...(ingredient.replacement_ingredient_ids || [])];
  return ingredientReplacementDrafts[ingredient.id];
}

function ingredientFilterCatalog(data) {
  return [...(data.ingredient_tag_catalog || [])].sort((left, right) => left.localeCompare(right, "es", { sensitivity: "base" }));
}

function ingredientNames() {
  return sortByName(dashboardData?.ingredients || []).map((item) => item.name);
}

function unitCatalog() {
  return sortByName((dashboardData?.units_catalog || []).map((unit) => ({ name: unit }))).map((item) => item.name);
}

function ingredientDataListOptions() {
  return ingredientNames().map((name) => `<option value="${escapeHtml(name)}"></option>`).join("");
}

function buildIngredientDatalist() {
  ingredientOptionsDataList.innerHTML = ingredientDataListOptions();
}

function buildUnitDatalist() {
  unitOptionsDataList.innerHTML = unitCatalog().map((unit) => `<option value="${escapeHtml(unit)}"></option>`).join("");
}

function renderStats(data) {
  const cards = [];
  if (isIngredientViewVisible() || isShoppingViewVisible()) {
    cards.push(
      { key: "stock", scope: "ingredients", label: "Ingredientes en stock", value: data.ingredients.filter((item) => item.in_stock).length },
      { key: "low", scope: "ingredients", label: "Stock bajo", value: data.ingredients.filter((item) => item.low_stock).length },
      { key: "shopping", scope: "ingredients", label: "Lista de compra", value: data.shopping.filter((item) => !item.done).length },
    );
  }
  if (isCocktailViewVisible()) {
    cards.push(
      { key: "catalog", scope: "cocktails", label: "Cocteles en catalogo", value: data.cocktails.length },
      { key: "available", scope: "cocktails", label: "Disponibles hoy", value: data.cocktails.filter((item) => item.is_available).length },
      {
        key: "one-missing",
        scope: "cocktails",
        label: "Les falta 1 ingrediente",
        value: data.cocktails.filter((item) => item.requirements.filter((group) => !group.available && !group.optional).length === 1).length,
      },
    );
  }
  statsGrid.innerHTML = cards.map((item) => `<button class="stat stat-button" data-stat-filter="${item.key}"><span>${item.label}</span><strong>${item.value}</strong></button>`).join("");
}

function renderNotice() {
  const existing = document.getElementById("adminNotice");
  if (!existing) return;
  existing.textContent = adminNotice;
  existing.classList.toggle("hidden", !adminNotice);
}

function renderAdminViewModes() {
  adminViewModeFilters.innerHTML = `
    <button class="chip ${adminViewMode === "both" ? "active" : ""}" data-admin-view="both">Ambos</button>
    <button class="chip ${adminViewMode === "ingredients" ? "active" : ""}" data-admin-view="ingredients">Ingredientes</button>
    <button class="chip ${adminViewMode === "cocktails" ? "active" : ""}" data-admin-view="cocktails">Cocteles</button>
  `;
  ingredientsColumn.classList.toggle("hidden", adminViewMode === "cocktails");
  cocktailsColumn.classList.toggle("hidden", adminViewMode === "ingredients");
}

function renderLeftPanelModes() {
  const controls = `
    <button class="chip ${leftPanelMode === "ingredients" ? "active" : ""}" data-left-panel="ingredients">Ingredientes</button>
    <button class="chip ${leftPanelMode === "shopping" ? "active" : ""}" data-left-panel="shopping">Lista de compras</button>
    <button class="chip ${leftPanelMode === "both" ? "active" : ""}" data-left-panel="both">Ambos</button>
  `;
  leftPanelModeFilters.innerHTML = controls;
  leftPanelModeFiltersShopping.innerHTML = controls;
  const sections = ingredientsColumn.querySelectorAll(".section-card");
  if (sections.length >= 2) {
    if (adminViewMode === "cocktails") {
      sections[0].classList.add("hidden");
      sections[1].classList.add("hidden");
      return;
    }
    sections[0].classList.toggle("hidden", leftPanelMode === "shopping");
    sections[1].classList.toggle("hidden", leftPanelMode === "ingredients");
    if (leftPanelMode === "both") {
      sections[0].classList.remove("hidden");
      sections[1].classList.remove("hidden");
    }
  }
}

function filteredIngredients(data) {
  const query = normalizeText(ingredientSearchInput.value);
  return sortByName(data.ingredients).filter((ingredient) => {
    if (inventoryStockOnly && !ingredient.in_stock) return false;
    if (inventoryFilter === "low" && !ingredient.low_stock) return false;
    if (inventoryFilter === "shopping" && !ingredient.in_shopping) return false;
    if (!["all", "low", "shopping"].includes(inventoryFilter)) {
      const normalizedFilter = normalizeText(inventoryFilter);
      if (normalizeText(ingredient.category || ingredient.normalized_category) !== normalizedFilter) return false;
    }
    const searchable = normalizeText(`${ingredient.name} ${ingredient.category || ingredient.normalized_category}`);
    return !query || searchable.includes(query);
  });
}

function renderInventoryFilters(data) {
  const categories = ingredientFilterCatalog(data);
  inventoryCategoryFilters.innerHTML =
    `<button class="chip ${inventoryFilter === "all" ? "active" : ""}" data-inventory-filter="all">Todos</button>` +
    `<button class="chip ${inventoryStockOnly ? "active" : ""}" data-inventory-stock="true">Stock</button>` +
    categories.map((item) => `<button class="chip ${inventoryFilter === item ? "active" : ""}" data-inventory-filter="${escapeHtml(item)}">${item}</button>`).join("");
}

function renderCocktailFavoriteToggle() {
  cocktailFavoriteFilter.innerHTML = cocktailFavoriteOnly ? "&#9733;" : "&#9734;";
  cocktailFavoriteFilter.classList.toggle("active", cocktailFavoriteOnly);
  cocktailFavoriteFilter.setAttribute("aria-pressed", cocktailFavoriteOnly ? "true" : "false");
}

function renderCocktailPickerOptions(optionsRoot, values, selectedValue, allLabel, selectFn) {
  optionsRoot.innerHTML =
    `<button class="picker-option ${selectedValue === "" ? "active" : ""}" type="button" data-picker-value="">${allLabel}</button>` +
    values.map((value) => `<button class="picker-option ${selectedValue === value ? "active" : ""}" type="button" data-picker-value="${escapeHtml(value)}">${escapeHtml(value)}</button>`).join("");
  optionsRoot.querySelectorAll("[data-picker-value]").forEach((button) => {
    button.addEventListener("click", () => selectFn(button.dataset.pickerValue || ""));
  });
}

function renderAdminTagPicker(cocktails = null) {
  const query = normalizeText(cocktailTagSearchInput.value);
  if (cocktails) {
    cocktailAvailableTags = [...new Set(cocktails.flatMap((cocktail) => cocktail.tags || []))].sort((a, b) => a.localeCompare(b, "es", { sensitivity: "base" }));
  }
  if (cocktailSelectedTag && !cocktailAvailableTags.includes(cocktailSelectedTag)) cocktailSelectedTag = "";
  const filtered = cocktailAvailableTags.filter((tag) => !query || normalizeText(tag).includes(query));
  cocktailTagFilterButton.textContent = cocktailSelectedTag || "Todos los tags";
  renderCocktailPickerOptions(cocktailTagFilterOptions, filtered, cocktailSelectedTag, "Todos los tags", (value) => {
    cocktailSelectedTag = value;
    cocktailTagFilterButton.textContent = cocktailSelectedTag || "Todos los tags";
    cocktailTagFilterPanel.classList.add("hidden");
    if (dashboardData) renderCatalog(dashboardData);
  });
}

function renderAdminGlassPicker(cocktails = null) {
  const query = normalizeText(cocktailGlassSearchInput.value);
  if (cocktails) {
    cocktailAvailableGlassware = [...new Set(cocktails.map((cocktail) => cocktail.glassware).filter(Boolean))].sort((a, b) => a.localeCompare(b, "es", { sensitivity: "base" }));
  }
  if (cocktailSelectedGlass && !cocktailAvailableGlassware.includes(cocktailSelectedGlass)) cocktailSelectedGlass = "";
  const filtered = cocktailAvailableGlassware.filter((glass) => !query || normalizeText(glass).includes(query));
  cocktailGlassFilterButton.textContent = cocktailSelectedGlass || "Todos los vasos";
  renderCocktailPickerOptions(cocktailGlassFilterOptions, filtered, cocktailSelectedGlass, "Todos los vasos", (value) => {
    cocktailSelectedGlass = value;
    cocktailGlassFilterButton.textContent = cocktailSelectedGlass || "Todos los vasos";
    cocktailGlassFilterPanel.classList.add("hidden");
    if (dashboardData) renderCatalog(dashboardData);
  });
}

function ingredientEditor(ingredient) {
  const cocktailCount = dashboardData.cocktails.filter((cocktail) =>
    cocktail.requirements.some((requirement) => requirement.options.some((option) => option.ingredient_id === ingredient.id)),
  ).length;
  const options = sortByName(dashboardData.ingredients)
    .filter((item) => item.id !== ingredient.id)
    .map((item) => {
      const count = dashboardData.cocktails.filter((cocktail) =>
        cocktail.requirements.some((requirement) => requirement.options.some((option) => option.ingredient_id === item.id)),
      ).length;
      return `<option value="${escapeHtml(`${item.name} (${count}) [${item.id}]`)}"></option>`;
    })
    .join("");
  const selectedReplacementIds = draftReplacementsForIngredient(ingredient);
  const selectedReplacementNames = selectedReplacementIds
    .map((replacementId) => dashboardData.ingredients.find((item) => item.id === replacementId))
    .filter(Boolean);
  return `
    <div class="ingredient-editor hidden" data-ingredient-editor="${ingredient.id}">
      <div class="form-grid">
        <label>Foto URL <input data-edit-ingredient-image="${ingredient.id}" value="${escapeHtml(ingredient.image_url || "")}" /></label>
        <label>Nombre <input data-edit-ingredient-name="${ingredient.id}" value="${escapeHtml(ingredient.name)}" /></label>
        <label>Categoria
          <select data-edit-ingredient-category-select="${ingredient.id}">
            <option value="${escapeHtml(ingredient.category || ingredient.normalized_category)}">${escapeHtml(ingredient.category || ingredient.normalized_category || "Selecciona una categoria")}</option>
            ${(dashboardData.ingredient_tag_catalog || []).filter((item) => normalizeText(item) !== normalizeText(ingredient.category || ingredient.normalized_category)).map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("")}
            <option value="__new__">Crear nueva categoria...</option>
          </select>
          <input data-edit-ingredient-category-input="${ingredient.id}" class="hidden" placeholder="Nueva categoria" />
        </label>
      </div>
      <div class="form-grid">
        <div class="token-editor-group">
          <span class="token-label">Reemplazable por</span>
          <div class="token-list">${selectedReplacementNames.map((item) => `<span class="token-chip">${escapeHtml(item.name)}<button type="button" class="token-remove" data-remove-ingredient-replacement="${ingredient.id}" data-replacement-id="${item.id}">x</button></span>`).join("") || `<span class="muted">Sin reemplazos globales.</span>`}</div>
          <div class="token-input-row">
            <input data-add-ingredient-replacement-input="${ingredient.id}" list="merge-options-${ingredient.id}" placeholder="Buscar ingrediente reemplazable" />
            <button class="secondary mini-button" type="button" data-add-ingredient-replacement="${ingredient.id}">Agregar reemplazo</button>
          </div>
        </div>
      </div>
      <div class="form-grid">
        <label>Fusionar con
          <input
            data-merge-target-input="${ingredient.id}"
            list="merge-options-${ingredient.id}"
            placeholder="Escribe para buscar ingrediente"
          />
          <datalist id="merge-options-${ingredient.id}">
            ${options}
          </datalist>
        </label>
        <label>Uso actual
          <input value="${cocktailCount} cocteles" disabled />
        </label>
      </div>
      <div class="row-top">
        <button class="secondary mini-button" data-save-ingredient="${ingredient.id}">Guardar ingrediente</button>
        <button class="secondary mini-button" data-merge-ingredient="${ingredient.id}">Fusionar</button>
        <button class="secondary mini-button" data-delete-ingredient="${ingredient.id}">Eliminar</button>
      </div>
    </div>`;
}

function ingredientShoppingChecked(ingredientId) {
  return dashboardData.ingredients.find((item) => item.id === ingredientId)?.in_shopping;
}

function renderInventory(data) {
  renderInventoryFilters(data);
  const items = filteredIngredients(data);
  const renderIngredientCard = (ingredient) => `
    <article class="ingredient-card" data-ingredient-card="${ingredient.id}">
      <div class="ingredient-row" data-toggle-ingredient="${ingredient.id}">
        <strong class="ingredient-title">${ingredient.name}</strong>
        <div class="ingredient-lower">
          <img class="ingredient-thumb" src="${ingredient.image_url || 'https://placehold.co/72x72/f4ead8/7a5c45?text=%20'}" alt="${escapeHtml(ingredient.name)}" />
          <div class="ingredient-checks">
          <label class="quick-check"><input data-stock-toggle="${ingredient.id}" type="checkbox" ${ingredient.in_stock ? "checked" : ""} /> <span>stock</span></label>
          <label class="quick-check"><input data-low-toggle="${ingredient.id}" type="checkbox" ${ingredient.low_stock ? "checked" : ""} /> <span>bajo</span></label>
          <label class="quick-check"><input data-shopping-toggle="${ingredient.id}" type="checkbox" ${ingredient.in_shopping ? "checked" : ""} /> <span>compra</span></label>
          </div>
        </div>
      </div>
      ${ingredientEditor(ingredient)}
    </article>
  `;
  if (!items.length) {
    inventoryList.innerHTML = `<div class="empty">No hay ingredientes para ese filtro.</div>`;
    return;
  }
  if (!["all", "stock", "low", "shopping"].includes(inventoryFilter)) {
    inventoryList.innerHTML = `
      <section class="inventory-group">
        <h4>${escapeHtml(inventoryFilter)}</h4>
        ${items.map(renderIngredientCard).join("")}
      </section>
    `;
    return;
  }
  inventoryList.innerHTML = items.map(renderIngredientCard).join("");
}

function renderShopping(data) {
  const explicit = data.shopping.filter((item) => !item.done);
  const lowStock = data.low_stock_items || [];
  const suggestions = data.shopping_suggestions || [];
  const ingredientById = new Map(data.ingredients.map((item) => [item.id, item]));
  function shoppingCard(item, mode) {
    const ingredient = ingredientById.get(item.ingredient_id) || ingredientById.get(item.ingredient_id ?? item.id) || {};
    const id = item.ingredient_id ?? item.id;
    const label = mode === "done" ? "comprado" : "compra";
    const attr = mode === "done" ? "data-shopping-done" : "data-shopping-toggle";
    const checked = mode === "done" ? "" : (ingredientShoppingChecked(id) ? "checked" : "");
    const impactLine = item.cocktail_count ? `<span class="muted">${item.cocktail_count} cocteles habilitados</span>` : "";
    return `<article class="ingredient-card"><div class="ingredient-row ingredient-row-shopping"><strong class="ingredient-title">${ingredient.name || item.ingredient_name}</strong>${impactLine}<div class="ingredient-lower"><img class="ingredient-thumb" src="${ingredient.image_url || 'https://placehold.co/72x72/f4ead8/7a5c45?text=%20'}" alt="${escapeHtml(ingredient.name || item.ingredient_name)}" /><div class="ingredient-checks"><label class="quick-check shopping-check"><input ${attr}="${id}" type="checkbox" ${checked} /> <span>${label}</span></label></div></div></div></article>`;
  }
  shoppingList.innerHTML = `
    <div class="shopping-block"><h4>Seleccionados para comprar</h4>${explicit.length ? explicit.map((item) => shoppingCard(item, "done")).join("") : `<div class="empty">No hay ingredientes marcados.</div>`}</div>
    <div class="shopping-block"><h4>Queda poco</h4>${lowStock.length ? lowStock.map((item) => shoppingCard(item, "shopping")).join("") : `<div class="empty">No hay ingredientes bajos.</div>`}</div>
    <div class="shopping-block"><h4>Sugeridos por impacto</h4>${suggestions.length ? suggestions.slice(0, 12).map((item) => shoppingCard(item, "shopping")).join("") : `<div class="empty">No hay sugerencias de impacto.</div>`}</div>
  `;
}

function requirementOptionNames(requirement) {
  return (requirement.options || []).map((option) => typeof option === "string" ? option : option.name).filter(Boolean);
}

function requirementEditor(requirement, index, scope = "edit") {
  const optionNames = requirementOptionNames(requirement);
  const rowKey = `${scope}-${index}-${Date.now()}`;
  return `<div class="requirement-editor" data-requirement-row="${rowKey}">
    <input data-field="amount" value="${escapeHtml(requirement.amount || "")}" placeholder="cantidad" />
    <input data-field="unit" list="unitOptionsDataList" value="${escapeHtml(requirement.unit || "")}" placeholder="unidad" />
    <input data-field="options" list="ingredientOptionsDataList" value="${escapeHtml(optionNames.join(" | "))}" placeholder="ingrediente o reemplazos" />
    <div class="requirement-actions">
      <label class="toggle-chip">
        <input data-field="optional" type="checkbox" ${requirement.optional ? "checked" : ""} />
        <span>Opcional</span>
      </label>
      <button class="secondary mini-button" type="button" data-remove-requirement="${rowKey}">Quitar</button>
    </div>
  </div>`;
}

function requirementStatus(requirement) {
  const selected = requirement.selected_options || [];
  const hasDirect = selected.some((option) => !option.is_replacement);
  const hasReplacement = selected.some((option) => option.is_replacement);
  if (hasDirect) return { key: "available", label: requirement.options.map((option) => option.name).join(" o ") };
  if (hasReplacement) return { key: "replacement", label: requirement.options.map((option) => option.name).join(" o ") };
  if (requirement.optional) return { key: "optional", label: requirement.options.map((option) => option.name).join(" o ") };
  return { key: "missing", label: requirement.options.map((option) => option.name).join(" o ") };
}

function cocktailEditor(cocktail) {
  const source = cocktail.source || {};
  const ingredientSummary = cocktail.requirements
    .map((requirement) => {
      const status = requirementStatus(requirement);
      return `<span class="summary-token ${status.key}">${escapeHtml(status.label)}</span>`;
    })
    .join("");
  return `<article class="editor-card ${cocktail.is_available ? "" : "editor-card-unavailable"}" data-editor-card="${cocktail.id}"><button class="editor-summary editor-summary-cocktail" type="button" data-toggle-editor="${cocktail.id}"><img class="editor-thumb" src="${cocktail.image_url || 'https://placehold.co/72x72/f4ead8/7a5c45?text=%20'}" alt="${escapeHtml(cocktail.name)}" /><div class="compact-main"><strong>${cocktail.name}${cocktail.is_favorite ? ' <span class="favorite-star">&#9733;</span>' : ""}</strong><span class="muted">${cocktail.rating.toFixed(1)} / 5 ${cocktail.is_available ? "" : "· no disponible"}</span><div class="summary-token-row">${ingredientSummary}</div></div></button><div class="editor-body hidden" data-editor-body="${cocktail.id}"><div class="form-grid"><label>Nombre <input data-edit-name="${cocktail.id}" value="${escapeHtml(cocktail.name)}" /></label><label>Foto URL <input data-edit-image="${cocktail.id}" value="${escapeHtml(cocktail.image_url || "")}" /></label><label>Preparación (min) <input data-edit-minutes="${cocktail.id}" type="number" value="${cocktail.prep_time_minutes}" /></label><label>Alcohol <select data-edit-alcohol-level="${cocktail.id}"><option value="Fuerte" ${cocktail.alcohol_level === "Fuerte" ? "selected" : ""}>Fuerte</option><option value="Medio" ${cocktail.alcohol_level === "Medio" ? "selected" : ""}>Medio</option><option value="Suave" ${cocktail.alcohol_level === "Suave" ? "selected" : ""}>Suave</option><option value="Sin alcohol" ${cocktail.alcohol_level === "Sin alcohol" ? "selected" : ""}>Sin alcohol</option></select></label></div><label>Descripcion <textarea data-edit-description="${cocktail.id}" rows="2">${escapeHtml(cocktail.description || "")}</textarea></label><div class="form-grid"><label>Tipo de vaso o copa <input data-edit-glassware="${cocktail.id}" value="${escapeHtml(cocktail.glassware || "")}" placeholder="Copa de coctel, vaso highball..." /></label><label>Tu rating (con votos de comensales: ${cocktail.rating.toFixed(1)}, ${cocktail.guest_rating_count || 0} votos) <input data-edit-rating="${cocktail.id}" type="number" min="0" max="5" step="0.1" value="${cocktail.admin_rating}" /></label><label>Tags separados por coma <input data-edit-tags="${cocktail.id}" value="${escapeHtml(cocktail.tags.join(", "))}" /></label><label>Importado desde <input data-edit-source-provider="${cocktail.id}" value="${escapeHtml(source.provider || "")}" /></label><label>Link fuente <input data-edit-source-url="${cocktail.id}" value="${escapeHtml(source.source_url || "")}" /></label></div><div class="compact-toolbar compact-toolbar-2"><label><input data-edit-favorite="${cocktail.id}" type="checkbox" ${cocktail.is_favorite ? "checked" : ""} /> Favorito</label><label><input data-edit-active="${cocktail.id}" type="checkbox" ${cocktail.is_active ? "checked" : ""} /> Activo</label></div><label>Pasos, uno por linea <textarea data-edit-steps="${cocktail.id}" rows="4">${escapeHtml(cocktail.steps.map((item) => item.instruction).join("\n"))}</textarea></label><div class="details"><div class="row-top"><strong>Ingredientes / reemplazos</strong><button class="secondary mini-button" type="button" data-add-requirement="${cocktail.id}">agregar fila</button></div><div class="requirement-stack" data-requirements-stack="${cocktail.id}">${cocktail.requirements.map((requirement, index) => requirementEditor(requirement, index, `edit-${cocktail.id}`)).join("")}</div></div><div class="row-top" style="margin-top:12px"><button data-save-cocktail="${cocktail.id}">Guardar cambios</button><button class="secondary" data-delete-cocktail="${cocktail.id}">Eliminar coctel</button></div></div></article>`;
}

function renderCatalog(data) {
  cocktailStatsFilters.innerHTML = `<button class="chip ${cocktailFilter === "all" ? "active" : ""}" data-cocktail-filter="all">Todos</button><button class="chip ${cocktailFilter === "available" ? "active" : ""}" data-cocktail-filter="available">Disponibles</button><button class="chip ${cocktailFilter === "unavailable" ? "active" : ""}" data-cocktail-filter="unavailable">No disponibles</button><button class="chip ${cocktailFilter === "one-missing" ? "active" : ""}" data-cocktail-filter="one-missing">Falta 1 ingrediente</button><button class="chip ${cocktailFilter === "favorites" ? "active" : ""}" data-cocktail-filter="favorites">Favoritos</button>`;
  renderAdminTagPicker(data.cocktails);
  renderAdminGlassPicker(data.cocktails);
  const query = normalizeText(cocktailSearchInput.value);
  const ratingMode = cocktailRatingFilter.value;
  const items = sortByName(data.cocktails).filter((cocktail) => {
    const ingredientNames = cocktail.requirements.flatMap((requirement) => requirement.options.map((option) => option.name));
    if (cocktailFilter === "available" && !cocktail.is_available) return false;
    if (cocktailFilter === "unavailable" && cocktail.is_available) return false;
    if (cocktailFilter === "one-missing" && cocktail.requirements.filter((group) => !group.available && !group.optional).length !== 1) return false;
    if (cocktailFilter === "favorites" && !cocktail.is_favorite) return false;
    if (cocktailFavoriteOnly && !cocktail.is_favorite) return false;
    if (cocktailSelectedTag && !(cocktail.tags || []).includes(cocktailSelectedTag)) return false;
    if (cocktailSelectedGlass && cocktail.glassware !== cocktailSelectedGlass) return false;
    if (ratingMode === "0" && Number(cocktail.rating || 0) !== 0) return false;
    if (ratingMode !== "all" && ratingMode !== "0" && Number(cocktail.rating || 0) < Number(ratingMode)) return false;
    return !query || normalizeText(`${cocktail.name} ${cocktail.tags.join(" ")} ${ingredientNames.join(" ")}`).includes(query);
  });
  catalogCocktailGrid.innerHTML = items.length ? items.map(cocktailEditor).join("") : `<div class="empty">No encontre cocteles con ese filtro.</div>`;
}

function suggestionDiffRows(suggestion, cocktail) {
  if (!cocktail) return [{ field: "Coctel", before: "(fue eliminado)", after: "" }];
  const proposed = suggestion.proposed;
  const rows = [];
  const compare = (label, beforeVal, afterVal) => {
    const before = (beforeVal ?? "").toString().trim();
    const after = (afterVal ?? "").toString().trim();
    if (before !== after) rows.push({ field: label, before, after });
  };
  compare("Nombre", cocktail.name, proposed.name);
  compare("Descripcion", cocktail.description, proposed.description);
  compare("Foto URL", cocktail.image_url, proposed.image_url);
  compare("Preparacion (min)", cocktail.prep_time_minutes, proposed.prep_time_minutes);
  compare("Alcohol", cocktail.alcohol_level, proposed.alcohol_level);
  compare("Vaso/copa", cocktail.glassware, proposed.glassware);
  compare("Tags", (cocktail.tags || []).join(", "), (proposed.tags || []).join(", "));
  compare(
    "Pasos",
    cocktail.steps.map((step) => step.instruction).join(" / "),
    (proposed.steps || []).map((step) => (step || "").trim()).filter(Boolean).join(" / "),
  );
  const source = cocktail.source || {};
  compare("Fuente", source.provider, proposed.source_provider);
  compare("Link fuente", source.source_url, proposed.source_url);
  const currentRequirements = cocktail.requirements
    .map((requirement) => `${requirement.amount || ""} ${requirement.unit || ""} ${requirement.options.map((option) => option.name).join(" o ")}${requirement.optional ? " (opcional)" : ""}`.trim())
    .join(" | ");
  const proposedRequirements = (proposed.requirements || [])
    .map((requirement) => `${requirement.amount || ""} ${requirement.unit || ""} ${(requirement.options || []).join(" o ")}${requirement.optional ? " (opcional)" : ""}`.trim())
    .join(" | ");
  compare("Ingredientes", currentRequirements, proposedRequirements);
  return rows;
}

function renderSuggestions(data) {
  const pending = (data.suggestions || []).filter((item) => item.status === "pending");
  if (!pending.length) {
    suggestionsList.innerHTML = `<div class="empty">No hay propuestas pendientes.</div>`;
    return;
  }
  suggestionsList.innerHTML = pending
    .map((suggestion) => {
      const cocktail = data.cocktails.find((item) => item.id === suggestion.cocktail_id);
      const rows = suggestionDiffRows(suggestion, cocktail);
      const diffHtml = rows.length
        ? rows
            .map(
              (row) =>
                `<div class="suggestion-diff-row"><span class="suggestion-diff-field">${escapeHtml(row.field)}:</span> <span class="suggestion-diff-before">${escapeHtml(row.before || "(vacio)")}</span> &rarr; <span class="suggestion-diff-after">${escapeHtml(row.after || "(vacio)")}</span></div>`,
            )
            .join("")
        : `<div class="muted">Sin cambios detectables.</div>`;
      return `
        <article class="suggestion-card">
          <div class="suggestion-meta">
            <strong>${escapeHtml(suggestion.cocktail_name)}</strong>
            <span class="muted">${escapeHtml(suggestion.submitted_by || "Anonimo")} &middot; ${escapeHtml(suggestion.submitted_at)}</span>
          </div>
          <div class="suggestion-diff">${diffHtml}</div>
          <div class="row-top">
            <button data-accept-suggestion="${suggestion.id}">Aprobar</button>
            <button class="secondary" data-reject-suggestion="${suggestion.id}">Rechazar</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderLists(data) {
  publicListsPanel.innerHTML = data.lists.length ? data.lists.map((item) => `<div class="compact-row compact-row-3"><div class="compact-main"><strong>${item.name}</strong><span class="muted">${item.description || "sin descripcion"}</span></div><span class="pill">publica</span></div>`).join("") : `<div class="empty">No hay listas publicas.</div>`;
}

async function loadDashboard() {
  const response = await fetch("/api/admin/dashboard");
  if (response.status === 401) {
    loginView.classList.remove("hidden");
    adminView.classList.add("hidden");
    return;
  }
  dashboardData = await response.json();
  Object.keys(ingredientReplacementDrafts).forEach((key) => delete ingredientReplacementDrafts[key]);
  loginView.classList.add("hidden");
  adminView.classList.remove("hidden");
  buildIngredientDatalist();
  buildUnitDatalist();
  renderStats(dashboardData);
  renderNotice();
  renderAdminViewModes();
  renderLeftPanelModes();
  renderCocktailFavoriteToggle();
  renderInventory(dashboardData);
  renderShopping(dashboardData);
  renderCatalog(dashboardData);
  renderSuggestions(dashboardData);
  renderLists(dashboardData);
  if (!newCocktailRequirements.children.length) {
    newCocktailRequirements.innerHTML = requirementEditor({ amount: "", unit: "", options: [], optional: false }, 1, "new");
  }
}

function collectRequirementRows(cocktailId) {
  const stack = cocktailId === "new" ? newCocktailRequirements : document.querySelector(`[data-requirements-stack="${cocktailId}"]`);
  return [...stack.querySelectorAll(".requirement-editor")].map((row, index) => ({
    group_key: `group-${index + 1}`,
    amount: row.querySelector('[data-field="amount"]').value,
    unit: row.querySelector('[data-field="unit"]').value,
    options: row.querySelector('[data-field="options"]').value.split("|").map((item) => item.trim()).filter(Boolean),
    optional: row.querySelector('[data-field="optional"]').checked,
  })).filter((row) => row.options.length);
}

async function updateIngredientState(ingredientId) {
  const ingredient = dashboardData.ingredients.find((item) => item.id === ingredientId);
  const stockChecked = document.querySelector(`[data-stock-toggle="${ingredientId}"]`)?.checked || false;
  const lowChecked = document.querySelector(`[data-low-toggle="${ingredientId}"]`)?.checked || false;
  let shoppingChecked = document.querySelector(`[data-shopping-toggle="${ingredientId}"]`)?.checked || false;
  if (stockChecked) {
    shoppingChecked = false;
  }
  await postJson("/api/admin/inventory", {
    ingredient_id: ingredientId,
    in_stock: stockChecked,
    low_stock: lowChecked,
    quantity_label: ingredient.quantity_label || "",
  });
  if (shoppingChecked || ingredientShoppingChecked(ingredientId)) {
    await postJson("/api/admin/shopping", {
      ingredient_id: ingredientId,
      note: "Marcado desde admin",
      done: !shoppingChecked,
    });
  }
  await loadDashboard();
}

function resolveMergeTargetId(sourceId, rawInputValue = null) {
  const rawValue = rawInputValue ?? document.querySelector(`[data-merge-target-input="${sourceId}"]`)?.value ?? "";
  const idMatch = rawValue.match(/\[(\d+)\]\s*$/);
  if (idMatch) {
    return Number(idMatch[1]);
  }
  const normalized = normalizeText(rawValue.replace(/\s*\([^)]*\)\s*$/, "").replace(/\s*\[[^\]]*\]\s*$/, ""));
  if (!normalized) return 0;
  const match = sortByName(dashboardData.ingredients).find((item) => item.id !== sourceId && normalizeText(item.name) === normalized);
  return match ? match.id : 0;
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
cocktailRatingFilter.addEventListener("change", () => dashboardData && renderCatalog(dashboardData));
cocktailTagSearchInput.addEventListener("input", () => renderAdminTagPicker());
cocktailGlassSearchInput.addEventListener("input", () => renderAdminGlassPicker());
cocktailFavoriteFilter.addEventListener("click", () => {
  cocktailFavoriteOnly = !cocktailFavoriteOnly;
  renderCocktailFavoriteToggle();
  if (dashboardData) renderCatalog(dashboardData);
});
cocktailTagFilterButton.addEventListener("click", () => {
  cocktailTagFilterPanel.classList.toggle("hidden");
  cocktailGlassFilterPanel.classList.add("hidden");
});
cocktailGlassFilterButton.addEventListener("click", () => {
  cocktailGlassFilterPanel.classList.toggle("hidden");
  cocktailTagFilterPanel.classList.add("hidden");
});
document.addEventListener("click", (event) => {
  if (!event.target.closest('[data-picker="admin-tag"]')) cocktailTagFilterPanel.classList.add("hidden");
  if (!event.target.closest('[data-picker="admin-glass"]')) cocktailGlassFilterPanel.classList.add("hidden");
});

document.addEventListener("click", async (event) => {
  const statFilter = event.target.closest("[data-stat-filter]")?.dataset.statFilter;
  const inventoryCat = event.target.closest("[data-inventory-filter]")?.dataset.inventoryFilter;
  const inventoryStock = event.target.closest("[data-inventory-stock]")?.dataset.inventoryStock;
  const cocktailStat = event.target.closest("[data-cocktail-filter]")?.dataset.cocktailFilter;
  const adminView = event.target.closest("[data-admin-view]")?.dataset.adminView;
  const leftPanel = event.target.closest("[data-left-panel]")?.dataset.leftPanel;
  const toggleEditor = event.target.closest("[data-toggle-editor]")?.dataset.toggleEditor;
  const toggleIngredient = event.target.closest("[data-toggle-ingredient]")?.dataset.toggleIngredient;
  const addRequirement = event.target.dataset.addRequirement;
  const removeRequirement = event.target.dataset.removeRequirement;
  const saveCocktail = event.target.dataset.saveCocktail;
  const saveIngredient = event.target.dataset.saveIngredient;
  const addIngredientReplacement = event.target.dataset.addIngredientReplacement;
  const removeIngredientReplacement = event.target.dataset.removeIngredientReplacement;
  const mergeIngredient = event.target.dataset.mergeIngredient;
  const deleteIngredient = event.target.dataset.deleteIngredient;
  const deleteCocktail = event.target.dataset.deleteCocktail;
  const acceptSuggestion = event.target.dataset.acceptSuggestion;
  const rejectSuggestion = event.target.dataset.rejectSuggestion;

  if (event.target.matches('input[type="checkbox"]')) return;
  if (acceptSuggestion) {
    try {
      await postJson("/api/admin/suggestions/accept", { suggestion_id: Number(acceptSuggestion) });
      adminNotice = "Propuesta aprobada y aplicada.";
    } catch (error) {
      adminNotice = error.message.includes("ingredient_not_found") ? "La propuesta tiene un ingrediente no valido; revisala manualmente antes de aprobar." : "No pude aprobar la propuesta.";
    }
    await loadDashboard();
    return;
  }
  if (rejectSuggestion) {
    await postJson("/api/admin/suggestions/reject", { suggestion_id: Number(rejectSuggestion) });
    adminNotice = "Propuesta rechazada.";
    await loadDashboard();
    return;
  }
  if (adminView) {
    adminViewMode = adminView;
    renderStats(dashboardData);
    renderAdminViewModes();
    renderLeftPanelModes();
    return;
  }
  if (leftPanel) {
    leftPanelMode = leftPanel;
    renderStats(dashboardData);
    renderLeftPanelModes();
    return;
  }
  if (statFilter) {
    if (["stock", "low", "shopping"].includes(statFilter)) {
      adminViewMode = "ingredients";
      leftPanelMode = statFilter === "shopping" ? "shopping" : "ingredients";
      if (statFilter === "stock") {
        inventoryStockOnly = true;
        inventoryFilter = "all";
      } else {
        inventoryStockOnly = false;
        inventoryFilter = statFilter;
      }
    }
    if (statFilter === "available") {
      adminViewMode = adminViewMode === "ingredients" ? "both" : adminViewMode;
      cocktailFilter = "available";
    }
    if (statFilter === "catalog") {
      adminViewMode = adminViewMode === "ingredients" ? "both" : adminViewMode;
      cocktailFilter = "all";
    }
    if (statFilter === "one-missing") {
      adminViewMode = adminViewMode === "ingredients" ? "both" : adminViewMode;
      cocktailFilter = "one-missing";
      cocktailSearchInput.value = "";
    }
    renderStats(dashboardData);
    renderAdminViewModes();
    renderInventory(dashboardData);
    renderCatalog(dashboardData);
    renderLeftPanelModes();
    return;
  }
  if (inventoryCat !== undefined) {
    inventoryFilter = inventoryCat;
    if (inventoryCat === "all") {
      // keep stock chip as-is so it can combinarse con Todos/otras categorias
    }
    renderInventory(dashboardData);
    return;
  }
  if (inventoryStock !== undefined) {
    inventoryStockOnly = !inventoryStockOnly;
    renderInventory(dashboardData);
    return;
  }
  if (cocktailStat) { cocktailFilter = cocktailStat; renderCatalog(dashboardData); return; }
  if (toggleEditor) {
    const body = document.querySelector(`[data-editor-body="${toggleEditor}"]`);
    const willOpen = body.classList.contains("hidden");
    document.querySelectorAll("[data-editor-body]").forEach((item) => item.classList.add("hidden"));
    if (willOpen) body.classList.remove("hidden");
    return;
  }
  if (toggleIngredient) {
    const body = document.querySelector(`[data-ingredient-editor="${toggleIngredient}"]`);
    const willOpen = body.classList.contains("hidden");
    document.querySelectorAll("[data-ingredient-editor]").forEach((item) => item.classList.add("hidden"));
    if (willOpen) body.classList.remove("hidden");
    return;
  }
  if (addRequirement) {
    document.querySelector(`[data-requirements-stack="${addRequirement}"]`).insertAdjacentHTML("beforeend", requirementEditor({ amount: "", unit: "", options: [], optional: false }, Date.now(), `edit-${addRequirement}`));
    return;
  }
  if (removeRequirement) { event.target.closest(".requirement-editor").remove(); return; }
  if (saveIngredient) {
    const id = Number(saveIngredient);
    const ingredient = dashboardData.ingredients.find((item) => item.id === id);
    const categorySelect = document.querySelector(`[data-edit-ingredient-category-select="${id}"]`);
    const categoryInput = document.querySelector(`[data-edit-ingredient-category-input="${id}"]`);
    const categoryValue = (categorySelect?.value === "__new__" ? categoryInput?.value : categorySelect?.value || ingredient.category || ingredient.normalized_category || "").trim();
    await postJson("/api/admin/ingredient-save", {
      ingredient_id: id,
      name: document.querySelector(`[data-edit-ingredient-name="${id}"]`).value,
      image_url: document.querySelector(`[data-edit-ingredient-image="${id}"]`).value,
      tags: [],
      category: categoryValue,
      replacement_ingredient_ids: draftReplacementsForIngredient(ingredient),
    });
    adminNotice = "Ingrediente guardado.";
    await loadDashboard();
    return;
  }
  if (addIngredientReplacement) {
    const id = Number(addIngredientReplacement);
    const ingredient = dashboardData.ingredients.find((item) => item.id === id);
    const input = document.querySelector(`[data-add-ingredient-replacement-input="${id}"]`);
    const targetId = resolveMergeTargetId(id, input?.value || "");
    if (!targetId) {
      adminNotice = "Selecciona un ingrediente valido para agregar como reemplazo.";
      renderNotice();
      return;
    }
    const draft = draftReplacementsForIngredient(ingredient);
    if (!draft.includes(targetId)) draft.push(targetId);
    if (input) input.value = "";
    renderInventory(dashboardData);
    document.querySelector(`[data-ingredient-editor="${id}"]`)?.classList.remove("hidden");
    return;
  }
  if (removeIngredientReplacement) {
    const id = Number(removeIngredientReplacement);
    const ingredient = dashboardData.ingredients.find((item) => item.id === id);
    const replacementId = Number(event.target.dataset.replacementId);
    ingredientReplacementDrafts[id] = draftReplacementsForIngredient(ingredient).filter((item) => item !== replacementId);
    renderInventory(dashboardData);
    document.querySelector(`[data-ingredient-editor="${id}"]`)?.classList.remove("hidden");
    return;
  }
  if (mergeIngredient) {
    const sourceId = Number(mergeIngredient);
    const targetId = resolveMergeTargetId(sourceId);
    if (targetId) {
      const result = await postJson("/api/admin/ingredient-merge", { source_ingredient_id: sourceId, target_ingredient_id: targetId });
      adminNotice = `Ingrediente fusionado: ${result.removed_ingredient_name} -> ${result.target_ingredient_name}. Cocteles actualizados: ${result.updated_cocktails}.`;
      await loadDashboard();
    } else {
      adminNotice = "Selecciona un ingrediente valido para fusionar.";
      renderNotice();
    }
    return;
  }
  if (deleteIngredient) {
    await postJson("/api/admin/ingredient-delete", { ingredient_id: Number(deleteIngredient) });
    await loadDashboard();
    return;
  }
  if (saveCocktail) {
    const id = Number(saveCocktail);
    try {
      await postJson("/api/admin/cocktail-save", {
        cocktail_id: id,
        name: document.querySelector(`[data-edit-name="${id}"]`).value,
        description: document.querySelector(`[data-edit-description="${id}"]`).value,
        image_url: document.querySelector(`[data-edit-image="${id}"]`).value,
        prep_time_minutes: Number(document.querySelector(`[data-edit-minutes="${id}"]`).value || 5),
        alcohol_level: document.querySelector(`[data-edit-alcohol-level="${id}"]`).value,
        glassware: document.querySelector(`[data-edit-glassware="${id}"]`).value,
        rating: Number(document.querySelector(`[data-edit-rating="${id}"]`).value || 0),
        is_favorite: document.querySelector(`[data-edit-favorite="${id}"]`).checked,
        is_active: document.querySelector(`[data-edit-active="${id}"]`).checked,
        tags: document.querySelector(`[data-edit-tags="${id}"]`).value.split(",").map((item) => item.trim()),
        steps: document.querySelector(`[data-edit-steps="${id}"]`).value.split("\n"),
        source_provider: document.querySelector(`[data-edit-source-provider="${id}"]`).value,
        source_url: document.querySelector(`[data-edit-source-url="${id}"]`).value,
        requirements: collectRequirementRows(id),
      });
      adminNotice = "Coctel guardado.";
      await loadDashboard();
    } catch (error) {
      adminNotice = error.message.includes("ingredient_not_found") ? "Hay un ingrediente no valido en la receta. Usa solo ingredientes existentes." : "No pude guardar el coctel.";
      renderNotice();
    }
    return;
  }
  if (deleteCocktail) {
    await postJson("/api/admin/cocktail-delete", { cocktail_id: Number(deleteCocktail) });
    await loadDashboard();
  }
});

document.addEventListener("change", async (event) => {
  const stockToggle = event.target.dataset.stockToggle;
  const lowToggle = event.target.dataset.lowToggle;
  const shoppingToggle = event.target.dataset.shoppingToggle;
  const shoppingDoneId = event.target.dataset.shoppingDone;
  const categorySelectId = event.target.dataset.editIngredientCategorySelect;
  if (categorySelectId) {
    const input = document.querySelector(`[data-edit-ingredient-category-input="${categorySelectId}"]`);
    if (input) {
      input.classList.toggle("hidden", event.target.value !== "__new__");
      if (event.target.value !== "__new__") input.value = "";
    }
    return;
  }
  if (stockToggle || lowToggle || shoppingToggle) {
    await updateIngredientState(Number(stockToggle || lowToggle || shoppingToggle));
    return;
  }
  if (shoppingDoneId) {
    const ingredientId = Number(shoppingDoneId);
    if (event.target.checked) {
      await postJson("/api/admin/inventory", {
        ingredient_id: ingredientId,
        in_stock: true,
        low_stock: false,
        quantity_label: "",
      });
      await postJson("/api/admin/shopping", {
        ingredient_id: ingredientId,
        note: "Marcado desde lista de compras",
        done: true,
      });
      adminNotice = "Ingrediente marcado como comprado y pasado a stock.";
    } else {
      await postJson("/api/admin/shopping", { ingredient_id: ingredientId, note: "Marcado desde lista de compras", done: false });
      adminNotice = "Ingrediente devuelto a la lista de compras.";
    }
    await loadDashboard();
  }
});

document.getElementById("saveCocktailButton").addEventListener("click", async () => {
  try {
    await postJson("/api/admin/cocktails", {
      name: document.getElementById("newCocktailName").value,
      description: document.getElementById("newCocktailDescription").value,
      image_url: document.getElementById("newCocktailImage").value,
      prep_time_minutes: Number(document.getElementById("newCocktailMinutes").value || 5),
      alcohol_level: document.getElementById("newCocktailAlcoholLevel").value,
      glassware: document.getElementById("newCocktailGlassware").value,
      instructions: document.getElementById("newCocktailInstructions").value,
      steps: newCocktailSteps.value.split("\n"),
      requirements: collectRequirementRows("new"),
    });
    adminNotice = "Coctel creado.";
    newCocktailRequirements.innerHTML = requirementEditor({ amount: "", unit: "", options: [], optional: false }, 1, "new");
    newCocktailSteps.value = "";
    await loadDashboard();
  } catch (error) {
    adminNotice = error.message.includes("ingredient_not_found") ? "Hay un ingrediente no valido en la receta nueva. Usa solo ingredientes existentes." : "No pude crear el coctel.";
    renderNotice();
  }
});

addNewRequirementButton.addEventListener("click", () => {
  newCocktailRequirements.insertAdjacentHTML("beforeend", requirementEditor({ amount: "", unit: "", options: [], optional: false }, Date.now(), "new"));
});

document.getElementById("saveListButton").addEventListener("click", async () => {
  await postJson("/api/admin/lists", { name: document.getElementById("newListName").value, description: document.getElementById("newListDescription").value, is_public: true });
  await loadDashboard();
});

fetch("/api/session").then((response) => response.json()).then((session) => { if (session.authenticated) loadDashboard(); });
