# python-project

This repository supports a four-member movie recommendation project built around component scores. Each teammate owns one scoring component, then the group merges, reviews, and presents final outputs.

## Repository Structure

```
python-project/
  data/
    raw/                # Read-only originals (for example data/raw/movies.xlsx)
    interim/
    processed/          # Drop any pre-processed datasets here
  notebooks/
  scripts/              # Component scripts and shared utilities
  reports/
    decks/              # Stage 3 slide decks (new)
    figures/
    logs/               # Member activity logs
    tables/             # Stage 1 component score outputs
    visualizations/     # Stage 3 web visualisations (new)
  app/
```

## Three-Stage Team Workflow

1. **Stage 1 - Component Scoring**
   - Each member runs their script (e.g. `scripts/01_content_scores.py`) to produce `reports/tables/0X_*scores.csv`.
   - Document methods in the matching log file (e.g. `reports/logs/01_content_log.txt`).
2. **Stage 2 - Score Merge & QA**
   - Combine the four component scores with a normalisation plus weighted merge script kept in `scripts/`.
   - Use `data/raw/movies.xlsx` as the single source of truth; flag missing `movie_id`, inconsistent ranges, and prepare a consolidated recommendation list.
   - Record how to run the merge script (CLI usage, config) so others can reproduce it.
3. **Stage 3 - Presentation & Visualisation**
   - **Slide deck**: Summarise goals, workflow, highlights, and sample recommendations. Save deliverables in `reports/decks/`.
   - **Web visualisation**: Build a Streamlit/Dash/static app showing the key metrics and interactive recommendations. Store code/assets in `reports/visualizations/` and include instructions for launching from the repository root (for example `streamlit run reports/visualizations/app.py`).

## Getting Started

1. Set up and activate a Python environment; install dependencies from `requirements.txt` if present.
2. Run your component script to populate the relevant CSV in `reports/tables/`.
3. Execute the Stage 2 merge workflow to produce the combined recommendation table used for Stage 3 assets.
4. Before presenting, verify `reports/decks/` and `reports/visualizations/` contain the latest outputs alongside run instructions or deployment notes.

Tip: share any intermediate figures or diagnostics inside appropriate `reports/` subdirectories to keep the project history traceable.
