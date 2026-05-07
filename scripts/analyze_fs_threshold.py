# -*- coding: utf-8 -*-

"""
Fellegi-Sunter threshold analysis script.

Analyzes the score distribution from Fellegi-Sunter probabilistic matching,
determines an appropriate threshold (automatically or manually), cross-validates
against exact deterministic matches, and reports field-level disagreement statistics.

Usage examples:
    # Automatic threshold with all methods, cross-validate against exact matches:
    python3 analyze_fs_threshold.py -i matched_fs.txt -r review.tsv -e matched_M_0.txt

    # Use a specific manual threshold:
    python3 analyze_fs_threshold.py -i matched_fs.txt -r review.tsv -e matched_M_0.txt -t 8.5

    # Only max_gap method, verbose:
    python3 analyze_fs_threshold.py -i matched_fs.txt -r review.tsv -m max_gap -v
"""

import argparse
import collections
import math
import re
import sys
import unicodedata


FIELD_NAMES = ["name", "father", "birth_year", "birth_place", "death_year", "death_place"]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_match_file(path):
    """Parse a match.py output file (paired JMS/MG lines).

    Each match is two lines:
        JMS: NAME | FATHER | BIRTHYEAR | BIRTHPLACE | DEATHYEAR | DEATHPLACE [| SCORE]
        MG:  \\tName | Father | BirthYear | Place | DeathYear | DeathPlace

    Returns a list of dicts with keys: jms (tuple), mg (tuple), score (float|None).
    """
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if line.startswith("\t") or line.strip() == "":
            i += 1
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            i += 1
            continue

        score = None
        if len(parts) >= 7:
            try:
                score = float(parts[-1])
                jms_fields = tuple(parts[:6])
            except ValueError:
                jms_fields = tuple(parts[:6])
        else:
            jms_fields = tuple(parts[:6])

        mg_fields = ()
        if i + 1 < len(lines) and lines[i + 1].startswith("\t"):
            mg_line = lines[i + 1].strip()
            mg_parts = [p.strip() for p in mg_line.split("|")]
            mg_fields = tuple(mg_parts[:6]) if len(mg_parts) >= 6 else tuple(mg_parts)
            i += 2
        else:
            i += 1

        pairs.append({"jms": jms_fields, "mg": mg_fields, "score": score})

    return pairs


def parse_review_file(path):
    """Parse a review.tsv file (tab-separated, with header).

    Columns: score, jms_name, jms_father, jms_year, jms_place,
             mg_name, mg_father, mg_year, mg_place

    Returns a list of dicts with keys: jms (tuple), mg (tuple), score (float).
    The tuples are padded to 6 fields with empty strings for death_year/death_place.
    """
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            try:
                score = float(parts[0])
            except ValueError:
                continue
            jms_fields = (parts[1], parts[2], parts[3], parts[4], "", "")
            mg_fields = (parts[5], parts[6], parts[7], parts[8], "", "")
            pairs.append({"jms": jms_fields, "mg": mg_fields, "score": score})
    return pairs


# ---------------------------------------------------------------------------
# Normalization for cross-validation
# ---------------------------------------------------------------------------

def normalize_for_comparison(s):
    """Lowercase, remove diacritics, strip asterisks and bracketed annotations."""
    s = s.lower().strip()
    s = re.sub(r"\*", "", s)
    s = re.sub(r"\[.*?\]", "", s)
    s = s.strip()
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.category(c).startswith("M"))


def make_pair_key(jms_fields, mg_fields):
    """Create a normalized key for a (JMS, MG) pair for cross-validation.

    Uses name, father, birth_year, birth_place from both sides.
    """
    jms_norm = tuple(normalize_for_comparison(f) for f in jms_fields[:4])
    mg_norm = tuple(normalize_for_comparison(f) for f in mg_fields[:4])
    return (jms_norm, mg_norm)


# ---------------------------------------------------------------------------
# Threshold methods
# ---------------------------------------------------------------------------

