# -*- coding: utf-8 -*-

import argparse
import json
import xlsxwriter
import math
import re
from tqdm import tqdm

try:
    from abydos.phonetic import BeiderMorse as _BeiderMorse
    _bm_encoder = _BeiderMorse()
    BEIDER_MORSE_AVAILABLE = True
except ImportError:
    BEIDER_MORSE_AVAILABLE = False

DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE = 0
DEFAULT_JWD_THRESHOLD = 0.85
DEFAULT_LD_THRESHOLD = 3
DEFAULT_DLD_THRESHOLD = 3
DEFAULT_NLD_THRESHOLD = 0.85
DEFAULT_BM_THRESHOLD = 0.5

DEFAULT_FS_UPPER_THRESHOLD = 8.0
DEFAULT_FS_LOWER_THRESHOLD = 2.0
DEFAULT_FS_LEVELS = 3
DEFAULT_FS_EM_ITERATIONS = 10

FUZZY_METHOD_JARO_WINKLER_DISTANCE = "jwd"
FUZZY_METHOD_LEVENSHTEIN_DISTANCE = "ld"
FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE = "dld"
FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE = "nld"
FUZZY_METHOD_BEIDER_MORSE = "bm"

HIGHER_IS_BETTER_METHODS = {FUZZY_METHOD_JARO_WINKLER_DISTANCE, FUZZY_METHOD_NORMALIZED_LEVENSHTEIN_DISTANCE, FUZZY_METHOD_BEIDER_MORSE}
LOWER_IS_BETTER_METHODS = {FUZZY_METHOD_LEVENSHTEIN_DISTANCE, FUZZY_METHOD_DAMERAU_LEVENSHTEIN_DISTANCE}

CAMP = "logor"

IN_CAMP = "u logoru"
JASENOVAC = "Jasenovac"
JAENOVAC = "Jaenovac"
UNKNOWN = "Nepoznato"
GRADISKA1 = "Stara Gradiška"
GRADISKA2 = "St. Gradiška"
GRADISKA3 = "St Gradiška"
GRADISKA4 = "Stara grediška"
GRADISKA5 = "Stara gardiška"
GRADISKA6 = "Stara gadiška"
GRADISKA7 = "St.gradiška"
UNKNOWN_CAMP1 = "Nepoznati logor"
UNKNOWN_CAMP2 = "Log. nepoznat"
UNKNOWN_CAMP3 = "Log.nepo."
UNKNOWN_CAMP4 = "Konc.logor"
JASENOVAC_CAMP = "Jasenovac-logor"
MLAKA = "Mlaka"
JABLANAC = "Jablanac"
KRAPJE = "Krapje"
BROCICE = "Bročice"
GRADINA = "Gradina"

COLUMN_WIDTH_OFFSET = 5

USE_SOURCES = True
SORT = True

JMS_MATCHING_WORKSHEET_NAME = " JasenovacVictimsList"
MG64_MATCHING_WORKSHEET_NAME = "MG1964"

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

def load_jms_data(input_path):
    with open(input_path, "r", encoding="utf8") as f:
        jms_data=json.load(f)
    return jms_data
        
def load_mg1964_data(input_path, sort=False):
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
    if sort is True:
        mg_data.sort(key=lambda x: (x["Surname"], x["Name"], x["FatherName"], x["BirthYear"], x["Place"], x["Municipality"], x["Nationality"], x["DeathYear"], x["DeathPlace"], x["Fate"], x["Circumstances"], x["IDNumber"], x["File"], x["Page"], x["Column"]))
    return mg_data

def get_jms_birth_year(person):
    return person.get("Date of Birth:", "").split("[")[0].rstrip()

def get_jms_birth_place(person):
    return person.get("Place of Birth:", "").split(",")[0].rstrip()

def get_jms_birth_municipality(person):
    return ",".join(person.get("Place of Birth:", "").split(",")[1:]).rstrip()

