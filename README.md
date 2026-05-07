# MG64 - A version of the 1964 Yugoslav victim list

This repository contains a data pipeline for downloading and preparing the version of the 1964 Yugoslav victim list available at the Museum of Genocide (MG) in Belgrade, downloading and preparing the Jasenovac victim list available at the United States Holocaust Memorial Museum (USHMM), and cross-referencing and matching victim records between these two for the cases where the fate statements are conflicting. The main results are the the mentioned lists in [mg1964.xlsx](1964/data/xlsx/mg1964.xlsx) and [jms.xlsx](jms/data/jms.xlsx) as well as the matched records with both these lists containing even more references and clickable internal links in [matched.xlsx](matched.xlsx). Should downloading the individual USHMM pages take too long, an archive with previously downloaded pages is available [here](https://www.dropbox.com/scl/fi/b4j9ejz0v7t8cdcwbr85j/45409.zip?rlkey=lolep1jf7jwug0d2p0jhgjuxv&st=9mgbshkh&dl=1).

## Overview

This project automates five major stages:

1. **Jasenovac victim list data extraction** (`jms/`) — Downloads individual victim pages from the USHMM, extracts structured fields (name and surname, father's name, birth year, place of birth, etc.) from HTML, and exports to JSON and XLSX.
2. **1964 Yugoslav victim list data extraction** (`1964/`) — Downloads the multi-part PDF publication from the Museum of Genocide, extracts two-column text via PyMuPDF, and parses victim records by Yugoslav republic component (Slo, Hrv, BiH, Crg, Mak, Srb, Kos, Voj).
3. **Record matching** (`scripts/`) — Matches records from both sources using multiple methods:
   - **Deterministic exact matching** with name normalization (diacritic removal, phonetic simplification, 156 domain-specific synonym pairs), configurable birth year tolerance, and name-surname swap handling.
   - **Levenshtein distance-based approximate matching** with configurable distance thresholds and birth year tolerances, enabling progressive relaxation from strict to fuzzy criteria.
   - **Fellegi–Sunter probabilistic record linkage** with EM-estimated parameters, composite likelihood-ratio scoring, and configurable classification thresholds.
   Results are exported to an `.xlsx` file with optional cross-links and grouping by death place.
4. **Biographical lexicon cross-referencing** (`hbl/`, `zbl/`) — Downloads and parses entries from the Croatian Biographical Lexicon (HBL) and the Jewish Biographical Lexicon (ZBL), published by the Miroslav Krleža Institute of Lexicography, and matches them against the Jasenovac victim list to identify well-documented individuals with contradictory records.
5. **Auschwitz death certificate cross-referencing** (`auschwitz/`) — Matches records from Auschwitz death certificates (Sterbebücher) against both MG64 and the Jasenovac victim list to identify individuals appearing in both sources.

## Requirements

- Python 3
- System packages: `wget` (for downloading source data)
- Core Python packages (see `requirements.txt`):
  - `pymupdf==1.19.2` — PDF text extraction
  - `xlsxwriter==3.0.1` — Excel file generation
  - `tqdm==4.62.3` — Progress bars
- Additional packages used by cross-referencing and plotting scripts:
  - `openpyxl` — Reading Excel files (Auschwitz matching)
  - `matplotlib` — Plotting
  - `opencv-python` (`cv2`) — Image cropping for plots
  - `numpy` — Numerical operations

Install core dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run the Full Pipeline

```bash
./pipeline.sh
```

This executes the five stages in order:
1. `jms/scripts/pipeline.sh` — download and extract the Jasenovac victim list data
2. `1964/scripts/pipeline.sh` — download and extract MG version of the 1964 Yugoslav victim list
3. `scripts/pipeline.sh` — deterministic matching and produce `matched.xlsx`
4. `zbl/pipeline.sh` — download and match Jewish Biographical Lexicon entries
5. `hbl/pipeline.sh` — download and match Croatian Biographical Lexicon entries

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

**Deterministic matching only** (requires pre-existing extracted data):

```bash
./scripts/pipeline.sh
```

**Full matching sweep** including Fellegi–Sunter probabilistic linkage with multiple parameter configurations:

```bash
./scripts/pipeline2.sh
```

**Biographical lexicon cross-referencing:**

```bash
./hbl/pipeline.sh
./zbl/pipeline.sh
```

**Auschwitz death certificate cross-referencing:**

```bash
./auschwitz/pipeline.sh
```

### Plotting Scripts

The `scripts/` directory contains several plotting scripts used to generate figures for the accompanying paper:

- `plot_number_of_matches.py` — Number of matches across different parameter settings
- `plot_alternative_birth_years_histogram.py` — Distribution of alternative birth years in source notes
- `plot_matched_alternative_birth_years_histogram.py` — Birth year differences in matched records
- `plot_fs_scores.py` — Fellegi–Sunter score distribution histogram
- `count_jasenovac_and_sg_cases.py` — Count and chart MG64 records by Jasenovac-related death place

## Output

The output `matched.xlsx` workbook contains the following worksheets:

- **JasenovacVictimsList** (with `-l`) — Full Jasenovac victim list with links from matched records.
- **MG1964** (with `-l`) — Full MG version of the 1964 Yugoslav victim list with links from matched records.
- **Matched** — Pairs of JMS and MG1964 records that match, optionally grouped by death place.