def find_max_gap_threshold(unique_scores, score_counts=None):
    """Find threshold at the largest gap in the sorted unique score list.

    If score_counts is provided (dict mapping score -> count), the gap is
    weighted by the log of the minimum population on each side, favouring
    gaps that separate two large groups rather than gaps inside a cluster.

    Returns (threshold_midpoint, gap_size, lower_score, upper_score).
    """
    if len(unique_scores) < 2:
        val = unique_scores[0] if unique_scores else 0.0
        return val, 0.0, val, val

    # Pre-compute cumulative counts if available
    if score_counts is not None:
        total = sum(score_counts.get(s, 0) for s in unique_scores)
        cum = 0
        cum_at = {}
        for s in unique_scores:
            cum += score_counts.get(s, 0)
            cum_at[s] = cum
    else:
        total = len(unique_scores)
        cum_at = None

    best_score = -1.0
    best_gap = 0.0
    best_lo = unique_scores[0]
    best_hi = unique_scores[1]

    for i in range(len(unique_scores) - 1):
        gap = unique_scores[i + 1] - unique_scores[i]
        if cum_at is not None:
            n_below = cum_at[unique_scores[i]]
            n_above = total - n_below
            # Weight: gap * log(1 + min(n_below, n_above))
            # This penalizes gaps inside a small cluster
            weight = gap * math.log1p(min(n_below, n_above))
        else:
            weight = gap

        if weight > best_score:
            best_score = weight
            best_gap = gap
            best_lo = unique_scores[i]
            best_hi = unique_scores[i + 1]

    midpoint = (best_lo + best_hi) / 2.0
    return midpoint, best_gap, best_lo, best_hi


def otsu_threshold(scores, unique_scores):
    """Find threshold using Otsu's method (minimize weighted intra-class variance).

    Returns (threshold_midpoint, between_class_variance).
    """
    if len(unique_scores) < 2:
        val = unique_scores[0] if unique_scores else 0.0
        return val, 0.0

    n = len(scores)
    total_mean = sum(scores) / n

    best_threshold = unique_scores[0]
    best_between_var = -1.0

    count_below = 0
    sum_below = 0.0
    for t in unique_scores[:-1]:
        for s in scores:
            pass  # too slow for large sets
        break  # we'll use a sorted approach

    # Efficient single-pass approach using sorted scores
    sorted_scores = sorted(scores)
    cum_count = 0
    cum_sum = 0.0
    total_sum = sum(scores)
    score_idx = 0

    for ti in range(len(unique_scores) - 1):
        t = unique_scores[ti]
        while score_idx < n and sorted_scores[score_idx] <= t:
            cum_count += 1
            cum_sum += sorted_scores[score_idx]
            score_idx += 1

        w0 = cum_count / n
        w1 = 1.0 - w0
        if w0 == 0 or w1 == 0:
            continue

        mean0 = cum_sum / cum_count
        mean1 = (total_sum - cum_sum) / (n - cum_count)
        between_var = w0 * w1 * (mean0 - mean1) ** 2

        if between_var > best_between_var:
            best_between_var = between_var
            best_threshold = t

    idx = unique_scores.index(best_threshold)
    if idx + 1 < len(unique_scores):
        midpoint = (unique_scores[idx] + unique_scores[idx + 1]) / 2.0
    else:
        midpoint = best_threshold
    return midpoint, best_between_var


def kde_valley_threshold(scores, unique_scores, bandwidth=None):
    """Find threshold at the deepest valley of a Gaussian KDE over the scores.

    Uses a simple Gaussian kernel density estimate evaluated at the midpoints
    between consecutive unique scores.  Returns (threshold, density_at_valley).
    Falls back to max-gap if fewer than 3 unique scores.
    """
    if len(unique_scores) < 3:
        t, _, _, _ = find_max_gap_threshold(unique_scores)
        return t, 0.0

    if bandwidth is None:
        # Silverman's rule of thumb
        std = (sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(scores)) ** 0.5
        bandwidth = 1.06 * std * len(scores) ** (-1.0 / 5)
        if bandwidth <= 0:
            bandwidth = 1.0

    n = len(scores)
    midpoints = [(unique_scores[i] + unique_scores[i + 1]) / 2.0
                 for i in range(len(unique_scores) - 1)]

    min_density = float("inf")
    best_mp = midpoints[0]
    inv_bw = 1.0 / bandwidth
    norm_factor = 1.0 / (n * bandwidth * math.sqrt(2.0 * math.pi))

    for mp in midpoints:
        density = 0.0
        for s in scores:
            z = (mp - s) * inv_bw
            density += math.exp(-0.5 * z * z)
        density *= norm_factor
        if density < min_density:
            min_density = density
            best_mp = mp

    return best_mp, min_density


# ---------------------------------------------------------------------------
# Field-level analysis
# ---------------------------------------------------------------------------

