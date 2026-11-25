from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models import PatientCreate
from app.repository import ClinicRepository, timestamp


@pytest.fixture
def repository(tmp_path: Path) -> ClinicRepository:
    repository = ClinicRepository(tmp_path / "clinic.sqlite3")
    repository.initialize()
    # Минимальный независимый набор для тестов; не зависит от демонстрационного наполнения.
    future = (datetime.now(UTC) + timedelta(days=2)).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    past = future - timedelta(days=3)
    with repository._connect() as connection:
        connection.execute("INSERT INTO clinics VALUES (1, 'Поликлиника №01', 'ул. Учебная, д. 1')")
        connection.execute(
            "INSERT INTO clinics VALUES (2, 'Поликлиника №02', 'ул. Парковая, д. 2')"
        )
        connection.execute(
            "INSERT INTO doctors VALUES (1, 1, 'Соколова Анна Сергеевна', 'Терапевт')"
        )
        connection.execute("INSERT INTO doctors VALUES (2, 1, 'Орлов Иван Петрович', 'Кардиолог')")
        connection.execute("INSERT INTO doctors VALUES (3, 2, 'Белов Игорь Олегович', 'Терапевт')")
        starts = [
            future,
            future,
            future + timedelta(minutes=15),
            future + timedelta(minutes=30),
            past,
            past + timedelta(hours=1),
        ]
        doctor_ids = [1, 2, 3, 1, 1, 2]
        connection.executemany(
            "INSERT INTO slots (id, doctor_id, starts_at, ends_at) VALUES (?, ?, ?, ?)",
            [
                (index, doctor_id, timestamp(start), timestamp(start + timedelta(minutes=30)))
                for index, (doctor_id, start) in enumerate(
                    zip(doctor_ids, starts, strict=True), start=1
                )
            ],
        )
    repository.create_patient(PatientCreate(full_name="Иванов Иван", birth_date="1990-01-01"))
    repository.create_patient(PatientCreate(full_name="Петрова Анна", birth_date="1995-05-10"))
    return repository


@pytest.fixture
def client(repository: ClinicRepository) -> Iterator[TestClient]:
    with TestClient(create_app(repository.database_path), base_url="http://127.0.0.1") as client:
        yield client


@pytest.fixture
def past_appointment(repository: ClinicRepository) -> int:
    # Прошедшую запись нельзя создать через API; она могла быть создана до начала приёма.
    with repository._connect() as connection:
        cursor = connection.execute(
            "INSERT INTO appointments (slot_id, patient_id, created_at) VALUES (5, 1, ?)",
            (timestamp(datetime.now(UTC) - timedelta(days=3)),),
        )
        assert cursor.lastrowid is not None
        return cursor.lastrowid
