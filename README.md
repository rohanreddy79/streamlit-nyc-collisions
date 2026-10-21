# NYC Motor Vehicle Collisions Dashboard

[![CI](https://github.com/rohanreddy79/-Data-Science-Web-App-with-Streamlit-and-Python/actions/workflows/ci.yml/badge.svg)](https://github.com/rohanreddy79/-Data-Science-Web-App-with-Streamlit-and-Python/actions/workflows/ci.yml)

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
hour, and a top-5 table of streets by injured pedestrians / cyclists / motorists. `Procfile`,
`setup.sh` and `requirements.txt` are Heroku deployment files (committed with a stray `.txt` suffix
until 2026-10). The code was committed in March 2022.

## Features

- `load_data(nrows)` cached with `@st.cache_data(persist=True)`: `pd.read_csv(..., nrows=100000,
  parse_dates=[['CRASH_DATE', 'CRASH_TIME']])`, `dropna` on `LATITUDE`/`LONGITUDE`, column rename.
- "Where are most people injured in NYC": slider 0-19 -> `st.map` of rows with
  `injured_persons >= threshold`.
- "How many collisions occur during a given time of day?": hour slider 0-23 -> `pdk.Deck` with a
  `HexagonLayer` (`radius=100`, `extruded=True`, `elevation_range=[0, 1000]`, `pitch=50`) centred on
  the mean latitude/longitude of that hour's crashes, pydeck's `light` (Carto Positron) basemap.
- "Breakdown by minute": `np.histogram` of the minute of each crash in the chosen hour (60 bins)
  rendered with `plotly.express.bar`.
- "Top 5 dangerous streets by affected type": select box (Pedestrians / Cyclists / Motorists) ->
  `on_street_name` sorted by the matching `injured_*` column, top five rows.
- "Show Raw Data" checkbox prints the hour-filtered DataFrame.

## How it works

| File | Purpose |
| --- | --- |
| `app.py` | The whole Streamlit app: data loading, widgets, map, pydeck deck, Plotly chart, tables |
| `requirements.txt` | Pinned `numpy`, `pandas`, `pydeck`, `streamlit`, `plotly` |
| `scripts/prepare_nyc_export.py` | Renames the columns of the NYC Open Data export to the layout `app.py` expects |
| `scripts/make_sample_csv.py` | Writes a small random CSV in that layout for smoke tests (used by CI) |
| `tests/test_app.py` | Streamlit `AppTest` smoke test on the synthetic CSV, one run per select-box option |
| `Procfile` | Heroku process line: `web: sh setup.sh && streamlit run app.py` |
| `setup.sh` | Writes `~/.streamlit/config.toml` with `headless = true`, `port = $PORT`, `enableCORS = false` |
| `.github/workflows/ci.yml` | `py_compile`, headless `streamlit run` + HTTP 200 check, `pytest` on Python 3.12 |

Data flow: CSV -> `load_data` (cached) -> `original_data` kept for the street table -> `data`
narrowed to the selected hour for the map, hexagon layer, histogram and raw-data view.

## Running it

Python 3.12; `requirements.txt` pins the versions that were verified.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Getting the data

`app.py` reads `Motor_Vehicle_Collisions_-_Crashes.csv` from the repository directory, or whatever
path or URL the `DATA_URL` environment variable points at. It expects the column layout of the
Coursera project's file (`CRASH_DATE`, `CRASH_TIME`, `LATITUDE`, `LONGITUDE`, `ON_STREET_NAME`,
`INJURED_PERSONS`, `INJURED_PEDESTRIANS`, `INJURED_CYCLISTS`, `INJURED_MOTORISTS`, ...), which is not
what NYC Open Data exports today (`CRASH DATE`, `NUMBER OF CYCLIST INJURED`, ...). So:

1. Download the export (about 450 MB, 2M+ rows) from
   https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
   ("Export" -> CSV), or
   `curl -L -o export.csv "https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD"`.
2. `python scripts/prepare_nyc_export.py export.csv` writes `Motor_Vehicle_Collisions_-_Crashes.csv`
   next to `app.py`.

Without the real data, `python scripts/make_sample_csv.py` writes a 2,000-row random CSV with the
same columns (this is what CI uses). `*.csv` is git-ignored.

### Starting the app

```bash
streamlit run app.py                                # http://localhost:8501
DATA_URL=/path/to/other.csv streamlit run app.py    # data somewhere else
```

### Verified on this machine (2026-10, Python 3.12, pinned requirements)

- `python -m py_compile app.py` -> no output (OK).
- `python scripts/make_sample_csv.py` -> `wrote 2000 rows to Motor_Vehicle_Collisions_-_Crashes.csv`.
- `streamlit run app.py --server.headless true --server.port 8765` on that file:
  `curl -s -o /dev/null -w '%{http_code}' http://localhost:8765/` returned `200` three seconds
  after start, `/_stcore/health` returned `ok`, the page showed all four views in a browser (injury
  map, hexagon deck on a light basemap, minute histogram, top-5 table), then the server was killed.
- `python -m pytest -q tests` -> `3 passed` (`AppTest` runs the script on the synthetic CSV and
  selects Pedestrians, Cyclists and Motorists in turn). The same test against the pre-fix `app.py`
  showed the two bugs: Pedestrians produced the *motorists* table and Cyclists raised
  `KeyError: 'injured_cyclistss'`.
- The same `AppTest` run on the first 120,000 rows of the real NYC export (converted with
  `scripts/prepare_nyc_export.py`) passed as well; top streets came out as SHERIDAN AVENUE
  (6 pedestrians injured), EAST 42 STREET (3 cyclists), BROAD STREET (18 motorists).

Not verified on this machine: the Heroku deployment (`Procfile`, `setup.sh`).

## Changelog

- 2026-10: fixed the street-table typos (`'Pedestrains'`, `injured_pedstrains`,
  `injured_cyclistss`); replaced the hard-coded Windows `DATA_URL` with a relative path plus the
  `DATA_URL` environment variable; `st.cache` -> `st.cache_data`; hexagon basemap switched from the
  token-only `mapbox://` style to pydeck's `light` Carto style; renamed `Procfile.txt`,
  `setup.sh.txt`, `requirements.txt.txt`; pinned requirements; added the export converter, the
  sample-data script, a smoke test, MIT license and CI.

## Limitations / Notes

- Only the first 100,000 rows of the export are loaded, so counts and "top streets" reflect a
  prefix of the data, not the whole city history.
- `load_data` combines the date and time columns with pandas' nested `parse_dates=[[...]]`, which
  pandas 2.2+ flags as deprecated and pandas 3 removes; `requirements.txt` therefore pins
  pandas 2.3.3.
- The NYC export has to be converted once with `scripts/prepare_nyc_export.py`; the app does not
  read the raw export directly.
- The only test is the headless smoke test; nothing checks the numbers in the views.