def analyze_fields(pairs):
    """Analyze field-level disagreement between JMS and MG for matched pairs.

    Returns a dict mapping field name -> {disagreements, pct, empty_jms, empty_mg}.
    """
    n_fields = len(FIELD_NAMES)
    disagreements = {name: 0 for name in FIELD_NAMES}
    empty_jms = {name: 0 for name in FIELD_NAMES}
    empty_mg = {name: 0 for name in FIELD_NAMES}
    total = len(pairs)

    if total == 0:
        return {}

    for pair in pairs:
        jms = pair["jms"]
        mg = pair["mg"]
        for i, name in enumerate(FIELD_NAMES):
            if i >= len(jms) or i >= len(mg):
                continue
            jms_val = normalize_for_comparison(jms[i])
            mg_val = normalize_for_comparison(mg[i])

            if jms_val == "":
                empty_jms[name] += 1
            if mg_val == "":
                empty_mg[name] += 1

            if jms_val != "" and mg_val != "" and jms_val != mg_val:
                disagreements[name] += 1

    results = {}
    for name in FIELD_NAMES:
        results[name] = {
            "disagreements": disagreements[name],
            "pct": 100.0 * disagreements[name] / total,
            "empty_jms": empty_jms[name],
            "empty_mg": empty_mg[name],
        }
    return results


# ---------------------------------------------------------------------------
# Printing helpers
# ---------------------------------------------------------------------------

def print_separator(char="-", width=72):
    print(char * width)


def print_score_distribution(all_scores, label="Score distribution"):
    counter = collections.Counter(round(s, 2) for s in all_scores)
    unique = sorted(counter.keys(), reverse=True)
    total = len(all_scores)

    print(f"\n{label} ({total} total pairs, {len(unique)} distinct scores):\n")
    cumulative = 0
    print(f"  {'Score':>8}  {'Count':>8}  {'Cumulative':>10}  {'Cum %':>7}")
    print(f"  {'-----':>8}  {'-----':>8}  {'----------':>10}  {'-----':>7}")
    for s in unique:
        cumulative += counter[s]
        pct = 100.0 * cumulative / total
        print(f"  {s:8.2f}  {counter[s]:8d}  {cumulative:10d}  {pct:6.1f}%")


def print_field_analysis(field_stats, total, label="Field-level disagreement analysis"):
    print(f"\n{label} ({total} pairs):\n")
    print(f"  {'Field':<14}  {'Disagree':>8}  {'Pct':>7}  {'Empty JMS':>9}  {'Empty MG':>8}")
    print(f"  {'-----':<14}  {'--------':>8}  {'---':>7}  {'---------':>9}  {'--------':>8}")
    for name in FIELD_NAMES:
        if name not in field_stats:
            continue
        s = field_stats[name]
        print(f"  {name:<14}  {s['disagreements']:8d}  {s['pct']:6.1f}%  {s['empty_jms']:9d}  {s['empty_mg']:8d}")


