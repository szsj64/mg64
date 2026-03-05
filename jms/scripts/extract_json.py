# -*- coding: utf-8 -*-

import argparse
from os import listdir
from os.path import join
import json
from tqdm import tqdm

def create_crude_data(input_dir, output_path, verbose=False):
    
    input_names=sorted(listdir(input_dir), key=int)
    
    person_dicts=[]
    
    taker=input_names
    if verbose is True:
        taker = tqdm(taker, desc="Extracting data", unit="pages")
    for input_name in taker:
        with open(join(input_dir, input_name), "r", encoding="utf8") as f:
            html=f.read()
        
        pattern="<h1>"
        p=html.find(pattern)
        p=html.find(pattern, p+1)+len(pattern)
        p2=html.find("<", p)
        
        name_and_surname=html[p:p2]
        
        fields=[]
        while(True):
            pattern="detail_title"
            p=html.find(pattern, p+1)
            if (p==-1):
                break
            p=html.find(">", p+1)+1
            p2=html.find("<", p)
            title=html[p:p2].strip("\r\n\t ")
            pattern="detail_content"
            p=html.find(pattern, p+1)
            p=html.find(">", p+1)+1
            p2=html.find("<", p)
            content=html[p:p2].strip("\r\n\t ")
            
            fields.append((title, content))
        
        person_dict=dict()
        person_dict["name_and_surname"]=name_and_surname
        for k, v in fields:
            person_dict[k]=v
        
        person_dicts.append(person_dict)
        
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(person_dicts, f)

def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-i", "--input", required=True, help="The input directory.")
    parser.add_argument("-o", "--output", required=True, help="The output path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to have status display.")
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output

    create_crude_data(input_dir=input_dir, output_path=output_dir, verbose=args.verbose)

if __name__ == "__main__":
    main()
