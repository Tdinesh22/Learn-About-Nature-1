const searchInput = document.getElementById("ai-search-input");
const searchButton = document.getElementById("ai-search-button");
const resultsContainer = document.getElementById("ai-results");
const statusText = document.getElementById("ai-status");

const setStatus = (message, isError = false) => {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
};

const clearResults = () => {
  resultsContainer.innerHTML = "";
};

const createWikipediaUrl = (title) => {
  const encoded = encodeURIComponent(title.trim().replace(/\s+/g, "_"));
  return `https://en.wikipedia.org/wiki/${encoded}`;
};

const renderResult = (data) => {
  const card = document.createElement("article");
  card.className = "ai-result-card";

  const header = document.createElement("div");
  header.className = "ai-result-header";

  const title = document.createElement("h3");
  title.className = "ai-result-title";
  title.textContent = data.title || "Unknown species";

  const subtitle = document.createElement("p");
  subtitle.className = "ai-result-subtitle";
  subtitle.textContent = data.extract ? data.displaytitle || data.title : data.title;

  header.appendChild(title);
  header.appendChild(subtitle);

  const body = document.createElement("p");
  body.className = "ai-result-body";
  body.textContent = data.extract || "No summary available.";

  const actions = document.createElement("div");
  actions.className = "ai-result-actions";

  const wikiLink = document.createElement("a");
  wikiLink.href = data.content_urls?.desktop?.page || createWikipediaUrl(data.title || searchInput.value);
  wikiLink.target = "_blank";
  wikiLink.rel = "noopener noreferrer";
  wikiLink.textContent = "View full Wikipedia page";

  actions.appendChild(wikiLink);

  card.appendChild(header);

  if (data.thumbnail?.source) {
    const img = document.createElement("img");
    img.className = "ai-thumbnail";
    img.src = data.thumbnail.source;
    img.alt = `${data.title} thumbnail`;
    card.appendChild(img);
  }

  card.appendChild(body);
  card.appendChild(actions);
  resultsContainer.appendChild(card);
};

const handleDisambiguation = (data) => {
  if (data.type === "disambiguation") {
    setStatus("Please be more specific.", true);
    return true;
  }
  return false;
};

const fetchSpeciesSummary = async (species) => {
  clearResults();
  setStatus("Searching...");

  try {
    const encoded = encodeURIComponent(species.trim());
    const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${encoded}`;
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        setStatus("No results found for that species.", true);
        return;
      }
      throw new Error(`API error ${response.status}`);
    }

    const data = await response.json();

    if (handleDisambiguation(data)) {
      return;
    }

    renderResult(data);
    setStatus("");
  } catch (error) {
    console.error(error);
    clearResults();
    setStatus("Failed to fetch data. Please try again.", true);
  }
};

const handleSearch = () => {
  const query = searchInput.value.trim();
  if (!query) {
    setStatus("Please enter a species name.", true);
    return;
  }
  fetchSpeciesSummary(query);
};

searchButton.addEventListener("click", handleSearch);
searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    handleSearch();
  }
});
