const API_BASE = "https://api.inaturalist.org/v1/taxa";
const OBSERVATIONS_BASE = "https://api.inaturalist.org/v1/observations";
const searchInput = document.getElementById("resource-search");
const resultsGrid = document.getElementById("results-grid");
const resultText = document.getElementById("result-text");
const emptyMessage = document.getElementById("empty-message");
const errorMessage = document.getElementById("error-message");
const loader = document.getElementById("resource-loader");
const filterButtons = document.querySelectorAll(".filter-button");

let currentQuery = "";
let currentFilter = null;

const debounce = (fn, delay = 300) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const showLoader = (show) => {
  loader.classList.toggle("hidden", !show);
};

const setStatus = (text) => {
  resultText.textContent = text;
};

const clearResults = () => {
  resultsGrid.innerHTML = "";
  emptyMessage.classList.add("hidden");
  errorMessage.classList.add("hidden");
};

const getObservationImage = (observation) => {
  const photo = observation.photos?.[0];
  if (!photo || !photo.url) {
    return null;
  }
  return photo.url.replace("square", "medium");
};

const buildCard = (item, isObservation = false) => {
  const imageUrl = isObservation ? getObservationImage(item) : null;
  if (!imageUrl) {
    return null;
  }

  const title = item.species_guess || "Unknown species";
  const scientific = item.taxon?.name || "Scientific name unavailable";

  const card = document.createElement("article");
  card.className = "resource-card";
  card.innerHTML = `
    <img src="${imageUrl}" alt="${title}" />
    <div class="card-body">
      <h3>${title}</h3>
      <p class="scientific">${scientific}</p>
    </div>
  `;
  return card;
};

function renderResults(results, isObservation = false) {
  clearResults();

  const cards = results
    .map((item) => buildCard(item, isObservation))
    .filter(Boolean);

  if (!cards.length) {
    setStatus("No results found.");
    emptyMessage.classList.remove("hidden");
    return;
  }

  cards.forEach((card) => resultsGrid.appendChild(card));

  const filterLabel = currentFilter ? ` (${currentFilter.charAt(0).toUpperCase() + currentFilter.slice(1)})` : "";
  setStatus(`Showing ${cards.length} result${cards.length === 1 ? "" : "s"}${filterLabel}`);
}

async function fetchPlants() {
  try {
    const url = new URL(OBSERVATIONS_BASE);
    url.searchParams.set("taxon_id", "47126");
    url.searchParams.set("has[]", "photos");
    url.searchParams.set("per_page", "20");

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();
    return data.results || [];
  } catch (error) {
    throw error;
  }
}

async function fetchTrees() {
  try {
    const url = new URL(OBSERVATIONS_BASE);
    url.searchParams.set("q", "tree");
    url.searchParams.set("has[]", "photos");
    url.searchParams.set("per_page", "20");

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();
    return data.results || [];
  } catch (error) {
    throw error;
  }
}

async function searchSpecies(query) {
  const normalizedQuery = query.trim() || "nature";
  const url = new URL(OBSERVATIONS_BASE);
  url.searchParams.set("q", normalizedQuery);
  url.searchParams.set("has[]", "photos");
  url.searchParams.set("per_page", "20");

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  const data = await response.json();
  return data.results || [];
}

function handleFilterChange(filter) {
  currentFilter = currentFilter === filter ? null : filter;
  filterButtons.forEach((button) => {
    button.classList.toggle("active", button.textContent.toLowerCase() === currentFilter);
  });

  if (filter === "plant") {
    fetchResources();
  } else if (filter === "tree") {
    fetchResources();
  } else {
    fetchResources(currentQuery);
  }
}

async function fetchResources(query = "") {
  clearResults();
  showLoader(true);
  setStatus("Loading resources...");

  try {
    if (currentFilter === "plant") {
      const plantResults = await fetchPlants();
      renderResults(plantResults, true);
      return;
    }

    if (currentFilter === "tree") {
      const treeResults = await fetchTrees();
      renderResults(treeResults, true);
      return;
    }

    const searchResults = await searchSpecies(query);
    renderResults(searchResults, true);
  } catch (err) {
    errorMessage.textContent = "Unable to load results";
    errorMessage.classList.remove("hidden");
    setStatus("Unable to load results");
    console.error(err);
  } finally {
    showLoader(false);
  }
}

const handleSearch = (event) => {
  currentQuery = event.target.value.trim();
  fetchResources(currentQuery);
};

searchInput.addEventListener("input", debounce(handleSearch, 300));

fetchResources();
