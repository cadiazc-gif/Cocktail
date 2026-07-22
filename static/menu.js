const grid = document.getElementById("cocktailGrid");
const filtersToggle = document.getElementById("filtersToggle");
const filtersPanel = document.getElementById("filtersPanel");
const ingredientFilter = document.getElementById("ingredientFilter");
const tagSearchInput = document.getElementById("tagSearchInput");
const tagFilterButton = document.getElementById("tagFilterButton");
const tagFilterPanel = document.getElementById("tagFilterPanel");
const tagFilterOptions = document.getElementById("tagFilterOptions");
const alcoholFilter = document.getElementById("alcoholFilter");
const glassSearchInput = document.getElementById("glassSearchInput");
const glassFilterButton = document.getElementById("glassFilterButton");
const glassFilterPanel = document.getElementById("glassFilterPanel");
const glassFilterOptions = document.getElementById("glassFilterOptions");
const listFilter = document.getElementById("listFilter");
const favoriteFilter = document.getElementById("favoriteFilter");
const ratingFilter = document.getElementById("ratingFilter");
const sortFilter = document.getElementById("sortFilter");
let favoriteOnly = false;
let availableTags = [];
let availableGlassware = [];
let selectedTag = "";
let selectedGlass = "";

function summaryIngredients(cocktail) {
  return cocktail.requirements
    .map((requirement) => requirement.options.map((option) => option.name).join(" o "))
    .join(", ");
}

function requirementStatus(requirement) {
  const selected = requirement.selected_options || [];
  const direct = selected.find((option) => !option.is_replacement);
  if (direct) {
    return { key: "available", note: "Disponible" };
  }
  const replacement = selected.find((option) => option.is_replacement);
  if (replacement) {
    const original = requirement.options.find((option) => option.ingredient_id === replacement.replaces_ingredient_id);
    return {
      key: "replacement",
      note: `Reemplazado: ${original?.name || "ingrediente"} por ${replacement.name}`,
    };
  }
  if (requirement.optional) {
    return { key: "optional", note: "Opcional" };
  }
  return { key: "missing", note: "Falta este ingrediente" };
}

function detailIngredient(requirement) {
  const amount = requirement.amount ? `${requirement.amount} ` : "";
  const unit = requirement.unit ? `${requirement.unit} ` : "";
  const options = requirement.options.map((option) => option.name).join(" o ");
  const status = requirementStatus(requirement);
  return `
    <div class="detail-ingredient ${status.key}">
      <div class="detail-ingredient-main">${`${amount}${unit}${options}`.trim()}</div>
      <div class="detail-ingredient-note">${status.note}</div>
    </div>
  `;
}

function sourceBlock(cocktail) {
  const source = cocktail.source || {};
  if (!source.provider && !source.source_url) {
    return `<span class="pill">Fuente no indicada</span>`;
  }
  if (source.source_url) {
    return `<a class="pill" href="${source.source_url}" target="_blank" rel="noreferrer">${source.provider || "Ver fuente"}</a>`;
  }
  return `<span class="pill">${source.provider}</span>`;
}

function star(cocktail) {
  return cocktail.is_favorite ? `<span class="favorite-star" title="Favorito">&#9733;</span>` : "";
}

