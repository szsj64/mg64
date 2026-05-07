# `match.py` — Command-Line Options

## Required Options

| Option | Description |
|---|---|
| `-j`, `--jms` | Path to the JMS (Jasenovac Memorial Site) input file (JSON format). |
| `-m`, `--mg` | Path to the MG1964 input file (TSV format). |

## Output Options

| Option | Description |
|---|---|
| `-o`, `--output` | Path for the Excel (.xlsx) output file containing matched records. If not provided, no output file is created. |
| `-r`, `--report` | Path for the text report file. Contains match statistics, name comparison analysis, empty field analysis, death place/circumstances breakdowns, and optionally birth year difference distributions. |
| `-L`, `--list` | Print the list of matches to stdout. Each match is two lines: the JMS record fields, then a tab-indented line with the MG64 record fields. |
| `-O`, `--matches-output` | Path for a text file with the same content as `-L`. Can be used independently or together with `-L`. |

## Output Formatting Options

These options affect the output produced by `-L` and `-O`.

| Option | Description |
|---|---|
| `--separator` | Separator string between fields in the match listing. Default: `" \| "` (space-pipe-space). |
| `-d`, `--death` | Include death year and camp/death place in the match listing. For JMS: appends year of death and camp. For MG64: appends death year and death place. |
| `-S`, `--source` | Include the JMS `Source` field as the last field in the JMS line of the match listing. |
| `--score` | Include the Fellegi-Sunter composite score in the match listing (`-L`/`-O`) and as an extra column in the Excel output. The score is appended as the last field on the JMS line in the listing, and as a "Score" column in the Excel worksheet. Only produces output when used with `--fs` (scores are `None` in deterministic mode). |

## Input Options

| Option | Description |
|---|---|
| `-u`, `--url` | Path to a file containing JMS record URLs (one per line). Used with `-l` to add hyperlinks in the Excel output. |

## Grouping (Blocking) Options

These control which fields are used to build the blocking key. Records must share the same blocking key to be compared.

| Option | Description |
|---|---|
| `-f`, `--father` | Include father's name in the blocking key. |
| `-y`, `--year` | Include birth year in the blocking key. |
| `-p`, `--place` | Include birth place in the blocking key. |
| `-n`, `--names` | Apply name normalization (synonym dictionary) when building blocking keys. Maps variant spellings to canonical forms (e.g., "Avram" to "Abram", "Cohen" to "Koen"). Also neutralizes Croatian diacritics and German umlauts. |
| `-s`, `--sort` | Sort name and surname parts alphabetically in the blocking key. Handles cases where name/surname order is swapped between sources. |

## Matching (Comparison) Options

These control which field comparisons are performed within each block.

| Option | Description |
|---|---|
| `-F`, `--check-father-name` | Check that father's names match between JMS and MG64 records. |
| `-Y`, `--check-birth-years` | Check that birth years match between JMS and MG64 records. |
| `-P`, `--check-birth-places` | Check that birth places match between JMS and MG64 records. Zagreb and Beograd variants are normalized. |
| `-M`, `--maximum` | Maximum allowed absolute difference between birth years for a direct match. Default: `0` (exact match only). For example, `-M 2` allows birth years to differ by up to 2. |
| `-a`, `--alternative` | Allow alternative matching via the JMS `Source` field. When a direct field comparison fails, the script searches the free-text source field for the MG64 value. Applies to father's name, birth year, and birth place. |
| `-e`, `--empty` | Allow matching when JMS father's name, birth year, or birth place is empty. Records with empty fields that are used for blocking get a second-pass relaxed matching with those fields removed from the blocking key. |

## Fuzzy Name Matching Options

These options enable fuzzy (approximate) name matching instead of the default exact matching. When active, blocking uses sorted initials (first letters of name parts, sorted) instead of full names, and names are compared using the chosen distance metric. Only one fuzzy method can be used at a time.

| Option | Description |
|---|---|
| `--jwd` | Use **Jaro-Winkler similarity** for name comparison. Returns a score from 0 to 1 (1 = identical). Match if score >= threshold. Default threshold: `0.85`. |
| `--ld` | Use **Levenshtein distance** (edit distance) for name comparison. Returns the minimum number of single-character edits (insertions, deletions, substitutions). Match if distance <= threshold. Default threshold: `3`. |
| `--dld` | Use **Damerau-Levenshtein distance** for name comparison. Like Levenshtein, but also counts transpositions of adjacent characters as a single edit. Match if distance <= threshold. Default threshold: `3`. |
| `--nld` | Use **Normalized Levenshtein similarity** for name comparison. Computed as `1 - (LD / max(len(s1), len(s2)))`, giving a length-independent score from 0 to 1. Match if score >= threshold. Default threshold: `0.85`. |
| `--bm` | Use **Beider-Morse phonetic matching** for name comparison. Generates phonetic encodings for each name and computes Jaccard similarity of the encoding sets. Match if score >= threshold. Default threshold: `0.5`. Requires the `abydos` Python library (`pip install abydos`). |
| `--ff`, `--fuzzy-father` | Apply the active fuzzy matching method to father's name comparison as well. When enabled and father's name checking is active (`-F`), if the exact father's name match fails, the same fuzzy method and threshold used for name matching are applied to compare the father's names. Requires a fuzzy method (`--jwd`, `--ld`, `--dld`, `--nld`, or `--bm`) to be active. Empty father's names are not fuzzy-compared. |
| `-b`, `--block` | Number of initial letters per name/surname part used in the blocking key for fuzzy matching. Default: `1` (first letter only). For example, `-b 2` uses the first two letters of each name part. Higher values create more specific blocks (fewer candidates per block, faster but potentially missing matches where early letters differ). |
| `-t`, `--threshold` | Override the default threshold for the chosen fuzzy matching method. For similarity-based methods (`--jwd`, `--nld`, `--bm`), higher threshold = stricter. For distance-based methods (`--ld`, `--dld`), lower threshold = stricter. |

