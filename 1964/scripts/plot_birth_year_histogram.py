# -*- coding: utf-8 -*-

import argparse
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
import cv2
import numpy as np

DEFAULT_INPUT_PATH = "../data/parsed/mg1964.txt"
DEFAULT_OUTPUT_PATH = "birth_year_histogram.png"

def crop_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray < 255
    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img[y0:y1, x0:x1, :]
    return cropped

def plot_birth_year_histogram(years_counts, xlabel="Birth year", ylabel="Number of born people", legend_patches=None, figsize=(13, 8), tick_fontsize=20, label_fontsize=30, selected_years=None, default_year_color="#1F77B4", year_colors=None, save_path=None, dpi=300, show=True, repaints=None, year_lambda=lambda x: x):
    years_counts = sorted(years_counts.items(), key=lambda x: x[0])
    years, counts = zip(*[(x[0], x[1]) for x in years_counts])

    colors = [default_year_color] * len(years)

    if year_colors is not None:
        year_index = {y: i for y, i in zip(years, range(len(years)))}
        for year, color in year_colors.items():
            if year in year_index.keys():
                colors[year_index[year]] = color

    matplotlib.rc("font", size=tick_fontsize)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(years, height=counts, width=1.0, align="center", edgecolor="black", color=colors)
    plt.ticklabel_format(style="plain")

    if repaints is not None:
        for x, h, c in repaints:
            if c is None:
                c = [default_year_color] * len(x)
            ax.bar(x, height=h, width=1.0, align="center", edgecolor="black", color=c)

    font = {"family": "normal", "weight": "bold", "size": tick_fontsize}
    plt.xlabel(xlabel, fontsize=label_fontsize)
    plt.ylabel(ylabel, fontsize=label_fontsize)

    if selected_years is None:
        selected_years = sorted(set([years[0], *filter(lambda x: x % 10 == 0, range(years[0], years[-1])), years[-1]]))

    plt.xticks(selected_years, list(map(year_lambda, selected_years)))

    if legend_patches is not None:
        handles = []
        for label, color in legend_patches:
            handles.append(mpatches.Patch(label=label, color=color))
        ax.legend(handles=handles, loc=2)

    plt.tight_layout()
    if save_path is not None:
        p = save_path.rfind(".")
        if p != -1:
            format = save_path[p + 1:]
        plt.savefig(save_path, format=format, dpi=dpi)

    if show is True:
        plt.show()

    plt.clf()

def plot_default_birth_year_histogram(years=None, counts=None, lower_bound=1840, upper_bound=1945, figsize=(13, 8), show=True, save_path=None, ww1_label="World War I", xlabel="Birth year", ylabel="Number of born people", year_lambda=lambda x: x, tick_fontsize=20, label_fontsize=30, default_year_color="#1F77B4", ww1_color="#555555", zero_color="#AAAAFF", two_color=None, seven_color=None):
    if years is None and counts is None:
        return

    if years is not None:
        years = list(filter(lambda x: lower_bound <= x and x <= upper_bound, years))
    if counts is None:
        counts = dict(Counter(years))

    year_colors = {}
    if ww1_label is None:
        legend_patches = None
        year_colors = {}
    else:
        legend_patches = [
            (ww1_label, ww1_color)
        ]
        year_colors = {1915: ww1_color, 1916: ww1_color, 1917: ww1_color, 1918: ww1_color}

    if zero_color is not None:
        for year in range((lower_bound//10) * 10, upper_bound + 1, 10):
            year_colors[year] = zero_color
        if legend_patches is None:
            legend_patches = []
        legend_patches.append(("Years ending with 0", zero_color))

    if two_color is not None:
        for year in range((lower_bound//10) * 10 + 2, upper_bound + 1, 10):
            year_colors[year] = two_color
        if legend_patches is None:
            legend_patches = []
        legend_patches.append(("Years ending with 2", two_color))

    if seven_color is not None:
        for year in range((lower_bound//10) * 10 + 7, upper_bound + 1, 10):
            year_colors[year] = seven_color
        if legend_patches is None:
            legend_patches = []
        legend_patches.append(("Years ending with 7", seven_color))

    plot_birth_year_histogram(counts, selected_years=list(range(lower_bound, 1945, 10)), year_colors=year_colors, xlabel=xlabel, ylabel=ylabel, legend_patches=legend_patches, figsize=figsize, show=show, save_path=save_path, year_lambda=year_lambda, tick_fontsize=tick_fontsize, label_fontsize=label_fontsize, default_year_color=default_year_color)

def load_persons(input_path):
    with open(input_path, "r", encoding="utf8") as f:
        input_lines = [line.strip("\r\n") for line in f.readlines()]

    persons = []
    for line in input_lines:
        name, surname, father_name, birth_year, place, municipality, nationality, death_year, death_place, fate, circumstances, id_number, *_ = line.split("\t")
        person_data = {
            "Name": name,
            "Surname": surname,
            "FatherName": father_name,
            "BirthYear": birth_year,
            "Place": place,
            "Municipality": municipality,
            "Nationality": nationality,
            "DeathYear": death_year,
            "DeathPlace": death_place,
            "Fate": fate,
            "Circumstances": circumstances,
            "IDNumber": id_number
        }
        persons.append(person_data)

    return persons

def main():
    parser = argparse.ArgumentParser(description="Plot birth year histogram.")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_PATH, help="Output file name.")
    parser.add_argument("-s", "--show", action="store_true", help="Show the plot.")
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT_PATH, help="Input file path.")
    parser.add_argument("-c", "--crop", action="store_true", help="Crop whitespace from the saved image.")
    parser.add_argument("-0", "--zero", action="store_true", help="Highlight years ending with 0.")
    parser.add_argument("-2", "--two", action="store_true", help="Highlight years ending with 2.")
    parser.add_argument("-7", "--seven", action="store_true", help="Highlight years ending with 7.")
    parser.add_argument("-f", "--flexible", action="store_true", help="Start histogram at the greatest multiple of 10 <= minimum birth year in the data.")
    args = parser.parse_args()

    persons = load_persons(input_path=args.input)
    years = [int(p["BirthYear"]) for p in persons if p["BirthYear"].isdigit()]

    lower_bound = (min(years) // 10) * 10 if args.flexible and years else 1840

    plot_default_birth_year_histogram(
        years=years,
        save_path=args.output,
        show=args.show and not args.crop,
        ww1_label=None,
        lower_bound=lower_bound,
        zero_color="#AAAAFF" if args.zero else None,
        two_color="#AAFFAA" if args.two else None,
        seven_color="#FFAAAA" if args.seven else None,
    )

    if args.crop:
        img = cv2.imread(args.output, cv2.IMREAD_COLOR)
        cropped = crop_image(img)
        cv2.imwrite(args.output, cropped)
        if args.show:
            cv2.imshow("Plot", cropped)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
