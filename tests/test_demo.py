from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from app.models import AppointmentStatus, PatientCreate, local_today
from app.repository import ClinicRepository


def test_demo_has_all_branches_and_working_scenarios(tmp_path: Path) -> None:
    repository = ClinicRepository(tmp_path / "demo.sqlite3")
    repository.initialize()
    assert repository.seed_demo()
    assert len(repository.list_clinics()) == 5
    assert len(repository.list_patients()) == 6
    assert len(repository.list_appointments()) == 6
    for clinic in repository.list_clinics():
        assert len(repository.list_doctors(clinic.id)) == 2
        slots = repository.list_slots(clinic.id, local_today() + timedelta(days=1))
        assert len(slots) == 12
        assert any(slot.is_available for slot in slots)
    assert len(repository.list_lab_results(1)) == 2
    assert {appointment.status for appointment in repository.list_appointments()} == set(
        AppointmentStatus
    )


def test_demo_does_not_duplicate_or_reset_data(tmp_path: Path) -> None:
    repository = ClinicRepository(tmp_path / "demo.sqlite3")
    repository.initialize()
    repository.seed_demo()
    scheduled = next(
        a for a in repository.list_appointments() if a.status == AppointmentStatus.SCHEDULED
    )
    repository.cancel(scheduled.id)
    before = repository.list_appointments()
    repository.initialize()
    assert not repository.seed_demo()
    assert repository.list_appointments() == before
    assert len(repository.list_patients()) == 6


def test_demo_skips_partially_filled_database(tmp_path: Path) -> None:
    repository = ClinicRepository(tmp_path / "partial.sqlite3")
    repository.initialize()
    repository.create_patient(PatientCreate(full_name="Свой пациент", birth_date="1990-01-01"))
    assert not repository.seed_demo()
    assert len(repository.list_patients()) == 1
    assert repository.list_clinics() == []


def test_empty_and_demo_pages(tmp_path: Path) -> None:
    with TestClient(create_app(tmp_path / "empty.sqlite3"), base_url="http://127.0.0.1") as client:
        for path, message in (
            ("/", "Расписание пока не подготовлено"),
            ("/patients", "Пациентов пока нет"),
            ("/appointments", "Записей пока нет"),
        ):
            response = client.get(path)
            assert response.status_code == 200
            assert message in response.text
    with TestClient(
        create_app(tmp_path / "demo.sqlite3", demo=True), base_url="http://127.0.0.1"
    ) as client:
        for path in (
            "/",
            "/?clinic_id=5",
            "/patients",
            "/patients/1",
            "/patients/6",
            "/appointments",
            "/appointments/1",
        ):
            assert client.get(path).status_code == 200
        assert "Общий анализ крови" in client.get("/patients/1").text
        assert "Плановый приём" in client.get("/patients/1").text


def test_boundary_dates_have_no_schedule(tmp_path: Path) -> None:
    with TestClient(
        create_app(tmp_path / "demo.sqlite3", demo=True), base_url="http://127.0.0.1"
    ) as client:
        for day in ("0001-01-01", "9999-12-31"):
            response = client.get("/api/slots", params={"clinic_id": 1, "date": day})
            assert response.status_code == 200
            assert response.json() == []
