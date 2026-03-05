# -*- coding: utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser(description="Parse two-column PDF and combine broken data rows.")
    parser.add_argument("-i", "--input", required=True, help="Input file path.")
    parser.add_argument("-l", "--location", default=None, help="Location file path.")
    parser.add_argument("-o", "--output", required=True, help="Output file path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to have status display.")
    args = parser.parse_args()

    verbose = args.verbose

    locations = None
    location_idx = 0
    if args.location is not None:
        with open(args.location, "r", encoding="utf8") as fi:
            locations = [line.strip() for line in fi.readlines()]
    with open(args.input, "r", encoding="utf8") as fi, open(args.output, "w", encoding="utf8") as fo:
        current_place = None
        taker = fi
        if verbose is True:
            from tqdm import tqdm
            lines = [line for line in taker.readlines()]
            taker = tqdm(lines)
        for line in taker:
            line = line.strip("\r\n")
            if line.startswith("\t") is False:
                current_municipality = line[len("Opština ") :]
            elif line.startswith("\t\t") is True:
                line = line.replace(",, rođen", ", rođen").replace(",) ", ") ")
                born_pattern = ", rođen"
                p = line.find(born_pattern)
                line = line[:p].replace(",", " ") + line[p:]
                line = " ".join(line.split())

                p = line.find(born_pattern)
                names_part = line[:p]
                line2 = line[p + len(born_pattern) :]
                if line2.startswith("a") is True or line2.startswith("o") is True:
                    line2 = line2[1:]
                line2 = line2.lstrip()

                left_p = names_part.find("(")
                right_p = names_part.find(")")

                surname = names_part[:left_p].strip()
                father_name = names_part[left_p + 1 : right_p].strip()
                name = names_part[right_p + 1 :].strip()

                number_length = 0
                while line2[: number_length + 1].isdigit() is True:
                    number_length += 1

                birth_year = line2[:number_length]

                line3 = line2[number_length:].lstrip(". ")

                p = line3.find(",")
                nationality = line3[:p].strip()

                line4 = line3[p + 1 :].lstrip()

                p = line4.find("19")
                fate = line4[:p].strip()
                death_year = line4[p : p + 4].strip()

                line5 = line4[p + 4 + 1 :].lstrip()

                p = line5.find(",")
                circumstances = line5[:p].strip()

                line6 = line5[p + 1 :].lstrip()

                left_p = line6.find("(")
                right_p = line6.find(")")
                death_place = line6[:left_p].strip()
                id_number = line6[left_p + 1 : right_p].strip()

                municipality = current_municipality
                place = current_place

                file_name = ""
                page_number = ""
                column = ""
                if locations is not None and location_idx < len(locations):
                    location_info = locations[location_idx].split("\t")
                    if len(location_info) == 3:
                        file_name, page_number, column = location_info
                    location_idx += 1
                final_line = f"{name}\t{surname}\t{father_name}\t{birth_year}\t{place}\t{municipality}\t{nationality}\t{death_year}\t{death_place}\t{fate}\t{circumstances}\t{id_number}\t{file_name}\t{page_number}\t{column}"
                fo.write(final_line + "\n")
            else:
                current_place = line.strip()

if __name__ == "__main__":
    main()
