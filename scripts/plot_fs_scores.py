# -*- coding: utf-8 -*-

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import argparse
import collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cv2
import numpy as np

DEFAULT_OUTPUT_PATH = "fs_scores_histogram.png"
DEFAULT_PLOT_TYPE = "lollipop"
PLOT_TYPES = ("lollipop", "bar", "cleveland", "cleveland2", "pareto", "histogram")
DEFAULT_HISTOGRAM_BINS = 50

def crop_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray < 255
    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img[y0:y1, x0:x1, :]
    return cropped

def parse_scores(path):
    scores = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("\t"):
                continue
            tail = line.rsplit("|", 1)
            if len(tail) != 2:
                continue
            try:
                scores.append(float(tail[1].strip()))
            except ValueError:
                continue
    return scores

def create_plot(scores, output_path, plot_type, bins=None, show=False):
    figsize = (13, 8)
    tick_fontsize = 20
    label_fontsize = 30
    linewidth = 2

    dpi = None
    format = "png"

    matplotlib.rc("font", size=tick_fontsize)
    fig, ax = plt.subplots(figsize=figsize)

    counter = collections.Counter(scores)
    unique = sorted(counter)
    counts = [counter[s] for s in unique]

    score_label = "Fellegi-Sunter score"
    matches_label = "Number of matches"

    if plot_type == "lollipop":
        ax.vlines(unique, 0, counts, linewidth=linewidth * 2)
        ax.plot(unique, counts, "o", markersize=12)
        ax.set_xlabel(score_label, fontsize=label_fontsize)
        ax.set_ylabel(matches_label, fontsize=label_fontsize)
    elif plot_type == "bar":
        if len(unique) > 1:
            range_span = unique[-1] - unique[0]
            min_gap = min(unique[i + 1] - unique[i] for i in range(len(unique) - 1))
            width = max(0.6 * min_gap, range_span / 100)
        else:
            width = 1.0
        ax.bar(unique, counts, width=width, linewidth=linewidth, edgecolor="black")
        ax.set_xlabel(score_label, fontsize=label_fontsize)
        ax.set_ylabel(matches_label, fontsize=label_fontsize)
    elif plot_type == "cleveland":
        y = np.arange(len(unique))
        ax.hlines(y, 0, counts, linewidth=linewidth * 2)
        ax.plot(counts, y, "o", markersize=12)
        ax.set_yticks(y)
        ax.set_yticklabels([f"{s:.2f}" for s in unique])
        ax.set_xlabel(matches_label, fontsize=label_fontsize)
        ax.set_ylabel(score_label, fontsize=label_fontsize)
    elif plot_type == "cleveland2":
        color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        matches_color = color_cycle[0]
        cumulative_color = color_cycle[1]

        y = np.arange(len(unique))
        ax.hlines(y, 0, counts, linewidth=linewidth * 2, color=matches_color)
        ax.plot(counts, y, "o", markersize=12, color=matches_color, label="Matches at score")
        ax.set_yticks(y)
        ax.set_yticklabels([f"{s:.2f}" for s in unique])
        ax.set_xlabel(matches_label, fontsize=label_fontsize)
        ax.set_ylabel(score_label, fontsize=label_fontsize)

        counts_arr = np.array(counts)
        total = counts_arr.sum()
        cumulative_high_to_low = np.cumsum(counts_arr[::-1])[::-1] / total * 100
        ax_top = ax.twiny()
        ax_top.plot(cumulative_high_to_low, y, marker="o", linewidth=linewidth, color=cumulative_color, label="Cumulative % (\u2265 score)")
        ax_top.set_xlabel("Cumulative %", fontsize=label_fontsize)
        ax_top.set_xlim(0, 105)
        ax_top.tick_params(axis="x", labelsize=tick_fontsize)

        handles_main, labels_main = ax.get_legend_handles_labels()
        handles_top, labels_top = ax_top.get_legend_handles_labels()
        ax.legend(handles_main + handles_top, labels_main + labels_top, loc="upper right")
    elif plot_type == "pareto":
        sorted_items = sorted(counter.items(), key=lambda kv: -kv[1])
        unique_p = [s for s, _ in sorted_items]
        counts_p = [c for _, c in sorted_items]
        x = np.arange(len(unique_p))
        ax.bar(x, counts_p, linewidth=linewidth, edgecolor="black")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{s:.2f}" for s in unique_p], rotation=45, ha="right")
        total = sum(counts_p)
        cumulative = np.cumsum(counts_p) / total * 100
        color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        ax2 = ax.twinx()
        ax2.plot(x, cumulative, color=color_cycle[1], marker="o", linewidth=linewidth)
        ax2.set_ylabel("Cumulative %", fontsize=label_fontsize)
        ax2.tick_params(axis="y", labelsize=tick_fontsize)
        ax2.set_ylim(0, 105)
        ax.set_xlabel(score_label, fontsize=label_fontsize)
        ax.set_ylabel(matches_label, fontsize=label_fontsize)
    elif plot_type == "histogram":
        bin_count = bins if bins is not None else DEFAULT_HISTOGRAM_BINS
        ax.hist(scores, bins=bin_count, linewidth=linewidth, edgecolor="black")
        ax.set_xlabel(score_label, fontsize=label_fontsize)
        ax.set_ylabel(matches_label, fontsize=label_fontsize)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

    ax.tick_params(axis="x", labelsize=tick_fontsize)
    ax.tick_params(axis="y", labelsize=tick_fontsize)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi, format=format, bbox_inches="tight")
    plt.close(fig)

    img = cv2.imread(output_path, 6)
    cropped = crop_image(img)
    cv2.imwrite(output_path, cropped)
    if show:
        cv2.imshow("Plot", cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Plot Fellegi-Sunter score frequencies from a match.py matches file (e.g., matched_fs.txt). The score is read from the last '|'-separated field on each non-indented JMS row.")
    parser.add_argument("-i", "--input", dest="input_path", required=True,
                        help="Input path of a match.py matches file containing Fellegi-Sunter scores")
    parser.add_argument("-o", "--output", dest="output_path", default=DEFAULT_OUTPUT_PATH,
                        help=f"Output path for the image (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("-t", "--type", dest="plot_type", default=DEFAULT_PLOT_TYPE,
                        choices=PLOT_TYPES,
                        help=f"Plot type: lollipop (one stem+marker per distinct score), bar (one bar per distinct score), cleveland (horizontal dot plot, score on y-axis), cleveland2 (cleveland + a side panel with the cumulative %% of matches at scores >= each level), pareto (bars sorted by count + cumulative %% line), histogram (binned, uses -b). Default: {DEFAULT_PLOT_TYPE}")
    parser.add_argument("-b", "--bins", dest="bins", type=int, default=None,
                        help=f"Number of bins for --type histogram (default: {DEFAULT_HISTOGRAM_BINS})")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-s", "--show", action="store_true", help="Show the image after saving it")
    args = parser.parse_args()

    scores = parse_scores(args.input_path)

    create_plot(scores=scores, output_path=args.output_path, plot_type=args.plot_type, bins=args.bins, show=args.show)

    if args.verbose:
        print(f"Verbose mode enabled.")
        print(f"Parsed file: {args.input_path}")
        print(f"Number of scores: {len(scores)}")
        print(f"Distinct scores: {len(set(scores))}")
        if scores:
            print(f"Min score: {min(scores):.3f}")
            print(f"Max score: {max(scores):.3f}")
            print(f"Mean score: {sum(scores) / len(scores):.3f}")
        print(f"Output image will be saved to: {args.output_path}")

if __name__ == "__main__":
    main()
