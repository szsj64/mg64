# MG64 - A version of the 1964 Yugoslav victim list

This repository contains a data pipeline for downloading and preparing the version of the 1964 Yugoslav victim list available at the Museum of Genocide (MG) in Belgrade, downloading and preparing the Jasenovac victim list available at the United States Holocaust Memorial Museum (USHMM), and cross-referencing and matching victim records between these two for the cases where the fate statements are conflicting. The main results are the the mentioned lists in [mg1964.xlsx](1964/data/xlsx/mg1964.xlsx) and [jms.xlsx](jms/data/jms.xlsx) as well as the matched records with both these lists containing even more references and clickable internal links in [matched.xlsx](matched.xlsx). Should downloading the individual USHMM pages take too long, an archive with previously downloaded pages is available [here](https://www.dropbox.com/scl/fi/b4j9ejz0v7t8cdcwbr85j/45409.zip?rlkey=lolep1jf7jwug0d2p0jhgjuxv&st=9mgbshkh&dl=1).

## Overview

This project automates three major stages:

1. **Jasenovac victim list data extraction** — Downloads individual victim pages from the USHMM, extracts structured fields (name and surname, father's name, birth year, place of birth, etc.) from HTML, and exports to JSON and XLSX.
2. **1964 Yugoslav victim list data extraction** — Downloads the multi-part PDF publication from the Museum of Genocide, extracts two-column text via PyMuPDF, and parses victim records by Yugoslav republic component (Slo, Hrv, BiH, Crg, Mak, Srb, Kos, Voj).
3. **Record matching** — Groups records from both sources by normalized name, surname, father's name, birth year, and place of birth, then matches them accounting for name variant normalization (Croatian/German diacritics, transliteration alternates), birth year tolerance, and alternative birth year references in source notes. Results are exported to an `.xlsx` file with optional cross-links and grouping by death place.

## Requirements

- Python 3
- System packages: `wget` (for downloading source data)
- Python packages (see `requirements.txt`):
  - `pymupdf==1.19.2` — PDF text extraction
  - `xlsxwriter==3.0.1` — Excel file generation
  - `tqdm==4.62.3` — Progress bars

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run the Full Pipeline

```bash
./pipeline.sh
```

This executes the three stages in order:
1. `jms/scripts/pipeline.sh` — download and extract the Jasenovac victim list data
2. `1964/scripts/pipeline.sh` — download and extract MG version of the 1964 Yugoslav victim list
3. `scripts/pipeline.sh` — match records and produce `matched.xlsx`

### Run with Docker

Run the script that builds the image and runs the pipeline in a container:

```bash
./pipeline_docker.sh
```

### Run Individual Stages

**The Jasenovac victim list data extraction:**

```bash
./jms/scripts/pipeline.sh
```

**The MG version of the 1964 Yugoslav victim list data extraction:**

```bash
./1964/scripts/pipeline.sh
```

**Matching only** (requires pre-existing extracted data):

```bash
./scripts/pipeline.sh
```

## Output

The output `matched.xlsx` workbook contains the following worksheets:

- **JasenovacVictimsList** (with `-l`) — Full Jasenovac victim list with links from matched records.
- **MG1964** (with `-l`) — Full MG version of the 1964 Yugoslav victim list with links from matched records.
- **Matched** — Pairs of JMS and MG1964 records that match, optionally grouped by death place.

