# -*- coding: utf-8 -*-

import argparse
import xlsxwriter

from export_xlsx_partial import create_worksheet

def export_xlsx_combined(inputs, output_path, add_source_info=False, sort=False, verbose=False):
    workbook = xlsxwriter.Workbook(output_path)
    
    for input_path, worksheet_name in inputs:
        if verbose is True:
            print("Processing " + input_path)
        create_worksheet(input_path=input_path, worksheet_name=worksheet_name, workbook=workbook, add_source_info=add_source_info, sort=sort, verbose=verbose)
    
    if verbose is True:
        print("Closing the output file...")

    workbook.close()

def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-o", "--output", required=True, help="The output path.")
    parser.add_argument("-f", "--source", action="store_true", help="Whether to include source information.")
    parser.add_argument("-s", "--sort", action="store_true", help="Whether to sort the data.")
    parser.add_argument("inputs", nargs="*", help="Input paths and names for the worksheets.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be verbose.")
    args = parser.parse_args()

    output_path = args.output
    initial_inputs = args.inputs
    verbose = args.verbose

    inputs_count = len(initial_inputs) // 2
    inputs = []
    for i in range(inputs_count):
        inputs.append((initial_inputs[i], initial_inputs[inputs_count + i]))

    export_xlsx_combined(inputs=inputs, output_path=output_path, add_source_info=args.source, sort=args.sort, verbose=verbose)

if __name__ == "__main__":
    main()
