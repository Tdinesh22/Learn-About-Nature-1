const API_BASE = "https://api.inaturalist.org/v1/taxa";
const DEFAULT_IMAGE = "https://via.placeholder.com/500x360?text=No+Image";
const RESULTS_PER_PAGE = 24;

const CATEGORY_TAXON_IDS = {
  birds: 3,
  mammals: 40151,
  reptiles: 26036,
  amphibians: 20978,
  insects: 47158,
};

const speciesGrid = document.getElementById("species-grid");
const statusPill = document.getElementById("status-pill");
const emptyState = document.getElementById("empty-state");
const searchInput = document.getElementById("search-input");
const clearBtn = document.getElementById("clear-btn");
const filterButtons = document.querySelectorAll(".filter-btn");

let activeFilter = "all";
let speciesData = [];

const debounce = (fn, delay = 400) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const setStatus = (text, isLoading = false) => {
  statusPill.textContent = text;
  statusPill.classList.toggle("loading", isLoading);
};

const getImageUrl = (taxon) => {
  return taxon.default_photo?.medium_url || taxon.default_photo?.square_url || DEFAULT_IMAGE;
};

const buildCard = (taxon) => {
  const card = document.createElement("article");
  card.className = "species-card";

  card.innerHTML = `
    <img src="${getImageUrl(taxon)}" alt="${taxon.preferred_common_name || taxon.name}">
    <div class="card-body">
      <span class="badge">${taxon.iconic_taxon_name || "Species"}</span>
      <h3>${taxon.preferred_common_name || "Unknown species"}</h3>
      <p class="scientific">${taxon.name || "Scientific name unavailable"}</p>
      <div class="card-actions">
        <button class="view-btn" type="button">View Details</button>
      </div>
    </div>
  `;

  const button = card.querySelector(".view-btn");
  button.addEventListener("click", () => {
    window.location.href = `/species/${taxon.id}/`;
  });
  return card;
};

const renderSpecies = () => {
  speciesGrid.innerHTML = "";

  if (!speciesData.length) {
    emptyState.classList.remove("hidden");
    setStatus("No species found for this filter or search.", false);
    return;
  }

  emptyState.classList.add("hidden");
  speciesData.forEach((taxon) => speciesGrid.appendChild(buildCard(taxon)));
  setStatus(`Showing ${speciesData.length} species`, false);
};

const buildSearchUrl = (query, filter = "all") => {
  const url = new URL(API_BASE);
  if (query) {
    url.searchParams.set("q", query);
  }
  url.searchParams.set("per_page", RESULTS_PER_PAGE.toString());
  url.searchParams.set("rank", "species");

  if (filter !== "all" && CATEGORY_TAXON_IDS[filter]) {
    url.searchParams.set("taxon_id", CATEGORY_TAXON_IDS[filter]);
  }

  return url;
};

const fetchSpecies = async (query = "", filter = "all") => {
  speciesGrid.innerHTML = "";
  emptyState.classList.add("hidden");
  setStatus("Loading species…", true);

  try {
    const response = await fetch(buildSearchUrl(query, filter));
    const data = await response.json();

    speciesData = data.results || [];
    if (!speciesData.length) {
      emptyState.classList.remove("hidden");
      setStatus("No species found. Try another search term.", false);
      return;
    }

    renderSpecies();
  } catch (error) {
    setStatus("Unable to load species. Please try again.", false);
    emptyState.classList.remove("hidden");
    speciesGrid.innerHTML = "";
    console.error("Fetch error:", error);
  }
};

const updateFilter = (filter) => {
  activeFilter = filter;
  filterButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === filter);
  });
  renderSpecies();
};

searchInput.addEventListener(
  "input",
  debounce((event) => {
    const query = event.target.value.trim();
    fetchSpecies(query, activeFilter);
  }, 450)
);

clearBtn.addEventListener("click", () => {
  searchInput.value = "";
  searchInput.focus();
  fetchSpecies("", activeFilter);
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    updateFilter(filter);
    fetchSpecies(searchInput.value.trim(), filter);
  });
});

fetchSpecies("", activeFilter);
