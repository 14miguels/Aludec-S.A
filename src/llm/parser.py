from src.schema.schema import Section, Substance
import json

def parse_sections(response : str) -> list[Section]:

    if response == None:
        return []
    
    response = response.strip()
    
    if response == "" or response == None:
        return []
    try:
        json_response = json.loads(response)
    except:
        return []

    # Normalize result to a list of sections
    if isinstance(json_response, dict):

        json_response = json_response.get("sections")
        if not isinstance(json_response, list):
            return []
        
    elif not isinstance(json_response, list):
        return []

    sections = []
    for sec in json_response:
        if not isinstance(sec, dict):
            continue

        sec_number = sec.get("section_number")
        sec_title = sec.get("title")
        sec_text = sec.get("raw_text")
        if not isinstance(sec_text, str):
            sec_text = "" if sec_text is None else str(sec_text)

        section = Section(
            section_number = sec_number,
            title = sec_title,
            raw_text = sec_text
        )

        sections.append(section)

    return sections

def parse_substances(response : str) -> list[Substance]:

    if response == None:
        return []
    
    response = response.strip()

    if response == "" :
        return []
    try:
        json_response = json.loads(response)
    except:
        return []

    # Normalize result to a list of substances
    if isinstance(json_response, dict):
        
        json_response = json_response.get("substances")
        if not isinstance(json_response, list):
            return []
        
    elif not isinstance(json_response, list):
        return []

    substances = []
    for sub in json_response:
        if not isinstance(sub, dict):
            continue

        sub_name = sub.get("name")
        if sub_name is None:
            sub_name = ""
        sub_cas = sub.get("cas_number")
        sub_percentage = sub.get("percentage")

        substance = Substance(
            name= sub_name,
            cas_number= sub_cas,
            percentage= sub_percentage
        )

        substances.append(substance)

    return substances
  