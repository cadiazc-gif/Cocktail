const grid = document.getElementById("cocktailGrid");
const filtersToggle = document.getElementById("filtersToggle");
const filtersPanel = document.getElementById("filtersPanel");
const globalSearch = document.getElementById("globalSearch");
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
let lastFetchedCocktails = [];

function normalizeText(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "");
}

function cocktailSearchHaystack(cocktail) {
  if (!cocktail._searchHaystack) {
    const ingredientNames = cocktail.requirements
      .flatMap((requirement) => requirement.options.map((option) => option.name))
      .join(" ");
    const stepsText = cocktail.steps.map((step) => step.instruction).join(" ");
    cocktail._searchHaystack = normalizeText(
      [cocktail.name, cocktail.description, ingredientNames, (cocktail.tags || []).join(" "), cocktail.glassware, stepsText].join(" ")
    );
  }
  return cocktail._searchHaystack;
}

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
    <svg class="gauge-icon" viewBox="0 0 24 24" width="34" height="34" aria-hidden="true">
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
    <svg class="gauge-icon" viewBox="0 0 24 24" width="34" height="34" aria-hidden="true">
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

function showToast(message) {
  let root = document.getElementById("publicToastRoot");
  if (!root) {
    root = document.createElement("div");
    root.id = "publicToastRoot";
    root.className = "public-toast-root";
    document.body.appendChild(root);
  }
  const toast = document.createElement("div");
  toast.className = "public-toast";
  toast.textContent = message;
  root.appendChild(toast);
  setTimeout(() => toast.remove(), 2600);
}

function localVotes() {
  try {
    return JSON.parse(localStorage.getItem("cocktail_votes") || "{}");
  } catch (err) {
    return {};
  }
}

function saveLocalVote(cocktailId, rating) {
  const votes = localVotes();
  votes[cocktailId] = rating;
  localStorage.setItem("cocktail_votes", JSON.stringify(votes));
}

function getGuestName() {
  return localStorage.getItem("guest_display_name") || "";
}

function setGuestName(name) {
  localStorage.setItem("guest_display_name", name || "");
}

function clickableStars(cocktail) {
  const votes = localVotes();
  const myVote = votes[cocktail.id] || 0;
  const stars = [1, 2, 3, 4, 5]
    .map((n) => `<button type="button" class="vote-star ${n <= myVote ? "active" : ""}" data-vote-star="${n}" data-vote-cocktail="${cocktail.id}" aria-label="Calificar con ${n}">&#9733;</button>`)
    .join("");
  return `
    <div class="vote-row">
      <span class="vote-label">${myVote ? "Tu voto:" : "Calificar:"}</span>
      <span class="vote-stars">${stars}</span>
    </div>
  `;
}

async function castVote(cocktailId, rating) {
  const votes = localVotes();
  const previous = votes[cocktailId] || null;
  const card = grid.querySelector(`[data-cocktail-card][data-id="${cocktailId}"]`);
  const wasExpanded = card ? card.classList.contains("expanded") : false;
  try {
    const response = await fetch("/api/public/cocktail-vote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cocktail_id: cocktailId, rating, previous_rating: previous }),
    });
    if (!response.ok) throw new Error("vote_failed");
    const data = await response.json();
    saveLocalVote(cocktailId, rating);
    const cocktail = lastFetchedCocktails.find((item) => item.id === cocktailId);
    if (cocktail) cocktail.rating = data.rating;
    if (cocktail && card) {
      card.outerHTML = cardTemplate(cocktail);
      if (wasExpanded) {
        const newCard = grid.querySelector(`[data-cocktail-card][data-id="${cocktailId}"]`);
        if (newCard) {
          newCard.classList.add("expanded");
          newCard.querySelector("[data-expanded]")?.classList.remove("hidden");
        }
      }
    }
    showToast("¡Gracias por tu voto!");
  } catch (err) {
    showToast("No se pudo registrar tu voto.");
  }
}

function requirementEditorRow(requirement, index) {
  const optionNames = (requirement.options || []).map((option) => (typeof option === "string" ? option : option.name)).filter(Boolean);
  const rowKey = `sugg-${index}-${Date.now()}`;
  return `<div class="requirement-editor" data-requirement-row="${rowKey}">
    <input data-field="amount" value="${requirement.amount || ""}" placeholder="cantidad" />
    <input data-field="unit" value="${requirement.unit || ""}" placeholder="unidad" />
    <input data-field="options" value="${optionNames.join(" | ")}" placeholder="ingrediente o reemplazos (separa con |)" />
    <div class="requirement-actions">
      <label class="toggle-chip"><input data-field="optional" type="checkbox" ${requirement.optional ? "checked" : ""} /> <span>Opcional</span></label>
      <button class="secondary mini-button" type="button" data-remove-requirement="${rowKey}">Quitar</button>
    </div>
  </div>`;
}

