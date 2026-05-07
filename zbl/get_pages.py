# -*- coding: utf-8 -*-

import argparse
import os
import re
import requests
from tqdm import tqdm

ROOT_URL = "https://zbl.lzmk.hr/"
NOT_FOUND_PATTERN = "Ups! Ta stranica nije"
BRUTE_STOP_THRESHOLD = 50


def collect_category_links(verbose=False):
    resp = requests.get(ROOT_URL)
    resp.raise_for_status()
    cat_ids = re.findall(r'href="https://zbl\.lzmk\.hr/\?cat=(\d+)"', resp.text)
    cat_ids = sorted(set(cat_ids), key=int)
    if verbose:
        print(f"Found {len(cat_ids)} category links.")
    return cat_ids


def collect_page_ids_from_category(cat_id, verbose=False):
    page_ids = set()
    page_num = 1
    while True:
        url = f"{ROOT_URL}?cat={cat_id}&paged={page_num}"
        resp = requests.get(url)
        if resp.status_code == 404 or NOT_FOUND_PATTERN in resp.text:
            break
        resp.raise_for_status()
        ids = re.findall(r'href="https://zbl\.lzmk\.hr/\?p=(\d+)"', resp.text)
        if not ids:
            break
        page_ids.update(ids)
        page_num += 1
    return page_ids


def main():
    parser = argparse.ArgumentParser(description="Download pages from ZBL")
    parser.add_argument("-o", "--output", default="zbl", help="Output directory (default: zbl)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show progress bars and messages")
    parser.add_argument("-w", "--overwrite", action="store_true", help="Overwrite existing pages")
    parser.add_argument("-b", "--brute", action="store_true", help="Brute force mode: try all IDs sequentially")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    saved_count = 0

    if args.brute:
        # Brute force mode: try IDs sequentially starting from 1
        if args.verbose:
            print("Brute force mode: trying all IDs sequentially...")
        consecutive_misses = 0
        page_id = 0
        while consecutive_misses < BRUTE_STOP_THRESHOLD:
            page_id += 1
            if args.verbose:
                print(f"\rFetching ID {page_id}...", end="", flush=True)
            filepath = os.path.join(args.output, f"{page_id}.html")
            if not args.overwrite and os.path.exists(filepath):
                consecutive_misses = 0
                saved_count += 1
                continue
            url = f"{ROOT_URL}?p={page_id}"
            resp = requests.get(url)
            if resp.status_code == 404 or NOT_FOUND_PATTERN in resp.text:
                consecutive_misses += 1
                continue
            resp.raise_for_status()
            consecutive_misses = 0
            saved_count += 1
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(resp.text)
        if args.verbose:
            print()
    else:
        # Step 1: collect category links
        cat_ids = collect_category_links(verbose=args.verbose)

        # Step 2: collect individual page IDs from each category page
        all_page_ids = set()
        if args.verbose:
            print("Collecting individual pages on category pages...")
            iterator = tqdm(cat_ids, desc="Category pages")
        else:
            iterator = cat_ids
        for cat_id in iterator:
            page_ids = collect_page_ids_from_category(cat_id, verbose=args.verbose)
            all_page_ids.update(page_ids)

        all_page_ids = sorted(all_page_ids, key=int)
        if args.verbose:
            print(f"Found {len(all_page_ids)} individual pages.")

        # Step 3: download individual pages
        if args.verbose:
            print("Downloading individual pages...")
            iterator = tqdm(all_page_ids, desc="Downloading pages")
        else:
            iterator = all_page_ids
        for page_id in iterator:
            filepath = os.path.join(args.output, f"{page_id}.html")
            if not args.overwrite and os.path.exists(filepath):
                saved_count += 1
                continue
            url = f"{ROOT_URL}?p={page_id}"
            resp = requests.get(url)
            resp.raise_for_status()
            saved_count += 1
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(resp.text)

    if args.verbose:
        print(f"Total pages obtained: {saved_count}")


if __name__ == "__main__":
    main()
