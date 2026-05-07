# -*- coding: utf-8 -*-

import argparse
import re
import requests

ROOT_URL = "https://docs.google.com/spreadsheets/d/1tGFHHICtguU5_S_QuCBpW0awQIGF-X7gY30j0URRlok/edit?gid=864982580"
DEFAULT_OUTPUT_PATH = "Auschwitz_Death_Certificates_1942-1943.xlsx"


def main():
    parser = argparse.ArgumentParser(description="Download Auschwitz Death Certificates table")
    parser.add_argument("-u", "--url", default=ROOT_URL, help=f"Google Sheets URL (default: {ROOT_URL})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_PATH, help=f"Output path (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show progress messages")
    args = parser.parse_args()

    url = args.url
    m = re.match(r"(https://docs\.google\.com/spreadsheets/d/[^/]+)", url)
    if not m:
        print(f"Error: URL does not match expected Google Sheets format: {url}")
        return

    base_url = m.group(1)
    export_url = base_url + "/export?format=xlsx"

    if args.verbose:
        print(f"Base URL: {base_url}")
        print(f"Export URL: {export_url}")
        print(f"Downloading...")

    resp = requests.get(export_url)
    resp.raise_for_status()

    if args.verbose:
        print(f"Saving to {args.output}...")

    with open(args.output, "wb") as f:
        f.write(resp.content)

    if args.verbose:
        print("Done.")


if __name__ == "__main__":
    main()