function collectSuggestRequirementRows(container) {
  return [...container.querySelectorAll(".requirement-editor")]
    .map((row) => ({
      group_key: "",
      amount: row.querySelector('[data-field="amount"]').value,
      unit: row.querySelector('[data-field="unit"]').value,
      options: row.querySelector('[data-field="options"]').value.split("|").map((item) => item.trim()).filter(Boolean),
      optional: row.querySelector('[data-field="optional"]').checked,
    }))
    .filter((row) => row.options.length);
}

function openSuggestForm(cocktail) {
  const overlay = document.createElement("div");
  overlay.className = "public-modal-overlay";
  overlay.innerHTML = `
    <div class="public-modal-card">
      <h2 class="public-modal-title">Proponer cambio: ${cocktail.name}</h2>
      <div class="public-modal-field"><label>Tu nombre (opcional)</label><input id="suggestName" value="${getGuestName()}" /></div>
      <div class="public-modal-field"><label>Nombre del cóctel</label><input id="suggestCocktailName" value="${cocktail.name}" /></div>
      <div class="public-modal-field"><label>Descripción</label><textarea id="suggestDescription" rows="2">${cocktail.description || ""}</textarea></div>
      <div class="public-modal-field"><label>Foto URL</label><input id="suggestImage" value="${cocktail.image_url || ""}" /></div>
      <div class="public-modal-field"><label>Preparación (min)</label><input id="suggestMinutes" type="number" value="${cocktail.prep_time_minutes}" /></div>
      <div class="public-modal-field"><label>Alcohol</label>
        <select id="suggestAlcohol">
          ${["Fuerte", "Medio", "Suave", "Sin alcohol"].map((level) => `<option value="${level}" ${cocktail.alcohol_level === level ? "selected" : ""}>${level}</option>`).join("")}
        </select>
      </div>
      <div class="public-modal-field"><label>Vaso o copa</label><input id="suggestGlassware" value="${cocktail.glassware || ""}" /></div>
      <div class="public-modal-field"><label>Tags separados por coma</label><input id="suggestTags" value="${(cocktail.tags || []).join(", ")}" /></div>
      <div class="public-modal-field"><label>Pasos, uno por línea</label><textarea id="suggestSteps" rows="4">${(cocktail.steps || []).map((step) => step.instruction).join("\n")}</textarea></div>
      <div class="details">
        <div class="row-top">
          <strong>Ingredientes / reemplazos</strong>
          <button class="secondary mini-button" type="button" id="suggestAddRequirement">agregar fila</button>
        </div>
        <div id="suggestRequirements" class="requirement-stack">
          ${cocktail.requirements.map((requirement, index) => requirementEditorRow(requirement, index)).join("")}
        </div>
      </div>
      <div class="public-modal-actions">
        <button class="secondary" id="suggestCancel" type="button">Cancelar</button>
        <button id="suggestSubmit" type="button">Enviar propuesta</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) overlay.remove();
    const removeBtn = event.target.closest("[data-remove-requirement]");
    if (removeBtn) removeBtn.closest(".requirement-editor").remove();
  });
  document.getElementById("suggestCancel").addEventListener("click", () => overlay.remove());
  document.getElementById("suggestAddRequirement").addEventListener("click", () => {
    document.getElementById("suggestRequirements").insertAdjacentHTML("beforeend", requirementEditorRow({ amount: "", unit: "", options: [], optional: false }, Date.now()));
  });
  document.getElementById("suggestSubmit").addEventListener("click", async () => {
    const name = document.getElementById("suggestName").value.trim();
    setGuestName(name);
    const payload = {
      cocktail_id: cocktail.id,
      submitted_by: name,
      name: document.getElementById("suggestCocktailName").value,
      description: document.getElementById("suggestDescription").value,
      image_url: document.getElementById("suggestImage").value,
      prep_time_minutes: Number(document.getElementById("suggestMinutes").value || 5),
      alcohol_level: document.getElementById("suggestAlcohol").value,
      glassware: document.getElementById("suggestGlassware").value,
      tags: document.getElementById("suggestTags").value.split(",").map((tag) => tag.trim()).filter(Boolean),
      steps: document.getElementById("suggestSteps").value.split("\n"),
      requirements: collectSuggestRequirementRows(document.getElementById("suggestRequirements")),
    };
    try {
      const response = await fetch("/api/public/cocktail-suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || "request_failed");
      }
      overlay.remove();
      showToast("¡Gracias! Tu propuesta quedó pendiente de revisión.");
    } catch (err) {
      showToast(err.message === "ingredient_not_found" ? "Hay un ingrediente que no reconozco en la receta." : "No se pudo enviar la propuesta.");
    }
  });
}

function cardTemplate(cocktail) {
  const ingredientsSummary = summaryIngredients(cocktail);
  const missingLine = cocktail.is_available
    ? ""
    : `<p class="menu-missing"><strong>Falta:</strong> ${missingIngredientNames(cocktail).join(", ")}</p>`;
  const tags = cocktail.tags.map((tag) => `<span class="tag">${tag}</span>`).join("");
  const detailIngredients = cocktail.requirements
    .map((requirement) => detailIngredient(requirement))
    .join("");
  const steps = cocktail.steps.length
    ? cocktail.steps.map((step) => `<div class="detail-line"><strong>${step.step_number}.</strong> ${step.instruction}</div>`).join("")
    : `<div class="detail-line muted">Sin pasos cargados.</div>`;

  return `
    <article class="menu-card${cocktail.is_available ? "" : " menu-card-unavailable"}" data-cocktail-card data-id="${cocktail.id}">
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
          ${missingLine}
        </div>
      </button>
      <div class="menu-expanded hidden" data-expanded>
        <div class="menu-expanded-head">
          <img class="menu-expanded-image" src="${cocktail.image_url}" alt="${cocktail.name}" data-toggle-card />
          <div class="menu-expanded-info">
            <h2 data-toggle-card tabindex="0">${cocktail.name} ${star(cocktail)}</h2>
            <p>${cocktail.description}</p>
            ${metaStrip(cocktail)}
            ${clickableStars(cocktail)}
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
        <div class="row-top" style="margin-top:14px">
          <button class="secondary mini-button" type="button" data-suggest-change="${cocktail.id}">Proponer un cambio</button>
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
    heroCount.textContent = cocktails.filter((cocktail) => cocktail.is_available).length;
  }
}

