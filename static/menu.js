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

let iconUid = 0;

function starRating(rating) {
  const safeRating = Math.max(0, Math.min(5, rating || 0));
  const pct = (safeRating / 5) * 100;
  return `
    <span class="star-rating" title="${safeRating.toFixed(1)} / 5">
      <span class="star-row star-row-bg">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
      <span class="star-row star-row-fg" style="width:${pct.toFixed(1)}%">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
    </span>
  `;
}

const ALCOHOL_LEVELS = {
  "Sin alcohol": 0,
  "Suave": 25,
  "Medio": 50,
  "Fuerte": 100,
};

function alcoholPct(level) {
  return level in ALCOHOL_LEVELS ? ALCOHOL_LEVELS[level] : 50;
}

function timePct(minutes) {
  const m = minutes || 0;
  if (m <= 3) return 25;
  if (m <= 6) return 50;
  if (m <= 12) return 75;
  return 100;
}

function glassGaugeIcon(pct) {
  const uid = ++iconUid;
  const bowlTop = 4;
  const bowlBottom = 15;
  const h = ((pct / 100) * (bowlBottom - bowlTop)).toFixed(2);
  const y = (bowlBottom - h).toFixed(2);
  return `
    <svg class="gauge-icon" viewBox="0 0 24 24" width="17" height="17" aria-hidden="true">
      <defs><clipPath id="clip-a-${uid}"><rect x="2" y="${y}" width="20" height="${h}" /></clipPath></defs>
      <path d="M3 4H21L12 15Z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" opacity="0.5" />
      <path d="M3 4H21L12 15Z" fill="currentColor" clip-path="url(#clip-a-${uid})" />
      <path d="M12 15V20M8 20.5H16" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity="0.5" />
    </svg>
  `;
}

function hourglassGaugeIcon(pct) {
  const uid = ++iconUid;
  const bulbTop = 12;
  const bulbBottom = 21;
  const h = ((pct / 100) * (bulbBottom - bulbTop)).toFixed(2);
  const y = (bulbBottom - h).toFixed(2);
  return `
    <svg class="gauge-icon" viewBox="0 0 24 24" width="17" height="17" aria-hidden="true">
      <defs><clipPath id="clip-t-${uid}"><rect x="2" y="${y}" width="20" height="${h}" /></clipPath></defs>
      <path d="M5 3H19M5 21H19" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" opacity="0.5" />
      <path d="M5 3L19 3L12 12L19 21L5 21L12 12Z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" opacity="0.5" />
      <path d="M12 12L19 21L5 21Z" fill="currentColor" clip-path="url(#clip-t-${uid})" />
    </svg>
  `;
}

function metaStrip(cocktail) {
  const alcoholLabel = cocktail.alcohol_level || "Medio";
  const minutes = cocktail.prep_time_minutes || 0;
  return `
    <div class="meta-strip">
      ${starRating(cocktail.rating)}
      <span class="gauge-item alcohol-gauge" title="Alcohol: ${alcoholLabel}">${glassGaugeIcon(alcoholPct(alcoholLabel))}</span>
      <span class="gauge-item time-gauge" title="Preparación: ${minutes} min">${hourglassGaugeIcon(timePct(minutes))}</span>
    </div>
  `;
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

  return `
    <article class="menu-card" data-cocktail-card>
      <button class="menu-summary" type="button" data-toggle-card>
        <img class="menu-thumb" src="${cocktail.image_url}" alt="${cocktail.name}" />
        <div class="menu-summary-content">
          <div class="menu-summary-top">
            <div>
              <h3>${cocktail.name} ${star(cocktail)}</h3>
              ${metaStrip(cocktail)}
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
            ${metaStrip(cocktail)}
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
