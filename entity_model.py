"""Этап 1 (Вариант Б): Моделирование пакета телеметрии куста, сохранение и чтение JSON.
Студент: Мусин Тимур Булатович
Номер N = 69
"""
import json
from typing import Any


def build_telemetry_packet() -> dict[str, Any]:
    """Формирует пакет телеметрии со списком датчиков по индивидуальным числам студента."""
    # N = 69
    # pad_id = PAD-19
    # well_id = W-269
    # p_res_mpa = 26.5 МПа
    # p_bhp_mpa = 15.6 МПа
    # mode = PUMPING
    # temp_c = 58.5 C
    # rate_m3d = 136.0 m3/d
    # Челлендж № 1: булево поле is_online и 3-й датчик устьевого давления P-01 (14.0 MPa)
    return {
        "pad_id": "PAD-19",
        "well_id": "W-269",
        "p_res_mpa": 26.5,
        "p_bhp_mpa": 15.6,
        "mode": "PUMPING",
        "is_online": True,
        "sensors": [
            {"code": "T-01", "value": 58.5, "unit": "C"},
            {"code": "Q-01", "value": 136.0, "unit": "m3/d"},
            {"code": "P-01", "value": 14.0, "unit": "MPa"},
        ],
    }


def save_to_json(data: dict[str, Any], filename: str = "data.json") -> None:
    """Сериализует пакет телеметрии в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_from_json(filename: str = "data.json") -> dict[str, Any]:
    """Читает JSON-файл с диска обратно в словарь Python."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def print_telemetry_summary(packet: dict[str, Any]) -> None:
    """Выводит сводку по пакету телеметрии и считает депрессию на пласт."""
    drawdown = packet["p_res_mpa"] - packet["p_bhp_mpa"]
    online_str = "В сети" if packet.get("is_online") else "Не в сети"
    print("=" * 58)
    print(f"ПАКЕТ ТЕЛЕМЕТРИИ: Куст {packet['pad_id']} | Скважина {packet['well_id']}")
    print("=" * 58)
    print(f"Статус соединения: {online_str} (is_online={packet.get('is_online')})")
    print(f"Режим работы: {packet['mode']}")
    print(
        f"Давления: Pпл = {packet['p_res_mpa']} МПа, Pзаб = {packet['p_bhp_mpa']} МПа (dP = {drawdown:.2f} МПа)"
    )
    print(f"Опрошено датчиков: {len(packet['sensors'])} шт.")
    for s in packet["sensors"]:
        print(f" -> Датчик {s['code']}: {s['value']} {s['unit']}")
    print("=" * 58)


if __name__ == "__main__":
    # 1. Формируем структуру в памяти Python
    pkt = build_telemetry_packet()

    # 2. Сериализация в файл data.json
    save_to_json(pkt, "data.json")
    print("[OK] Файл 'data.json' успешно записан на диск!")

    # 3. Десериализация и проверка корректности
    loaded_pkt = load_from_json("data.json")
    assert loaded_pkt == pkt, "Ошибка: данные при чтении JSON исказились!"
    print("[OK] Обратное чтение через json.load() прошло успешно!\n")

    # 4. Вывод инженерной сводки
    print_telemetry_summary(loaded_pkt)
