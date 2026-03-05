# -*- coding: utf-8 -*-

import argparse
import xlsxwriter
from tqdm import tqdm

COLUMN_WIDTH_OFFSET = 5

def create_worksheet(input_path, worksheet_name, workbook, add_source_info=False, sort=False, verbose=False):
    if verbose is True:
        print("Loading data...")
    with open(input_path, "r", encoding="utf8") as f:
        input_lines = [line.strip("\r\n") for line in f.readlines()]
    
    persons = []
    for line in input_lines:
        name, surname, father_name, birth_year, place, municipality, nationality, death_year, death_place, fate, circumstances, id_number, file_name, page_number, column = line.split("\t")
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
            "IDNumber": id_number,
            "File": file_name,
            "Page": page_number,
            "Column": column
        }
        persons.append(person_data)
        
    column_names = ["Name", "Surname", "FatherName", "BirthYear", "Place", "Municipality", "Nationality", "DeathYear", "DeathPlace", "Fate", "Circumstances", "IDNumber"]
    if add_source_info is True:
        column_names.extend(["File", "Page", "Column"])
              
    worksheet = workbook.add_worksheet(worksheet_name)
    bold = workbook.add_format({"bold": True})
    for i, column_name in enumerate(column_names):
        worksheet.write(0, i, column_name, bold)
    
    worksheet.freeze_panes(1, 0)
    

    if sort is True:
        persons.sort(key=lambda x: (x["Surname"], x["Name"], x["FatherName"], x["BirthYear"], x["Place"], x["Municipality"], x["Nationality"], x["DeathYear"], x["DeathPlace"], x["Fate"], x["Circumstances"], x["IDNumber"], x["File"], x["Page"], x["Column"]))

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

def export_xlsx(input_path, output_path, add_source_info=False, sort=False, verbose=False):
    workbook = xlsxwriter.Workbook(output_path)
    
    create_worksheet(input_path=input_path, worksheet_name="Victims list from 1964", workbook=workbook, add_source_info=add_source_info, sort=sort, verbose=verbose)
    
    if verbose is True:
        print("Closing the output file...")

    workbook.close()

def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-i", "--input", required=True, help="The input path.")
    parser.add_argument("-o", "--output", required=True, help="The output path.")
    parser.add_argument("-f", "--source", action="store_true", help="Whether to include source information.")
    parser.add_argument("-s", "--sort", action="store_true", help="Whether to sort the data.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be verbose.")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    export_xlsx(input_path=input_path, output_path=output_path, sort=args.sort, add_source_info=args.source, verbose=args.verbose)

if __name__ == "__main__":
    main()
