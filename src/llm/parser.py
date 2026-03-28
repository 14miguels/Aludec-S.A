from src.schema.schema import Section, Substance, Hazard, TransportInfo, SevesoInfo, PhysicalProperties
import json

def parse_sections(response : str) -> list[Section]:

    if response is None:
        return []
    
    response = response.strip()
    
    if response == "":
        return []
    try:
        json_response = json.loads(response)
    except json.JSONDecodeError:
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

    if response is None:
        return []
    
    response = response.strip()

    if response == "" :
        return []
    try:
        json_response = json.loads(response)
    except json.JSONDecodeError:
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
        if not isinstance(sub_name, str):
            sub_name = "" if sub_name is None else str(sub_name)

        sub_cas = sub.get("cas_number")
        sub_percentage = sub.get("percentage")

        substance = Substance(
            name= sub_name,
            cas_number= sub_cas,
            percentage= sub_percentage
        )

        substances.append(substance)

    return substances
  
def parse_hazards(response : str) -> list[Hazard]:


    if response is None:
        return []
    
    response = response.strip()

    if response == "":
        return []
    
    try:
        json_response = json.loads(response)
    except json.JSONDecodeError:
        return []
    
    if isinstance(json_response, dict):
        json_response = json_response.get("hazards")
        if not isinstance(json_response, list):
            return []
    elif not isinstance(json_response, list):
        return []
    
    hazards = []

    for haz in json_response:
        if not isinstance(haz,dict):
            continue

        haz_code = haz.get("code")
        if haz_code is None:
            haz_code =""
        
        haz_description = haz.get("description")
        if haz_description is None:
            haz_description = ""

        hazard = Hazard(
            code=haz_code,
            description=haz_description
        )
        hazards.append(hazard)

    return hazards

def parse_transport_info(response : str) -> TransportInfo | None:

    if response is None:
        return None
    
    response = response.strip()

    if response == "":
        return None
    
    try:
        json_response = json.loads(response)
    except json.JSONDecodeError:
        return None

    if isinstance(json_response, dict):
        json_response = json_response.get("transport_info")

    if not isinstance(json_response, dict):
        return None

    tra_un_number = json_response.get("un_number") or ""
    tra_shipping_name = json_response.get("shipping_name") or ""
    tra_hazard_class = json_response.get("hazard_class") or ""
    tra_packing_group = json_response.get("packing_group") or ""
    tra_environmental_hazard = json_response.get("environmental_hazard") or ""

    return TransportInfo(
        un_number=tra_un_number,
        shipping_name=tra_shipping_name,
        hazard_class=tra_hazard_class,
        packing_group=tra_packing_group,
        environmental_hazard=tra_environmental_hazard
    )

def parse_seveso_info(response : str) -> SevesoInfo | None:

    if response is None:
        return None
    
    response = response.strip()

    if response == "":
        return None
    
    try:
        json_response = json.loads(response)
    except json.JSONDecodeError:
        return None

    if isinstance(json_response, dict):
        json_response = json_response.get("seveso_info")

    if not isinstance(json_response, dict):
        return None

    sev_cat = json_response.get("category") or ""

    return SevesoInfo(
        category=sev_cat
    )

def parse_physical_properties(response : str) -> PhysicalProperties | None:

    if response is None:
        return None
    
    response = response.strip()

    if response == "":
        return None
    try:
        json_response = json.loads(response)
    except json.JSONDecodeError:
        return None

    if isinstance(json_response, dict):
        json_response = json_response.get("physical_properties")

    if not isinstance(json_response, dict):
        return None

    pro_state = json_response.get("state") or ""
    pro_density = json_response.get("density") or ""
    pro_flash_point = json_response.get("flash_point") or ""
    pro_voc = json_response.get("voc") or ""

    return PhysicalProperties(
        state=pro_state,
        density=pro_density,
        flash_point=pro_flash_point,
        voc=pro_voc
    )