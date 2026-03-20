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
class ProcessingMetadata:
    """Class para info sobre como o documento foi processado"""
    extraction_method : Optional[str] #vai me dizer se extraiu com regex/llm/hybrid
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
    metadata : Optional[ProcessingMetadata]
