from src.schema.schema import ProcessingMetadata, Substance, SDSDocument, Hazard, PhysicalProperties, SevesoInfo, TransportInfo

def init_metadata() -> ProcessingMetadata: 
    return ProcessingMetadata(
        extraction_method=None,
        warnings=[],
        confidence=None
    )
def init_sds(filename: str,
             metadata_splitter: ProcessingMetadata,
             metadata_hazards: ProcessingMetadata,
             metadata_substances: ProcessingMetadata,
             metadata_physical_properties: ProcessingMetadata,
             metadata_seveso_info: ProcessingMetadata,
             metadata_transport_info: ProcessingMetadata) -> SDSDocument:
    return SDSDocument(

        file_name=filename,
        language=None,
        sections=[],
        substances=[],
        hazards=[],
        physical_properties=None,
        transport=None,
        seveso=None,

        #Metadatas

        splitter_metadata=metadata_splitter,
        substances_metadata=metadata_substances,
        hazards_metadata=metadata_hazards,
        physical_properties_metadata=metadata_physical_properties,
        transport_metadata=metadata_transport_info,
        seveso_metadata=metadata_seveso_info
    )

def validation_substances(substances : list[Substance]) -> list[str]:
    """Gives all the warnings from the build"""
    warnings = []
    if not substances: 
        warnings.append("Failed to extract section3")
        return warnings
    
    for substance in substances:

        if substance.name is None:
            warnings.append("Missing substance name")
        
        if substance.cas_number is None:
            if not substance.name:
                warnings.append("Missing CAS")
            else:
                warnings.append(f'Missing CAS for {substance.name}')
                
        if substance.percentage is None:
            if not substance.name:
                warnings.append("Missing percentage")
            else:
                warnings.append(f'Missing percentage for {substance.name}')

    return warnings

def confidence_substances(substances : list[Substance]) -> float:
    """Gives extimate confidence from 0.0-1"""

    confidence = 1.0

    if not substances:
        confidence = 0
        return confidence
    
    tax = 1 / len(substances)

    
    for substance in substances:

        if substance.name is None:
            confidence-= tax*0.5
        
        if substance.cas_number is None:
            confidence-= tax*0.3

        if substance.percentage is None:
            confidence-= tax*0.3

    if confidence <= 0:
        return 0.0
    return round(confidence,2)

def validation_hazards(hazards : list[Hazard]) -> list[str]:
    """Gives all the warnings from the build"""
    warnings = []
    if not hazards: 
        warnings.append("Failed to extract section3")
        return warnings
    
    for hazard in hazards:

        if hazard.code is None:
            warnings.append("Missing hazard code")
        
        if hazard.description is None:
            if not hazard.code:
                warnings.append("Missing Description")
            else:
                warnings.append(f'Missing Description for {hazard.code}')
        

    return warnings

def confidence_hazards(hazards : list[Hazard]) -> float:
    """Gives extimate confidence from 0.0-1"""

    confidence = 1.0

    if not hazards:
        confidence = 0
        return confidence
    
    tax = 1 / len(hazards)

    
    for hazard in hazards:

        if hazard.code is None:
            confidence-= tax*0.5
        
        if hazard.description is None:
            confidence-= tax*0.3

    if confidence <= 0:
        return 0.0
    return round(confidence,2)

def validation_physical_properties(properties: PhysicalProperties) -> list[str]:
    """Gives all the warnings from the build"""
    warnings = []

    if properties is None:
        warnings.append("Failed to extract section9")
        return warnings

    if properties.state is None or properties.state == "":
        warnings.append("Missing state")

    if properties.density is None or properties.density == "":
        warnings.append("Missing density")

    if properties.flash_point is None or properties.flash_point == "":
        warnings.append("Missing flash_point")

    if properties.voc is None or properties.voc == "":
        warnings.append("Missing voc")

    return warnings


def confidence_physical_properties(properties: PhysicalProperties) -> float:
    """Gives estimate confidence from 0.0-1"""

    if properties is None:
        return 0.0

    confidence = 1.0

    fields = [
        properties.state,
        properties.density,
        properties.flash_point,
        properties.voc
    ]

    tax = 1 / len(fields)

    for field in fields:
        if field is None or field == "":
            confidence -= tax

    if confidence <= 0:
        return 0.0

    return round(confidence, 2)

def validation_transport(transport: TransportInfo) -> list[str]:
    """Gives all the warnings from the build"""
    warnings = []

    if transport is None:
        warnings.append("Failed to extract section14")
        return warnings

    if transport.un_number is None or transport.un_number == "":
        warnings.append("Missing UN number")

    if transport.shipping_name is None or transport.shipping_name == "":
        warnings.append("Missing shipping name")

    if transport.hazard_class is None or transport.hazard_class == "":
        warnings.append("Missing hazard class")

    if transport.packing_group is None or transport.packing_group == "":
        warnings.append("Missing packing group")

    if transport.environmental_hazard is None or transport.environmental_hazard == "":
        warnings.append("Missing environmental hazard")

    return warnings


def confidence_transport(transport: TransportInfo) -> float:
    """Gives estimate confidence from 0.0-1"""

    if transport is None:
        return 0.0

    confidence = 1.0

    fields = [
        transport.un_number,
        transport.shipping_name,
        transport.hazard_class,
        transport.packing_group,
        transport.environmental_hazard
    ]

    tax = 1 / len(fields)

    for field in fields:
        if field is None or field == "":
            confidence -= tax

    if confidence <= 0:
        return 0.0

    return round(confidence, 2)

def validation_seveso(seveso: SevesoInfo) -> list[str]:
    """Gives all the warnings from the build"""
    warnings = []

    if seveso is None:
        warnings.append("Failed to extract section15")
        return warnings

    if seveso.category is None or seveso.category == "":
        warnings.append("Missing Seveso category")

    return warnings


def confidence_seveso(seveso: SevesoInfo) -> float:
    """Gives estimate confidence from 0.0-1"""

    if seveso is None:
        return 0.0

    if seveso.category is None or seveso.category == "":
        return 0.0

    return 1.0
