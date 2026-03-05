# -*- coding: utf-8 -*-

import argparse
import json
import xlsxwriter
from tqdm import tqdm

COLUMN_WIDTH_OFFSET = 5

def export_xlsx(input_path, output_path, verbose=False):
    if verbose is True:
        print("Loading data...")
    with open(input_path, "r", encoding="utf8") as f:
        person_dicts = json.load(f)
    
    persons = []
    for p in person_dicts:
        person_data = {
            "NameAndSurname": p.get("name_and_surname", ""),
            "Sex": p.get("Sex:", ""),
            "FatherName": p.get("Father Name:", ""),
            "Notes": p.get("Notes:", ""),
            "BirthYear": p.get("Date of Birth:", ""),
            "BirthPlace": p.get("Place of Birth:", "").split(",")[0].rstrip(),
            "BirthMunicipality": "" if "," not in p.get("Place of Birth:", "") else p.get("Place of Birth:", "").split(",")[1].lstrip(),
            "NationalityEthnicity": p.get("Nationality/Ethnicity:", ""),
            "Killed": p.get("Killed:", ""),
            "DeathYear": p.get("Year of Death:", ""),
            "DeathPlace": p.get("Death Place:", ""),
            "Camp": p.get("Camp:", ""),
            "Source": p.get("Source:", "")
        }
        persons.append(person_data)
        
    column_names = ["NameAndSurname", "FatherName", "BirthPlace", "BirthMunicipality", "BirthYear", "DeathYear", "Sex", "NationalityEthnicity", "DeathPlace", "Killed", "Camp", "Notes", "Source"]
              
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Jasenovac victims list")
    bold = workbook.add_format({"bold": True})
    for i, column_name in enumerate(column_names):
        worksheet.write(0, i, column_name, bold)
    
    worksheet.freeze_panes(1, 0)
    
    taker = list(enumerate(persons))
    if verbose is True:
        taker = tqdm(taker, desc="Writing persons data", unit="persons")
    column_max_lengths = {column_name: 0 for column_name in column_names}
    for i, person in taker:
        for j, column_name in enumerate(column_names):
            value = person.get(column_name, "")
            worksheet.write(i + 1, j, value)
            column_max_lengths[column_name] = max(column_max_lengths[column_name], len(value))
    
    for i, column_name in enumerate(column_names):
        worksheet.set_column(i, i, column_max_lengths[column_name] + COLUMN_WIDTH_OFFSET)

    if verbose is True:
        print("Closing the output file...")

    workbook.close()

def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-i", "--input", required=True, help="The input path.")
    parser.add_argument("-o", "--output", required=True, help="The output path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be verbose.")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    export_xlsx(input_path=input_path, output_path=output_path, verbose=args.verbose)

if __name__ == "__main__":
    main()
