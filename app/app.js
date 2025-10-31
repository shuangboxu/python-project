const DATA_URL = "../reports/logs/recommendation_data.json";

const ageInput = document.getElementById("age-input");
const languageSelect = document.getElementById("language-select");
const searchInput = document.getElementById("keyword-search");
const grid = document.getElementById("recommendations-grid");
const resultsCount = document.getElementById("results-count");
const noResults = document.getElementById("no-results");
const pagination = document.getElementById("pagination");
const prevButton = document.getElementById("prev-page");
const nextButton = document.getElementById("next-page");
const paginationStatus = document.getElementById("pagination-status");

const PAGE_SIZE = 12;

let movies = [];
let metadata = {};
let filteredMovies = [];
let currentPage = 1;

async function loadData() {
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) {
      throw new Error(`Failed to load data (${response.status})`);
    }
    const data = await response.json();
    movies = data.movies || [];
    metadata = data.metadata || {};
    populateLanguageOptions();
    filteredMovies = movies.slice();
    renderCurrentPage();
  } catch (error) {
    grid.innerHTML = `<p class="empty-state">Unable to load movie data. ${error.message}</p>`;
    resultsCount.textContent = "0";
    pagination.hidden = true;
  }
}

function populateLanguageOptions() {
  const languages = metadata.languages || [];
  languages.forEach(({ code, label }) => {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = label;
    languageSelect.appendChild(option);
  });
}

function formatRuntime(runtime) {
  if (!runtime) return null;
  const hours = Math.floor(runtime / 60);
  const minutes = runtime % 60;
  if (!hours) return `${runtime} min`;
  return `${hours}h ${minutes.toString().padStart(2, "0")}m`;
}

function createMovieCard(movie) {
  const card = document.createElement("article");
  card.className = "movie-card";
  card.tabIndex = 0;

  const runtime = formatRuntime(movie.runtime);
  const metaParts = [];
  if (movie.release_date) metaParts.push(movie.release_date);
  if (runtime) metaParts.push(runtime);
  if (movie.language_label) metaParts.push(movie.language_label);
  if (movie.vote_average) metaParts.push(`⭐ ${movie.vote_average.toFixed(1)} (${movie.vote_count || 0})`);

  const genres = movie.genres.slice(0, 6);
  const keywords = movie.keywords.slice(0, 6);
  const languages = (movie.spoken_languages && movie.spoken_languages.length
    ? movie.spoken_languages
    : [movie.language_label].filter(Boolean)
  ).slice(0, 3);

  card.innerHTML = `
    <header>
      <div class="movie-card__labels">
        <span class="chip">Rank #${movie.rank}</span>
        <span class="chip">Score ${movie.final_score.toFixed(2)}</span>
        ${movie.is_restricted_for_minors ? '<span class="chip">Mature</span>' : ""}
      </div>
      <h3>${movie.title}</h3>
      <div class="movie-card__meta">${metaParts.map((item) => `<span>${item}</span>`).join("")}</div>
    </header>
    <p class="movie-card__overview">${movie.overview || "No synopsis available."}</p>
    <div>
      ${
        genres.length
          ? `<ul class="genre-list">${genres
              .map((genre) => `<li class="chip">${genre}</li>`)
              .join("")}</ul>`
          : ""
      }
      ${
        languages.length
          ? `<ul class="keyword-list">${languages
              .map((language) => `<li class="chip">${language}</li>`)
              .join("")}</ul>`
          : ""
      }
      ${
        keywords.length
          ? `<ul class="keyword-list">${keywords
              .map((keyword) => `<li class="chip">${keyword}</li>`)
              .join("")}</ul>`
          : ""
      }
    </div>
    <a class="movie-card__cta" href="${movie.homepage}" target="_blank" rel="noopener">Visit movie page</a>
  `;

  return card;
}

function movieMatchesFilters(movie) {
  const ageValue = parseInt(ageInput.value, 10);
  const languageValue = languageSelect.value;
  const searchValue = searchInput.value.trim().toLowerCase();

  if (!Number.isNaN(ageValue) && ageValue < 18 && movie.is_restricted_for_minors) {
    return false;
  }

  if (languageValue && languageValue !== "all") {
    if (movie.language_code?.toLowerCase() !== languageValue.toLowerCase()) {
      return false;
    }
  }

  if (searchValue) {
    const haystack = [
      movie.title,
      movie.overview,
      movie.language_label,
      ...(movie.genres || []),
      ...(movie.keywords || []),
    ]
      .join(" ")
      .toLowerCase();
    if (!haystack.includes(searchValue)) {
      return false;
    }
  }

  return true;
}

function renderMovies(list) {
  grid.innerHTML = "";
  if (!list.length) {
    noResults.hidden = false;
    resultsCount.textContent = "0";
    pagination.hidden = true;
    return;
  }

  noResults.hidden = true;
  const fragment = document.createDocumentFragment();
  list.forEach((movie) => fragment.appendChild(createMovieCard(movie)));
  grid.appendChild(fragment);
}

function handleFiltersChange() {
  filteredMovies = movies.filter(movieMatchesFilters);
  currentPage = 1;
  renderCurrentPage();
}

ageInput.addEventListener("input", handleFiltersChange);
languageSelect.addEventListener("change", handleFiltersChange);
searchInput.addEventListener("input", handleFiltersChange);

function renderCurrentPage() {
  const total = filteredMovies.length;
  resultsCount.textContent = String(total);

  if (!total) {
    renderMovies([]);
    return;
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);
  currentPage = Math.min(Math.max(currentPage, 1), totalPages);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const pageItems = filteredMovies.slice(startIndex, startIndex + PAGE_SIZE);

  renderMovies(pageItems);
  updatePagination(total, totalPages);
}

function updatePagination(total, totalPages) {
  if (total <= PAGE_SIZE) {
    pagination.hidden = true;
    paginationStatus.textContent = "";
    return;
  }

  pagination.hidden = false;
  const start = (currentPage - 1) * PAGE_SIZE + 1;
  const end = Math.min(start + PAGE_SIZE - 1, total);
  paginationStatus.textContent = `Showing ${start}–${end} of ${total}`;
  prevButton.disabled = currentPage === 1;
  nextButton.disabled = currentPage === totalPages;
}

prevButton.addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage -= 1;
    renderCurrentPage();
    grid.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

nextButton.addEventListener("click", () => {
  const totalPages = Math.ceil(filteredMovies.length / PAGE_SIZE);
  if (currentPage < totalPages) {
    currentPage += 1;
    renderCurrentPage();
    grid.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

loadData();
