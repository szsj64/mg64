# -*- coding: utf-8 -*-

import argparse
import matplotlib
import matplotlib.pyplot as plt
import cv2
import numpy as np

DEFAULT_OUTPUT_PATH = "number_of_matches.png"

def crop_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray < 255
    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img[y0:y1, x0:x1, :]
    return cropped

def create_plot(groups, output_path, show = False):
    figsize = (13, 8)
    tick_fontsize = 20
    label_fontsize = 30
    linewidth = 2

    dpi = None
    format = "png"

    import numpy as np
    matplotlib.rc("font", size = tick_fontsize)
    fig, ax = plt.subplots(figsize = figsize)

    x = np.arange(0, len(groups[0][1]))
    for group in groups:
        label, y = group
        ax.plot(x, y, marker = "o", linewidth = linewidth, label = label)

    ax.set_xlabel("Maximum allowed birth year difference", fontsize = label_fontsize)
    ax.set_ylabel("Number of matches", fontsize = label_fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in x])
    ax.tick_params(axis = "x", labelsize = tick_fontsize)
    ax.tick_params(axis = "y", labelsize = tick_fontsize)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_path, dpi = dpi, format = format)
    plt.close(fig)

    import cv2
    img = cv2.imread(output_path, 6)
    cropped = crop_image(img)
    cv2.imwrite(output_path, cropped)
    if show:
        cv2.imshow("Plot", cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def create_groups():
    input_paths = [
        ("Exact matching", ["matched_M_0.txt", "matched_M_1.txt", "matched_M_2.txt", "matched_M_3.txt", "matched_M_4.txt", "matched_M_5.txt"]),
        ("Levenshtein distance $\leq$ 1", ["matched_M_0_b_2_ld_1_ff.txt", "matched_M_1_b_2_ld_1_ff.txt", "matched_M_2_b_2_ld_1_ff.txt", "matched_M_3_b_2_ld_1_ff.txt", "matched_M_4_b_2_ld_1_ff.txt", "matched_M_5_b_2_ld_1_ff.txt"]),
        ("Levenshtein distance $\leq$ 2", ["matched_M_0_b_2_ld_2_ff.txt", "matched_M_1_b_2_ld_2_ff.txt", "matched_M_2_b_2_ld_2_ff.txt", "matched_M_3_b_2_ld_2_ff.txt", "matched_M_4_b_2_ld_2_ff.txt", "matched_M_5_b_2_ld_2_ff.txt"]),
        ("Levenshtein distance $\leq$ 3", ["matched_M_0_b_2_ld_3_ff.txt", "matched_M_1_b_2_ld_3_ff.txt", "matched_M_2_b_2_ld_3_ff.txt", "matched_M_3_b_2_ld_3_ff.txt", "matched_M_4_b_2_ld_3_ff.txt", "matched_M_5_b_2_ld_3_ff.txt"]),
    ]

    groups = []
    for label, paths in input_paths:
        counts = []
        for path in paths:
            try:
                with open(path, "r") as f:
                    num_lines = sum(1 for _ in f)
                count = num_lines // 2
            except Exception:
                count = 0
            counts.append(count)
        groups.append((label, counts))
    return groups

def main():
    
    parser = argparse.ArgumentParser(description="Plot number of matches.")
    parser.add_argument("-o", "--output", dest="output_path", default=DEFAULT_OUTPUT_PATH,
                        help=f"Output path for the image (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-s", "--show", action="store_true", help="Show the image after saving it")
    args = parser.parse_args()
    output_path = args.output_path
    verbose = args.verbose
    show = args.show
    groups = create_groups()
    create_plot(groups = groups, output_path = output_path, show = show)
    if verbose:
        print(f"Verbose mode enabled.")
        print(f"Output image will be saved to: {output_path}")

if __name__ == "__main__":
    main()
