# -*- coding: utf-8 -*-

import fitz
import argparse
from os.path import basename

CONTENT_AREA = fitz.Rect(40, 45, 560, 798) 

COLUMN_DIVIDER = 298 

MAIN_HEADING_THRESHOLD = 10.0
SUBHEADING_THRESHOLD = 8.0

DATA_ROW_TYPE = "Data Row"
MAIN_HEADING_TYPE = "Main Heading"
SUBHEADING_TYPE = "Subheading"

def parse_two_column_pdf(file_path, verbose=False):
    
    base_name = basename(file_path)
    with fitz.open(file_path) as doc:
        all_pages_data = []

        taker = list(range(len(doc)))
        if verbose is True:
            from tqdm import tqdm
            taker = tqdm(taker)
        for page_number in taker:
            page = doc.load_page(page_number)
            blocks = page.get_text("dict", clip=CONTENT_AREA)["blocks"]
            page_data = []

            for block in blocks:
                if block["type"] == 0: 
                    for line in block["lines"]:
                        for span in line["spans"]:
                            bbox = span["bbox"]
                            text = span["text"].strip()
                            font_size = span["size"]
                            
                            if not text:
                                continue 

                            column = "left" if bbox[0] < COLUMN_DIVIDER else "right"

                            text_type = DATA_ROW_TYPE
                            if font_size >= MAIN_HEADING_THRESHOLD:
                                text_type = MAIN_HEADING_TYPE
                            elif font_size >= SUBHEADING_THRESHOLD:
                                text_type = SUBHEADING_TYPE
                            
                            page_data.append({
                                "text": text,
                                "type": text_type,
                                "file": base_name,
                                "page": page_number + 1,
                                "column": column,
                                "font_size": round(font_size, 2),
                                "y1": bbox[3]
                            })
            
            all_pages_data.append(page_data)

    return all_pages_data

def combine_broken_rows(parsed_data, max_spacing_diff=1.5):
    combined_data = []
    
    for items in parsed_data:
        if not items:
            continue

        final_items = []
        current_item = items[0]
        
        for i in range(1, len(items)):
            next_item = items[i]
            
            if current_item["type"] == DATA_ROW_TYPE and next_item["type"] == DATA_ROW_TYPE and current_item["column"] == next_item["column"]:
                
                vertical_gap = next_item["y1"] - current_item["y1"]
                
                if vertical_gap < current_item["font_size"] + max_spacing_diff:
                    current_item["text"] += " " + next_item["text"]
                    current_item["y1"] = next_item["y1"]
                else:
                    final_items.append(current_item)
                    current_item = next_item
            else:
                final_items.append(current_item)
                current_item = next_item
        
        final_items.append(current_item)
        combined_data.append(final_items)
        
    return combined_data

def main():
    
    parser = argparse.ArgumentParser(description="Parse two-column PDF and combine broken data rows.")
    parser.add_argument("-i", "--input", required=True, help="Input PDF file path.")
    parser.add_argument("-o", "--output", required=True, help="Output file path.")
    parser.add_argument("-l", "--location", default=None, help="Location information.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to have status display.")
    args = parser.parse_args()

    verbose = args.verbose
    
    file_name = args.input
    location_output_path = args.location
    try:
        parsed_content = parse_two_column_pdf(file_name, verbose=verbose)
        final_content = combine_broken_rows(parsed_content, max_spacing_diff=1.5) 
        output_locations = None
        if location_output_path is not None:
            output_locations = []
        with open(args.output, "w", encoding="utf8") as fo:
            for data in final_content:
                for item in data:
                    before = ""
                    if item["type"] == MAIN_HEADING_TYPE:
                        before = ""
                    elif item["type"] == SUBHEADING_TYPE:
                        before = "\t"
                    else:
                        before = "\t\t"
                        if output_locations is not None:
                            output_locations.append(f'{item["file"]}\t{item["page"]}\t{item["column"]}')

                    fo.write(f'{before}{item["text"]}\n')
        if location_output_path is not None:
            with open(location_output_path, "w", encoding="utf8") as fo:
                for location in output_locations:
                    fo.write(f"{location}\n")
    except Exception as e:
        print(f"An error occurred during parsing: {e}")

if __name__ == "__main__":
    main()
