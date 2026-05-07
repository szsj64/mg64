# -*- coding: utf-8 -*-

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import argparse
import collections

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT_PATH = os.path.join(SCRIPT_DIR, "..", "1964", "data", "parsed", "mg1964.txt")
DEFAULT_OUTPUT_PATH = "jasenovac_sg_pie.png"

CATEGORIES = collections.OrderedDict([
    ("Jasenovac",        "Jasenovac"),
    ("Jaenovac",         "Jaenovac"),
    ("Stara Gradiška",   "Stara Gradiška"),
    ("St. Gradiška",     "St. Gradiška"),
    ("St Gradiška",      "St Gradiška"),
    ("Stara grediška",   "Stara grediška"),
    ("Stara gardiška",   "Stara gardiška"),
    ("Stara gadiška",    "Stara gadiška"),
    ("St.gradiška",      "St.gradiška"),
    ("Jasenovac-logor",  "Jasenovac-logor"),
    ("Mlaka",            "Mlaka"),
    ("Jablanac",         "Jablanac"),
    ("Krapje",           "Krapje"),
    ("Bročice",          "Bročice"),
    ("Gradina",          "Gradina"),
])


def load_mg1964_death_places(input_path):
    death_places = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            fields = line.strip("\r\n").split("\t")
            if len(fields) >= 9:
                death_places.append(fields[8])
    return death_places


def count_categories(death_places):
    counts = collections.OrderedDict()
    for label in CATEGORIES:
        counts[label] = 0

    for dp in death_places:
        dp_lower = dp.lower()
        for label, value in CATEGORIES.items():
            if value.lower() in dp_lower:
                counts[label] += 1
                break

    return counts


def crop_image(img):
    import cv2
    import numpy as np
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray < 255
    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    return img[y0:y1, x0:x1, :]


def create_pie_chart(counts, output_path, crop=False, show=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Merge Jasenovac variants into one group
    jasenovac_total = 0
    jasenovac_keys = ["Jasenovac", "Jaenovac", "Jasenovac-logor"]
    # Merge Gradiška variants into one group
    gradiska_total = 0
    gradiska_keys = [
        "Stara Gradiška", "St. Gradiška", "St Gradiška",
        "Stara grediška", "Stara gardiška", "Stara gadiška", "St.gradiška"
    ]
    rest = collections.OrderedDict()
    for label, count in counts.items():
        if label in jasenovac_keys:
            jasenovac_total += count
        elif label in gradiska_keys:
            gradiska_total += count
        else:
            rest[label] = count

    # Merge remaining localities into one group
    other_keys = ["Mlaka", "Jablanac", "Krapje", "Bročice", "Gradina"]
    other_total = 0
    for label, count in rest.items():
        if label in other_keys:
            other_total += count

    merged = collections.OrderedDict()
    if jasenovac_total > 0:
        merged["Jasenovac (all variants)"] = jasenovac_total
    if gradiska_total > 0:
        merged["Stara Gradiška (all variants)"] = gradiska_total
    if other_total > 0:
        merged["Other localities (Mlaka, Jablanac, Gradina, Krapje, Bročice)"] = other_total

    # Filter out zero counts
    labels = [l for l, c in merged.items() if c > 0]
    values = [c for c in merged.values() if c > 0]

    fig, ax = plt.subplots(figsize=(16, 12))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct / 100.0 * sum(values))):,})",
        startangle=90,
        textprops={"fontsize": 26},
    )
    for at in autotexts:
        at.set_fontsize(22)

    ax.set_title("MG64 records by Jasenovac-related death place", fontsize=32, pad=20)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    if crop:
        import cv2
        img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
        cropped = crop_image(img)
        cv2.imwrite(output_path, cropped)

    if show:
        import cv2
        img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
        cv2.imshow("Pie Chart", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description="Count MG64 records whose death place matches Jasenovac, Stara Gradiška, "
                    "and related camp locations, and optionally produce a pie chart."
    )
    parser.add_argument("-i", "--input", dest="input_path", default=DEFAULT_INPUT_PATH,
                        help=f"Path to mg1964.txt (default: {DEFAULT_INPUT_PATH})")
    parser.add_argument("-o", "--output", dest="output_path", default=DEFAULT_OUTPUT_PATH,
                        help=f"Output path for the pie chart (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("-c", "--crop", action="store_true",
                        help="Crop whitespace from the saved chart")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print detailed counts and totals")
    parser.add_argument("-s", "--show", action="store_true",
                        help="Show the chart after saving")
    parser.add_argument("--no-chart", action="store_true",
                        help="Skip chart generation, only print counts")
    args = parser.parse_args()

    death_places = load_mg1964_death_places(args.input_path)
    counts = count_categories(death_places)

    total_mg64 = len(death_places)
    total_matched = sum(counts.values())

    if args.verbose:
        max_label_len = max(len(l) for l in counts)
        print(f"{'Category':<{max_label_len}}  {'Count':>8}  {'Share':>7}")
        print("-" * (max_label_len + 19))
        for label, count in counts.items():
            pct = 100.0 * count / total_mg64 if total_mg64 > 0 else 0
            print(f"{label:<{max_label_len}}  {count:>8,}  {pct:>6.2f}%")
        print("-" * (max_label_len + 19))
        print(f"{'Total matched':<{max_label_len}}  {total_matched:>8,}  {100.0 * total_matched / total_mg64:>6.2f}%")
        print(f"{'Total MG64 records':<{max_label_len}}  {total_mg64:>8,}")
    else:
        print(f"Total Jasenovac/SG-related records: {total_matched:,} / {total_mg64:,} ({100.0 * total_matched / total_mg64:.2f}%)")

    if not args.no_chart:
        create_pie_chart(counts, args.output_path, crop=args.crop, show=args.show)
        if args.verbose:
            print(f"\nChart saved to: {args.output_path}")


if __name__ == "__main__":
    main()
