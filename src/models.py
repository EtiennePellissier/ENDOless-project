"""
ENDOless PRIM - Data Models
Définition des structures de données pour les brouillons, observations et résumés de consultation.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SymptomDomain(str, Enum):
    PAIN = "pain"
    FATIGUE = "fatigue"
    SLEEP = "sleep_disturbance"
    MOOD = "mood"
    MENSTRUAL = "menstrual_bleeding"
    DAILY_IMPACT = "daily_impact"
    CONTEXT_NOTE = "context_note"


class ExtractedObservation(BaseModel):
    concept_key: SymptomDomain
    assertion: str = Field(..., regex="^(reported|explicitly_absent|unknown)$")
    value: Optional[Any] = None
    unit: Optional[str] = None
    event_date: Optional[date] = None
    time_label: Optional[str] = None
    source_excerpt: str


class JournalDraft(BaseModel):
    draft_id: str
    user_id: str
    target_date: date
    observations: List[ExtractedObservation]
    unreported_domains: List[SymptomDomain]
    created_at: datetime
    is_confirmed: bool = False


class CommitReceipt(BaseModel):
    status: str
    receipt_id: str
    timestamp: datetime
    record_id: str
