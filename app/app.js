const DATA_URL = "../reports/logs/recommendation_data.json";

const ageInput = document.getElementById("age-input");
const languageSelect = document.getElementById("language-select");
const searchInput = document.getElementById("keyword-search");
const grid = document.getElementById("recommendations-grid");
const resultsCount = document.getElementById("results-count");
const noResults = document.getElementById("no-results");

let movies = [];
let metadata = {};

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
    renderMovies(movies);
  } catch (error) {
    grid.innerHTML = `<p class="empty-state">Unable to load movie data. ${error.message}</p>`;
    resultsCount.textContent = "0";
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
    return;
  }

  noResults.hidden = true;
  const fragment = document.createDocumentFragment();
  list.forEach((movie) => fragment.appendChild(createMovieCard(movie)));
  grid.appendChild(fragment);
  resultsCount.textContent = String(list.length);
}

function handleFiltersChange() {
  const filtered = movies.filter(movieMatchesFilters);
  renderMovies(filtered);
}

ageInput.addEventListener("input", handleFiltersChange);
languageSelect.addEventListener("change", handleFiltersChange);
searchInput.addEventListener("input", handleFiltersChange);

loadData();
