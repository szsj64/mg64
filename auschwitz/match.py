# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import openpyxl
from tqdm import tqdm

try:
    from abydos.phonetic import BeiderMorse as _BeiderMorse
    _bm_encoder = _BeiderMorse()
    BEIDER_MORSE_AVAILABLE = True
except ImportError:
    BEIDER_MORSE_AVAILABLE = False

DEFAULT_AUSCHWITZ_PATH = "Auschwitz_Death_Certificates_1942-1943.xlsx"

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

def adjust_birth_place(place):
    place = place.lower().strip()
    place = place.replace("w", "v")
    place = place.replace("agram", "zagreb")
    place = place.replace("belgrade", "beograd")
    return place

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

def group_jms_data(data, use_birth_year=True, use_birth_place=False, prepare_names=False, use_initials_for_grouping=False, block_letters=1):
    jms_prepare = lambda x: x.lower().replace("*", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    def get_jms_key(x):
        name_value = names_preparation(x.get("name_and_surname", ""))
        if use_initials_for_grouping is True:
            name_value = get_sorted_initials(name_value, num_letters=block_letters)
        parts = [name_value]
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

def load_auschwitz_data(input_path, verbose=False):
    if verbose:
        print(f"Loading Auschwitz data from {input_path}...")
    wb = openpyxl.load_workbook(input_path, read_only=True)
    ws = wb.worksheets[0]
    data = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        surname = str(row[0]).strip() if row[0] else ""
        name = str(row[1]).strip() if row[1] else ""
        birth_date = str(row[2]).strip() if row[2] else ""
        death_date = str(row[3]).strip() if row[3] else ""
        birth_place = str(row[4]).strip() if row[4] else ""
        residence = str(row[5]).strip() if row[5] else ""
        religion = str(row[6]).strip() if row[6] else ""
        birth_year = birth_date[:4] if len(birth_date) >= 4 else ""
        death_year = death_date[:4] if len(death_date) >= 4 else ""
        name_and_surname = (name + " " + surname).strip()
        entry = {
            "surname": surname,
            "name": name,
            "name_and_surname": name_and_surname,
            "birth_date": birth_date,
            "death_date": death_date,
            "birth_place": birth_place,
            "residence": residence,
            "religion": religion,
            "birth_year": birth_year,
            "death_year": death_year,
            "row_idx": row_idx + 2,
        }
        data.append(entry)
    wb.close()
    if verbose:
        print(f"Loaded {len(data)} rows.")
    return data

def group_auschwitz_data(data, use_birth_year=True, use_birth_place=False, prepare_names=False, add_reversed_name_and_surname=True, use_initials_for_grouping=False, block_letters=1, verbose=False):
    aus_prepare = lambda x: x.lower().replace("-", "").strip() if x else ""
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    aus_groups = dict()
    iterator = tqdm(data, desc="Grouping Auschwitz data", unit="rows") if verbose else data
    for entry in iterator:
        name_and_surname = names_preparation(entry["name_and_surname"]) if prepare_names else entry["name_and_surname"]
        aus_key_parts = [name_and_surname]
        if use_initials_for_grouping is True:
            aus_key_parts[0] = get_sorted_initials(name_and_surname, num_letters=block_letters)
        if use_birth_year is True:
            aus_key_parts.append(entry["birth_year"])
        if use_birth_place is True:
            aus_key_parts.append(entry["birth_place"])
        aus_key = tuple(map(aus_prepare, aus_key_parts))
        if aus_key not in aus_groups:
            aus_groups[aus_key] = []
        aus_groups[aus_key].append(entry)
        if add_reversed_name_and_surname is True:
            reversed_name = (entry["surname"] + " " + entry["name"]).strip()
            reversed_name = names_preparation(reversed_name) if prepare_names else reversed_name
            reversed_key_parts = [reversed_name]
            if use_initials_for_grouping is True:
                reversed_key_parts[0] = get_sorted_initials(reversed_name, num_letters=block_letters)
            if use_birth_year is True:
                reversed_key_parts.append(entry["birth_year"])
            if use_birth_place is True:
                reversed_key_parts.append(entry["birth_place"])
            reversed_key = tuple(map(aus_prepare, reversed_key_parts))
            if reversed_key != aus_key:
                if reversed_key not in aus_groups:
                    aus_groups[reversed_key] = []
                aus_groups[reversed_key].append(entry)
    return aus_groups

def find_matches(jms_groups, aus_groups, use_birth_place_for_matching=True, use_birth_year_for_matching=True, max_allowed_birth_year_difference=None, look_for_birth_place_in_source=True, look_for_birth_year_in_source=False, allow_empty_jms_birth_place=True, allow_empty_jms_birth_year=True, allow_empty_jms_birth_place_and_year=False, allow_residence_as_birth_place=True, fuzzy_method=None, fuzzy_threshold=None, prepare_names=False, verbose=False):
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    common_keys = sorted(set(jms_groups.keys()).intersection(set(aus_groups.keys())))
    matches = []
    iterator = tqdm(common_keys, desc="Finding matches", unit="keys") if verbose else common_keys
    for k in iterator:
        for jms_person in jms_groups[k]:
            candidates = []
            for aus_entry in aus_groups[k]:
                birth_place = aus_entry["birth_place"]
                birth_year = aus_entry["birth_year"]
                death_year = aus_entry["death_year"]
                residence = aus_entry["residence"]
                # Fuzzy name check
                if fuzzy_method is not None:
                    jms_name = names_preparation(jms_person.get("name_and_surname", "")).lower().replace("*", "").replace("-", "")
                    aus_name = names_preparation(aus_entry["name_and_surname"]).lower().replace("-", "").strip()
                    name_score = compute_name_score(jms_name, aus_name, fuzzy_method)
                    # Also try reversed name (surname + name) to handle name swaps
                    aus_reversed = names_preparation((aus_entry["surname"] + " " + aus_entry["name"]).strip()).lower().replace("-", "").strip()
                    reversed_score = compute_name_score(jms_name, aus_reversed, fuzzy_method)
                    if fuzzy_method in HIGHER_IS_BETTER_METHODS:
                        name_score = max(name_score, reversed_score)
                    else:
                        name_score = min(name_score, reversed_score)
                    if not passes_threshold(name_score, fuzzy_threshold, fuzzy_method):
                        continue
                else:
                    name_score = None
                if allow_empty_jms_birth_place_and_year is False:
                    jms_bp = adjust_birth_place(get_jms_birth_place(jms_person))
                    jms_by = get_jms_birth_year(jms_person).replace("-", "").replace("*", "").strip()
                    if jms_bp == "" and jms_by == "":
                        continue
                if use_birth_place_for_matching is True:
                    jms_birth_place = adjust_birth_place(get_jms_birth_place(jms_person))
                    if not (allow_empty_jms_birth_place is True and jms_birth_place == ""):
                        aus_birth_place = adjust_birth_place(birth_place) if birth_place else ""
                        birth_place_matched = jms_birth_place == aus_birth_place
                        if not birth_place_matched and allow_residence_as_birth_place is True:
                            aus_residence = adjust_birth_place(residence) if residence else ""
                            birth_place_matched = jms_birth_place == aus_residence
                        if not birth_place_matched:
                            if look_for_birth_place_in_source is True and aus_birth_place:
                                jms_source = adjust_birth_place(jms_person.get("Source:", ""))
                                if aus_birth_place not in jms_source:
                                    if allow_residence_as_birth_place is True and aus_residence and aus_residence in jms_source:
                                        pass
                                    else:
                                        continue
                            else:
                                continue
                if use_birth_year_for_matching is True:
                    jms_birth_year = get_jms_birth_year(jms_person).replace("-", "").replace("*", "").strip()
                    if not (allow_empty_jms_birth_year is True and jms_birth_year == ""):
                        aus_birth_year = birth_year.strip() if birth_year else ""
                        birth_year_matched = False
                        if max_allowed_birth_year_difference is not None:
                            try:
                                if abs(int(jms_birth_year) - int(aus_birth_year)) <= max_allowed_birth_year_difference:
                                    birth_year_matched = True
                            except ValueError:
                                if jms_birth_year == aus_birth_year:
                                    birth_year_matched = True
                        else:
                            if jms_birth_year == aus_birth_year:
                                birth_year_matched = True
                        if not birth_year_matched:
                            if look_for_birth_year_in_source is True and aus_birth_year:
                                jms_source = jms_person.get("Source:", "")
                                if aus_birth_year not in jms_source:
                                    continue
                            else:
                                continue
                candidates.append((aus_entry, name_score))

            if candidates:
                if fuzzy_method is not None:
                    best_entry, best_score = select_best_candidate(candidates, fuzzy_method)
                    matches.append((jms_person, best_entry))
                else:
                    for aus_entry, _ in candidates:
                        matches.append((jms_person, aus_entry))

    return matches

def save_matches(matches, output_path=None, verbose=False):
    outfile = open(output_path, "w", encoding="utf8") if output_path else None
    try:
        for jms_person, aus_entry in matches:
            jms_name = jms_person.get("name_and_surname", "")
            jms_birth_year = get_jms_birth_year(jms_person)
            jms_birth_place = get_jms_birth_place(jms_person)
            jms_death_year = jms_person.get("Year of Death:", "")
            jms_camp = jms_person.get("Camp:", "")
            line1 = f"{jms_name} | {jms_birth_year} | {jms_birth_place} | {jms_death_year} | {jms_camp}"
            aus_name = aus_entry["name_and_surname"]
            aus_birth_year = aus_entry["birth_year"]
            aus_death_year = aus_entry["death_year"]
            aus_birth_place = aus_entry["birth_place"]
            aus_residence = aus_entry["residence"]
            line2 = f"\t{aus_name} | {aus_birth_year} | {aus_death_year} | {aus_birth_place} | {aus_residence}"
            print(line1)
            print(line2)
            if outfile:
                outfile.write(line1 + "\n")
                outfile.write(line2 + "\n")
    finally:
        if outfile:
            outfile.close()

def match_data(jms_input_path, auschwitz_path, output_path, verbose=False, fuzzy_method=None, fuzzy_threshold=None, block_letters=1):
    if verbose is True:
        print("Loading JMS data...")
    jms_data = load_jms_data(input_path=jms_input_path)

    if verbose is True:
        print("Grouping JMS data...")
    use_birth_year = False
    use_birth_place = False
    prepare_names = True
    use_initials = fuzzy_method is not None
    jms_groups = group_jms_data(data=jms_data, use_birth_year=use_birth_year, use_birth_place=use_birth_place, prepare_names=prepare_names, use_initials_for_grouping=use_initials, block_letters=block_letters)

    if verbose is True:
        print(f"Number of JMS groups: {len(jms_groups)}")

    if verbose is True:
        print("Loading Auschwitz data...")
    aus_data = load_auschwitz_data(input_path=auschwitz_path, verbose=verbose)

    if verbose is True:
        print(f"Number of Auschwitz rows loaded: {len(aus_data)}")

    if verbose is True:
        print("Grouping Auschwitz data...")
    aus_groups = group_auschwitz_data(data=aus_data, use_birth_year=use_birth_year, use_birth_place=use_birth_place, prepare_names=prepare_names, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)

    if verbose is True:
        print(f"Number of Auschwitz groups: {len(aus_groups)}")

    matches = find_matches(jms_groups=jms_groups, aus_groups=aus_groups, fuzzy_method=fuzzy_method, fuzzy_threshold=fuzzy_threshold, prepare_names=prepare_names, verbose=verbose)

    if verbose is True:
        print(f"Number of matches: {len(matches)}")

    matches.sort(key=lambda m: (m[0].get("name_and_surname", ""), m[0].get("Date of Birth:", ""), m[1]["name_and_surname"]))

    if verbose is True:
        print("Saving matches...")
    save_matches(matches=matches, output_path=output_path, verbose=verbose)


def main():
    parser = argparse.ArgumentParser(description="Match JMS and Auschwitz data")
    parser.add_argument("-j", "--jms", required=True, help="JMS input path.")
    parser.add_argument("-a", "--auschwitz", default=DEFAULT_AUSCHWITZ_PATH, help="Auschwitz XLSX path.")
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
    auschwitz_path = args.auschwitz
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

    match_data(jms_input_path=jms_input_path, auschwitz_path=auschwitz_path, output_path=output_path, verbose=verbose, fuzzy_method=fuzzy_method, fuzzy_threshold=fuzzy_threshold, block_letters=block_letters)

if __name__ == "__main__":
    main()
