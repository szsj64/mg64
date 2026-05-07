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
DEFAULT_MG1964_PATH = "1964/data/parsed/mg1964.txt"

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
        ("elia", "ilija"),
        ("eliash", "ilija"),
        ("elias", "ilija"),
        ("elieser", "eleazar"),
        ("eliezer", "eleazar"),
        ("elijas", ", ilija"),
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
        print(f"Loaded {len(data)} Auschwitz rows.")
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

def load_mg1964_data(input_path, verbose=False):
    if verbose:
        print(f"Loading MG1964 data from {input_path}...")
    mg_data = []
    with open(input_path, "r", encoding="utf8") as f:
        for line in f.readlines():
            name, surname, father_name, birth_year, place, municipality, nationality, death_year, death_place, fate, circumstances, id_number, file_name, page_number, column = line.strip("\r\n").split("\t")
            mg_data.append({
                "Name": name,
                "Surname": surname,
                "FatherName": father_name,
                "BirthYear": birth_year,
                "Place": place,
                "Municipality": municipality,
                "Nationality": nationality,
                "DeathYear": death_year,
                "DeathPlace": death_place,
                "Fate": fate,
                "Circumstances": circumstances,
                "IDNumber": id_number,
                "File": file_name,
                "Page": page_number,
                "Column": column
            })
    if verbose:
        print(f"Loaded {len(mg_data)} MG1964 rows.")
    return mg_data