function cardTemplate(cocktail) {
  const ingredientsSummary = summaryIngredients(cocktail);
  const tags = cocktail.tags.map((tag) => `<span class="tag">${tag}</span>`).join("");
  const detailIngredients = cocktail.requirements
    .map((requirement) => detailIngredient(requirement))
    .join("");
  const steps = cocktail.steps.length
    ? cocktail.steps.map((step) => `<div class="detail-line"><strong>${step.step_number}.</strong> ${step.instruction}</div>`).join("")
    : `<div class="detail-line muted">Sin pasos cargados.</div>`;
  const alcoholLabel = cocktail.alcohol_level || "Medio";
  const prepLabel = `${cocktail.prep_time_minutes || 0} min`;

  return `
    <article class="menu-card" data-cocktail-card>
      <button class="menu-summary" type="button" data-toggle-card>
        <img class="menu-thumb" src="${cocktail.image_url}" alt="${cocktail.name}" />
        <div class="menu-summary-content">
          <div class="menu-summary-top">
            <div>
              <h3>${cocktail.name} ${star(cocktail)}</h3>
              <p class="menu-rating">${cocktail.rating.toFixed(1)} / 5</p>
            </div>
          </div>
          <p class="menu-ingredients"><strong>Ingredientes:</strong> ${ingredientsSummary}</p>
        </div>
      </button>
      <div class="menu-expanded hidden" data-expanded>
        <div class="menu-expanded-head">
          <img class="menu-expanded-image" src="${cocktail.image_url}" alt="${cocktail.name}" data-toggle-card />
          <div class="menu-expanded-info">
            <h2 data-toggle-card tabindex="0">${cocktail.name} ${star(cocktail)}</h2>
            <p>${cocktail.description}</p>
            <div class="meta-row">
              <span class="pill">Favorito: ${cocktail.is_favorite ? "Si" : "No"}</span>
              <span class="pill">Rating: ${cocktail.rating.toFixed(1)} / 5</span>
              <span class="pill">Alcohol: ${alcoholLabel}</span>
              <span class="pill">Vaso: ${cocktail.glassware || "No especificado"}</span>
              <span class="pill">Preparación: ${prepLabel}</span>
            </div>
            <div class="meta-row">${sourceBlock(cocktail)}</div>
            <div class="tag-row">${tags}</div>
          </div>
        </div>
        <div class="details details-glass">
          <div class="details-header"><span class="details-icon"></span>Vaso o copa</div>
          <div class="detail-list">
            <div class="detail-line">${cocktail.glassware || "Vaso/copa no especificado"}</div>
          </div>
        </div>
        <div class="details details-ingredients">
          <div class="details-header"><span class="details-icon"></span>Ingredientes con cantidades</div>
          <div class="detail-list">${detailIngredients}</div>
        </div>
        <div class="details details-steps">
          <div class="details-header"><span class="details-icon"></span>Preparación</div>
          <div class="detail-list">${steps}</div>
        </div>
      </div>
    </article>
  `;
}

function renderFavoriteToggle() {
  favoriteFilter.innerHTML = favoriteOnly ? "&#9733;" : "&#9734;";
  favoriteFilter.classList.toggle("active", favoriteOnly);
  favoriteFilter.setAttribute("aria-pressed", favoriteOnly ? "true" : "false");
}

function updateHeroCount(cocktails) {
  const heroCount = document.getElementById("heroCount");
  if (heroCount) {
    heroCount.textContent = cocktails.length;
  }
}

function renderPickerOptions(optionsRoot, values, selectedValue, allLabel, selectFn) {
  optionsRoot.innerHTML =
    `<button class="picker-option ${selectedValue === "" ? "active" : ""}" type="button" data-picker-value="">${allLabel}</button>` +
    values.map((value) => `<button class="picker-option ${selectedValue === value ? "active" : ""}" type="button" data-picker-value="${value}">${value}</button>`).join("");
  optionsRoot.querySelectorAll("[data-picker-value]").forEach((button) => {
    button.addEventListener("click", () => selectFn(button.dataset.pickerValue || ""));
  });
}

function renderTagPicker(cocktails = null) {
  const query = String(tagSearchInput.value || "").trim().toLowerCase();
  if (cocktails) {
    availableTags = [...new Set(cocktails.flatMap((cocktail) => cocktail.tags || []))]
      .sort((left, right) => left.localeCompare(right, "es", { sensitivity: "base" }));
  }
  const filteredTags = availableTags.filter((tag) => !query || tag.toLowerCase().includes(query));
  if (selectedTag && !availableTags.includes(selectedTag)) selectedTag = "";
  tagFilterButton.textContent = selectedTag || "Todos los tags";
  renderPickerOptions(tagFilterOptions, filteredTags, selectedTag, "Todos los tags", (value) => {
    selectedTag = value;
    tagFilterButton.textContent = selectedTag || "Todos los tags";
    tagFilterPanel.classList.add("hidden");
    loadCocktails();
  });
}

function renderGlassPicker(cocktails = null) {
  const query = String(glassSearchInput.value || "").trim().toLowerCase();
  if (cocktails) {
    availableGlassware = [...new Set(cocktails.map((cocktail) => cocktail.glassware).filter(Boolean))]
      .sort((left, right) => left.localeCompare(right, "es", { sensitivity: "base" }));
  }
  const filteredGlassware = availableGlassware.filter((glass) => !query || glass.toLowerCase().includes(query));
  if (selectedGlass && !availableGlassware.includes(selectedGlass)) selectedGlass = "";
  glassFilterButton.textContent = selectedGlass || "Todos los vasos";
  renderPickerOptions(glassFilterOptions, filteredGlassware, selectedGlass, "Todos los vasos", (value) => {
    selectedGlass = value;
    glassFilterButton.textContent = selectedGlass || "Todos los vasos";
    glassFilterPanel.classList.add("hidden");
    loadCocktails();
  });
}

