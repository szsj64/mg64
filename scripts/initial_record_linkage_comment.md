# Record Linkage Analysis of `match.py`

This script performs **deterministic (rule-based) record linkage** between two Holocaust victim lists:

- **JMS** — the Jasenovac Memorial Site victims list (JSON, with fields like `name_and_surname`, `Father Name:`, `Date of Birth:`, `Place of Birth:`, `Source:`, etc.)
- **MG64** — a 1964 memorial book/register (TSV, with fields `Name`, `Surname`, `FatherName`, `BirthYear`, `Place`, etc.)

## Linkage Strategy

### 1. Blocking (grouping)

Rather than comparing every JMS record to every MG64 record (O(n*m)), the script partitions both datasets into groups using a **blocking key**. The key is built from the lowercased, cleaned name+surname, and optionally father's name, birth year, and/or birth place (`-f`, `-y`, `-p` flags). Only records sharing the same blocking key are compared. This is textbook blocking to reduce the comparison space.

### 2. Pre-processing / standardization

Before comparison:
- Croatian diacritics (č, ć, đ, š, ž) and German umlauts are neutralized (`neutralize_croatian_letters`, `neutralize_german_letters`).
- An extensive **name normalization table** (`prepare_name`) maps name variants to canonical forms (e.g., "Avram" -> "Abram", "Cohen" -> "Koen", "Alessandro" -> "Aleksandar"). This is a manually curated synonym dictionary — essentially a domain-specific equivalence mapping for names common in the Jewish communities of the former Yugoslavia.
- Optionally (`-s`), name parts are sorted alphabetically to handle swapped name/surname order.

### 3. Comparison / matching rules

Within each block, the script applies deterministic matching rules:
- **Father's name** (`-F`): exact match after normalization, or found in the JMS `Source:` field (alternative matching via `-a`), or allowed to be empty (`-e`).
- **Birth year** (`-Y`): exact match, or within a configurable tolerance (`-M`), or the MG64 year (within tolerance) appears in the JMS `Source:` field, or the JMS field is empty.
- **Birth place** (`-P`): exact match (with Zagreb/Beograd prefix normalization), or found in source, or empty.

This is a **conjunctive rule** — all enabled checks must pass simultaneously.

### 4. Fallback to source field

A distinctive feature is the use of the JMS `Source:` free-text field as a fallback evidence source. When a direct field doesn't match, the script searches the source text for the MG64 value. This is a pragmatic approach to compensate for incomplete or inconsistent structured data entry — the source field may contain transcribed original document text with the correct values.

### 5. Two-pass relaxed matching

When empty fields are allowed (`-e`) and those fields are also used for blocking (`-f`, `-y`, `-p`), the script runs a second pass. Records with empty blocking fields that didn't match in the first pass are re-grouped with fewer blocking dimensions (dropping the empty fields), then matched again. This prevents records from being stranded in overly specific blocks they can't match in.

### 6. Domain-specific filtering

Before matching, MG64 records are filtered by `filter_mg1964_data`, which excludes records whose death place mentions Jasenovac-system camps (Jasenovac, Stara Gradiška, Mlaka, Gradina, etc.). This suggests the goal is to find matches for MG64 victims who died *outside* the Jasenovac camp system — presumably because the Jasenovac victims are already well-documented in JMS, and the interest is in linking the less obvious cases.

## Classification in Record Linkage Terms

| Concept | Implementation |
|---|---|
| **Linkage type** | Deterministic / rule-based (no probabilistic weights) |
| **Blocking** | Composite key on name(+father, +year, +place) |
| **String comparison** | Exact match after normalization; no fuzzy/edit-distance |
| **Standardization** | Diacritic removal, synonym dictionary, prefix normalization |
| **Missing data handling** | Configurable: skip comparison, or use relaxed re-blocking |
| **Secondary evidence** | Free-text source field searched as fallback |
| **Match cardinality** | 1:1 greedy — each JMS person matches the *first* eligible MG64 person (via `break`) |
| **Classification** | Binary (match/non-match); no "possible match" / clerical review tier |

## Observations and Potential Considerations

- **Greedy 1:1 assignment**: The `break` on first MG64 match means the result depends on iteration order. If multiple MG64 candidates exist in a block, the first one wins. There is no scoring or ranking of candidates, so a suboptimal pairing could shadow the true match.
- **No fuzzy matching**: The comparison is strictly exact (post-normalization). Typos or OCR errors not covered by the synonym table will cause misses. Edit-distance or phonetic matching (e.g., Soundex, Beider-Morse) could increase recall, at the cost of precision.
- **No probabilistic weighting**: All fields are treated as equally decisive pass/fail gates. A Fellegi-Sunter style approach would assign weights based on field reliability and discriminating power, allowing trade-offs (e.g., a rare surname match compensating for a missing birth year).
- **The synonym table is a major asset**: The ~200-entry `prepare_name` table encodes deep domain knowledge about naming conventions in this specific population. This is the kind of curation that automated approaches struggle to replicate.
- **Source field search is substring-based**: Searching `str(mg_birth_year) in source_text` could produce false positives (e.g., "1923" matching inside an address or document number). In practice, for 4-digit years this is probably rare, but for shorter strings (father names) it could be noisier.

## Precision vs Recall Trade-off

The overall design is tuned for **precision over recall**. The matches it finds are high-confidence — two records must agree on name (after normalization) and pass all enabled checks (father's name, birth year, birth place) either directly or through the source field. The conjunctive rule and exact matching make false positives unlikely.

However, it will miss valid matches that fall outside its strict rules. Records that refer to the same person but have:
- a name variant not in the synonym table,
- a typo or OCR error (e.g., "Abramović" vs "Abramovič" if not covered),
- a swapped or truncated name that sorting alone doesn't resolve,
- missing data in fields used for blocking (unless `-e` is enabled),

will simply not link, silently.

The relaxed matching (`-e`, `-a`) and the source-field fallback are mechanisms to push recall higher without sacrificing too much precision, but they stay within the deterministic paradigm. A probabilistic or machine-learning approach could potentially recover more of those borderline matches, but at the cost of introducing uncertain matches that would need manual review.

## Summary

Overall, this is a well-structured deterministic linkage pipeline with thoughtful domain adaptations — the name synonym table, the source-field fallback, and the two-pass relaxed matching for missing data are all pragmatic solutions tailored to the specific challenges of linking historical Holocaust records across different documentation efforts.
