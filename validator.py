"""Этап 2 (Вариант Б): Валидация пакета data.json по контракту schema.json.
Студент: Мусин Тимур Булатович
Номер N = 69
"""
import copy
import json
import os
from typing import Any


def load_json_file(filename: str) -> dict[str, Any]:
    """Загружает JSON-файл с диска в словарь Python."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_by_schema(packet: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Проверяет пакет телеметрии по правилам из файла schema.json и бизнес-логике."""
    errors: list[str] = []
    req_fields: list[str] = schema.get("required", [])
    props: dict[str, Any] = schema.get("properties", {})

    # 1. Проверка обязательных полей верхнего уровня
    for field in req_fields:
        if field not in packet:
            errors.append(f"Отсутствует обязательное поле '{field}'")
    if errors:
        return False, errors

    # 2. Проверка давлений по границам из schema.json
    for p_field in ("p_res_mpa", "p_bhp_mpa"):
        rules = props[p_field]
        val = packet[p_field]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            errors.append(f"Поле '{p_field}' должно быть числом")
        elif not (rules["minimum"] <= float(val) <= rules["maximum"]):
            errors.append(
                f"Давление {p_field}={val} вне границ схемы [{rules['minimum']}; {rules['maximum']}]"
            )

    # 3. Проверка режима работы по списку enum из schema.json
    allowed_modes = props["mode"]["enum"]
    if packet["mode"] not in allowed_modes:
        errors.append(f"Режим mode='{packet['mode']}' не входит в enum {allowed_modes}")

    if not isinstance(packet["is_online"], bool):
        errors.append("Поле 'is_online' должно быть логическим типом (boolean)")

    # Перекрёстное физическое правило
    if isinstance(packet["p_res_mpa"], (int, float)) and isinstance(packet["p_bhp_mpa"], (int, float)):
        if packet["mode"] == "PUMPING" and float(packet["p_bhp_mpa"]) > float(packet["p_res_mpa"]):
            errors.append("Физическое противоречие: при режиме PUMPING Pзаб > Pпл!")

    # 4. Проверка массива датчиков sensors (minItems и enum единиц измерения)
    sensors_schema = props["sensors"]
    min_items = sensors_schema["minItems"]
    allowed_units = sensors_schema["items"]["properties"]["unit"]["enum"]
    sensors = packet["sensors"]

    if not isinstance(sensors, list) or len(sensors) < min_items:
        errors.append(f"Массив 'sensors' должен содержать минимум {min_items} датчика")
    else:
        for idx, item in enumerate(sensors):
            if not isinstance(item, dict):
                errors.append(f"Датчик #{idx} должен быть объектом (dict)")
                continue
            for s_req in sensors_schema["items"]["required"]:
                if s_req not in item:
                    errors.append(f"В датчике #{idx} отсутствует поле '{s_req}'")
            if "unit" in item and item["unit"] not in allowed_units:
                errors.append(
                    f"Датчик #{idx}: единица '{item['unit']}' не входит в enum {allowed_units}"
                )
            if "value" in item and (
                not isinstance(item["value"], (int, float)) or isinstance(item["value"], bool)
            ):
                errors.append(f"Датчик #{idx}: поле 'value' должно быть числом")

    return len(errors) == 0, errors


if __name__ == "__main__":
    schema_doc = load_json_file("schema.json")
    valid_pkt = load_json_file("data.json")

    print("=" * 66)
    print("ЗАПУСК ПРОВЕРКИ КОНТРАКТА ДАННЫХ ПО ФАЙЛУ schema.json (Вариант Б)")
    print("=" * 66)

    # Сценарий 1: Эталонный пакет из data.json
    ok1, errs1 = validate_by_schema(valid_pkt, schema_doc)
    print(f"\n[Сценарий 1] Эталонный файл data.json -> {'УСПЕШНО (VALID)' if ok1 else 'ОШИБКА'}")

    # Сценарий 2: Нарушение enum режима и единицы измерения датчика
    bad_enum = copy.deepcopy(valid_pkt)
    bad_enum["mode"] = "OVERDRIVE"
    bad_enum["sensors"][0]["unit"] = "psi"
    ok2, errs2 = validate_by_schema(bad_enum, schema_doc)
    print(f"\n[Сценарий 2] Нарушение списков enum -> {'УСПЕШНО' if ok2 else 'ОТКЛОНЕНО'}")
    for e in errs2:
        print(f" x {e}")

    # Сценарий 3: Слишком мало датчиков в массиве (меньше minItems: 2)
    too_few = copy.deepcopy(valid_pkt)
    too_few["sensors"] = [valid_pkt["sensors"][0]]
    ok3, errs3 = validate_by_schema(too_few, schema_doc)
    print(
        f"\n[Сценарий 3] Только 1 датчик в массиве sensors -> {'УСПЕШНО' if ok3 else 'ОТКЛОНЕНО'}"
    )
    for e in errs3:
        print(f" x {e}")

    # Сценарий 4: Физическое противоречие давлений при PUMPING (Pзаб > Pпл)
    bad_phys = copy.deepcopy(valid_pkt)
    bad_phys["mode"] = "PUMPING"
    bad_phys["p_bhp_mpa"] = 50.0
    bad_phys["p_res_mpa"] = 20.0
    ok4, errs4 = validate_by_schema(bad_phys, schema_doc)
    print(
        f"\n[Сценарий 4] Противоречие давлений (Pзаб > Pпл) -> {'УСПЕШНО' if ok4 else 'ОТКЛОНЕНО'}"
    )
    for e in errs4:
        print(f" x {e}")

    # Сценарий 5 (Челлендж № 2): «Слепая проверка: найди диверсию в JSON» (broken_data.json)
    if os.path.exists("broken_data.json"):
        broken_pkt = load_json_file("broken_data.json")
        ok5, errs5 = validate_by_schema(broken_pkt, schema_doc)
        print(
            f"\n[Сценарий 5] Челлендж № 2: broken_data.json -> {'УСПЕШНО' if ok5 else 'ОТКЛОНЕНО'}"
        )
        for e in errs5:
            print(f" x {e}")