function missingIngredientNames(cocktail) {
  return cocktail.requirements
    .filter((requirement) => requirementStatus(requirement).key === "missing")
    .map((requirement) => requirement.options.map((option) => option.name).join(" o "));
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
    applyFiltersAndRender();
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
    applyFiltersAndRender();
  });
}

async function loadLists() {
  const response = await fetch("/api/public/lists");
  const data = await response.json();
  listFilter.innerHTML =
    `<option value="">Todas las listas</option>` +
    data.lists.map((item) => `<option value="${item.id}">${item.name}</option>`).join("");
}

function applyFiltersAndRender() {
  const query = normalizeText(globalSearch.value.trim());
  const items = lastFetchedCocktails.filter((cocktail) => {
    if (selectedTag && !(cocktail.tags || []).includes(selectedTag)) return false;
    if (selectedGlass && cocktail.glassware !== selectedGlass) return false;
    if (favoriteOnly && !cocktail.is_favorite) return false;
    if (ratingFilter.value === "0") {
      if (Number(cocktail.rating || 0) !== 0) return false;
    } else if (ratingFilter.value !== "all" && Number(cocktail.rating || 0) < Number(ratingFilter.value)) {
      return false;
    }
    if (query && !cocktailSearchHaystack(cocktail).includes(query)) return false;
    return true;
  });
  items.sort((left, right) => {
    const availabilityDiff = Number(right.is_available) - Number(left.is_available);
    if (availabilityDiff !== 0) return availabilityDiff;
    if (sortFilter.value === "alpha-asc") {
      return left.name.localeCompare(right.name, "es", { sensitivity: "base" });
    }
    const favoriteDiff = Number(right.is_favorite) - Number(left.is_favorite);
    if (favoriteDiff !== 0) return favoriteDiff;
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

async function loadCocktails() {
  const params = new URLSearchParams({
    ingredient: ingredientFilter.value.trim(),
    alcohol: alcoholFilter.value,
    list_id: listFilter.value,
  });

  const response = await fetch(`/api/public/cocktails?${params.toString()}`);
  const data = await response.json();
  lastFetchedCocktails = data.cocktails;
  renderTagPicker(data.cocktails);
  renderGlassPicker(data.cocktails);
  applyFiltersAndRender();
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
grid.addEventListener("click", (event) => {
  const voteBtn = event.target.closest("[data-vote-star]");
  if (voteBtn) {
    castVote(Number(voteBtn.dataset.voteCocktail), Number(voteBtn.dataset.voteStar));
    return;
  }
  const suggestBtn = event.target.closest("[data-suggest-change]");
  if (suggestBtn) {
    const cocktail = lastFetchedCocktails.find((item) => item.id === Number(suggestBtn.dataset.suggestChange));
    if (cocktail) openSuggestForm(cocktail);
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
globalSearch.addEventListener("input", applyFiltersAndRender);
tagSearchInput.addEventListener("input", () => renderTagPicker());
glassSearchInput.addEventListener("input", () => renderGlassPicker());
[alcoholFilter, listFilter].forEach((input) => input.addEventListener("change", loadCocktails));
[ratingFilter, sortFilter].forEach((input) => input.addEventListener("change", applyFiltersAndRender));
favoriteFilter.addEventListener("click", () => {
  favoriteOnly = !favoriteOnly;
  renderFavoriteToggle();
  applyFiltersAndRender();
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
