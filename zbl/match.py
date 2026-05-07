# -*- coding: utf-8 -*-

import argparse
import json
import math
import os
import re
from tqdm import tqdm

try:
    from abydos.phonetic import BeiderMorse as _BeiderMorse
    _bm_encoder = _BeiderMorse()
    BEIDER_MORSE_AVAILABLE = True
except ImportError:
    BEIDER_MORSE_AVAILABLE = False

DEFAULT_ZBL_PAGES_DIR = "pages"

DEFAULT_JWD_THRESHOLD = 0.85
DEFAULT_LD_THRESHOLD = 3
DEFAULT_DLD_THRESHOLD = 3
DEFAULT_NLD_THRESHOLD = 0.85
DEFAULT_BM_THRESHOLD = 0.5

FUZZY_METHOD_JARO_WINKLER_DISTANCE = "jwd"
FUZZY_METHOD_LEVENSHTEIN_DISTANCE = "ld"
FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE = "dld"
FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE = "nld"
FUZZY_METHOD_BEIDER_MORSE = "bm"

HIGHER_IS_BETTER_METHODS = {FUZZY_METHOD_JARO_WINKLER_DISTANCE, FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE, FUZZY_METHOD_BEIDER_MORSE}
LOWER_IS_BETTER_METHODS = {FUZZY_METHOD_LEVENSHTEIN_DISTANCE, FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE}

def neutralize_croatian_letters(value):
    return value.replace("č", "c").replace("ć", "c").replace("đ", "d").replace("š", "s").replace("ž", "z").replace("Č", "C").replace("Ć", "C").replace("Đ", "D").replace("Š", "S").replace("Ž", "Z")

def neutralize_german_letters(value):
    return value.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss").replace("Ä", "A").replace("Ö", "O").replace("Ü", "U")

