# -*- coding: utf-8 -*-

import argparse
import requests
from tqdm import tqdm
from os import makedirs
from os.path import join

def download_initial_links(source_id, output_dir, output_path, verbose=False):

    makedirs(output_dir, exist_ok=True)

    initial_url = "https://www.ushmm.org/online/hsv/source_view.php?SourceId=" + str(source_id)

    session = requests.session()
    r = session.get(initial_url)

    url = "https://www.ushmm.org/online/hsv/person_advance_search.php?SourceId=" + str(source_id) + "&sort=name_primary_sort"
    r = session.get(url, headers={"Referer": initial_url})

    html = r.text
    pattern = "</strong> of <strong>"
    p = html.find(pattern)
    if p == -1:
        if verbose is True:
            print("A problem occured when determining the number of documents.")
        return False
    p += len(pattern)
    p2 = html.find("<", p)
    count = int(html[p:p2].replace(".", "").replace(",", ""))

    with open(output_path, "w", encoding="utf8") as f:
        taker = list(range(count))
        if verbose:
            taker = tqdm(taker, desc="Downloading pages and links", unit="pages")
        for i in taker:
            url = "https://www.ushmm.org/online/hsv/show_doc_person.php?start_doc=" + str(i + 1)
            while True:
                try:
                    r = session.get(url)
                    if r.url.find("PersonId") != -1:
                        break
                except Exception as e:
                    pass
            with open(join(output_dir, str(i)), "w", encoding="utf8") as fo:
                fo.write(r.text)
            f.write(r.url + "\n")
            f.flush()

def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-i", "--id", required=True, help="Source ID.")
    parser.add_argument("-l", "--list", required=True, help="Output IDs file path.")
    parser.add_argument("-o", "--output", required=True, help="Output directory path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to have status display.")
    args = parser.parse_args()

    source_id = args.id

    download_initial_links(source_id=source_id, output_path=args.list, output_dir=args.output, verbose=args.verbose)

if __name__ == "__main__":
    main()
