from dataclasses import dataclass
from typing import Optional


@dataclass
class Section:
    """Class para raepresentar uma secção do PDF"""
    section_number : Optional[int]
    title : Optional[str]
    raw_text : str

@dataclass
class Substance:
    """Class para representar uma substância quimica"""
    name : str
    cas_number : Optional[str]
    percentage : Optional[str]


@dataclass
class Hazard:
    """Class para representar os perigos / classificações"""
    code : Optional[str]
    description : Optional[str]

@dataclass
class PhysicalProperties:
    state: Optional[str]
    density: Optional[float]
    flash_point: Optional[str]
    voc: Optional[str]

@dataclass
class TransportInfo:
    un_number: Optional[str]
    shipping_name: Optional[str]
    hazard_class: Optional[str]
    packing_group: Optional[str]
    environmental_hazard: Optional[bool]

@dataclass
class SevesoInfo:
    category: Optional[str]  

@dataclass
class ProcessingMetadata:
    """Class para info sobre como o documento foi processado"""
    extraction_method : Optional[str]
    warnings : list[str]
    confidence : Optional[float]


@dataclass
class SDSDocument:
    """Class para representar o documento inteiro"""
    file_name : str
    language : Optional[str]
    sections : list[Section]
    substances : list[Substance]
    hazards : list[Hazard]
    transport: Optional[TransportInfo]
    seveso: Optional[SevesoInfo]
    physical_properties: Optional[PhysicalProperties]
    splitter_metadata : Optional[ProcessingMetadata]
    substances_metadata : Optional[ProcessingMetadata]
    hazards_metadata : Optional[ProcessingMetadata]
    transport_metadata : Optional[ProcessingMetadata]
    seveso_metadata : Optional[ProcessingMetadata]
    physical_properties_metadata : Optional[ProcessingMetadata]
    