def group_mg1964_data(data, use_birth_year=True, use_birth_place=False, prepare_names=False, use_initials_for_grouping=False, block_letters=1, verbose=False):
    mg_prepare = lambda x: x.lower().replace("9999", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    place_preparation = lambda x: "Zagreb" if x.lower().startswith("zagreb") else "Beograd" if x.lower().startswith("beograd") else x
    mg_groups = dict()
    iterator = tqdm(data, desc="Grouping MG1964 data", unit="rows") if verbose else data
    for person in iterator:
        name_and_surname = names_preparation(person["Name"] + " " + person["Surname"]) if prepare_names else person["Name"] + " " + person["Surname"]
        mg_key_parts = [name_and_surname]
        if use_initials_for_grouping is True:
            mg_key_parts[0] = get_sorted_initials(name_and_surname, num_letters=block_letters)
        if use_birth_year is True:
            mg_key_parts.append(person["BirthYear"])
        if use_birth_place is True:
            mg_key_parts.append(place_preparation(person["Place"]))
        mg_key = tuple(map(mg_prepare, mg_key_parts))
        if mg_key not in mg_groups:
            mg_groups[mg_key] = []
        mg_groups[mg_key].append(person)
    return mg_groups

def find_matches(aus_groups, mg_groups, use_birth_place_for_matching=True, use_birth_year_for_matching=True, max_allowed_birth_year_difference=None, allow_empty_aus_birth_place=True, allow_empty_mg_birth_place=True, allow_empty_aus_birth_year=True, allow_empty_mg_birth_year=True, allow_residence_as_birth_place=True, fuzzy_method=None, fuzzy_threshold=None, prepare_names=False, verbose=False):
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    common_keys = sorted(set(aus_groups.keys()).intersection(set(mg_groups.keys())))
    matches = []
    iterator = tqdm(common_keys, desc="Finding matches", unit="keys") if verbose else common_keys
    for k in iterator:
        for aus_entry in aus_groups[k]:
            candidates = []
            for mg_person in mg_groups[k]:
                aus_birth_place = aus_entry["birth_place"]
                aus_birth_year = aus_entry["birth_year"]
                aus_residence = aus_entry["residence"]
                mg_birth_place = mg_person["Place"]
                mg_birth_year = mg_person["BirthYear"].replace("9999", "")
                # Fuzzy name check
                if fuzzy_method is not None:
                    aus_name = names_preparation(aus_entry["name_and_surname"]).lower().replace("-", "").strip()
                    mg_name = names_preparation(mg_person["Name"] + " " + mg_person["Surname"]).lower().replace("-", "")
                    name_score = compute_name_score(aus_name, mg_name, fuzzy_method)
                    # Also try reversed Auschwitz name and reversed MG name to handle name swaps
                    aus_reversed = names_preparation((aus_entry["surname"] + " " + aus_entry["name"]).strip()).lower().replace("-", "").strip()
                    mg_reversed = names_preparation(mg_person["Surname"] + " " + mg_person["Name"]).lower().replace("-", "")
                    reversed_scores = [
                        compute_name_score(aus_reversed, mg_name, fuzzy_method),
                        compute_name_score(aus_name, mg_reversed, fuzzy_method),
                        compute_name_score(aus_reversed, mg_reversed, fuzzy_method),
                    ]
                    if fuzzy_method in HIGHER_IS_BETTER_METHODS:
                        name_score = max(name_score, *reversed_scores)
                    else:
                        name_score = min(name_score, *reversed_scores)
                    if not passes_threshold(name_score, fuzzy_threshold, fuzzy_method):
                        continue
                else:
                    name_score = None
                if use_birth_place_for_matching is True:
                    aus_bp = adjust_birth_place(aus_birth_place) if aus_birth_place else ""
                    mg_bp = adjust_birth_place(mg_birth_place) if mg_birth_place else ""
                    if allow_empty_aus_birth_place is True and aus_bp == "":
                        pass
                    elif allow_empty_mg_birth_place is True and mg_bp == "":
                        pass
                    else:
                        birth_place_matched = aus_bp == mg_bp
                        if not birth_place_matched and allow_residence_as_birth_place is True:
                            aus_res = adjust_birth_place(aus_residence) if aus_residence else ""
                            birth_place_matched = aus_res == mg_bp
                        if not birth_place_matched:
                            continue
                if use_birth_year_for_matching is True:
                    aus_by = aus_birth_year.strip() if aus_birth_year else ""
                    mg_by = mg_birth_year.strip() if mg_birth_year else ""
                    if allow_empty_aus_birth_year is True and aus_by == "":
                        pass
                    elif allow_empty_mg_birth_year is True and mg_by == "":
                        pass
                    else:
                        birth_year_matched = False
                        if max_allowed_birth_year_difference is not None:
                            try:
                                if abs(int(aus_by) - int(mg_by)) <= max_allowed_birth_year_difference:
                                    birth_year_matched = True
                            except ValueError:
                                if aus_by == mg_by:
                                    birth_year_matched = True
                        else:
                            if aus_by == mg_by:
                                birth_year_matched = True
                        if not birth_year_matched:
                            continue
                candidates.append((mg_person, name_score))

            if candidates:
                if fuzzy_method is not None:
                    best_entry, best_score = select_best_candidate(candidates, fuzzy_method)
                    matches.append((aus_entry, best_entry))
                else:
                    for mg_person, _ in candidates:
                        matches.append((aus_entry, mg_person))

    return matches

def save_matches(matches, output_path=None, verbose=False):
    outfile = open(output_path, "w", encoding="utf8") if output_path else None
    try:
        for aus_entry, mg_person in matches:
            aus_name = aus_entry["name_and_surname"]
            aus_birth_year = aus_entry["birth_year"]
            aus_death_year = aus_entry["death_year"]
            aus_birth_place = aus_entry["birth_place"]
            aus_residence = aus_entry["residence"]
            line1 = f"{aus_name} | {aus_birth_year} | {aus_death_year} | {aus_birth_place} | {aus_residence}"
            mg_name = mg_person["Name"] + " " + mg_person["Surname"]
            mg_father = mg_person["FatherName"]
            mg_birth_year = mg_person["BirthYear"]
            mg_birth_place = mg_person["Place"]
            mg_death_year = mg_person["DeathYear"]
            mg_death_place = mg_person["DeathPlace"]
            mg_circumstances = mg_person["Circumstances"]
            line2 = f"\t{mg_name} | {mg_father} | {mg_birth_year} | {mg_birth_place} | {mg_death_year} | {mg_death_place} | {mg_circumstances}"
            print(line1)
            print(line2)
            if outfile:
                outfile.write(line1 + "\n")
                outfile.write(line2 + "\n")
    finally:
        if outfile:
            outfile.close()

def match_data(auschwitz_path, mg1964_path, output_path=None, verbose=False, fuzzy_method=None, fuzzy_threshold=None, block_letters=1):
    if verbose is True:
        print("Loading Auschwitz data...")
    aus_data = load_auschwitz_data(input_path=auschwitz_path, verbose=verbose)

    if verbose is True:
        print("Loading MG1964 data...")
    mg_data = load_mg1964_data(input_path=mg1964_path, verbose=verbose)

    use_birth_year = False
    use_birth_place = False
    prepare_names = True
    use_initials = fuzzy_method is not None

    if verbose is True:
        print("Grouping Auschwitz data...")
    aus_groups = group_auschwitz_data(data=aus_data, use_birth_year=use_birth_year, use_birth_place=use_birth_place, prepare_names=prepare_names, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)

    if verbose is True:
        print(f"Number of Auschwitz groups: {len(aus_groups)}")

    if verbose is True:
        print("Grouping MG1964 data...")
    mg_groups = group_mg1964_data(data=mg_data, use_birth_year=use_birth_year, use_birth_place=use_birth_place, prepare_names=prepare_names, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)

    if verbose is True:
        print(f"Number of MG1964 groups: {len(mg_groups)}")

    matches = find_matches(aus_groups=aus_groups, mg_groups=mg_groups, fuzzy_method=fuzzy_method, fuzzy_threshold=fuzzy_threshold, prepare_names=prepare_names, verbose=verbose)

    if verbose is True:
        print(f"Number of matches: {len(matches)}")

    matches.sort(key=lambda m: (m[0]["name_and_surname"], m[0]["birth_year"], m[1]["Name"] + " " + m[1]["Surname"]))

    if verbose is True:
        print("Printing matches...")
    save_matches(matches=matches, output_path=output_path, verbose=verbose)


def main():
    parser = argparse.ArgumentParser(description="Match Auschwitz and MG1964 data")
    parser.add_argument("-a", "--auschwitz", default=DEFAULT_AUSCHWITZ_PATH, help="Auschwitz XLSX path.")
    parser.add_argument("-m", "--mg1964", default=DEFAULT_MG1964_PATH, help="MG1964 TSV path.")
    parser.add_argument("-o", "--output", default=None, help="Output file path.")
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

    auschwitz_path = args.auschwitz
    mg1964_path = args.mg1964
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

    match_data(auschwitz_path=auschwitz_path, mg1964_path=mg1964_path, output_path=output_path, verbose=verbose, fuzzy_method=fuzzy_method, fuzzy_threshold=fuzzy_threshold, block_letters=block_letters)

if __name__ == "__main__":
    main()
