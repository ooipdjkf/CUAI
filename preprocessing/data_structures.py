from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

class RequirementType(Enum):
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    CONDITIONAL = "conditional"

@dataclass
class Requirement:
    """规范要求"""
    text_es: str
    text_zh: str = ""
    type: RequirementType = RequirementType.MANDATORY
    conditions: List[str] = field(default_factory=list)
    related_formulas: List[str] = field(default_factory=list)
    related_tables: List[str] = field(default_factory=list)

@dataclass
class Formula:
    """公式"""
    id: str
    expression: str
    variables: Dict[str, str] = field(default_factory=dict)
    context_es: str = ""
    context_zh: str = ""
    section_id: str = ""
    referenced_by: List[str] = field(default_factory=list)
    units: List[str] = field(default_factory=list)
    requirements: List[Requirement] = field(default_factory=list)

@dataclass
class Table:
    """表格"""
    id: str
    caption_es: str
    caption_zh: str = ""
    headers: List[str] = field(default_factory=list)
    data: List[List[str]] = field(default_factory=list)
    section_id: str = ""
    referenced_by: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class Section:
    """章节"""
    id: str
    title_es: str
    title_zh: str = ""
    content_es: str = ""
    content_zh: str = ""
    level: int = 1
    parent_section: Optional[str] = None
    subsections: List[str] = field(default_factory=list)
    formulas: List[Formula] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    requirements: List[Requirement] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)

@dataclass
class Document:
    """文档"""
    filename: str
    sections: Dict[str, Section] = field(default_factory=dict)
    formulas: Dict[str, Formula] = field(default_factory=dict)
    tables: Dict[str, Table] = field(default_factory=dict)
    terminology: Dict[str, str] = field(default_factory=dict)
    units: Set[str] = field(default_factory=set)
    special_symbols: Set[str] = field(default_factory=set) 