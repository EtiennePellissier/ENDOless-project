"""
ENDOless PRIM - Tests d'Acceptation P0
"""

from datetime import date, datetime, timedelta
import pytest
from src.commit_service import BackendCommitService
from src.context_validator import ContextSelectionValidator
from src.models import ExtractedObservation, JournalDraft, SymptomDomain


def test_R04_unconfirmed_draft_fails_to_save():
    service = BackendCommitService()
    draft = JournalDraft(
        draft_id="d_001",
        user_id="usr_test",
        target_date=date.today(),
        observations=[],
        unreported_domains=[SymptomDomain.PAIN],
        created_at=datetime.now(),
        is_confirmed=False,  # Non confirmé
    )

    with pytest.raises(ValueError, match="non confirmé"):
        service.commit_draft(draft, commit_token="token_1")


def test_R05_idempotent_commit():
    service = BackendCommitService()
    draft = JournalDraft(
        draft_id="d_002",
        user_id="usr_test",
        target_date=date.today(),
        observations=[],
        unreported_domains=[],
        created_at=datetime.now(),
        is_confirmed=True,
    )

    r1 = service.commit_draft(draft, commit_token="token_unique")
    r2 = service.commit_draft(draft, commit_token="token_unique")

    assert r1.status == "SAVED"
    assert r2.status == "ALREADY_SAVED"


def test_R15_context_selection_limits():
    today = date.today()
    valid_rec = {
        "record_id": "r1",
        "user_id": "usr_test",
        "is_confirmed": True,
        "record_date": today - timedelta(days=2),
    }
    old_rec = {
        "record_id": "r2",
        "user_id": "usr_test",
        "is_confirmed": True,
        "record_date": today - timedelta(days=10),
    }

    # Ok avec 1 record récent
    res = ContextSelectionValidator.validate_context("usr_test", [valid_rec], today)
    assert len(res) == 1

    # Exception si record > 7 jours
    with pytest.raises(ValueError, match="dépasse la fenêtre autorisée"):
        ContextSelectionValidator.validate_context("usr_test", [old_rec], today)