async function loadLists() {
  const response = await fetch("/api/public/lists");
  const data = await response.json();
  listFilter.innerHTML =
    `<option value="">Todas las listas</option>` +
    data.lists.map((item) => `<option value="${item.id}">${item.name}</option>`).join("");
}

async function loadCocktails() {
  const params = new URLSearchParams({
    ingredient: ingredientFilter.value.trim(),
    alcohol: alcoholFilter.value,
    list_id: listFilter.value,
  });

  const response = await fetch(`/api/public/cocktails?${params.toString()}`);
  const data = await response.json();
  renderTagPicker(data.cocktails);
  renderGlassPicker(data.cocktails);
  const items = data.cocktails.filter((cocktail) => {
    if (selectedTag && !(cocktail.tags || []).includes(selectedTag)) return false;
    if (selectedGlass && cocktail.glassware !== selectedGlass) return false;
    if (favoriteOnly && !cocktail.is_favorite) return false;
    if (ratingFilter.value === "0") return Number(cocktail.rating || 0) === 0;
    if (ratingFilter.value !== "all" && ratingFilter.value !== "0" && Number(cocktail.rating || 0) < Number(ratingFilter.value)) return false;
    return true;
  });
  items.sort((left, right) => {
    if (sortFilter.value === "alpha-asc") {
      return left.name.localeCompare(right.name, "es", { sensitivity: "base" });
    }
    const ratingDiff = Number(right.rating || 0) - Number(left.rating || 0);
    if (ratingDiff !== 0) return ratingDiff;
    return left.name.localeCompare(right.name, "es", { sensitivity: "base" });
  });
  updateHeroCount(items);
  if (!items.length) {
    grid.innerHTML = `<div class="empty">No hay cocteles disponibles con esos filtros hoy.</div>`;
    return;
  }
  grid.innerHTML = items.map(cardTemplate).join("");
}

grid.addEventListener("click", (event) => {
  const toggle = event.target.closest("[data-toggle-card]");
  if (!toggle) return;
  const card = toggle.closest("[data-cocktail-card]");
  const expanded = card.querySelector("[data-expanded]");
  const willOpen = expanded.classList.contains("hidden");

  if (!willOpen) {
    card.classList.remove("expanded");
    expanded.classList.add("hidden");
    return;
  }

  grid.querySelectorAll("[data-cocktail-card]").forEach((item) => {
    item.classList.remove("expanded");
    const detail = item.querySelector("[data-expanded]");
    if (detail) detail.classList.add("hidden");
  });

  if (willOpen) {
    expanded.classList.remove("hidden");
    card.classList.add("expanded");
  }
});
grid.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  const toggle = event.target.closest("[data-toggle-card]");
  if (!toggle) return;
  event.preventDefault();
  toggle.click();
});

ingredientFilter.addEventListener("input", loadCocktails);
tagSearchInput.addEventListener("input", () => renderTagPicker());
glassSearchInput.addEventListener("input", () => renderGlassPicker());
[alcoholFilter, listFilter, ratingFilter, sortFilter].forEach((input) => input.addEventListener("change", loadCocktails));
favoriteFilter.addEventListener("click", () => {
  favoriteOnly = !favoriteOnly;
  renderFavoriteToggle();
  loadCocktails();
});
filtersToggle.addEventListener("click", () => {
  const isExpanded = filtersToggle.getAttribute("aria-expanded") === "true";
  filtersToggle.setAttribute("aria-expanded", isExpanded ? "false" : "true");
  filtersPanel.classList.toggle("hidden", isExpanded);
  filtersToggle.closest(".filters").classList.toggle("is-collapsed", isExpanded);
  filtersToggle.querySelector(".filters-toggle-icon").textContent = isExpanded ? "+" : "-";
});
tagFilterButton.addEventListener("click", () => {
  tagFilterPanel.classList.toggle("hidden");
  glassFilterPanel.classList.add("hidden");
});
glassFilterButton.addEventListener("click", () => {
  glassFilterPanel.classList.toggle("hidden");
  tagFilterPanel.classList.add("hidden");
});
document.addEventListener("click", (event) => {
  if (!event.target.closest('[data-picker="public-tag"]')) tagFilterPanel.classList.add("hidden");
  if (!event.target.closest('[data-picker="public-glass"]')) glassFilterPanel.classList.add("hidden");
});

renderFavoriteToggle();
loadLists().then(loadCocktails);
