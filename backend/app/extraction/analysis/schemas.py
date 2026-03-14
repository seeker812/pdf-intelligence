from pydantic import BaseModel
from typing import List, Dict


class Section(BaseModel):
    section_title: str
    section_summary: str


class Entities(BaseModel):
    people: List[str] = []
    organizations: List[str] = []
    locations: List[str] = []
    dates: List[str] = []
    monetary_values: List[str] = []
    other_entities: List[str] = []


class DocumentIntelligence(BaseModel):

    document_type: str
    category: str
    sub_category: str

    short_summary: str
    detailed_summary: str

    topics: List[str]

    entities: Entities

    key_insights: List[str]

    sections: List[Section]