## Fellegi-Sunter Probabilistic Matching

These options enable the Fellegi-Sunter probabilistic record linkage model as an alternative to the default deterministic matching. Instead of requiring each field check to pass independently, the model computes a composite log-likelihood ratio score across all fields, allowing strong agreement on some fields to compensate for weaker agreement on others. The m (match) and u (non-match) probabilities are estimated automatically using the EM algorithm. Pairs are classified as matches (score >= upper threshold), non-matches (score < lower threshold), or review candidates (in between). Empty/missing fields are excluded from the score (they contribute no evidence either way). The `-a`/`--alternative` and `-e`/`--empty` flags are not used in Fellegi-Sunter mode.

| Option | Description |
|---|---|
| `--fs` | Enable Fellegi-Sunter probabilistic matching. Uses the same blocking as the deterministic mode. Field comparisons (`-F`, `-Y`, `-P`) control which fields contribute to the composite score. A fuzzy method (`--jwd`, etc.) controls how name similarity is computed and discretized; without one, name comparison is binary (exact match or not). |
| `--fs-upper` | Upper threshold for the composite score. Pairs scoring at or above this are classified as matches. Default: `8.0`. |
| `--fs-lower` | Lower threshold. Pairs scoring below this are classified as non-matches. Pairs between the lower and upper thresholds are in the review zone. Default: `2.0`. |
| `--fs-levels` | Number of discretization levels for continuous similarity fields (name, and father's name if `--ff` is active). Similarity scores are split into equal-width bins over [0, 1]. Higher values capture finer-grained similarity differences. Default: `3`. |
| `--fs-em-iterations` | Maximum number of EM iterations for estimating m and u probabilities. Default: `10`. |
| `--fs-review` | Path to an output file for pairs in the review zone (scores between `--fs-lower` and `--fs-upper`). Written as a TSV file with score, JMS fields, and MG fields. If not specified, review-zone pairs are discarded. |

## Candidate Selection

| Option | Description |
|---|---|
| `-A`, `--all` | Include all matching candidates for each JMS record, not just the best one. Without this flag, only the single best-scoring candidate is kept (highest similarity for `--jwd`/`--nld`/`--bm`, lowest distance for `--ld`/`--dld`, or first match for exact matching). With this flag, all candidates that pass all checks are included in the output, resulting in 1:many matching. |

## Other Options

| Option | Description |
|---|---|
| `-g`, `--group` | Group matched records by MG64 death place in the Excel output. |
| `-l`, `--link` | Include the full JMS and MG64 tables as separate worksheets in the Excel output and add hyperlinks from matched records to their source rows. |
| `-v`, `--verbose` | Print progress messages to stderr during execution. |

## Default Threshold Constants

| Method | Constant | Default Value |
|---|---|---|
| Jaro-Winkler | `DEFAULT_JWD_THRESHOLD` | 0.85 |
| Levenshtein | `DEFAULT_LD_THRESHOLD` | 3 |
| Damerau-Levenshtein | `DEFAULT_DLD_THRESHOLD` | 3 |
| Normalized Levenshtein | `DEFAULT_NLD_THRESHOLD` | 0.85 |
| Beider-Morse | `DEFAULT_BM_THRESHOLD` | 0.5 |
| Birth year difference | `DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE` | 0 |
| Fellegi-Sunter upper | `DEFAULT_FS_UPPER_THRESHOLD` | 8.0 |
| Fellegi-Sunter lower | `DEFAULT_FS_LOWER_THRESHOLD` | 2.0 |
| Fellegi-Sunter levels | `DEFAULT_FS_LEVELS` | 3 |
| Fellegi-Sunter EM iterations | `DEFAULT_FS_EM_ITERATIONS` | 10 |

## Usage Examples

```bash
# Basic exact matching with name normalization and all field checks
python match.py -j jms.json -m mg64.tsv -o output.xlsx -n -F -Y -P

# Fuzzy matching with Jaro-Winkler, allowing alternative source matching
python match.py -j jms.json -m mg64.tsv -o output.xlsx --jwd -t 0.8 -F -Y -P -a

# Fuzzy matching with Jaro-Winkler applied also to father's name
python match.py -j jms.json -m mg64.tsv -o output.xlsx --jwd --ff -F -Y -P

# Print match list with death info and source, using Damerau-Levenshtein
python match.py -j jms.json -m mg64.tsv --dld -t 2 -F -Y -P -L -d -S

# Generate a report with all candidates shown
python match.py -j jms.json -m mg64.tsv -r report.txt --nld -A -F -Y -P -a -e

# Write match list to file with custom separator
python match.py -j jms.json -m mg64.tsv -O matches.txt --separator " ; " -n -F -Y -P

# Fellegi-Sunter probabilistic matching with Jaro-Winkler and scores in output
python match.py -j jms.json -m mg64.tsv -o output.xlsx --fs --jwd -F -Y -P --score -v

# Fellegi-Sunter with custom thresholds, review output, and score in listing
python match.py -j jms.json -m mg64.tsv -o output.xlsx --fs --jwd --ff -F -Y -P --fs-upper 6 --fs-lower 1.5 --fs-review review.tsv --score -O matched_fs.txt
```
