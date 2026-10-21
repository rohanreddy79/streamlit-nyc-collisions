# NYC Motor Vehicle Collisions Dashboard

**A single-file Streamlit app that loads the NYC Open Data "Motor Vehicle Collisions - Crashes" CSV and lets you explore where and when crashes injure people, with an injury map, a 3-D hexagon layer by hour, a per-minute histogram and a "most dangerous streets" table.**

Originally titled "Build a Data Science Web App with Streamlit and Python" (the name of the
Coursera guided project it follows). Dataset:
https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95

## Overview

`app.py` is the entire application. It reads the first 100,000 rows of the collisions export with
pandas, merges `CRASH_DATE` and `CRASH_TIME` into one `date/time` timestamp, drops rows without
coordinates and lower-cases the column names. Streamlit widgets (two sliders, a select box, a
checkbox) drive four views: a `st.map` of collisions filtered by number of injured people, a pydeck
`HexagonLayer` of collisions in a chosen hour, a Plotly bar chart of crashes per minute inside that
hour, and a top-5 table of streets by injured pedestrians / cyclists / motorists. The three
`*.txt` files are Heroku deployment files (`Procfile`, `setup.sh`, `requirements.txt`) saved with an
extra `.txt` suffix. The code was committed in March 2022.

## Features

- `load_data(nrows)` cached with `@st.cache(persist=True)`: `pd.read_csv(..., nrows=100000,
  parse_dates=[['CRASH_DATE', 'CRASH_TIME']])`, `dropna` on `LATITUDE`/`LONGITUDE`, column rename.
- "Where are most people injured in NYC": slider 0-19 -> `st.map` of rows with
  `injured_persons >= threshold`.
- "How many collisions occur during a given time of day?": hour slider 0-23 -> `pdk.Deck` with a
  `HexagonLayer` (`radius=100`, `extruded=True`, `elevation_range=[0, 1000]`, `pitch=50`) centred on
  the mean latitude/longitude of that hour's crashes, Mapbox `light-v9` style.
- "Breakdown by minute": `np.histogram` of the minute of each crash in the chosen hour (60 bins)
  rendered with `plotly.express.bar`.
- "Top 5 dangerous streets by affected type": select box (Pedestrians / Cyclists / Motorists) ->
  `on_street_name` sorted by the matching `injured_*` column, top five rows.
- "Show Raw Data" checkbox prints the hour-filtered DataFrame.

## How it works

| File | Purpose |
| --- | --- |
| `app.py` | The whole Streamlit app: data loading, widgets, map, pydeck deck, Plotly chart, tables |
| `requirements.txt.txt` | `numpy`, `pandas`, `pydeck`, `streamlit`, `plotly` |
| `Procfile.txt` | Heroku process line: `web: sh setup.sh && streamlit run app.py` |
| `setup.sh.txt` | Writes `~/.streamlit/config.toml` with `headless = true`, `port = $PORT`, `enableCORS = false` |

Data flow: CSV -> `load_data` (cached) -> `original_data` kept for the street table -> `data`
narrowed to the selected hour for the map, hexagon layer, histogram and raw-data view.

## Running it

1. Download the collisions CSV from the NYC Open Data link above and save it as
   `Motor_Vehicle_Collisions_-_Crashes.csv`.
2. Edit `DATA_URL` at the top of `app.py`; it is currently a hard-coded Windows path
   (`C:/Users/Rohan/Desktop/Project/project 2/streamlit-nyc/...`).
3. Install and run:

```bash
pip install streamlit pandas numpy pydeck plotly
streamlit run app.py
```

For Heroku, rename the three `*.txt` files to `Procfile`, `setup.sh` and `requirements.txt` first.

Not verified on this machine: the dataset is not in the repository and the path is hard-coded, so
the app was read but not launched.

## Limitations / Notes

- Only the first 100,000 rows of the export are loaded, so counts and "top streets" reflect a
  prefix of the data, not the whole city history.
- The street table has typos that break two of its three branches: the comparison
  `select == 'Pedestrains'` never matches the option `'Pedestrians'` (and references a
  non-existent `injured_pedstrains` column), so choosing Pedestrians falls through to the
  Motorists query; the Cyclists branch sorts by `injured_cyclistss`, which raises a `KeyError`.
- `st.cache` has been deprecated in favour of `st.cache_data` and removed from recent Streamlit
  releases, and the Mapbox map style may need a Mapbox token; expect to update both on a current
  Streamlit install.
- No tests, no configuration beyond the hard-coded path, and the committed README was a two-line
  stub before this one.
