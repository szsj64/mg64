# -*- coding: utf-8 -*-

import argparse
import json
import xlsxwriter
import re
from tqdm import tqdm

DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE = 0

CAMP = "logor"

IN_CAMP = "u logoru"
JASENOVAC = "Jasenovac"
JAENOVAC = "Jaenovac"
UNKNOWN = "Nepoznato"
GRADISKA1 = "Stara Gradiška"
GRADISKA2 = "St. Gradiška"
GRADISKA3 = "St Gradiška"
GRADISKA4 = "Stara grediška"
GRADISKA4 = "Stara grediška"
GRADISKA5 = "Stara gardiška"
GRADISKA6 = "Stara gadiška"
UNKNOWN_CAMP = "Nepoznati logor"
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

def group_jms_data(data, use_birth_year=True, prepare_names=False):
    jms_prepare = lambda x: x.lower().replace("*", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    if use_birth_year is True:
        get_jms_key=lambda x: tuple(map(jms_prepare, [names_preparation(x.get("name_and_surname", "")), names_preparation(x.get("Father Name:", "")), get_jms_birth_year(x), get_jms_birth_place(x)]))
    else:
        get_jms_key=lambda x: tuple(map(jms_prepare, [names_preparation(x.get("name_and_surname", "")), names_preparation(x.get("Father Name:", "")), get_jms_birth_place(x)]))
    
    jms_groups = dict()
    for person in data:
        k = get_jms_key(person)
        jms_groups[k] = []
    for person in data:
        k = get_jms_key(person)
        jms_groups[k].append(person)
    
    return jms_groups

def group_mg1964_data(data, use_birth_year=True, prepare_names=False):
    mg_prepare = lambda x: x.lower().replace("9999", "").replace("-", "")
    names_preparation = prepare_name if prepare_names is True else lambda x: x
    #place_preparation = lambda x: "Zagreb" if x.lower().startswith("zagreb") else x
    place_preparation = lambda x: "Zagreb" if x.lower().startswith("zagreb") else "Beograd" if x.lower().startswith("beograd") else x
    #place_preparation = lambda x: x if "-" not in x else x.split("-")[0].rstrip()
    if use_birth_year is True:
        get_mg_key=lambda x: tuple(map(mg_prepare, [names_preparation(x["Name"] + " " + x["Surname"]), names_preparation(x["FatherName"]), x["BirthYear"], place_preparation(x["Place"])]))
    else:
        get_mg_key=lambda x: tuple(map(mg_prepare, [names_preparation(x["Name"] + " " + x["Surname"]), names_preparation(x["FatherName"]), place_preparation(x["Place"])]))
    
    mg_groups = dict()
    for person in data:
        k = get_mg_key(person)
        mg_groups[k] = []
    for person in data:
        k = get_mg_key(person)
        mg_groups[k].append(person)
    
    return mg_groups

def filter_mg1964_data(data):
    filtered_data = []

    filter_keywords = [IN_CAMP, JASENOVAC, JAENOVAC, UNKNOWN, GRADISKA1, GRADISKA2, GRADISKA3, GRADISKA4, GRADISKA5, GRADISKA6, UNKNOWN_CAMP, JASENOVAC_CAMP, JASENOVAC, MLAKA, JABLANAC, KRAPJE, BROCICE, GRADINA]
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

def check_matches(jms_groups, mg_groups, common_keys, check_birth_years=True, allow_for_alternative_birth_year=False, maximum_direct_birth_year_difference=None):
    matches = []
    for k in common_keys:
        for jms_person in jms_groups[k]:
            matched_person = None
            for mg_person in mg_groups[k]:
                if check_birth_years is False:
                    matched_person = mg_person
                    break
                else:
                    jms_birth_year = int("0" + get_jms_birth_year(jms_person).replace("*", "").replace("-", ""))
                    mg_birth_year = int("0" + mg_person["BirthYear"].replace("9999", ""))
                    if jms_birth_year == mg_birth_year \
                        or (allow_for_alternative_birth_year is True and jms_birth_year > 0 and str(jms_birth_year) in jms_person.get("Source:", "")) \
                        or (maximum_direct_birth_year_difference is not None and abs(jms_birth_year - mg_birth_year) <= maximum_direct_birth_year_difference):
                        matched_person = mg_person
                        break
            birth_year_in_sources = False
            if jms_birth_year != mg_birth_year and (allow_for_alternative_birth_year is True and jms_birth_year > 0 and str(jms_birth_year) in jms_person.get("Source:", "")):
                birth_year_in_sources = True
            if matched_person is not None:
                matches.append((jms_person, matched_person, birth_year_in_sources))
    
    return matches

def find_matches(jms_data, mg_data, verbose=False):
    
    use_birth_year = False
    prepare_names = True
    allow_for_alternative_birth_year = True
    maximum_direct_birth_year_difference = DEFAULT_MAXIMUM_DIRECT_BIRTH_YEAR_DIFFERENCE
    check_birth_years = True

    if verbose is True:
        print("Grouping JMS data...")
    jms_groups = group_jms_data(data=jms_data, use_birth_year=use_birth_year, prepare_names=prepare_names)

    if verbose is True:
        print("Grouping MG 1964 data...")
    mg_groups = group_mg1964_data(data=mg_data, use_birth_year=use_birth_year, prepare_names=prepare_names)

    common_keys = list(set(jms_groups.keys()).intersection(set(mg_groups.keys())))
    
    matches = check_matches(jms_groups=jms_groups, mg_groups=mg_groups, common_keys=common_keys, check_birth_years=check_birth_years, allow_for_alternative_birth_year=allow_for_alternative_birth_year, maximum_direct_birth_year_difference=maximum_direct_birth_year_difference)

    return matches

def write_match(jms_person, mg_person, worksheet, current_row, column_max_lengths, link=False, birth_year_in_sources=False):
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

def save_matches(matched, output_path, group_by_death_place=False, link=False, jms_data=None, mg_data=None, verbose=False):

    groups = None
    if group_by_death_place is True:
        groups = dict()
        for jms_person, mg_person, birth_year_in_sources in matched:
            death_place = mg_person["DeathPlace"]
            groups[death_place] = []
        for jms_person, mg_person, birth_year_in_sources in matched:
            death_place = mg_person["DeathPlace"]
            groups[death_place].append((jms_person, mg_person, birth_year_in_sources))

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
              
    bold = workbook.add_format({"bold": True})
    for i, column_name in enumerate(column_names):
        worksheet.write(current_row, i, column_name, bold)
    worksheet.freeze_panes(current_row + 1, 0)
    column_max_lengths = [len(column_name) for column_name in column_names]

    current_row += 2
    
    if verbose is True:
        print("Writing the matched data...")
    
    if groups is None:
        for jms_person, mg_person, birth_year_in_sources in matched:
            current_row = write_match(jms_person, mg_person, worksheet, current_row, column_max_lengths, link=link, birth_year_in_sources=birth_year_in_sources)
    else:
        for group, group_matched in sorted(groups.items()):
            worksheet.write(current_row, 0, group, group_font)
            worksheet.set_row(current_row, 20)
            current_row += 2

            for jms_person, mg_person, birth_year_in_sources in group_matched:
                current_row = write_match(jms_person, mg_person, worksheet, current_row, column_max_lengths, link=link, birth_year_in_sources=birth_year_in_sources)

            current_row += 2

    for i in range(len(column_max_lengths)):
        worksheet.set_column(i, i, column_max_lengths[i] + COLUMN_WIDTH_OFFSET)

    workbook.close()

def match_data(jms_input_path, mg1964_input_path, output_path, jms_links_path=None, group_by_death_place=False, link=False, verbose=False):
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

    matched = find_matches(jms_data=jms_data, mg_data=filtered_mg_data, verbose=verbose)

    if verbose is True:
        print(f"The number of found matches is {len(matched)}.")

    if verbose is True:
        print("Creating the output file...")
    save_matches(matched=matched, output_path=output_path, group_by_death_place=group_by_death_place, link=link, jms_data=jms_data if link is True else None, mg_data=mg_data if link is True else None, verbose=verbose)
    
def main():
    parser = argparse.ArgumentParser(description="Input parse ")
    parser.add_argument("-j", "--jms", required=True, help="JMS input path.")
    parser.add_argument("-u", "--url", default=None, help="JMS links path.")
    parser.add_argument("-m", "--mg", required=True, help="MG1964 input path.")
    parser.add_argument("-o", "--output", required=True, help="Output path.")
    parser.add_argument("-g", "--group", action="store_true", help="Whether to group by death place.")
    parser.add_argument("-l", "--link", action="store_true", help="Whether to include the whole tables and add links to matched records.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Whether to be verbose.")
    args = parser.parse_args()

    jms_input_path = args.jms
    jms_links_path = args.url
    mg1964_input_path = args.mg
    output_path = args.output
    group_by_death_place = args.group
    link = args.link
    verbose = args.verbose

    match_data(jms_input_path=jms_input_path, mg1964_input_path=mg1964_input_path, output_path=output_path, jms_links_path=jms_links_path, group_by_death_place=group_by_death_place, link=link, verbose=verbose)

if __name__ == "__main__":
    main()
