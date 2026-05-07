# -*- coding: utf-8 -*-

import argparse
import os
import re
import requests
from tqdm import tqdm

ROOT_URL = "https://hbl.lzmk.hr"
LIST_URL = f"{ROOT_URL}/Abecedarij?q=%20&s=0&n=30000"


def download_list_page(list_path, overwrite=False, verbose=False):
    if not overwrite and os.path.exists(list_path):
        if verbose:
            print(f"List file already exists: {list_path}")
        return
    if verbose:
        print(f"Downloading list page to {list_path}...")
    resp = requests.get(LIST_URL)
    resp.raise_for_status()
    with open(list_path, "w", encoding="utf-8") as f:
        f.write(resp.text)


def extract_hrefs(list_path):
    with open(list_path, "r", encoding="utf-8") as f:
        html = f.read()
    tags = re.findall(r'<a\s[^>]*class=["\']priblizanTekst["\'][^>]*>', html)
    hrefs = []
    for tag in tags:
        m = re.search(r"href=[\"']([^\"']*)[\"']", tag)
        if m:
            hrefs.append(m.group(1))
    return hrefs


def main():
    parser = argparse.ArgumentParser(description="Download pages from HBL")
    parser.add_argument("-o", "--output", default="hbl", help="Output directory (default: hbl)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show progress bars and messages")
    parser.add_argument("-w", "--overwrite", action="store_true", help="Overwrite existing pages")
    parser.add_argument("-l", "--list", default="list.html", help="List page file (default: list.html)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Step 1: download list page
    download_list_page(args.list, overwrite=args.overwrite, verbose=args.verbose)

    # Step 2: extract hrefs from list page
    hrefs = extract_hrefs(args.list)
    if args.verbose:
        print(f"Found {len(hrefs)} article links.")

    # Step 3: download individual pages
    saved_count = 0
    if args.verbose:
        iterator = tqdm(hrefs, desc="Downloading pages")
    else:
        iterator = hrefs
    for href in iterator:
        parts = href.split("/clanak/")
        if len(parts) < 2:
            continue
        name = parts[-1]
        filepath = os.path.join(args.output, name)
        if not args.overwrite and os.path.exists(filepath):
            saved_count += 1
            continue
        url = ROOT_URL + href
        resp = requests.get(url)
        resp.raise_for_status()
        saved_count += 1
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(resp.text)

    if args.verbose:
        print(f"Total pages obtained: {saved_count}")


if __name__ == "__main__":
    main()
