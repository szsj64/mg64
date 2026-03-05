# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as mpatches
from collections import Counter

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
            format = save_path[p + 1 :]
        plt.savefig(save_path, format=format, dpi=dpi)

    if show is True:
        plt.show()

    plt.clf()

def plot_default_birth_year_histogram(years=None, counts=None, lower_bound=1840, upper_bound=1945, figsize=(13, 8), show=True, save_path=None, ww1_label="World War I", xlabel="Birth year", ylabel="Number of born people", year_lambda=lambda x: x, tick_fontsize=20, label_fontsize=30, default_year_color="#1F77B4", ww1_color="#555555", zero_color="#AAAAFF"):
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

    plot_birth_year_histogram(counts, selected_years=list(range(lower_bound, 1945, 10)), year_colors=year_colors, xlabel=xlabel, ylabel=ylabel, legend_patches=legend_patches, figsize=figsize, show=show, save_path=save_path, year_lambda=year_lambda, tick_fontsize=tick_fontsize, label_fontsize=label_fontsize, default_year_color=default_year_color)

def load_persons(input_path):
    with open(input_path, "r", encoding="utf8") as f:
        input_lines = [line.strip("\r\n") for line in f.readlines()]
    
    persons = []
    for line in input_lines:
        name, surname, father_name, birth_year, place, municipality, nationality, death_year, death_place, fate, circumstances, id_number = line.split("\t")
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

def test1():
    input_path = "../data/parsed/mg1964.txt"

    persons = load_persons(input_path=input_path)

    
    years = [int(p["BirthYear"]) for p in persons if p["BirthYear"].isdigit()]
    plot_default_birth_year_histogram(years=years, save_path="birth_year_histogram.png", show=True, ww1_label=None)
    
    pass

def test2():
    input_path = "../data/parsed/mg1964.txt"

    persons = load_persons(input_path=input_path)
    
    death_places = [p["DeathPlace"] for p in persons]
    death_places = [p["DeathPlace"] for p in persons if p["Circumstances"] == "u logoru"]
    death_places_count = dict(Counter(death_places))
    sorted_death_places_count = sorted(death_places_count.items(), key=lambda x: -x[1])
    
    for death_place, count in sorted_death_places_count:
        print(f"{death_place}: {count} {100*count/len(death_places):.2f}%")
        if count/len(death_places) < 0.01:
            break

    print()

    circumstances = [p["Circumstances"] for p in persons]
    circumstances_count = dict(Counter(circumstances))
    sorted_circumstances_count = sorted(circumstances_count.items(), key=lambda x: -x[1])
    
    print(len(sorted_circumstances_count))
    for circumstance, count in sorted_circumstances_count:
        if count/len(circumstances) < 0.01:
            break
        print(f"{circumstance}: {count} {100*count/len(circumstances):.2f}%")

    pass

def main():
    
    # draw the birth year histogram
    #test1()

    # check simple statistics
    test2()
    
    pass

if __name__ == "__main__":
    main()