def prepare_name(name):
    pairs=[
        ("abenon", "abinum"),
        ("abinon", "abinum"),
        ("abinun", "abinum"),
        ("aharon", "aron"),
        ("ahron", "aron"),
        ("alberto", "albert"),
        ("alcalay", "alkalaj"),
        ("aleksander", "aleksandar"),
        ("alessandro", "aleksandar"),
        ("alexandar", "aleksandar"),
        ("alexander", "aleksandar"),
        ("alhalel", "alkalaj"),
        ("alkajal", "alkalaj"),
        ("alkalay", "alkalaj"),
        ("alkelai", "alkalaj"),
        ("alnahari", "albahari"),
        ("altarak", "altarac"),
        ("altaras", "altarac"),
        ("altaratz", "altarac"),
        ("altaraz", "altarac"),
        ("altarec", "altarac"),
        ("alterac", "altarac"),
        ("andjela", "andela"),
        ("angela", "andela"),
        ("aronne", "aron"),
        ("ashkenazi", "eskenazi"),
        ("askenazi", "eskenazi"),
        ("attias", "atias"),
        ("avigail", "abigal"),
        ("avram", "abram"),
        ("avramovicj", "abramovic"),
        ("awinon", "abinon"),
        ("bencijon", "bencion"),
        ("beniamin", "benjamin"),
        ("bension", "bencion"),
        ("bentzion", "bencion"),
        ("benzion", "bencion"),
        ("bernhard", "bernard"),
        ("bernhart", "bernard"),
        ("blanca", "blanka"),
        ("bogdanovitz", "bogdanovic"),
        ("cabiglio", "kabiljo"),
        ("cabilio", "kabiljo"),
        ("cohen", "koen"),
        ("conforti", "konforti"),
        ("elazar", "eleazar"),
        ("elia", "ilija"),
        ("eliash", "ilija"),
        ("elias", "ilija"),
        ("elieser", "eleazar"),
        ("eliezer", "eleazar"),
        ("elijas", "ilija"),
        ("elijau", "ilija"),
        ("elisha", "ilija"),
        ("elkelai", "alkalaj"),
        ("engel", "angel"),
        ("eshenazi", "eskenazi"),
        ("eskanazi", "eskenazi"),
        ("esparansa", "esperanca"),
        ("esperansa", "esperanca"),
        ("estera", "ester"),
        ("esther", "ester"),
        ("eugel", "eugen"),
        ("fincy", "finci"),
        ("finki", "finci"),
        ("fintzi", "finci"),
        ("gott", "got"),
        ("grunwald", "grinvald"),
        ("hajnrich", "heinrich"),
        ("hajnrich", "henrik"),
        ("hajnrih", "heinrich"),
        ("hajnrih", "henrik"),
        ("hayim", "haim"),
        ("heim", "haim"),
        ("heinrich", "henrik"),
        ("heinrih", "heinrich"),
        ("henrich", "henrik"),
        ("hertzer", "hercer"),
        ("icchak", "isak"),
        ("israejl", "israel"),
        ("izak", "isak"),
        ("izrael", "israel"),
        ("jaakow", "jakov"),
        ("jacob", "jakov"),
        ("jacov", "jakov"),
        ("jakob", "jakov"),
        ("jakow", "jakov"),
        ("janihel", "jahiel"),
        ("jcchak", "isak"),
        ("jichak", "isak"),
        ("johann", "johan"),
        ("josif", "josef"),
        ("josip", "josef"),
        ("jozef", "josef"),
        ("julius", "julio"),
        ("jzaak", "isak"),
        ("kabiglio", "kabiljo"),
        ("kabilio", "kabiljo"),
        ("kabilo", "kabiljo"),
        ("khana", "hana"),
        ("kohen", "koen"),
        ("komforte", "konforti"),
        ("komforti", "konforti"),
        ("konforte", "konforti"),
        ("kunorti", "konforti"),
        ("liliana", "ljiljana"),
        ("lilli", "lili"),
        ("lilly", "lili"),
        ("lily", "lili"),
        ("macstro", "maestro"),
        ("mekhael", "mihael"),
        ("menaham", "menahem"),
        ("mihajlo", "mihael"),
        ("moise", "mose"),
        ("moisie", "mose"),
        ("moiso", "mose"),
        ("mojsije", "mose"),
        ("mordechai", "mordehaj"),
        ("mosche", "mose"),
        ("moshe", "mose"),
        ("moso", "mose"),
        ("mosze", "mose"),
        ("nadezhda", "nadezda"),
        ("pinhas", "pinkas"),
        ("pollak", "polak"),
        ("rafajl", "rafael"),
        ("rakhel", "rahel"),
        ("refael", "rafael"),
        ("rifca", "rifka"),
        ("rifha", "rifka"),
        ("rifika", "rifka"),
        ("rivka", "rifka"),
        ("riwka", "rifka"),
        ("sabedaj", "sabetaj"),
        ("salomon", "salamon"),
        ("samoel", "samuel"),
        ("schwarc", "svarc"),
        ("schwarz", "svarc"),
        ("shabtai", "sabetaj"),
        ("shimshon", "simson"),
        ("shmuel", "samuel"),
        ("shtern", "stern"),
        ("smuel", "samuel"),
        ("sofie", "sofija"),
        ("solomon", "salamon"),
        ("szalom", "salamon"),
        ("tzadok", "zadok"),
        ("yaakov", "jakov"),
        ("yacob", "jakov"),
        ("yakow", "jakov"),
        ("yehoshua", "jesua"),
        ("yekhiel", "jahiel"),
        ("yisrael", "israel"),
        ("yitzkhak", "isak"),
        ("yosef", "josef"),
        ("ytzkhak", "isak"),
    ]
    name = name.lower()
    name = neutralize_german_letters(neutralize_croatian_letters(name))

    for a, b in pairs:
        name = name.replace(a, b)

    letter_simplifications = [("hh", "h"), ("ll", "l"), ("ph", "f"), ("dj", "d"), ("ch", "h"), ("th", "t"), ("y", "j"), ("kh", "h"), ("sh", "s"), ("ae", "a"), ("oe", "o"), ("ue", "u"), ("tz", "c"), ("z", "s"), ("ss", "s"), ("ije", "je"), ("je", "e"), ("ij", "i"), ("j", "i"), ("w", "v")]

    for a, b in letter_simplifications:
        name = name.replace(a, b)

    name = re.sub(r"(\w)\1+", r"\1", name)

    return name

def jaro_similarity(s1, s2):
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    match_distance = max(len1, len2) // 2 - 1
    if match_distance < 0:
        match_distance = 0
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    return (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3

def jaro_winkler_similarity(s1, s2, p=0.1):
    jaro = jaro_similarity(s1, s2)
    prefix = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
    return jaro + prefix * p * (1 - jaro)

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def damerau_levenshtein_distance(s1, s2):
    len1 = len(s1)
    len2 = len(s2)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost
            )
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)
    return d[len1][len2]

