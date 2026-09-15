import pytest
from pydantic import ValidationError
from app.models import PhoneNumber, PhoneNumberCreate, PhoneStatus


def test_phone_status_are_stringuri():
    assert PhoneStatus.AVAILABLE == "AVAILABLE"
    assert PhoneStatus.RESERVED == "RESERVED"
    assert PhoneStatus.ACTIVE == "ACTIVE"
    assert PhoneStatus.RELEASED == "RELEASED"


def test_phone_number_create_necesita_campuri():
    with pytest.raises(ValidationError):
        PhoneNumberCreate()  # type: ignore


def test_phone_number_are_valori_implicite_corecte():
    n = PhoneNumber(id=1, e164="+14155550101", country_code="US", current_carrier="Verizon")
    assert n.status == PhoneStatus.AVAILABLE
    assert n.version == 1
    assert n.customer_id is None
    assert n.signature is None


def test_phone_number_model_copy_actualizeaza_status():
    n = PhoneNumber(id=1, e164="+14155550101", country_code="US", current_carrier="Verizon")
    updated = n.model_copy(update={"status": PhoneStatus.RESERVED, "version": 2})
    assert updated.status == PhoneStatus.RESERVED
    assert updated.version == 2
    assert n.status == PhoneStatus.AVAILABLE  # originalul neschimbat