def group_jms_data(data, use_birth_year_for_grouping=True, use_birth_place_for_grouping=True, use_father_name_for_grouping=True, prepare_names=False, sort_name_parts=False, use_initials_for_grouping=False, block_letters=1, verbose=False):
    jms_prepare = lambda x: x.lower().replace("*", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    def get_jms_key(x):
        name_value = names_preparation(x.get("name_and_surname", ""))
        if use_initials_for_grouping is True:
            name_value = get_sorted_initials(name_value, num_letters=block_letters)
        elif sort_name_parts is True:
            name_value = " ".join(sorted(name_value.split()))
        parts = [name_value]
        if use_father_name_for_grouping is True:
            parts.append(names_preparation(x.get("Father Name:", "")))
        if use_birth_year_for_grouping is True:
            parts.append(get_jms_birth_year(x))
        if use_birth_place_for_grouping is True:
            parts.append(get_jms_birth_place(x))
        return tuple(map(jms_prepare, parts))

    jms_groups = dict()
    iterator = tqdm(data, desc="Grouping JMS data", unit="records") if verbose else data
    for person in iterator:
        k = get_jms_key(person)
        if k not in jms_groups:
            jms_groups[k] = []
        jms_groups[k].append(person)

    return jms_groups

def group_mg1964_data(data, use_birth_year_for_grouping=True, use_birth_place_for_grouping=True, use_father_name_for_grouping=True, prepare_names=False, sort_name_parts=False, use_initials_for_grouping=False, block_letters=1, verbose=False):
    mg_prepare = lambda x: x.lower().replace("9999", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    #place_preparation = lambda x: "Zagreb" if x.lower().startswith("zagreb") else x
    place_preparation = lambda x: "Zagreb" if x.lower().startswith("zagreb") else "Beograd" if x.lower().startswith("beograd") else x
    #place_preparation = lambda x: x if "-" not in x else x.split("-")[0].rstrip()
    def get_mg_key(x):
        name_value = names_preparation(x["Name"] + " " + x["Surname"])
        if use_initials_for_grouping is True:
            name_value = get_sorted_initials(name_value, num_letters=block_letters)
        elif sort_name_parts is True:
            name_value = " ".join(sorted(name_value.split()))
        parts = [name_value]
        if use_father_name_for_grouping is True:
            parts.append(names_preparation(x["FatherName"]))
        if use_birth_year_for_grouping is True:
            parts.append(x["BirthYear"])
        if use_birth_place_for_grouping is True:
            parts.append(place_preparation(x["Place"]))
        return tuple(map(mg_prepare, parts))

    mg_groups = dict()
    iterator = tqdm(data, desc="Grouping MG1964 data", unit="records") if verbose else data
    for person in iterator:
        k = get_mg_key(person)
        if k not in mg_groups:
            mg_groups[k] = []
        mg_groups[k].append(person)

    return mg_groups

def filter_mg1964_data(data):
    filtered_data = []

    filter_keywords = [IN_CAMP, JASENOVAC, JAENOVAC, UNKNOWN, GRADISKA1, GRADISKA2, GRADISKA3, GRADISKA4, GRADISKA5, GRADISKA6, GRADISKA7, UNKNOWN_CAMP1, UNKNOWN_CAMP2, UNKNOWN_CAMP3, UNKNOWN_CAMP4, JASENOVAC_CAMP, JASENOVAC, MLAKA, JABLANAC, KRAPJE, BROCICE, GRADINA]
    for person in data:
        death_place = person["DeathPlace"].lower()
        #circumstances = person["Circumstances"].lower()
        #if IN_CAMP.lower() in circumstances or CAMP.lower() in circumstances:
        if True:
            skip = False
            for keyword in filter_keywords:
                if keyword.lower() in death_place:
                    skip = True
            if skip is True:
                continue
        filtered_data.append(person)
 
    return filtered_data

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

def normalize_fuzzy_score(score, s1, s2, method):
    """Normalize a fuzzy score to [0, 1] range where higher means more similar."""
    if method in HIGHER_IS_BETTER_METHODS:
        return score
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return max(0.0, 1.0 - score / max_len)

def discretize_score(normalized_score, num_levels):
    """Convert a [0, 1] similarity score to a discrete level from 0 to num_levels - 1."""
    level = int(normalized_score * num_levels)
    return min(level, num_levels - 1)

def compute_comparison_vector(jms_person, mg_person, fuzzy_method, fuzzy_father, check_father_names, check_birth_years, check_birth_places, fs_levels, maximum_direct_birth_year_difference, names_preparation):
    """Compute a Fellegi-Sunter comparison vector for a pair of records.

    Returns a list of (field_name, level, num_levels) tuples.
    Fields with missing/empty data are excluded from the vector.
    """
    vector = []

    jms_name = names_preparation(jms_person.get("name_and_surname", "")).lower().replace("*", "").replace("-", "")
    mg_name = names_preparation(mg_person["Name"] + " " + mg_person["Surname"]).lower().replace("9999", "").replace("-", "")
    if fuzzy_method is not None:
        score = compute_name_score(jms_name, mg_name, fuzzy_method)
        normalized = normalize_fuzzy_score(score, jms_name, mg_name, fuzzy_method)
        level = discretize_score(normalized, fs_levels)
        vector.append(("name", level, fs_levels))
    else:
        level = 1 if jms_name == mg_name else 0
        vector.append(("name", level, 2))

    if check_father_names:
        jms_father = names_preparation(jms_person.get("Father Name:", "")).lower().replace("*", "").replace("-", "")
        mg_father = names_preparation(mg_person["FatherName"]).lower().replace("9999", "").replace("-", "")
        if jms_father != "" and mg_father != "":
            if fuzzy_father and fuzzy_method is not None:
                score = compute_name_score(jms_father, mg_father, fuzzy_method)
                normalized = normalize_fuzzy_score(score, jms_father, mg_father, fuzzy_method)
                level = discretize_score(normalized, fs_levels)
                vector.append(("father", level, fs_levels))
            else:
                level = 1 if jms_father == mg_father else 0
                vector.append(("father", level, 2))

    if check_birth_years:
        jms_birth_year = int("0" + get_jms_birth_year(jms_person).replace("*", "").replace("-", ""))
        mg_birth_year = int("0" + mg_person["BirthYear"].replace("9999", ""))
        if jms_birth_year > 0 and mg_birth_year > 0:
            if jms_birth_year == mg_birth_year:
                level = 1
            elif maximum_direct_birth_year_difference is not None and abs(jms_birth_year - mg_birth_year) <= maximum_direct_birth_year_difference:
                level = 1
            else:
                level = 0
            vector.append(("year", level, 2))

    if check_birth_places:
        place_preparation = lambda x: "zagreb" if x.lower().startswith("zagreb") else "beograd" if x.lower().startswith("beograd") else x.lower().strip()
        jms_birth_place = place_preparation(get_jms_birth_place(jms_person)).strip()
        mg_birth_place = place_preparation(mg_person["Place"]).strip()
        if jms_birth_place not in ("", "-", "*") and mg_birth_place != "":
            level = 1 if jms_birth_place == mg_birth_place else 0
            vector.append(("place", level, 2))

    return vector

def em_estimate_mu(comparison_vectors, max_iterations=DEFAULT_FS_EM_ITERATIONS):
    """Estimate m and u probabilities using the EM algorithm.

    Returns:
        m_probs: dict mapping (field_name, level) to P(level | match)
        u_probs: dict mapping (field_name, level) to P(level | non-match)
    """
    if not comparison_vectors:
        return {}, {}

    field_levels = {}
    for vector in comparison_vectors:
        for field_name, level, num_levels in vector:
            field_levels[field_name] = num_levels

    m_probs = {}
    u_probs = {}
    for field_name, num_levels in field_levels.items():
        for level in range(num_levels):
            if level == num_levels - 1:
                m_probs[(field_name, level)] = 0.9
                u_probs[(field_name, level)] = 0.1
            else:
                m_probs[(field_name, level)] = 0.1 / max(1, num_levels - 1)
                u_probs[(field_name, level)] = 0.9 / max(1, num_levels - 1)

    p_match = 0.1
    n = len(comparison_vectors)

    for _ in range(max_iterations):
        match_weights = []
        for vector in comparison_vectors:
            log_m = 0.0
            log_u = 0.0
            for field_name, level, num_levels in vector:
                log_m += math.log(max(m_probs.get((field_name, level), 1e-10), 1e-10))
                log_u += math.log(max(u_probs.get((field_name, level), 1e-10), 1e-10))
            log_pm = log_m + math.log(max(p_match, 1e-10))
            log_pu = log_u + math.log(max(1 - p_match, 1e-10))
            max_log = max(log_pm, log_pu)
            w = math.exp(log_pm - max_log) / (math.exp(log_pm - max_log) + math.exp(log_pu - max_log))
            match_weights.append(w)

        sum_w = sum(match_weights)
        p_match = sum_w / n

        m_counts = {}
        u_counts = {}
        m_totals = {}
        u_totals = {}
        for vi, vector in enumerate(comparison_vectors):
            w = match_weights[vi]
            for field_name, level, num_levels in vector:
                key = (field_name, level)
                m_counts[key] = m_counts.get(key, 0) + w
                u_counts[key] = u_counts.get(key, 0) + (1 - w)
                m_totals[field_name] = m_totals.get(field_name, 0) + w
                u_totals[field_name] = u_totals.get(field_name, 0) + (1 - w)

        new_m = {}
        new_u = {}
        for field_name, num_levels in field_levels.items():
            for level in range(num_levels):
                key = (field_name, level)
                m_total = m_totals.get(field_name, 1e-10)
                u_total = u_totals.get(field_name, 1e-10)
                new_m[key] = (m_counts.get(key, 0) + 1e-6) / (m_total + num_levels * 1e-6)
                new_u[key] = (u_counts.get(key, 0) + 1e-6) / (u_total + num_levels * 1e-6)

        m_probs = new_m
        u_probs = new_u

    return m_probs, u_probs

def load_estimation(path):
    """Load pre-estimated m/u probabilities from a file.

    Expected format (one entry per line):
      field_name level L/N: m=M_VAL, u=U_VAL, weight=W_VAL
    """
    m_probs = {}
    u_probs = {}
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            m = re.match(r'(\w+)\s+level\s+(\d+)/(\d+):\s+m=([\d.]+),\s+u=([\d.]+)', line)
            if m:
                field_name = m.group(1)
                level = int(m.group(2))
                m_val = float(m.group(4))
                u_val = float(m.group(5))
                m_probs[(field_name, level)] = m_val
                u_probs[(field_name, level)] = u_val
    return m_probs, u_probs

def compute_fs_score(vector, m_probs, u_probs):
    """Compute the Fellegi-Sunter composite score (sum of log2 likelihood ratios)."""
    score = 0.0
    for field_name, level, num_levels in vector:
        m_val = max(m_probs.get((field_name, level), 1e-10), 1e-10)
        u_val = max(u_probs.get((field_name, level), 1e-10), 1e-10)
        score += math.log2(m_val / u_val)
    return score

def check_matches_fellegi_sunter(jms_groups, mg_groups, common_keys, check_father_names=False, check_birth_years=False, check_birth_places=False, fuzzy_method=None, fuzzy_father=False, prepare_names=False, maximum_direct_birth_year_difference=None, fs_upper=DEFAULT_FS_UPPER_THRESHOLD, fs_lower=DEFAULT_FS_LOWER_THRESHOLD, fs_levels=DEFAULT_FS_LEVELS, fs_em_iterations=DEFAULT_FS_EM_ITERATIONS, match_all=False, verbose=False, estimation_path=None):
    """Match records using the Fellegi-Sunter probabilistic model.

    Returns:
        matches: list of (jms_person, mg_person, False, False, False) tuples
        review: list of (jms_person, mg_person, score) tuples for pairs in the review zone
    """
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    keys_iterator = tqdm(common_keys, desc="Computing comparison vectors", unit="keys") if verbose else common_keys

    all_candidates = []
    for k in keys_iterator:
        for jms_person in jms_groups[k]:
            for mg_person in mg_groups[k]:
                vector = compute_comparison_vector(
                    jms_person, mg_person,
                    fuzzy_method=fuzzy_method,
                    fuzzy_father=fuzzy_father,
                    check_father_names=check_father_names,
                    check_birth_years=check_birth_years,
                    check_birth_places=check_birth_places,
                    fs_levels=fs_levels,
                    maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
                    names_preparation=names_preparation
                )
                all_candidates.append((jms_person, mg_person, vector))

    if not all_candidates:
        return [], []

    vectors = [v for _, _, v in all_candidates]
    if estimation_path is not None:
        if verbose:
            print(f"Loading pre-estimated m/u probabilities from {estimation_path}...")
        m_probs, u_probs = load_estimation(estimation_path)
    else:
        if verbose:
            print(f"Running EM on {len(vectors)} candidate pairs...")
        m_probs, u_probs = em_estimate_mu(vectors, max_iterations=fs_em_iterations)

    if verbose:
        field_levels = {}
        for vector in vectors:
            for field_name, level, num_levels in vector:
                field_levels[field_name] = num_levels
        print("Estimated m/u probabilities:" if estimation_path is None else "Loaded m/u probabilities:")
        for field_name in sorted(field_levels.keys()):
            num_levels = field_levels[field_name]
            for level in range(num_levels):
                m_val = m_probs.get((field_name, level), 0)
                u_val = u_probs.get((field_name, level), 0)
                weight = math.log2(max(m_val, 1e-10) / max(u_val, 1e-10))
                print(f"  {field_name} level {level}/{num_levels-1}: m={m_val:.4f}, u={u_val:.4f}, weight={weight:+.2f}")

    matches = []
    review = []

    jms_candidates = {}
    candidates_iterator = tqdm(all_candidates, desc="Scoring candidate pairs", unit="pairs") if verbose else all_candidates
    for jms_person, mg_person, vector in candidates_iterator:
        score = compute_fs_score(vector, m_probs, u_probs)
        jms_id = id(jms_person)
        if jms_id not in jms_candidates:
            jms_candidates[jms_id] = []
        jms_candidates[jms_id].append((jms_person, mg_person, score))

    for jms_id, candidates in jms_candidates.items():
        above_upper = [(jms, mg, s) for jms, mg, s in candidates if s >= fs_upper]
        in_review = [(jms, mg, s) for jms, mg, s in candidates if fs_lower <= s < fs_upper]

        if above_upper:
            if match_all:
                for jms, mg, s in above_upper:
                    matches.append((jms, mg, False, False, False, s))
            else:
                best = max(above_upper, key=lambda x: x[2])
                matches.append((best[0], best[1], False, False, False, best[2]))

        review.extend(in_review)

    return matches, review

def get_sorted_initials(name_value, num_letters=1):
    initials = sorted([part[:num_letters] for part in name_value.split() if part])
    return "".join(initials)

def check_matches(jms_groups, mg_groups, common_keys, check_birth_years=True, allow_for_alternative_birth_year=False, maximum_direct_birth_year_difference=None, check_birth_places=True, allow_for_alternative_birth_place=False, check_father_names=False, allow_for_alternative_father_name=False, allow_empty_father_name=False, allow_empty_birth_year=False, allow_empty_birth_place=False, prepare_names=False, fuzzy_method=None, fuzzy_threshold=None, fuzzy_father=False, match_all=False, verbose=False):
    matches = []
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    keys_iterator = tqdm(common_keys, desc="Verifying matches", unit="keys") if verbose else common_keys
    for k in keys_iterator:
        for jms_person in jms_groups[k]:
            candidates = []
            for mg_person in mg_groups[k]:
                # Fuzzy name check
                if fuzzy_method is not None:
                    jms_name = names_preparation(jms_person.get("name_and_surname", "")).lower().replace("*", "").replace("-", "")
                    mg_name = names_preparation(mg_person["Name"] + " " + mg_person["Surname"]).lower().replace("9999", "").replace("-", "")
                    name_score = compute_name_score(jms_name, mg_name, fuzzy_method)
                    if not passes_threshold(name_score, fuzzy_threshold, fuzzy_method):
                        continue
                else:
                    name_score = None

                year_ok = True
                place_ok = True
                father_ok = True

                if check_father_names is True:
                    jms_father = names_preparation(jms_person.get("Father Name:", "")).lower().replace("*", "").replace("-", "")
                    mg_father = names_preparation(mg_person["FatherName"]).lower().replace("9999", "").replace("-", "")
                    if jms_father == mg_father:
                        pass
                    elif allow_empty_father_name is True and jms_father == "":
                        pass
                    elif allow_for_alternative_father_name is True and len(mg_father) > 0 and mg_father in jms_person.get("Source:", "").lower():
                        pass
                    elif fuzzy_father and fuzzy_method is not None and jms_father != "" and mg_father != "" and passes_threshold(compute_name_score(jms_father, mg_father, fuzzy_method), fuzzy_threshold, fuzzy_method):
                        pass
                    else:
                        father_ok = False

                if check_birth_years is True:
                    jms_birth_year = int("0" + get_jms_birth_year(jms_person).replace("*", "").replace("-", ""))
                    mg_birth_year = int("0" + mg_person["BirthYear"].replace("9999", ""))
                    if allow_empty_birth_year is True and jms_birth_year == 0:
                        pass
                    elif jms_birth_year == mg_birth_year:
                        pass
                    elif allow_for_alternative_birth_year is True and mg_birth_year > 0 and str(mg_birth_year) in jms_person.get("Source:", ""):
                        pass
                    elif maximum_direct_birth_year_difference is not None and abs(jms_birth_year - mg_birth_year) <= maximum_direct_birth_year_difference:
                        pass
                    elif allow_for_alternative_birth_year is True and maximum_direct_birth_year_difference is not None and maximum_direct_birth_year_difference > 0 and mg_birth_year > 0 and any(str(mg_birth_year + delta) in jms_person.get("Source:", "") for delta in range(-maximum_direct_birth_year_difference, maximum_direct_birth_year_difference + 1)):
                        pass
                    else:
                        year_ok = False

                if check_birth_places is True:
                    place_preparation = lambda x: "zagreb" if x.lower().startswith("zagreb") else "beograd" if x.lower().startswith("beograd") else x.lower().strip()
                    jms_birth_place = place_preparation(get_jms_birth_place(jms_person)).strip()
                    mg_birth_place = place_preparation(mg_person["Place"]).strip()
                    mg_birth_place_for_source = mg_birth_place  # normalized for source lookup
                    if allow_empty_birth_place is True and get_jms_birth_place(jms_person).strip() in ("", "-", "*"):
                        pass
                    elif jms_birth_place == mg_birth_place:
                        pass
                    elif allow_for_alternative_birth_place is True and len(mg_birth_place_for_source) > 0 and mg_birth_place_for_source in jms_person.get("Source:", "").lower():
                        pass
                    else:
                        place_ok = False

                if year_ok and place_ok and father_ok:
                    father_name_in_sources = False
                    birth_year_in_sources = False
                    birth_place_in_sources = False
                    if check_father_names is True and jms_father != mg_father and (allow_for_alternative_father_name is True and len(mg_father) > 0 and mg_father in jms_person.get("Source:", "").lower()):
                        father_name_in_sources = True
                    if check_birth_years is True and jms_birth_year != mg_birth_year and ((allow_for_alternative_birth_year is True and mg_birth_year > 0 and str(mg_birth_year) in jms_person.get("Source:", "")) or (allow_for_alternative_birth_year is True and maximum_direct_birth_year_difference is not None and maximum_direct_birth_year_difference > 0 and mg_birth_year > 0 and any(str(mg_birth_year + delta) in jms_person.get("Source:", "") for delta in range(-maximum_direct_birth_year_difference, maximum_direct_birth_year_difference + 1)))):
                        birth_year_in_sources = True
                    if check_birth_places is True and jms_birth_place != mg_birth_place and (allow_for_alternative_birth_place is True and len(mg_birth_place_for_source) > 0 and mg_birth_place_for_source in jms_person.get("Source:", "").lower()):
                        birth_place_in_sources = True
                    candidates.append((mg_person, name_score, father_name_in_sources, birth_year_in_sources, birth_place_in_sources))

            if candidates:
                if match_all is True:
                    for mg_person, score, f_src, y_src, p_src in candidates:
                        matches.append((jms_person, mg_person, f_src, y_src, p_src, None))
                else:
                    best = select_best_candidate(candidates, fuzzy_method)
                    mg_person, score, f_src, y_src, p_src = best
                    matches.append((jms_person, mg_person, f_src, y_src, p_src, None))

    return matches

def find_matches(jms_data, mg_data, verbose=False, maximum_direct_birth_year_difference=DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE, use_father_name=False, use_birth_year=False, use_birth_place=False, check_father_names=False, check_birth_years=False, check_birth_places=False, prepare_names=False, sort_name_parts=False, allow_for_alternative_father_name=False, allow_for_alternative_birth_year=False, allow_for_alternative_birth_place=False, allow_empty_father_name=False, allow_empty_birth_place=False, allow_empty_birth_year=False, fuzzy_method=None, fuzzy_threshold=None, fuzzy_father=False, fs_mode=False, fs_upper=DEFAULT_FS_UPPER_THRESHOLD, fs_lower=DEFAULT_FS_LOWER_THRESHOLD, fs_levels=DEFAULT_FS_LEVELS, fs_em_iterations=DEFAULT_FS_EM_ITERATIONS, match_all=False, block_letters=1, estimation_path=None):


    use_initials = fuzzy_method is not None
    jms_groups = group_jms_data(data=jms_data, use_birth_year_for_grouping=use_birth_year, use_birth_place_for_grouping=use_birth_place, use_father_name_for_grouping=use_father_name, prepare_names=prepare_names, sort_name_parts=sort_name_parts, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)

    mg_groups = group_mg1964_data(data=mg_data, use_birth_year_for_grouping=use_birth_year, use_birth_place_for_grouping=use_birth_place, use_father_name_for_grouping=use_father_name, prepare_names=prepare_names, sort_name_parts=sort_name_parts, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)

    common_keys = list(set(jms_groups.keys()).intersection(set(mg_groups.keys())))

    review = []

    if fs_mode:
        matches, review_batch = check_matches_fellegi_sunter(
            jms_groups=jms_groups,
            mg_groups=mg_groups,
            common_keys=common_keys,
            check_father_names=check_father_names,
            check_birth_years=check_birth_years,
            check_birth_places=check_birth_places,
            fuzzy_method=fuzzy_method,
            fuzzy_father=fuzzy_father,
            prepare_names=prepare_names,
            maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
            fs_upper=fs_upper,
            fs_lower=fs_lower,
            fs_levels=fs_levels,
            fs_em_iterations=fs_em_iterations,
            match_all=match_all,
            verbose=verbose,
            estimation_path=estimation_path
        )
        review.extend(review_batch)
    else:
        matches = check_matches(
            jms_groups=jms_groups,
            mg_groups=mg_groups,
            common_keys=common_keys,
            check_father_names=check_father_names,
            allow_for_alternative_father_name=allow_for_alternative_father_name,
            allow_empty_father_name=allow_empty_father_name,
            check_birth_years=check_birth_years,
            allow_for_alternative_birth_year=allow_for_alternative_birth_year,
            maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
            check_birth_places=check_birth_places,
            allow_for_alternative_birth_place=allow_for_alternative_birth_place,
            allow_empty_birth_year=allow_empty_birth_year,
            allow_empty_birth_place=allow_empty_birth_place,
            prepare_names=prepare_names,
            fuzzy_method=fuzzy_method,
            fuzzy_threshold=fuzzy_threshold,
            fuzzy_father=fuzzy_father,
            match_all=match_all,
            verbose=verbose
        )

    if (allow_empty_father_name and use_father_name) or (allow_empty_birth_year and use_birth_year) or (allow_empty_birth_place and use_birth_place):
        matched_jms_ids = set(id(j) for j, _, _, _, _, _ in matches)

        def is_value_empty(value):
            return value.strip().replace("*", "").replace("-", "") == ""

        relaxed_jms = [p for p in jms_data if id(p) not in matched_jms_ids and (
            (allow_empty_father_name and use_father_name and is_value_empty(p.get("Father Name:", ""))) or
            (allow_empty_birth_year and use_birth_year and is_value_empty(get_jms_birth_year(p))) or
            (allow_empty_birth_place and use_birth_place and is_value_empty(get_jms_birth_place(p)))
        )]

        if len(relaxed_jms) > 0:

            use_father_name_relaxed = use_father_name and not allow_empty_father_name
            use_birth_year_relaxed = use_birth_year and not allow_empty_birth_year
            use_birth_place_relaxed = use_birth_place and not allow_empty_birth_place

            if verbose is True:
                print(f"Relaxed matching for {len(relaxed_jms)} entries with empty fields...")

            jms_groups_r = group_jms_data(data=relaxed_jms, use_birth_year_for_grouping=use_birth_year_relaxed, use_birth_place_for_grouping=use_birth_place_relaxed, use_father_name_for_grouping=use_father_name_relaxed, prepare_names=prepare_names, sort_name_parts=sort_name_parts, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)
            mg_groups_r = group_mg1964_data(data=mg_data, use_birth_year_for_grouping=use_birth_year_relaxed, use_birth_place_for_grouping=use_birth_place_relaxed, use_father_name_for_grouping=use_father_name_relaxed, prepare_names=prepare_names, sort_name_parts=sort_name_parts, use_initials_for_grouping=use_initials, block_letters=block_letters, verbose=verbose)

            common_keys_r = list(set(jms_groups_r.keys()).intersection(set(mg_groups_r.keys())))

            if fs_mode:
                matches_r, review_r = check_matches_fellegi_sunter(
                    jms_groups=jms_groups_r,
                    mg_groups=mg_groups_r,
                    common_keys=common_keys_r,
                    check_father_names=(check_father_names or (use_father_name and allow_empty_father_name)),
                    check_birth_years=check_birth_years,
                    check_birth_places=check_birth_places,
                    fuzzy_method=fuzzy_method,
                    fuzzy_father=fuzzy_father,
                    prepare_names=prepare_names,
                    maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
                    fs_upper=fs_upper,
                    fs_lower=fs_lower,
                    fs_levels=fs_levels,
                    fs_em_iterations=fs_em_iterations,
                    match_all=match_all,
                    verbose=verbose,
                    estimation_path=estimation_path
                )
                review.extend(review_r)
            else:
                matches_r = check_matches(
                    jms_groups=jms_groups_r,
                    mg_groups=mg_groups_r,
                    common_keys=common_keys_r,
                    check_father_names=(check_father_names or (use_father_name and allow_empty_father_name)),
                    allow_for_alternative_father_name=allow_for_alternative_father_name,
                    allow_empty_father_name=allow_empty_father_name,
                    check_birth_years=check_birth_years,
                    allow_for_alternative_birth_year=allow_for_alternative_birth_year,
                    maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
                    check_birth_places=check_birth_places,
                    allow_for_alternative_birth_place=allow_for_alternative_birth_place,
                    allow_empty_birth_year=allow_empty_birth_year,
                    allow_empty_birth_place=allow_empty_birth_place,
                    prepare_names=prepare_names,
                    fuzzy_method=fuzzy_method,
                    fuzzy_threshold=fuzzy_threshold,
                    fuzzy_father=fuzzy_father,
                    match_all=match_all,
                    verbose=verbose
                )

            matches.extend(matches_r)

    return matches, review

def write_match(jms_person, mg_person, worksheet, current_row, column_max_lengths, link=False, birth_year_in_sources=False, fs_score=None, include_score=False):
    jms_columns = ["NameAndSurname", "FatherName", "BirthYear", "BirthPlace", "DeathYear"]
    mg_columns = [("Name", "Surname"), "FatherName", "BirthYear", "Place", "DeathYear", "Circumstances", "DeathPlace"]

    jms_person_data = {
        "NameAndSurname": jms_person.get("name_and_surname", ""),
        "Sex": jms_person.get("Sex:", ""),
        "FatherName": jms_person.get("Father Name:", ""),
        "Notes": jms_person.get("Notes:", ""),
        "BirthYear": jms_person.get("Date of Birth:", ""),
        "BirthPlace": get_jms_birth_place(jms_person),
        "BirthMunicipality": get_jms_birth_municipality(jms_person),
        "NationalityEthnicity": jms_person.get("Nationality/Ethnicity:", ""),
        "Killed": jms_person.get("Killed:", ""),
        "DeathYear": jms_person.get("Year of Death:", ""),
        "DeathPlace": jms_person.get("Death Place:", ""),
        "Camp": jms_person.get("Camp:", ""),
        "Source": jms_person.get("Source:", ""),
        "Row": jms_person.get("Row", None)
    }

    mg_person_data = mg_person

    if link is True:
        mg_row = mg_person_data["Row"]
        jms_row = jms_person_data["Row"]

    jms_column_to_column_relationship = {
        0: "A", # name and surname to name
        1: "B", # father name to father name
        2: "E", # birth year to birth year
        3: "C", # place to birth place
        4: "F", # death year to death year
    }
    jms_column_to_column_relationship_birth_year_in_sources = {
        0: "A", # name and surname to name
        1: "B", # father name to father name
        2: "M", # birth year to birth year
        3: "C", # place to birth place
        4: "F", # death year to death year
    }

    for i, jms_column in enumerate(jms_columns):
        if isinstance(jms_column, str):
            value = jms_person_data.get(jms_column, "")
        else:
            value = " ".join(jms_person_data.get(individual_jms_column, "") for individual_jms_column in jms_column)
        if link is True:
            relationship = jms_column_to_column_relationship_birth_year_in_sources if birth_year_in_sources is True else jms_column_to_column_relationship
            worksheet.write_url(current_row, i, f"internal:'{JMS_MATCHING_WORKSHEET_NAME}'!{relationship[i]}{jms_row}", string=value)
        else:
            worksheet.write(current_row, i, value)
        column_max_lengths[i] = max(column_max_lengths[i], len(value))
    
    current_row += 1

    mg_column_to_column_relationship = {
        0: "A", # name and surname to name
        1: "C", # father name to father name
        2: "D", # birth year to birth year
        3: "E", # place to place
        4: "H", # death year to death year
        5: "K", # circumstances to circumstances
        6: "I", # death place to death place
    }

    for i, mg_column in enumerate(mg_columns):
        if isinstance(mg_column, str):
            value = mg_person_data.get(mg_column, "")
        else:
            value = " ".join(mg_person_data.get(individual_mg_column, "") for individual_mg_column in mg_column)
        if link is True:
            worksheet.write_url(current_row, i, f"internal:'{MG64_MATCHING_WORKSHEET_NAME}'!{mg_column_to_column_relationship[i]}{mg_row}", string=value)
        else:
            worksheet.write(current_row, i, value)
        column_max_lengths[i] = max(column_max_lengths[i], len(value))

    if include_score and fs_score is not None:
        score_col = len(mg_columns)
        score_str = f"{fs_score:.2f}"
        worksheet.write(current_row - 1, score_col, score_str)
        column_max_lengths[score_col] = max(column_max_lengths[score_col], len(score_str))

    current_row += 1
    current_row += 1

    return current_row

def create_jms_worksheet(data, worksheet_name, workbook, add_source_info=False, verbose=False):
    
    persons = []
    for p in data:
        person_data = {
            "NameAndSurname": p.get("name_and_surname", ""),
            "Sex": p.get("Sex:", ""),
            "FatherName": p.get("Father Name:", ""),
            "Notes": p.get("Notes:", ""),
            "BirthYear": p.get("Date of Birth:", ""),
            "BirthPlace": p.get("Place of Birth:", "").split(",")[0].rstrip(),
            "BirthMunicipality": "" if "," not in p.get("Place of Birth:", "") else p.get("Place of Birth:", "").split(",")[1].lstrip(),
            "NationalityEthnicity": p.get("Nationality/Ethnicity:", ""),
            "Killed": p.get("Killed:", ""),
            "DeathYear": p.get("Year of Death:", ""),
            "DeathPlace": p.get("Death Place:", ""),
            "Camp": p.get("Camp:", ""),
            "Source": p.get("Source:", ""),
            "URL": p.get("URL", None)
        }
        persons.append(person_data)
        
    column_names = ["NameAndSurname", "FatherName", "BirthPlace", "BirthMunicipality", "BirthYear", "DeathYear", "Sex", "NationalityEthnicity", "DeathPlace", "Killed", "Camp", "Notes", "Source"]
    if add_source_info is True:
        column_names.append("URL")
              
    worksheet = workbook.add_worksheet(worksheet_name)
    bold = workbook.add_format({"bold": True})
    for i, column_name in enumerate(column_names):
        worksheet.write(0, i, column_name, bold)
    
    worksheet.freeze_panes(1, 0)
    
    taker = list(enumerate(persons))
    if verbose is True:
        taker = tqdm(taker, desc="Writing persons data", unit="persons")
    column_max_lengths = {column_name: 0 for column_name in column_names}
    for i, person in taker:
        for j, column_name in enumerate(column_names):
            value = person.get(column_name, "")
            worksheet.write(i + 1, j, value)
            column_max_lengths[column_name] = max(column_max_lengths[column_name], len(value))
    
    for i, column_name in enumerate(column_names):
        worksheet.set_column(i, i, column_max_lengths[column_name] + COLUMN_WIDTH_OFFSET)

def create_mg64_worksheet(data, worksheet_name, workbook, add_source_info=False, verbose=False):
        
    column_names = ["Name", "Surname", "FatherName", "BirthYear", "Place", "Municipality", "Nationality", "DeathYear", "DeathPlace", "Fate", "Circumstances", "IDNumber"]
    if add_source_info is True:
        column_names.extend(["File", "Page", "Column"])
              
    worksheet = workbook.add_worksheet(worksheet_name)
    bold = workbook.add_format({"bold": True})
    for i, column_name in enumerate(column_names):
        worksheet.write(0, i, column_name, bold)
    
    worksheet.freeze_panes(1, 0)
    
    taker = list(enumerate(data))
    if verbose is True:
        taker = tqdm(taker, desc="Writing persons data", unit="persons")
    column_max_lengths = {column_name: 0 for column_name in column_names}
    for i, person in taker:
        for j, column_name in enumerate(column_names):
            value = person.get(column_name, "")
            worksheet.write(i + 1, j, value)
            column_max_lengths[column_name] = max(column_max_lengths[column_name], len(value))
    
    for i, column_name in enumerate(column_names):
        worksheet.set_column(i, i, column_max_lengths[column_name] + COLUMN_WIDTH_OFFSET)

def save_matches(matched, output_path, group_by_death_place=False, link=False, jms_data=None, mg_data=None, verbose=False, include_score=False):

    groups = None
    if group_by_death_place is True:
        groups = dict()
        for jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, fs_score in matched:
            death_place = mg_person["DeathPlace"]
            groups[death_place] = []
        for jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, fs_score in matched:
            death_place = mg_person["DeathPlace"]
            groups[death_place].append((jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, fs_score))

    workbook = xlsxwriter.Workbook(output_path, {"strings_to_urls": False})

    if link is True:
        if verbose is True:
            print("Storing the JMS data...")
        create_jms_worksheet(data=jms_data, worksheet_name=JMS_MATCHING_WORKSHEET_NAME, workbook=workbook, add_source_info=USE_SOURCES, verbose=False)
        if verbose is True:
            print("Storing the 1964 data...")
        create_mg64_worksheet(data=mg_data, worksheet_name=MG64_MATCHING_WORKSHEET_NAME, workbook=workbook, add_source_info=USE_SOURCES, verbose=False)

    worksheet = workbook.add_worksheet("Matched")
    bold = workbook.add_format({"bold": True})
    group_font = workbook.add_format({"bold": True, "font_size": 20})
    
    current_row = 0

    column_names = ["Name and surname", "Father's name", "Birth year", "Place", "Death year (JMS and MG)", "Circumstances (MG)", "DeathPlace (MG)"]
    if include_score:
        column_names.append("Score")
              
    bold = workbook.add_format({"bold": True})
    for i, column_name in enumerate(column_names):
        worksheet.write(current_row, i, column_name, bold)
    worksheet.freeze_panes(current_row + 1, 0)
    column_max_lengths = [len(column_name) for column_name in column_names]

    current_row += 2
    
    if verbose is True:
        print("Writing the matched data...")
    
    if groups is None:
        for jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, fs_score in matched:
            current_row = write_match(jms_person, mg_person, worksheet, current_row, column_max_lengths, link=link, birth_year_in_sources=birth_year_in_sources, fs_score=fs_score, include_score=include_score)
    else:
        for group, group_matched in sorted(groups.items()):
            worksheet.write(current_row, 0, group, group_font)
            worksheet.set_row(current_row, 20)
            current_row += 2

            for jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, fs_score in group_matched:
                current_row = write_match(jms_person, mg_person, worksheet, current_row, column_max_lengths, link=link, birth_year_in_sources=birth_year_in_sources, fs_score=fs_score, include_score=include_score)

            current_row += 2

    for i in range(len(column_max_lengths)):
        worksheet.set_column(i, i, column_max_lengths[i] + COLUMN_WIDTH_OFFSET)

    workbook.close()

def write_report(matches, report_path, allow_empty=False, sort_name_parts=False, options=None):
    total = len(matches)
    exact_name_count = 0
    exact_surname_count = 0
    exact_name_and_surname_count = 0
    sorted_name_match_count = 0
    father_name_in_sources_count = 0
    birth_year_in_sources_count = 0
    birth_year_diff_counts = {}
    birth_place_in_sources_count = 0

    # 2x2 table: exact/adjusted name vs exact/adjusted surname
    exact_name_exact_surname = 0
    exact_name_adjusted_surname = 0
    adjusted_name_exact_surname = 0
    adjusted_name_adjusted_surname = 0

    for jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, _ in matches:
        jms_full = jms_person.get("name_and_surname", "").strip()
        mg_name = mg_person["Name"].strip()
        mg_surname = mg_person["Surname"].strip()

        jms_parts = jms_full.split()
        jms_name = jms_parts[0] if jms_parts else ""
        jms_surname = " ".join(jms_parts[1:]) if len(jms_parts) > 1 else ""

        name_exact = jms_name.lower() == mg_name.lower()
        surname_exact = jms_surname.lower() == mg_surname.lower()
        name_adjusted = prepare_name(jms_name) == prepare_name(mg_name)
        surname_adjusted = prepare_name(jms_surname) == prepare_name(mg_surname)

        if name_exact:
            exact_name_count += 1
        if surname_exact:
            exact_surname_count += 1
        if name_exact and surname_exact:
            exact_name_and_surname_count += 1
        if sort_name_parts:
            use_prepare_names = options.get("prepare_names", False) if options else False
            _names_prep = prepare_name if use_prepare_names else lambda x: x
            _cleanup = lambda x: x.lower().replace("*", "").replace("-", "").replace("9999", "")
            jms_key_unsorted = _cleanup(_names_prep(jms_full))
            mg_key_unsorted = _cleanup(_names_prep(mg_name + " " + mg_surname))
            jms_key_sorted = " ".join(sorted(jms_key_unsorted.split()))
            mg_key_sorted = " ".join(sorted(mg_key_unsorted.split()))
            if jms_key_unsorted != mg_key_unsorted and jms_key_sorted == mg_key_sorted:
                sorted_name_match_count += 1
        if father_name_in_sources:
            father_name_in_sources_count += 1
        if birth_year_in_sources:
            birth_year_in_sources_count += 1
            jms_by = int("0" + get_jms_birth_year(jms_person).replace("*", "").replace("-", ""))
            mg_by = int("0" + mg_person["BirthYear"].replace("9999", ""))
            if jms_by > 0 and mg_by > 0:
                diff = abs(jms_by - mg_by)
                birth_year_diff_counts[diff] = birth_year_diff_counts.get(diff, 0) + 1
        if birth_place_in_sources:
            birth_place_in_sources_count += 1

        if name_exact and surname_exact:
            exact_name_exact_surname += 1
        elif name_exact and not surname_exact:
            exact_name_adjusted_surname += 1
        elif not name_exact and surname_exact:
            adjusted_name_exact_surname += 1
        else:
            adjusted_name_adjusted_surname += 1

    # Death year comparison
    death_year_earlier = 0  # MG64 death year earlier than JMS
    death_year_identical = 0
    death_year_later = 0    # MG64 death year later than JMS
    death_year_missing = 0  # one or both missing

    for jms_person, mg_person, _, _, _, _ in matches:
        jms_dy_str = jms_person.get("Year of Death:", "").strip().replace("*", "").replace("-", "")
        mg_dy_str = mg_person["DeathYear"].strip().replace("9999", "").replace("-", "")
        if not jms_dy_str or not mg_dy_str:
            death_year_missing += 1
        else:
            try:
                jms_dy = int(jms_dy_str)
                mg_dy = int(mg_dy_str)
                if jms_dy == 0 or mg_dy == 0:
                    death_year_missing += 1
                elif mg_dy < jms_dy:
                    death_year_earlier += 1
                elif mg_dy == jms_dy:
                    death_year_identical += 1
                else:
                    death_year_later += 1
            except ValueError:
                death_year_missing += 1

    # Empty field analysis
    def is_value_empty(value):
        return value.strip().replace("*", "").replace("-", "") == ""

    def is_mg_value_empty(value):
        return value.strip().replace("9999", "").replace("-", "") == ""

    empty_father = 0
    empty_father_mg_nonempty = 0
    empty_birth_year = 0
    empty_birth_year_mg_nonempty = 0
    empty_birth_place = 0
    empty_birth_place_mg_nonempty = 0

    # Individual (exclusive — only that one field is empty)
    empty_only_father = 0
    empty_only_birth_year = 0
    empty_only_birth_place = 0

    # Combinations
    empty_father_and_birth_year = 0
    empty_father_and_birth_place = 0
    empty_birth_year_and_birth_place = 0
    empty_all_three = 0

    for jms_person, mg_person, father_name_in_sources, birth_year_in_sources, birth_place_in_sources, _ in matches:
        jms_father_empty = is_value_empty(jms_person.get("Father Name:", ""))
        jms_birth_year_empty = is_value_empty(get_jms_birth_year(jms_person))
        jms_birth_place_empty = is_value_empty(get_jms_birth_place(jms_person))

        if jms_father_empty:
            empty_father += 1
            if not is_mg_value_empty(mg_person["FatherName"]):
                empty_father_mg_nonempty += 1
        if jms_birth_year_empty:
            empty_birth_year += 1
            if not is_mg_value_empty(mg_person["BirthYear"]):
                empty_birth_year_mg_nonempty += 1
        if jms_birth_place_empty:
            empty_birth_place += 1
            if not is_mg_value_empty(mg_person["Place"]):
                empty_birth_place_mg_nonempty += 1

        if jms_father_empty and not jms_birth_year_empty and not jms_birth_place_empty:
            empty_only_father += 1
        if jms_birth_year_empty and not jms_father_empty and not jms_birth_place_empty:
            empty_only_birth_year += 1
        if jms_birth_place_empty and not jms_father_empty and not jms_birth_year_empty:
            empty_only_birth_place += 1

        if jms_father_empty and jms_birth_year_empty:
            empty_father_and_birth_year += 1
        if jms_father_empty and jms_birth_place_empty:
            empty_father_and_birth_place += 1
        if jms_birth_year_empty and jms_birth_place_empty:
            empty_birth_year_and_birth_place += 1
        if jms_father_empty and jms_birth_year_empty and jms_birth_place_empty:
            empty_all_three += 1

    lines = []
    lines.append("--- Match Report ---")
    lines.append("")
    if options is not None:
        lines.append("Options:")
        for key, value in options.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
    lines.append(f"Total matches: {total}")
    if total > 0:
        lines.append(f"Exact first name matches: {exact_name_count} ({100 * exact_name_count / total:.1f}%)")
        lines.append(f"Exact surname matches: {exact_surname_count} ({100 * exact_surname_count / total:.1f}%)")
        lines.append(f"Exact full name (name + surname) matches: {exact_name_and_surname_count} ({100 * exact_name_and_surname_count / total:.1f}%)")
        if sort_name_parts:
            lines.append(f"Matched only due to sorted name parts: {sorted_name_match_count} ({100 * sorted_name_match_count / total:.1f}%)")
        lines.append(f"Father's name found in sources (not direct match): {father_name_in_sources_count} ({100 * father_name_in_sources_count / total:.1f}%)")
        lines.append(f"Birth year found in sources (not direct match): {birth_year_in_sources_count} ({100 * birth_year_in_sources_count / total:.1f}%)")
        if birth_year_diff_counts:
            lines.append("  Absolute birth year differences (JMS birth year field vs MG64 birth year):")
            for diff in sorted(birth_year_diff_counts.keys()):
                count = birth_year_diff_counts[diff]
                lines.append(f"    |diff| = {diff}: {count} ({100 * count / birth_year_in_sources_count:.1f}%)")
        lines.append(f"Birth place found in sources (not direct match): {birth_place_in_sources_count} ({100 * birth_place_in_sources_count / total:.1f}%)")
        lines.append("")
        lines.append("Name vs Surname match table (exact / adjusted):")
        lines.append("")
        col_w = max(len(str(exact_name_exact_surname)), len(str(exact_name_adjusted_surname)), len(str(adjusted_name_exact_surname)), len(str(adjusted_name_adjusted_surname)), len("Exact surname"), len("Adjusted surname")) + 2
        header = f"{'':>20} {'Exact surname':>{col_w}} {'Adjusted surname':>{col_w}}"
        lines.append(header)
        lines.append(f"{'Exact name':>20} {exact_name_exact_surname:>{col_w}} {exact_name_adjusted_surname:>{col_w}}")
        lines.append(f"{'Adjusted name':>20} {adjusted_name_exact_surname:>{col_w}} {adjusted_name_adjusted_surname:>{col_w}}")

        if allow_empty:
            lines.append("")
            lines.append("--- Empty Field Analysis (JMS side) ---")
            lines.append("")
            lines.append("Individual empty fields:")
            lines.append(f"  Father's name empty: {empty_father} ({100 * empty_father / total:.1f}%), MG field non-empty: {empty_father_mg_nonempty}")
            lines.append(f"  Birth year empty:    {empty_birth_year} ({100 * empty_birth_year / total:.1f}%), MG field non-empty: {empty_birth_year_mg_nonempty}")
            lines.append(f"  Birth place empty:   {empty_birth_place} ({100 * empty_birth_place / total:.1f}%), MG field non-empty: {empty_birth_place_mg_nonempty}")
            lines.append("")
            lines.append("Combinations of empty fields:")
            lines.append(f"  Only father's name empty:          {empty_only_father}")
            lines.append(f"  Only birth year empty:             {empty_only_birth_year}")
            lines.append(f"  Only birth place empty:            {empty_only_birth_place}")
            lines.append(f"  Father's name + birth year empty:  {empty_father_and_birth_year}")
            lines.append(f"  Father's name + birth place empty: {empty_father_and_birth_place}")
            lines.append(f"  Birth year + birth place empty:    {empty_birth_year_and_birth_place}")
            lines.append(f"  All three empty:                   {empty_all_three}")
        # Death year comparison
        lines.append("")
        lines.append("--- Death Year Comparison (MG64 vs JMS) ---")
        lines.append("")
        lines.append(f"MG64 death year earlier than JMS: {death_year_earlier} ({100 * death_year_earlier / total:.1f}%)")
        lines.append(f"Identical death years:            {death_year_identical} ({100 * death_year_identical / total:.1f}%)")
        lines.append(f"MG64 death year later than JMS:   {death_year_later} ({100 * death_year_later / total:.1f}%)")
        lines.append(f"One or both missing:              {death_year_missing} ({100 * death_year_missing / total:.1f}%)")

        # MG64 death place and circumstances analysis
        death_place_counts = {}
        circumstances_counts = {}
        in_camp_death_place_counts = {}
        for _, mg_person, _, _, _, _ in matches:
            dp = mg_person["DeathPlace"].strip()
            ci = mg_person["Circumstances"].strip()
            death_place_counts[dp] = death_place_counts.get(dp, 0) + 1
            circumstances_counts[ci] = circumstances_counts.get(ci, 0) + 1
            if ci.lower() == IN_CAMP.lower():
                in_camp_death_place_counts[dp] = in_camp_death_place_counts.get(dp, 0) + 1

        lines.append("")
        lines.append("--- MG64 Death Place Analysis ---")
        lines.append("")
        lines.append(f"Distinct death places: {len(death_place_counts)}")
        lines.append("")
        lines.append("Death places by frequency:")
        for dp, count in sorted(death_place_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {dp}: {count} ({100 * count / total:.1f}%)")

        lines.append("")
        lines.append("--- MG64 Circumstances of Death Analysis ---")
        lines.append("")
        lines.append(f"Distinct circumstances: {len(circumstances_counts)}")
        lines.append("")
        lines.append("Circumstances by frequency:")
        for ci, count in sorted(circumstances_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {ci}: {count} ({100 * count / total:.1f}%)")

        if in_camp_death_place_counts:
            lines.append("")
            lines.append(f"--- Death places for \"{IN_CAMP}\" circumstances ---")
            lines.append("")
            in_camp_total = sum(in_camp_death_place_counts.values())
            lines.append(f"Total \"{IN_CAMP}\" matches: {in_camp_total}")
            lines.append("")
            for dp, count in sorted(in_camp_death_place_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {dp}: {count} ({100 * count / in_camp_total:.1f}%)")

    else:
        lines.append("No matches found.")

    with open(report_path, "w", encoding="utf8") as f:
        f.write("\n".join(lines) + "\n")

def match_data(jms_input_path, mg1964_input_path, output_path, jms_links_path=None, group_by_death_place=False, link=False, report_path=None, verbose=False, maximum_direct_birth_year_difference=DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE, use_father_name_for_grouping=False, use_birth_year_for_grouping=False, use_birth_place_for_grouping=False, check_father_names=False, check_birth_years=False, check_birth_places=False, prepare_names=False, sort_name_parts=False, allow_for_alternative_father_name=False, allow_for_alternative_birth_year=False, allow_for_alternative_birth_place=False, allow_empty_father_name=False, allow_empty_birth_place=False, allow_empty_birth_year=False, list_matches=False, matches_output_path=None, separator=" | ", include_death=False, include_source=False, include_score=False, fuzzy_method=None, fuzzy_threshold=None, fuzzy_father=False, fs_mode=False, fs_upper=DEFAULT_FS_UPPER_THRESHOLD, fs_lower=DEFAULT_FS_LOWER_THRESHOLD, fs_levels=DEFAULT_FS_LEVELS, fs_em_iterations=DEFAULT_FS_EM_ITERATIONS, fs_review_path=None, match_all=False, block_letters=1, estimation_path=None):
    if verbose is True:
        print("Loading JMS data...")
    jms_data = load_jms_data(input_path=jms_input_path)

    jms_urls = None
    if jms_links_path is not None:
        jms_urls = []
        with open(jms_links_path, "r", encoding="utf8") as f:
            for line in f.readlines():
                jms_urls.append(line.strip("\r\n"))

    if verbose is True:
        print("Loading MG 1964 data...")
    mg_data = load_mg1964_data(input_path=mg1964_input_path, sort=SORT)

    if link is True:
        for pi, person in enumerate(jms_data):
            person["Row"] = pi + 2
            if jms_urls is not None:
                person["URL"] = jms_urls[pi] if pi < len(jms_urls) else None
        for pi, person in enumerate(mg_data):
            person["Row"] = pi + 2

    if verbose is True:
        print("Filtering MG 1964 data...")
    filtered_mg_data = filter_mg1964_data(data=mg_data)

    matched, review = find_matches(
        jms_data=jms_data,
        mg_data=filtered_mg_data,
        verbose=verbose,
        maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
        use_father_name=use_father_name_for_grouping,
        use_birth_year=use_birth_year_for_grouping,
        use_birth_place=use_birth_place_for_grouping,
        check_father_names=check_father_names,
        check_birth_years=check_birth_years,
        check_birth_places=check_birth_places,
        prepare_names=prepare_names,
        sort_name_parts=sort_name_parts,
        allow_for_alternative_father_name=allow_for_alternative_father_name,
        allow_for_alternative_birth_year=allow_for_alternative_birth_year,
        allow_for_alternative_birth_place=allow_for_alternative_birth_place,
        allow_empty_father_name=allow_empty_father_name,
        allow_empty_birth_place=allow_empty_birth_place,
        allow_empty_birth_year=allow_empty_birth_year,
        fuzzy_method=fuzzy_method,
        fuzzy_threshold=fuzzy_threshold,
        fuzzy_father=fuzzy_father,
        fs_mode=fs_mode,
        fs_upper=fs_upper,
        fs_lower=fs_lower,
        fs_levels=fs_levels,
        fs_em_iterations=fs_em_iterations,
        match_all=match_all,
        block_letters=block_letters,
        estimation_path=estimation_path
    )

    if verbose is True:
        print(f"The number of found matches is {len(matched)}.")

    if list_matches is True or matches_output_path is not None:
        pairs = []
        for jms_person, mg_person, _, _, _, fs_score in matched:
            jms_name_and_surname = jms_person.get("name_and_surname", "")
            jms_father = jms_person.get("Father Name:", "")
            jms_birth_year = get_jms_birth_year(jms_person)
            jms_birth_place = get_jms_birth_place(jms_person)
            jms_parts = [jms_name_and_surname, jms_father, jms_birth_year, jms_birth_place]
            if include_death is True:
                jms_parts.append(jms_person.get("Year of Death:", ""))
                jms_parts.append(jms_person.get("Camp:", ""))
            if include_source is True:
                jms_parts.append(jms_person.get("Source:", ""))
            if include_score and fs_score is not None:
                jms_parts.append(f"{fs_score:.2f}")
            jms_line = separator.join(jms_parts)
            mg_name_and_surname = mg_person["Name"] + " " + mg_person["Surname"]
            mg_father = mg_person["FatherName"]
            mg_birth_year = mg_person["BirthYear"]
            mg_birth_place = mg_person["Place"]
            mg_parts = [mg_name_and_surname, mg_father, mg_birth_year, mg_birth_place]
            if include_death is True:
                mg_parts.append(mg_person["DeathYear"])
                mg_parts.append(mg_person["DeathPlace"])
            mg_line = "\t" + separator.join(mg_parts)
            pairs.append((jms_line, mg_line))
        pairs.sort(key=lambda p: p[0] + p[1])
        lines = []
        for jms_line, mg_line in pairs:
            lines.append(jms_line)
            lines.append(mg_line)
        if list_matches is True:
            for line in lines:
                print(line)
        if matches_output_path is not None:
            with open(matches_output_path, "w", encoding="utf8") as f:
                f.write("\n".join(lines) + "\n")

    if output_path is not None:
        if verbose is True:
            print("Creating the output file...")
        save_matches(matched=matched, output_path=output_path, group_by_death_place=group_by_death_place, link=link, jms_data=jms_data if link is True else None, mg_data=mg_data if link is True else None, verbose=verbose, include_score=include_score)

    if report_path is not None:
        report_options = {
            "use_father_name_for_grouping": use_father_name_for_grouping,
            "use_birth_year_for_grouping": use_birth_year_for_grouping,
            "use_birth_place_for_grouping": use_birth_place_for_grouping,
            "check_father_names": check_father_names,
            "check_birth_years": check_birth_years,
            "check_birth_places": check_birth_places,
            "prepare_names": prepare_names,
            "sort_name_parts": sort_name_parts,
            "allow_for_alternative_father_name": allow_for_alternative_father_name,
            "allow_for_alternative_birth_year": allow_for_alternative_birth_year,
            "allow_for_alternative_birth_place": allow_for_alternative_birth_place,
            "allow_empty_father_name": allow_empty_father_name,
            "allow_empty_birth_year": allow_empty_birth_year,
            "allow_empty_birth_place": allow_empty_birth_place,
            "maximum_direct_birth_year_difference": maximum_direct_birth_year_difference,
            "fuzzy_father": fuzzy_father,
            "fellegi_sunter": fs_mode,
        }
        write_report(matched, report_path, allow_empty=allow_empty_father_name or allow_empty_birth_year or allow_empty_birth_place, sort_name_parts=sort_name_parts, options=report_options)
        if verbose is True:
            print(f"Report has been created at {report_path}.")

    if fs_review_path is not None and review:
        review_lines = []
        for jms_person, mg_person, score in review:
            jms_name = jms_person.get("name_and_surname", "")
            jms_father = jms_person.get("Father Name:", "")
            jms_birth_year = get_jms_birth_year(jms_person)
            jms_birth_place = get_jms_birth_place(jms_person)
            mg_name = mg_person["Name"] + " " + mg_person["Surname"]
            mg_father = mg_person["FatherName"]
            mg_birth_year = mg_person["BirthYear"]
            mg_birth_place = mg_person["Place"]
            review_lines.append(f"{score:.2f}\t{jms_name}\t{jms_father}\t{jms_birth_year}\t{jms_birth_place}\t{mg_name}\t{mg_father}\t{mg_birth_year}\t{mg_birth_place}")
        review_lines.sort(key=lambda x: -float(x.split("\t")[0]))
        with open(fs_review_path, "w", encoding="utf8") as f:
            f.write("score\tjms_name\tjms_father\tjms_year\tjms_place\tmg_name\tmg_father\tmg_year\tmg_place\n")
            f.write("\n".join(review_lines) + "\n")
        if verbose is True:
            print(f"Review pairs ({len(review_lines)}) written to {fs_review_path}.")

def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-j", "--jms", required=True, help="JMS input path.")
    parser.add_argument("-u", "--url", default=None, help="JMS links path.")
    parser.add_argument("-m", "--mg", required=True, help="MG1964 input path.")
    parser.add_argument("-o", "--output", default=None, help="Output path. If not provided, no output file will be created.")
    parser.add_argument("-g", "--group", action="store_true", help="Whether to group by death place.")
    parser.add_argument("-l", "--link", action="store_true", help="Whether to include the whole tables and add links to matched records.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be verbose.")
    parser.add_argument("-r", "--report", default=None, help="Report output file path.")
    parser.add_argument("-M", "--maximum", type=int, default=DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE, help="Maximum direct birth year difference for matching.")
    parser.add_argument("-f", "--father", action="store_true", help="Use father's name in grouping keys.")
    parser.add_argument("-y", "--year", action="store_true", help="Use birth year in grouping keys.")
    parser.add_argument("-p", "--place", action="store_true", help="Use birth place in grouping keys.")
    parser.add_argument("-F", "--check-father-name", action="store_true", help="Check father's name in matching.")
    parser.add_argument("-Y", "--check-birth-years", action="store_true", help="Check birth years in matching.")
    parser.add_argument("-P", "--check-birth-places", action="store_true", help="Check birth places in matching.")
    parser.add_argument("-n", "--names", action="store_true", help="Use name normalization in grouping keys.")
    parser.add_argument("-s", "--sort", action="store_true", help="Sort name and surname parts alphabetically in grouping keys.")
    parser.add_argument("-a", "--alternative", action="store_true", help="Allow alternative father name, birth year, and place matching.")
    parser.add_argument("-e", "--empty", action="store_true", help="Allow matching when JMS father name, birth year, or birth place is empty.")
    parser.add_argument("-L", "--list", action="store_true", help="Print the list of matches to stdout.")
    parser.add_argument("-O", "--matches-output", default=None, help="Output file path for the list of matches.")
    parser.add_argument("--separator", default=" | ", help="Separator for the list of matches (default: \" | \").")
    parser.add_argument("-d", "--death", action="store_true", help="Include death year and death place in the list of matches.")
    parser.add_argument("-S", "--source", action="store_true", help="Include JMS source as the last field in the list of matches.")
    parser.add_argument("--score", action="store_true", help="Include the Fellegi-Sunter composite score in the match listing and Excel output.")
    fuzzy_group = parser.add_mutually_exclusive_group()
    fuzzy_group.add_argument("--jwd", action="store_true", help="Use Jaro-Winkler distance for fuzzy name matching.")
    fuzzy_group.add_argument("--ld", action="store_true", help="Use Levenshtein distance for fuzzy name matching.")
    fuzzy_group.add_argument("--dld", action="store_true", help="Use Damerau-Levenshtein distance for fuzzy name matching.")
    fuzzy_group.add_argument("--nld", action="store_true", help="Use normalized Levenshtein distance for fuzzy name matching.")
    fuzzy_group.add_argument("--bm", action="store_true", help="Use Beider-Morse phonetic matching.")
    parser.add_argument("-t", "--threshold", type=float, default=None, help="Threshold for fuzzy matching. Defaults: JWD=0.85, LD=3, DLD=3, NLD=0.85, BM=0.5.")
    parser.add_argument("--ff", "--fuzzy-father", action="store_true", dest="fuzzy_father", help="Apply fuzzy matching to father's name comparison (requires a fuzzy method to be active).")
    parser.add_argument("-b", "--block", type=int, default=1, help="Number of initial letters per name/surname part used in the blocking key for fuzzy matching (default: 1).")
    parser.add_argument("--fs", action="store_true", help="Use Fellegi-Sunter probabilistic matching.")
    parser.add_argument("--fs-upper", type=float, default=DEFAULT_FS_UPPER_THRESHOLD, help=f"Fellegi-Sunter upper threshold (match). Default: {DEFAULT_FS_UPPER_THRESHOLD}.")
    parser.add_argument("--fs-lower", type=float, default=DEFAULT_FS_LOWER_THRESHOLD, help=f"Fellegi-Sunter lower threshold (non-match below). Default: {DEFAULT_FS_LOWER_THRESHOLD}.")
    parser.add_argument("--fs-levels", type=int, default=DEFAULT_FS_LEVELS, help=f"Discretization levels for continuous similarity fields in Fellegi-Sunter mode. Default: {DEFAULT_FS_LEVELS}.")
    parser.add_argument("--fs-em-iterations", type=int, default=DEFAULT_FS_EM_ITERATIONS, help=f"Maximum EM iterations for Fellegi-Sunter parameter estimation. Default: {DEFAULT_FS_EM_ITERATIONS}.")
    parser.add_argument("--fs-review", default=None, help="Output file for Fellegi-Sunter review-zone pairs (scores between lower and upper thresholds).")
    parser.add_argument("-E", "--estimation", default=None, help="Path to a file with pre-estimated m/u probabilities for Fellegi-Sunter matching (skips EM estimation).")
    parser.add_argument("-A", "--all", action="store_true", help="Include all matching candidates, not just the best.")
    args = parser.parse_args()

    jms_input_path = args.jms
    jms_links_path = args.url
    mg1964_input_path = args.mg
    output_path = args.output
    group_by_death_place = args.group
    link = args.link
    verbose = args.verbose
    report_path = args.report
    maximum_direct_birth_year_difference = args.maximum
    use_father_name_for_grouping = args.father
    use_birth_year_for_grouping = args.year
    use_birth_place_for_grouping = args.place
    check_father_names = args.check_father_name
    check_birth_years = args.check_birth_years
    check_birth_places = args.check_birth_places
    prepare_names = args.names
    sort_name_parts = args.sort
    allow_for_alternative = args.alternative
    allow_empty = args.empty
    list_matches = args.list
    matches_output_path = args.matches_output
    separator = args.separator
    include_death = args.death
    include_source = args.source
    include_score = args.score

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

    fuzzy_father = args.fuzzy_father
    if fuzzy_father and fuzzy_method is None:
        parser.error("--ff/--fuzzy-father requires a fuzzy method (--jwd, --ld, --dld, --nld, or --bm).")

    fs_mode = args.fs
    fs_upper = args.fs_upper
    fs_lower = args.fs_lower
    fs_levels = args.fs_levels
    fs_em_iterations = args.fs_em_iterations
    fs_review_path = args.fs_review
    estimation_path = args.estimation

    match_all = args.all
    block_letters = args.block

    match_data(
        jms_input_path=jms_input_path,
        mg1964_input_path=mg1964_input_path,
        output_path=output_path,
        jms_links_path=jms_links_path,
        group_by_death_place=group_by_death_place,
        link=link,
        report_path=report_path,
        verbose=verbose,
        maximum_direct_birth_year_difference=maximum_direct_birth_year_difference,
        use_father_name_for_grouping=use_father_name_for_grouping,
        use_birth_year_for_grouping=use_birth_year_for_grouping,
        use_birth_place_for_grouping=use_birth_place_for_grouping,
        check_father_names=check_father_names,
        check_birth_years=check_birth_years,
        check_birth_places=check_birth_places,
        prepare_names=prepare_names,
        sort_name_parts=sort_name_parts,
        allow_for_alternative_father_name=allow_for_alternative,
        allow_for_alternative_birth_year=allow_for_alternative,
        allow_for_alternative_birth_place=allow_for_alternative,
        allow_empty_father_name=allow_empty,
        allow_empty_birth_place=allow_empty,
        allow_empty_birth_year=allow_empty,
        list_matches=list_matches,
        matches_output_path=matches_output_path,
        separator=separator,
        include_death=include_death,
        include_source=include_source,
        include_score=include_score,
        fuzzy_method=fuzzy_method,
        fuzzy_threshold=fuzzy_threshold,
        fuzzy_father=fuzzy_father,
        fs_mode=fs_mode,
        fs_upper=fs_upper,
        fs_lower=fs_lower,
        fs_levels=fs_levels,
        fs_em_iterations=fs_em_iterations,
        fs_review_path=fs_review_path,
        match_all=match_all,
        block_letters=block_letters,
        estimation_path=estimation_path
    )

if __name__ == "__main__":
    main()
