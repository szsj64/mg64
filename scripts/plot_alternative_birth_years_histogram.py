# -*- coding: utf-8 -*-

import argparse
import json
import re
import matplotlib
import matplotlib.pyplot as plt
import cv2
import numpy as np

YEAR_PATTERN = re.compile(r"\d{4}")
MIN_BIRTH_YEAR = 1800
MAX_BIRTH_YEAR = 1945
DEFAULT_OUTPUT_PATH = "alternative_birth_years_histogram.png"

def crop_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray < 255
    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img[y0:y1, x0:x1, :]
    return cropped

def get_jms_birth_year(person):
    return person.get("Date of Birth:", "").split("[")[0].rstrip()

def parse_birth_year(person):
    raw = get_jms_birth_year(person).replace("*", "").replace("-", "").strip()
    if not raw:
        return None
    try:
        year = int(raw)
    except ValueError:
        return None
    if MIN_BIRTH_YEAR <= year <= MAX_BIRTH_YEAR:
        return year
    return None

def extract_alternative_years(source):
    if not source:
        return []
    years = []
    for match in YEAR_PATTERN.findall(source):
        year = int(match)
        if MIN_BIRTH_YEAR <= year <= MAX_BIRTH_YEAR:
            years.append(year)
    return years

def compute_differences(data):
    differences = []
    for person in data:
        birth_year = parse_birth_year(person)
        if birth_year is None:
            continue
        alternatives = extract_alternative_years(person.get("Source:", ""))
        if not alternatives:
            continue
        closest_diff = min(abs(birth_year - alt) for alt in alternatives)
        differences.append(closest_diff)
    return differences

def load_match_count(path):
    try:
        with open(path, "r") as f:
            num_lines = sum(1 for _ in f)
        return num_lines // 2
    except OSError:
        return None

def collect_match_difference_groups(use_full_groups, max_m=10):
    if use_full_groups:
        groups = [
            ("Exact matching", "matched_M_{m}.txt"),
            (r"Levenshtein distance $\leq$ 1", "matched_M_{m}_b_2_ld_1_ff.txt"),
            (r"Levenshtein distance $\leq$ 2", "matched_M_{m}_b_2_ld_2_ff.txt"),
            (r"Levenshtein distance $\leq$ 3", "matched_M_{m}_b_2_ld_3_ff.txt"),
        ]
    else:
        groups = [("Exact matching", "matched_M_{m}.txt")]

    result = []
    for label, template in groups:
        counts = {}
        for m in range(0, max_m + 1):
            c = load_match_count(template.format(m=m))
            if c is not None:
                counts[m] = c
        xs, ys = [], []
        for m in sorted(counts):
            if m >= 1 and (m - 1) in counts:
                xs.append(m)
                ys.append(counts[m] - counts[m - 1])
        if xs:
            result.append((label, xs, ys))
    return result

def create_plot(differences, output_path, begin, maximum, show=False, match_groups=None):
    figsize = (13, 8)
    tick_fontsize = 20
    label_fontsize = 30
    linewidth = 2

    dpi = None
    format = "png"

    matplotlib.rc("font", size=tick_fontsize)
    fig, ax = plt.subplots(figsize=figsize)

    line_max = 0
    if match_groups:
        for _, xs, _ in match_groups:
            if xs:
                line_max = max(line_max, max(xs))

    if maximum is None:
        hist_max = max(differences) if differences else begin
        maximum = max(hist_max, line_max)

    filtered = [d for d in differences if begin <= d <= maximum]
    counts = np.bincount(filtered, minlength=maximum + 1)[begin:maximum + 1]
    x = np.arange(begin, maximum + 1)

    histogram_label = "Closest birth year alternative" if match_groups else None
    ax.bar(x, counts, linewidth=linewidth, edgecolor="black", label=histogram_label)

    if match_groups:
        color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        for index, (label, xs, ys) in enumerate(match_groups):
            xs_a = np.array(xs)
            ys_a = np.array(ys)
            mask = (xs_a >= begin) & (xs_a <= maximum)
            if mask.any():
                color = color_cycle[(index + 1) % len(color_cycle)]
                ax.plot(xs_a[mask], ys_a[mask], marker="o", linewidth=linewidth, label=label, color=color)
        ax.legend()

    ax.set_xlabel("Absolute difference to the closest birth year alternative", fontsize=label_fontsize)
    ax.set_ylabel("Number of individuals", fontsize=label_fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in x])
    ax.tick_params(axis="x", labelsize=tick_fontsize)
    ax.tick_params(axis="y", labelsize=tick_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi, format=format)
    plt.close(fig)

    img = cv2.imread(output_path, 6)
    cropped = crop_image(img)
    cv2.imwrite(output_path, cropped)
    if show:
        cv2.imshow("Plot", cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Plot histogram of differences between JMS birth years and the closest alternative birth years given in the sources.")
    parser.add_argument("-i", "--input", dest="input_path", required=True,
                        help="Input path of the JSON textual file with JMS data")
    parser.add_argument("-o", "--output", dest="output_path", default=DEFAULT_OUTPUT_PATH,
                        help=f"Output path for the image (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("-b", "--begin", dest="begin", type=int, default=0,
                        help="Difference at which the histogram begins (default: 0)")
    parser.add_argument("-m", "--maximum", dest="maximum", type=int, default=None,
                        help="Maximum difference to draw in the histogram (default: maximum found)")
    parser.add_argument("-f", "--found", action="store_true",
                        help="Overlay a line of differences in the number of matches per allowed birth-year difference (exact-matching variant only, M up to 10)")
    parser.add_argument("-F", "--found-all", dest="found_all", action="store_true",
                        help="Overlay four lines (Exact + Levenshtein <=1/<=2/<=3), as in plot_number_of_matches.py")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-s", "--show", action="store_true", help="Show the image after saving it")
    args = parser.parse_args()

    with open(args.input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    differences = compute_differences(data)

    if args.found_all:
        match_groups = collect_match_difference_groups(use_full_groups=True)
    elif args.found:
        match_groups = collect_match_difference_groups(use_full_groups=False)
    else:
        match_groups = None

    create_plot(differences=differences, output_path=args.output_path, begin=args.begin, maximum=args.maximum, show=args.show, match_groups=match_groups)

    if args.verbose:
        print(f"Verbose mode enabled.")
        print(f"Loaded {len(data)} entries from: {args.input_path}")
        print(f"Computed {len(differences)} differences.")
        if differences:
            print(f"Minimum difference: {min(differences)}")
            print(f"Maximum difference: {max(differences)}")
        print(f"Output image will be saved to: {args.output_path}")

if __name__ == "__main__":
    main()
