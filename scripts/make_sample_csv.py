"""Write a small synthetic collisions CSV in the layout app.py expects.

Used by CI and for local smoke tests when the real NYC Open Data export is
not available. The values are random and carry no information about NYC.

Usage: python scripts/make_sample_csv.py [OUTPUT_PATH] [ROWS]
"""
import csv
import random
import sys

COLUMNS = [
    "CRASH_DATE", "CRASH_TIME", "BOROUGH", "ZIP_CODE", "LATITUDE", "LONGITUDE",
    "ON_STREET_NAME", "INJURED_PERSONS", "KILLED_PERSONS", "INJURED_PEDESTRIANS",
    "KILLED_PEDESTRIANS", "INJURED_CYCLISTS", "KILLED_CYCLISTS", "INJURED_MOTORISTS",
    "KILLED_MOTORISTS",
]
STREETS = ["BROADWAY", "ATLANTIC AVENUE", "FLATBUSH AVENUE", "QUEENS BOULEVARD", "3 AVENUE"]


def main(path="Motor_Vehicle_Collisions_-_Crashes.csv", rows=2000):
    rng = random.Random(0)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        for i in range(rows):
            hour, minute = i % 24, rng.randrange(60)  # every hour of the day is covered
            ped, cyc, mot = (rng.randrange(3) for _ in range(3))
            writer.writerow([
                "2019-%02d-%02d" % (1 + i % 12, 1 + i % 28), "%02d:%02d" % (hour, minute),
                rng.choice(["BROOKLYN", "QUEENS", "MANHATTAN"]), 10000 + rng.randrange(500),
                round(40.5 + rng.random() * 0.4, 6), round(-74.2 + rng.random() * 0.5, 6),
                rng.choice(STREETS), ped + cyc + mot, 0, ped, 0, cyc, 0, mot, 0,
            ])
    print("wrote %d rows to %s" % (rows, path))


if __name__ == "__main__":
    main(*sys.argv[1:2], *(int(a) for a in sys.argv[2:3]))
