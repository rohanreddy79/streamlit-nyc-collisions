"""Convert the NYC Open Data "Motor Vehicle Collisions - Crashes" CSV export into
the column layout app.py expects (the layout of the Coursera guided project's file).

The export names columns "CRASH DATE", "NUMBER OF PERSONS INJURED", "NUMBER OF CYCLIST
INJURED", ...; the app wants CRASH_DATE, INJURED_PERSONS, INJURED_CYCLISTS, ... .

Usage: python scripts/prepare_nyc_export.py EXPORT.csv [Motor_Vehicle_Collisions_-_Crashes.csv]
"""
import sys

import pandas as pd

RENAME = {
    "NUMBER OF PERSONS INJURED": "INJURED_PERSONS",
    "NUMBER OF PERSONS KILLED": "KILLED_PERSONS",
    "NUMBER OF PEDESTRIANS INJURED": "INJURED_PEDESTRIANS",
    "NUMBER OF PEDESTRIANS KILLED": "KILLED_PEDESTRIANS",
    "NUMBER OF CYCLIST INJURED": "INJURED_CYCLISTS",
    "NUMBER OF CYCLIST KILLED": "KILLED_CYCLISTS",
    "NUMBER OF MOTORIST INJURED": "INJURED_MOTORISTS",
    "NUMBER OF MOTORIST KILLED": "KILLED_MOTORISTS",
}


def main(src, dst="Motor_Vehicle_Collisions_-_Crashes.csv"):
    raw = pd.read_csv(src, low_memory=False)
    raw.rename(columns=lambda c: RENAME.get(c, c.replace(" ", "_"))).to_csv(dst, index=False)
    print("wrote %d rows to %s" % (len(raw), dst))


if __name__ == "__main__":
    main(*sys.argv[1:3])