def print_cross_validation(fs_keys, exact_keys, threshold, label="Cross-validation"):
    fs_above = fs_keys
    overlap = fs_above & exact_keys
    fs_only = fs_above - exact_keys
    exact_only = exact_keys - fs_above

    print(f"\n{label} (threshold = {threshold:.2f}):\n")
    print(f"  FS matches above threshold:     {len(fs_above):>8}")
    print(f"  Exact matches:                  {len(exact_keys):>8}")
    print(f"  In both (overlap):              {len(overlap):>8}")
    print(f"  FS-only (not in exact):         {len(fs_only):>8}")
    print(f"  Exact-only (not in FS):         {len(exact_only):>8}")
    if len(exact_keys) > 0:
        recall = 100.0 * len(overlap) / len(exact_keys)
        print(f"  Recall (exact recovered by FS): {recall:>7.1f}%")
    if len(fs_above) > 0:
        precision = 100.0 * len(overlap) / len(fs_above)
        print(f"  Precision (FS confirmed by exact): {precision:>4.1f}%")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze Fellegi-Sunter score distribution, determine threshold, "
                    "cross-validate against exact matches, and report field-level statistics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 analyze_fs_threshold.py -i matched_fs.txt -r review.tsv -e matched_M_0.txt\n"
               "  python3 analyze_fs_threshold.py -i matched_fs.txt -r review.tsv -t 8.5\n"
               "  python3 analyze_fs_threshold.py -i matched_fs.txt -m max_gap -v\n"
    )
    parser.add_argument("-i", "--input", dest="input_path", required=True,
                        help="FS match file from match.py with scores (e.g., matched_fs.txt)")
    parser.add_argument("-r", "--review", dest="review_path", default=None,
                        help="Review-zone TSV from match.py (e.g., review.tsv)")
    parser.add_argument("-e", "--exact", dest="exact_path", default=None,
                        help="Exact match file for cross-validation (e.g., matched_M_0.txt)")
    parser.add_argument("-t", "--threshold", type=float, default=None,
                        help="Manual threshold (skip automatic determination, use this value)")
    parser.add_argument("-m", "--method", choices=["max_gap", "otsu", "kde_valley", "all"],
                        default="all",
                        help="Automatic threshold method (default: all)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # 1. Load data
    # -----------------------------------------------------------------------
    print("Loading FS match file:", args.input_path)
    fs_pairs = parse_match_file(args.input_path)
    scored_pairs = [p for p in fs_pairs if p["score"] is not None]
    print(f"  Loaded {len(fs_pairs)} pairs ({len(scored_pairs)} with scores)")

    review_pairs = []
    if args.review_path:
        print("Loading review file:", args.review_path)
        review_pairs = parse_review_file(args.review_path)
        print(f"  Loaded {len(review_pairs)} review-zone pairs")

    all_scored = scored_pairs + review_pairs
    all_scores = [p["score"] for p in all_scored]

    if not all_scores:
        print("No scored pairs found. Nothing to analyze.")
        sys.exit(1)

    unique_scores = sorted(set(round(s, 2) for s in all_scores))

    # -----------------------------------------------------------------------
    # 2. Score distribution
    # -----------------------------------------------------------------------
    print_separator("=")
    print_score_distribution(all_scores, label="Complete score distribution (match + review)")

    if scored_pairs:
        match_scores = [p["score"] for p in scored_pairs]
        print_score_distribution(match_scores, label="Match-zone only")

    # -----------------------------------------------------------------------
    # 3. Threshold determination
    # -----------------------------------------------------------------------
    print_separator("=")
    thresholds = {}

    if args.threshold is not None:
        print(f"\nUsing manual threshold: {args.threshold:.2f}")
        chosen_threshold = args.threshold
    else:
        print("\nAutomatic threshold determination:\n")
        methods_to_run = (["max_gap", "otsu", "kde_valley"]
                          if args.method == "all"
                          else [args.method])

        score_counts = collections.Counter(round(s, 2) for s in all_scores)
        for method in methods_to_run:
            if method == "max_gap":
                t, gap, lo, hi = find_max_gap_threshold(unique_scores, score_counts)
                thresholds[method] = t
                print(f"  max_gap:    threshold = {t:.2f}  "
                      f"(gap = {gap:.2f}, between {lo:.2f} and {hi:.2f})")
            elif method == "otsu":
                t, bvar = otsu_threshold(all_scores, unique_scores)
                thresholds[method] = t
                print(f"  otsu:       threshold = {t:.2f}  "
                      f"(between-class variance = {bvar:.2f})")
            elif method == "kde_valley":
                t, density = kde_valley_threshold(all_scores, unique_scores)
                thresholds[method] = t
                print(f"  kde_valley: threshold = {t:.2f}  "
                      f"(valley density = {density:.6f})")

        # Prefer Otsu (standard bimodal separation), fall back to max_gap
        chosen_threshold = thresholds.get("otsu",
                           thresholds.get("max_gap",
                                          next(iter(thresholds.values()))))
        chosen_method = ("otsu" if "otsu" in thresholds else
                         "max_gap" if "max_gap" in thresholds else
                         next(iter(thresholds.keys())))

        if len(thresholds) > 1:
            vals = list(thresholds.values())
            if all(abs(v - vals[0]) < 0.01 for v in vals):
                print(f"\n  All methods agree: threshold = {chosen_threshold:.2f}")
            else:
                print(f"\n  Selected threshold ({chosen_method}): {chosen_threshold:.2f}")

    # -----------------------------------------------------------------------
    # 4. Apply threshold and report counts
    # -----------------------------------------------------------------------
    above = [p for p in all_scored if p["score"] >= chosen_threshold]
    below = [p for p in all_scored if p["score"] < chosen_threshold]

    print_separator("-")
    print(f"\nThreshold = {chosen_threshold:.2f}")
    print(f"  Pairs above threshold (matches): {len(above):>8}")
    print(f"  Pairs below threshold:           {len(below):>8}")
    print(f"  Total scored pairs:              {len(all_scored):>8}")

    # If multiple automatic thresholds were computed, show counts for each
    if args.threshold is None and len(thresholds) > 1:
        print("\n  Match counts at each automatic threshold:")
        for method, t in sorted(thresholds.items()):
            n_above = sum(1 for p in all_scored if p["score"] >= t)
            print(f"    {method:<14} (t={t:.2f}): {n_above} matches")

    # -----------------------------------------------------------------------
    # 5. Cross-validation against exact matches
    # -----------------------------------------------------------------------
    if args.exact_path:
        print_separator("=")
        print("Loading exact match file:", args.exact_path)
        exact_pairs = parse_match_file(args.exact_path)
        print(f"  Loaded {len(exact_pairs)} exact match pairs")

        exact_keys = set()
        for p in exact_pairs:
            if len(p["mg"]) >= 4:
                exact_keys.add(make_pair_key(p["jms"], p["mg"]))

        fs_above_keys = set()
        for p in above:
            if len(p["mg"]) >= 4:
                fs_above_keys.add(make_pair_key(p["jms"], p["mg"]))

        print_cross_validation(fs_above_keys, exact_keys, chosen_threshold)

        # If multiple thresholds, show cross-validation for each
        if args.threshold is None and len(thresholds) > 1:
            print("\n  Cross-validation at each automatic threshold:")
            for method, t in sorted(thresholds.items()):
                keys_at_t = set()
                for p in all_scored:
                    if p["score"] >= t and len(p["mg"]) >= 4:
                        keys_at_t.add(make_pair_key(p["jms"], p["mg"]))
                overlap = keys_at_t & exact_keys
                recall = 100.0 * len(overlap) / len(exact_keys) if exact_keys else 0
                print(f"    {method:<14} (t={t:.2f}): "
                      f"{len(keys_at_t)} FS matches, "
                      f"{len(overlap)} overlap, "
                      f"recall={recall:.1f}%")

    # -----------------------------------------------------------------------
    # 6. Field-level disagreement analysis
    # -----------------------------------------------------------------------
    # Only analyze pairs from the match file (which have all 6 fields)
    above_from_match_file = [p for p in scored_pairs if p["score"] >= chosen_threshold]
    if above_from_match_file:
        print_separator("=")
        field_stats = analyze_fields(above_from_match_file)
        print_field_analysis(field_stats, len(above_from_match_file),
                             label="Field-level disagreement for matches above threshold")

    below_from_match_file = [p for p in scored_pairs if p["score"] < chosen_threshold]
    if below_from_match_file:
        field_stats_below = analyze_fields(below_from_match_file)
        print_field_analysis(field_stats_below, len(below_from_match_file),
                             label="Field-level disagreement for match-file pairs below threshold")

    # -----------------------------------------------------------------------
    # 7. Verbose: show top gaps and example pairs near the threshold
    # -----------------------------------------------------------------------
    if args.verbose:
        print_separator("=")
        print(f"\nTop 10 score gaps (weighted by population balance):\n")
        gaps = []
        score_counts = collections.Counter(round(s, 2) for s in all_scores)
        total_n = len(all_scores)
        cum = 0
        cum_at = {}
        for s in unique_scores:
            cum += score_counts.get(s, 0)
            cum_at[s] = cum
        for idx in range(len(unique_scores) - 1):
            lo = unique_scores[idx]
            hi = unique_scores[idx + 1]
            gap = hi - lo
            n_below = cum_at[lo]
            n_above = total_n - n_below
            weight = gap * math.log1p(min(n_below, n_above))
            gaps.append((weight, gap, lo, hi, n_below, n_above))
        gaps.sort(reverse=True)
        print(f"  {'Weight':>8}  {'Gap':>6}  {'Below':>6}  {'Above':>6}  {'Low':>8}  {'High':>8}  {'Midpoint':>8}")
        print(f"  {'------':>8}  {'---':>6}  {'-----':>6}  {'-----':>6}  {'---':>8}  {'----':>8}  {'--------':>8}")
        for w, g, lo, hi, nb, na in gaps[:10]:
            mp = (lo + hi) / 2.0
            print(f"  {w:8.2f}  {g:6.2f}  {nb:6d}  {na:6d}  {lo:8.2f}  {hi:8.2f}  {mp:8.2f}")

    if args.verbose and all_scored:
        print_separator("=")
        print(f"\nExample pairs near threshold ({chosen_threshold:.2f}):\n")

        near = sorted(all_scored, key=lambda p: abs(p["score"] - chosen_threshold))[:10]
        for p in sorted(near, key=lambda p: -p["score"]):
            zone = "ABOVE" if p["score"] >= chosen_threshold else "BELOW"
            jms_str = " | ".join(p["jms"][:6]) if len(p["jms"]) >= 6 else " | ".join(p["jms"])
            mg_str = " | ".join(p["mg"][:6]) if len(p["mg"]) >= 6 else " | ".join(p["mg"])
            print(f"  [{zone}] score={p['score']:.2f}")
            print(f"    JMS: {jms_str}")
            print(f"    MG:  {mg_str}")
            print()

    print_separator("=")
    print("Done.")


if __name__ == "__main__":
    main()
