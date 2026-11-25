"""Вымышленные данные. Вызывается только для полностью пустой базы."""

import sqlite3
from datetime import UTC, date, datetime, time, timedelta

from app.models import LOCAL_TIMEZONE
from app.repository import timestamp


def populate_demo(connection: sqlite3.Connection, *, today: date) -> None:
    streets = ("Учебная", "Солнечная", "Парковая", "Зелёная", "Центральная")
    surnames = (
        "Соколова",
        "Морозов",
        "Волкова",
        "Орлов",
        "Лебедева",
        "Зайцев",
        "Павлова",
        "Новиков",
        "Петрова",
        "Фёдоров",
    )
    given_names = (
        "Анна Сергеевна",
        "Алексей Игоревич",
        "Мария Андреевна",
        "Дмитрий Олегович",
        "Елена Викторовна",
        "Иван Петрович",
        "Наталья Игоревна",
        "Павел Сергеевич",
        "Ирина Олеговна",
        "Сергей Андреевич",
    )
    now = datetime.now(UTC)
    connection.executemany(
        "INSERT INTO clinics (id, name, address) VALUES (?, ?, ?)",
        [
            (number, f"Поликлиника №{number:02d}", f"ул. {streets[(number - 1) % 5]}, д. {number}")
            for number in range(1, 6)
        ],
    )
    doctors = []
    for clinic_id in range(1, 6):
        for offset, specialty in enumerate(("Терапевт", "Кардиолог")):
            doctor_id = (clinic_id - 1) * 2 + offset + 1
            index = doctor_id - 1
            full_name = f"{surnames[index]} {given_names[index]}"
            doctors.append((doctor_id, clinic_id, full_name, specialty))
    connection.executemany(
        "INSERT INTO doctors (id, clinic_id, full_name, specialty) VALUES (?, ?, ?, ?)", doctors
    )
    patients = (
        ("Александрова Ольга Игоревна", "1991-04-12", "+7 (900) 000-00-01"),
        ("Белов Михаил Андреевич", "1985-09-23", "+7 (900) 000-00-02"),
        ("Васильева Ирина Павловна", "1974-01-30", ""),
        ("Громов Артём Сергеевич", "2001-07-15", "+7 (900) 000-00-04"),
        ("Данилова Екатерина Олеговна", "1998-11-06", "+7 (900) 000-00-05"),
        ("Егоров Павел Викторович", "1969-03-18", ""),
    )
    connection.executemany(
        "INSERT INTO patients (full_name, birth_date, phone, created_at) VALUES (?, ?, ?, ?)",
        [(*patient, timestamp(now - timedelta(days=10))) for patient in patients],
    )
    # У каждого врача — шесть получасовых слотов в день: вчера, сегодня и 14 дней вперёд.
    slots = []
    for doctor_id, *_ in doctors:
        for day_offset in range(-1, 15):
            day = today + timedelta(days=day_offset)
            for hour, minute in ((9, 0), (9, 30), (10, 0), (10, 30), (14, 0), (14, 30)):
                start = datetime.combine(day, time(hour, minute), LOCAL_TIMEZONE)
                slots.append(
                    (doctor_id, timestamp(start), timestamp(start + timedelta(minutes=30)))
                )
    connection.executemany(
        "INSERT INTO slots (doctor_id, starts_at, ends_at) VALUES (?, ?, ?)", slots
    )

    def slot_id(doctor_id: int, day_offset: int, hour: int, minute: int = 0) -> int:
        start = datetime.combine(
            today + timedelta(days=day_offset), time(hour, minute), LOCAL_TIMEZONE
        )
        return connection.execute(
            "SELECT id FROM slots WHERE doctor_id = ? AND starts_at = ?",
            (doctor_id, timestamp(start)),
        ).fetchone()[0]

    connection.executemany(
        """
        INSERT INTO appointments (slot_id, patient_id, status, note, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                slot_id(1, -1, 9),
                1,
                "completed",
                "Плановый приём. Жалобы и рекомендации внесены в учебную медицинскую карту.",
                timestamp(now - timedelta(days=3)),
                timestamp(datetime.combine(today - timedelta(days=1), time(9, 30), LOCAL_TIMEZONE)),
            ),
            (slot_id(2, -1, 10), 2, "scheduled", "", timestamp(now - timedelta(days=3)), None),
            (slot_id(1, 1, 9), 3, "scheduled", "", timestamp(now - timedelta(hours=2)), None),
            (slot_id(2, 1, 9, 30), 1, "scheduled", "", timestamp(now - timedelta(hours=1)), None),
            (slot_id(3, 2, 10), 4, "scheduled", "", timestamp(now), None),
            (slot_id(1, 1, 10), 5, "cancelled", "", timestamp(now - timedelta(hours=3)), None),
        ],
    )
    connection.executemany(
        "INSERT INTO lab_results (patient_id, study_name, result, received_at) VALUES (?, ?, ?, ?)",
        [
            (
                1,
                "Общий анализ крови",
                "Гемоглобин: 132 г/л. Лейкоциты: 5,6 × 10⁹/л.",
                timestamp(now - timedelta(days=2)),
            ),
            (1, "Глюкоза крови", "Глюкоза: 4,8 ммоль/л.", timestamp(now - timedelta(days=1))),
            (
                2,
                "Липидный профиль",
                "Общий холестерин: 4,5 ммоль/л.",
                timestamp(now - timedelta(days=3)),
            ),
        ],
    )