def normalized_levenshtein_similarity(s1, s2):
    if len(s1) == 0 and len(s2) == 0:
        return 1.0
    ld = levenshtein_distance(s1, s2)
    return 1.0 - ld / max(len(s1), len(s2))

def beider_morse_similarity(s1, s2):
    if not BEIDER_MORSE_AVAILABLE:
        raise RuntimeError("Beider-Morse requires the 'abydos' library. Install it with: pip install abydos")
    codes1 = set()
    for word in s1.split():
        if word:
            codes1.update(re.split(r'[\s|]+', _bm_encoder.encode(word)))
    codes2 = set()
    for word in s2.split():
        if word:
            codes2.update(re.split(r'[\s|]+', _bm_encoder.encode(word)))
    codes1.discard("")
    codes2.discard("")
    if not codes1 or not codes2:
        return 0.0
    intersection = codes1 & codes2
    union = codes1 | codes2
    return len(intersection) / len(union)

def compute_name_score(s1, s2, method):
    if method == FUZZY_METHOD_JARO_WINKLER_DISTANCE:
        return jaro_winkler_similarity(s1, s2)
    elif method == FUZZY_METHOD_LEVENSHTEIN_DISTANCE:
        return levenshtein_distance(s1, s2)
    elif method == FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE:
        return damerau_levenshtein_distance(s1, s2)
    elif method == FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE:
        return normalized_levenshtein_similarity(s1, s2)
    elif method == FUZZY_METHOD_BEIDER_MORSE:
        return beider_morse_similarity(s1, s2)

def passes_threshold(score, threshold, method):
    if method in HIGHER_IS_BETTER_METHODS:
        return score >= threshold
    else:
        return score <= threshold

def get_default_threshold(method):
    defaults = {
        FUZZY_METHOD_JARO_WINKLER_DISTANCE: DEFAULT_JWD_THRESHOLD,
        FUZZY_METHOD_LEVENSHTEIN_DISTANCE: DEFAULT_LD_THRESHOLD,
        FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE: DEFAULT_DLD_THRESHOLD,
        FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE: DEFAULT_NLD_THRESHOLD,
        FUZZY_METHOD_BEIDER_MORSE: DEFAULT_BM_THRESHOLD,
    }
    return defaults[method]

def select_best_candidate(candidates, fuzzy_method):
    if len(candidates) == 1:
        return candidates[0]
    if fuzzy_method is None:
        return candidates[0]
    if fuzzy_method in HIGHER_IS_BETTER_METHODS:
        return max(candidates, key=lambda c: c[1])
    else:
        return min(candidates, key=lambda c: c[1])

def get_sorted_initials(name_value, num_letters=1):
    initials = sorted([part[:num_letters] for part in name_value.split() if part])
    return "".join(initials)

def load_jms_data(input_path):
    with open(input_path, "r", encoding="utf8") as f:
        jms_data=json.load(f)
    return jms_data

def get_jms_birth_year(person):
    return person.get("Date of Birth:", "").split("[")[0].rstrip()

def get_jms_birth_place(person):
    return person.get("Place of Birth:", "").split(",")[0].rstrip()

def get_jms_birth_municipality(person):
    return ",".join(person.get("Place of Birth:", "").split(",")[1:]).rstrip()

def group_jms_data(data, use_birth_year=True, use_father_name=True, use_birth_place=False, prepare_names=False, use_initials_for_grouping=False, block_letters=1):
    jms_prepare = lambda x: x.lower().replace("*", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    def get_jms_key(x):
        name_value = names_preparation(x.get("name_and_surname", ""))
        if use_initials_for_grouping is True:
            name_value = get_sorted_initials(name_value, num_letters=block_letters)
        parts = [name_value]
        if use_father_name is True:
            parts.append(names_preparation(x.get("Father Name:", "")))
        if use_birth_year is True:
            parts.append(get_jms_birth_year(x))
        if use_birth_place is True:
            parts.append(get_jms_birth_place(x))
        return tuple(map(jms_prepare, parts))

    jms_groups = dict()
    for person in data:
        k = get_jms_key(person)
        if k not in jms_groups:
            jms_groups[k] = []
        jms_groups[k].append(person)

    return jms_groups

def group_zbl_data(data, use_birth_year=True, use_birth_place=False, prepare_names=False, simple_birth_place=True, use_initials_for_grouping=False, block_letters=1, verbose=False):
    zbl_prepare = lambda x: x.lower().replace("-", "").strip() if x else ""
    zbl_groups = dict()
    iterator = tqdm(data, desc="Grouping ZBL data", unit="pages") if verbose else data
    for zbl_id, page in iterator:
        start_tag = '<p class="Normal"><span class="Bold">'
        start_idx = page.find(start_tag)
        if start_idx == -1:
            continue
        start_idx += len(start_tag)
        end_idx = page.find("</span>", start_idx)
        raw_name = page[start_idx:end_idx]
        raw_name_text = re.sub(r'<[^>]+>', '', raw_name).strip()
        paren_in_name = re.search(r'\(([^)]*)\)', raw_name_text)
        name_text = re.sub(r'\([^)]*\)', '', raw_name_text).strip()
        name_words = name_text.replace("-", " ").replace(",", " ").split()
        non_caps = [w for w in name_words if not w.isupper()]
        caps = [w for w in name_words if w.isupper()]
        name_and_surname = " ".join(non_caps + caps)
        if prepare_names is True:
            name_and_surname = prepare_name(name_and_surname)

        # Extract birth place and birth year from parentheses after </span>
        after_tag = page[end_idx:end_idx + 100]
        paren_match = None
        for m in re.finditer(r'\(([^)]*)\)', after_tag):
            if re.search(r'\d{4}', m.group(1)):
                paren_match = m
                break
        birth_place = ""
        birth_year = ""
        death_place = None
        death_year = None
        if paren_match:
            paren_content = paren_match.group(1)
            birth_place = re.sub(r'[^\w ]', '', paren_content.split(",")[0].strip())
            if simple_birth_place:
                words = birth_place.split()
                capital_words = []
                for w in words:
                    if w and w[0].isupper():
                        capital_words.append(w)
                    else:
                        break
                if capital_words:
                    birth_place = " ".join(capital_words)
            year_match = re.search(r'\d{4}', paren_content)
            if year_match:
                birth_year = year_match.group(0)
            death_place = None
            if "–" in paren_content:
                after_dash = paren_content.split("–", 1)[1]
                death_place = re.sub(r'[^\w ]', '', after_dash.split(",")[0].strip())
                death_year_match = re.search(r'\d{4}', after_dash)
                if death_year_match:
                    death_year = death_year_match.group(0)

        if paren_match:
            snippet_end = end_idx + paren_match.end()
        else:
            snippet_end = end_idx
        raw_snippet = page[start_idx:snippet_end]
        snippet = re.sub(r'<[^>]+>', '', raw_snippet).strip()

        zbl_key_parts = [name_and_surname]
        if use_initials_for_grouping is True:
            zbl_key_parts[0] = get_sorted_initials(name_and_surname, num_letters=block_letters)
        if use_birth_year is True:
            zbl_key_parts.append(birth_year)
        if use_birth_place is True:
            zbl_key_parts.append(birth_place)
        zbl_key = tuple(map(zbl_prepare, zbl_key_parts))

        entry = (zbl_id, name_and_surname, birth_place, birth_year, death_place, death_year, snippet, page)
        if zbl_key not in zbl_groups:
            zbl_groups[zbl_key] = []
        zbl_groups[zbl_key].append(entry)

        if paren_in_name is not None:
            paren_name_content = paren_in_name.group(1)
            if "," in paren_name_content:
                # Parenthesized content has commas: treat it as an alternate full name
                # (e.g. "SURNAME, Firstname") and create an additional group key for it
                alt_words = paren_name_content.replace(",", " ").split()
                if len(alt_words) >= 2:
                    alt_non_caps = [w for w in alt_words if not w.isupper()]
                    alt_caps = [w for w in alt_words if w.isupper()]
                    alt_name_and_surname = " ".join(alt_non_caps + alt_caps)
                    if prepare_names is True:
                        alt_name_and_surname = prepare_name(alt_name_and_surname)
                    alt_zbl_key_parts = [alt_name_and_surname]
                    if use_initials_for_grouping is True:
                        alt_zbl_key_parts[0] = get_sorted_initials(alt_name_and_surname, num_letters=block_letters)
                    if use_birth_year is True:
                        alt_zbl_key_parts.append(birth_year)
                    if use_birth_place is True:
                        alt_zbl_key_parts.append(birth_place)
                    alt_zbl_key = tuple(map(zbl_prepare, alt_zbl_key_parts))
                    if alt_zbl_key not in zbl_groups:
                        zbl_groups[alt_zbl_key] = []
                    zbl_groups[alt_zbl_key].append(entry)
            else:
                paren_words_single = paren_name_content.split()
                if len(paren_words_single) == 1 and name_words:
                    paren_word = paren_words_single[0]
                    # Only proceed if all outside words start with different letters,
                    # so there is no ambiguity about which word to replace
                    first_letters = [w[0].lower() for w in name_words if w]
                    if len(set(first_letters)) > 1:
                        paren_first = paren_word[0].lower() if paren_word else ""
                        # Replace the first outside word whose initial matches the paren word's initial
                        alt_name_words = []
                        replaced = False
                        for w in name_words:
                            if not replaced and w and w[0].lower() == paren_first:
                                alt_name_words.append(paren_word)
                                replaced = True
                            else:
                                alt_name_words.append(w)
                        if replaced:
                            # Build the alternate name with the same caps/non-caps reordering
                            alt_non_caps = [w for w in alt_name_words if not w.isupper()]
                            alt_caps = [w for w in alt_name_words if w.isupper()]
                            alt_name_and_surname = " ".join(alt_non_caps + alt_caps)
                            if prepare_names is True:
                                alt_name_and_surname = prepare_name(alt_name_and_surname)
                            alt_zbl_key_parts = [alt_name_and_surname]
                            if use_initials_for_grouping is True:
                                alt_zbl_key_parts[0] = get_sorted_initials(alt_name_and_surname, num_letters=block_letters)
                            if use_birth_year is True:
                                alt_zbl_key_parts.append(birth_year)
                            if use_birth_place is True:
                                alt_zbl_key_parts.append(birth_place)
                            alt_zbl_key = tuple(map(zbl_prepare, alt_zbl_key_parts))
                            if alt_zbl_key not in zbl_groups:
                                zbl_groups[alt_zbl_key] = []
                            zbl_groups[alt_zbl_key].append(entry)

    return zbl_groups

def get_zbl_file_paths(zbl_dir):
    file_names = [f for f in os.listdir(zbl_dir) if f.endswith(".html")]
    file_names.sort(key=lambda x: int(x.replace(".html", "")))
    file_paths = [os.path.join(zbl_dir, f) for f in file_names]
    return file_paths

def load_zbl_data(zbl_dir, verbose=False):
    file_paths = get_zbl_file_paths(zbl_dir)

    zbl_data = []
    iterator = tqdm(file_paths, desc="Loading ZBL pages", unit="pages") if verbose else file_paths
    for file_path in iterator:
        with open(file_path, "r", encoding="utf8") as f:
            content = f.read()
        zbl_id = int(os.path.basename(file_path).replace(".html", ""))
        zbl_data.append((zbl_id, content))

    return zbl_data

def find_matches(jms_groups, zbl_groups, exclude_death_places=["jasenovac", "gradiška"], exclude_exact_death_places=["logor"], look_for_father_name=True, drop_father_name_letters=2, min_shortened_father_name_length=3, use_birth_place_for_matching=True, use_birth_year_for_matching=True, max_allowed_birth_year_difference=None, look_for_birth_place_in_source=True, look_for_birth_year_in_source=False, allow_empty_death_place=True, no_death_place_patterns=["preživio", "preživjela"], look_for_a_year_after_death_year=True, allow_empty_jms_father_name=False, allow_empty_jms_birth_place=True, allow_empty_jms_birth_year=False, allow_empty_jms_birth_place_and_year=False, fuzzy_method=None, fuzzy_threshold=None, prepare_names=False, verbose=False):
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    common_keys = sorted(set(jms_groups.keys()).intersection(set(zbl_groups.keys())))
    matches = []
    iterator = tqdm(common_keys, desc="Finding matches", unit="keys") if verbose else common_keys
    for k in iterator:
        for jms_person in jms_groups[k]:
            candidates = []
            for zbl_entry in zbl_groups[k]:
                zbl_id, name_and_surname, birth_place, birth_year, death_place, death_year, snippet, page = zbl_entry

                # Fuzzy name check
                if fuzzy_method is not None:
                    jms_name = names_preparation(jms_person.get("name_and_surname", "")).lower().replace("*", "").replace("-", "")
                    zbl_name = name_and_surname.lower().replace("-", "").strip()
                    name_score = compute_name_score(jms_name, zbl_name, fuzzy_method)
                    # Also try reversed word order to handle name swaps
                    zbl_reversed = " ".join(reversed(zbl_name.split()))
                    jms_reversed = " ".join(reversed(jms_name.split()))
                    reversed_scores = [
                        compute_name_score(jms_name, zbl_reversed, fuzzy_method),
                        compute_name_score(jms_reversed, zbl_name, fuzzy_method),
                    ]
                    if fuzzy_method in HIGHER_IS_BETTER_METHODS:
                        name_score = max(name_score, *reversed_scores)
                    else:
                        name_score = min(name_score, *reversed_scores)
                    if not passes_threshold(name_score, fuzzy_threshold, fuzzy_method):
                        continue
                else:
                    name_score = None

                if allow_empty_jms_birth_place_and_year is False:
                    jms_bp = get_jms_birth_place(jms_person).lower().strip()
                    jms_by = get_jms_birth_year(jms_person).replace("-", "").replace("*", "").strip()
                    if jms_bp == "" and jms_by == "":
                        continue
                if use_birth_place_for_matching is True:
                    jms_birth_place = get_jms_birth_place(jms_person).lower().strip()
                    if not (allow_empty_jms_birth_place is True and jms_birth_place == ""):
                        zbl_birth_place = birth_place.lower().strip() if birth_place else ""
                        if jms_birth_place != zbl_birth_place:
                            if look_for_birth_place_in_source is True and zbl_birth_place:
                                jms_source = jms_person.get("Source:", "")
                                if zbl_birth_place not in jms_source.lower():
                                    continue
                            else:
                                continue
                if use_birth_year_for_matching is True:
                    jms_birth_year = get_jms_birth_year(jms_person).replace("-", "").replace("*", "").strip()
                    if not (allow_empty_jms_birth_year is True and jms_birth_year == ""):
                        zbl_birth_year = birth_year.strip() if birth_year else ""
                        birth_year_matched = False
                        if max_allowed_birth_year_difference is not None:
                            try:
                                if abs(int(jms_birth_year) - int(zbl_birth_year)) <= max_allowed_birth_year_difference:
                                    birth_year_matched = True
                            except ValueError:
                                if jms_birth_year == zbl_birth_year:
                                    birth_year_matched = True
                        else:
                            if jms_birth_year == zbl_birth_year:
                                birth_year_matched = True
                        if not birth_year_matched:
                            if look_for_birth_year_in_source is True and zbl_birth_year:
                                jms_source = jms_person.get("Source:", "")
                                if zbl_birth_year not in jms_source:
                                    continue
                            else:
                                continue
                death_place_ok = (death_place is not None and death_place != "") or allow_empty_death_place is True
                if death_place_ok and all(exclude not in (death_place or "").lower() for exclude in exclude_death_places) and all(exclude not in (death_place or "").lower() for exclude in exclude_exact_death_places):
                    if (death_place is None or death_place == "") and no_death_place_patterns is not None:
                        footer_idx_dp = page.find('<footer class="entry-footer">')
                        page_body_dp = page[:footer_idx_dp] if footer_idx_dp != -1 else page
                        page_text_dp = re.sub(r'<[^>]+>', '', page_body_dp).lower()
                        if not any(pattern.lower() in page_text_dp for pattern in no_death_place_patterns):
                            if look_for_a_year_after_death_year is True:
                                jms_death_year = jms_person.get("Year of Death:", "").replace("-", "").replace("*", "").strip()
                                if jms_death_year:
                                    try:
                                        death_year_int = int(jms_death_year)
                                        # Filter out years >= 2000 as they are not valid historical years for this dataset
                                        years_in_text = [int(y) for y in re.findall(r'\d{4}', page_text_dp) if int(y) < 2000]
                                        if not any(y > death_year_int for y in years_in_text):
                                            continue
                                    except ValueError:
                                        continue
                                else:
                                    continue
                            else:
                                continue
                    jms_father_name = jms_person.get("Father Name:", "").lower()
                    footer_idx = page.find('<footer class="entry-footer">')
                    page_body = page[:footer_idx] if footer_idx != -1 else page
                    name_start = page_body.find('<p class="Normal"><span class="Bold">')
                    if name_start != -1:
                        page_body = page_body[name_start:]
                    page_text = re.sub(r'<[^>]+>', '', page_body).lower()
                    father_name_search = jms_father_name if drop_father_name_letters is None else jms_father_name[:-drop_father_name_letters]
                    # If there is no father name in JMS, skip all father name conditions
                    if look_for_father_name is False or jms_father_name == "" or (allow_empty_jms_father_name is True and jms_father_name == ""):
                        father_name_found = True
                    elif len(father_name_search) >= min_shortened_father_name_length:
                        # Full shortened name is long enough: search for it preceded by a space
                        father_name_found = (" " + father_name_search) in page_text
                    else:
                        # Shortened name is too short for a reliable standalone match;
                        # fall back to searching for it after the word "Sin" (son of) or "Kći" (daughter of)
                        father_name_found = (" sin " + father_name_search) in page_text or (" kći " + father_name_search) in page_text
                    if father_name_found:
                        candidates.append((zbl_entry, name_score))

            if candidates:
                if fuzzy_method is not None:
                    best_entry, best_score = select_best_candidate(candidates, fuzzy_method)
                    matches.append((jms_person, best_entry))
                else:
                    for zbl_entry, _ in candidates:
                        matches.append((jms_person, zbl_entry))

    return matches

def save_matches(matches, output_path, min_shortened_father_name_length=3, verbose=False):
    for jms_person, zbl_entry in matches:
        jms_name = jms_person.get("name_and_surname", "")
        jms_father = jms_person.get("Father Name:", "")
        jms_birth_year = get_jms_birth_year(jms_person)
        jms_birth_place = get_jms_birth_place(jms_person)
        jms_death_year = jms_person.get("Year of Death:", "")
        jms_camp = jms_person.get("Camp:", "")
        print(f"{jms_name} | {jms_father} | {jms_birth_year} | {jms_birth_place} | {jms_death_year} | {jms_camp}")
        zbl_id, name_and_surname, birth_place, birth_year, death_place, death_year, snippet, page = zbl_entry
        jms_father_name = jms_person.get("Father Name:", "").lower()
        father_name_search = jms_father_name[:-2] if len(jms_father_name) > 2 else jms_father_name
        print(f"\t{snippet} [{father_name_search}]")
        footer_idx = page.find('<footer class="entry-footer">')
        page_body = page[:footer_idx] if footer_idx != -1 else page
        name_start = page_body.find('<p class="Normal"><span class="Bold">')
        if name_start != -1:
            page_body = page_body[name_start:]
        page_text = re.sub(r'<[^>]+>', '', page_body)
        father_idx = page_text.lower().find(" " + father_name_search) if father_name_search and len(father_name_search) >= min_shortened_father_name_length else -1
        if father_idx != -1:
            ctx_start = max(0, father_idx - 40)
            ctx_end = min(len(page_text), father_idx + len(father_name_search) + 1 + 40)
            father_ctx = page_text[ctx_start:ctx_end].strip()
            print(f"\t[...{father_ctx}...]")
        print(f"\thttps://zbl.lzmk.hr/?p={zbl_id}")

    return

    output = []
    for jms_person, zbl_entry in matches:
        zbl_id, name_and_surname, birth_place, birth_year, death_place, death_year, snippet, page = zbl_entry
        output.append({
            "jms": jms_person,
            "zbl": {
                "id": zbl_id,
                "name_and_surname": name_and_surname,
                "birth_place": birth_place,
                "birth_year": birth_year,
                "death_place": death_place,
                "death_year": death_year,
            }
        })
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

def match_data(jms_input_path, zbl_dir, output_path, verbose=False, fuzzy_method=None, fuzzy_threshold=None, block_letters=1):
    if verbose is True:
        print("Loading JMS data...")
    jms_data = load_jms_data(input_path=jms_input_path)

    if verbose is True:
        print("Grouping JMS data...")
    use_birth_year = True
    use_father_name = False
    use_birth_place = False
    prepare_names = True
    use_initials = fuzzy_method is not None
    jms_groups = group_jms_data(data=jms_data, use_birth_year=use_birth_year, use_father_name=use_father_name, use_birth_place=use_birth_place, prepare_names=prepare_names, use_initials_for_grouping=use_initials, block_letters=block_letters)

    if verbose is True:
        print(f"Number of JMS groups: {len(jms_groups)}")

    if verbose is True:
        print("Loading ZBL data...")
    zbl_data = load_zbl_data(zbl_dir=zbl_dir, verbose=verbose)

    if verbose is True:
        print(f"Number of ZBL pages loaded: {len(zbl_data)}")

    if verbose is True:
        print("Grouping ZBL data...")
    zbl_groups = group_zbl_data(data=zbl_data, use_birth_year=use_birth_year, use_birth_place=use_birth_place, prepare_names=prepare_names, use_initials_for_grouping=use_initials, block_letters=block_letters)

    if verbose is True:
        print(f"Number of ZBL groups: {len(zbl_groups)}")

    matches = find_matches(jms_groups=jms_groups, zbl_groups=zbl_groups, fuzzy_method=fuzzy_method, fuzzy_threshold=fuzzy_threshold, prepare_names=prepare_names, verbose=verbose)

    if verbose is True:
        print(f"Number of matches: {len(matches)}")

    matches.sort(key=lambda m: (m[0].get("name_and_surname", ""), m[0].get("Date of Birth:", ""), m[1][0]))

    if verbose is True:
        print("Saving matches...")
    save_matches(matches=matches, output_path=output_path, verbose=verbose)


def main():
    parser = argparse.ArgumentParser(description="Match JMS and ZBL data")
    parser.add_argument("-j", "--jms", required=True, help="JMS input path.")
    parser.add_argument("-z", "--zbl", default=DEFAULT_ZBL_PAGES_DIR, help="ZBL pages directory.")
    parser.add_argument("-o", "--output", required=True, help="Output path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be verbose.")
    fuzzy_group = parser.add_mutually_exclusive_group()
    fuzzy_group.add_argument("--jwd", action="store_true", help="Use Jaro-Winkler distance for fuzzy name matching.")
    fuzzy_group.add_argument("--ld", action="store_true", help="Use Levenshtein distance for fuzzy name matching.")
    fuzzy_group.add_argument("--dld", action="store_true", help="Use Damerau-Levenshtein distance for fuzzy name matching.")
    fuzzy_group.add_argument("--nld", action="store_true", help="Use normalized Levenshtein distance for fuzzy name matching.")
    fuzzy_group.add_argument("--bm", action="store_true", help="Use Beider-Morse phonetic matching.")
    parser.add_argument("-t", "--threshold", type=float, default=None, help="Threshold for fuzzy matching. Defaults: JWD=0.85, LD=3, DLD=3, NLD=0.85, BM=0.5.")
    parser.add_argument("-b", "--block", type=int, default=1, help="Number of initial letters per name/surname part used in the blocking key for fuzzy matching (default: 1).")
    args = parser.parse_args()

    jms_input_path = args.jms
    zbl_dir = args.zbl
    output_path = args.output
    verbose = args.verbose

    fuzzy_method = None
    if args.jwd:
        fuzzy_method = FUZZY_METHOD_JARO_WINKLER_DISTANCE
    elif args.ld:
        fuzzy_method = FUZZY_METHOD_LEVENSHTEIN_DISTANCE
    elif args.dld:
        fuzzy_method = FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE
    elif args.nld:
        fuzzy_method = FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE
    elif args.bm:
        if not BEIDER_MORSE_AVAILABLE:
            parser.error("Beider-Morse phonetic matching requires the 'abydos' library. Install it with: pip install abydos")
        fuzzy_method = FUZZY_METHOD_BEIDER_MORSE

    if args.threshold is not None:
        fuzzy_threshold = args.threshold
    elif fuzzy_method is not None:
        fuzzy_threshold = get_default_threshold(fuzzy_method)
    else:
        fuzzy_threshold = None

    block_letters = args.block

    match_data(jms_input_path=jms_input_path, zbl_dir=zbl_dir, output_path=output_path, verbose=verbose, fuzzy_method=fuzzy_method, fuzzy_threshold=fuzzy_threshold, block_letters=block_letters)

if __name__ == "__main__":
    main()
