"""Seed data for warehouse outbound records (来塔物资全年出库决算分项).

Parses 来塔物资全年出库决算分项.txt from project root directory.
~3400+ records of materials shipped from China to Tajikistan.
"""
import os
import re
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.procurement import WarehouseOutbound


def _parse_number(s: str):
    if not s:
        return None
    s = s.strip().replace(",", "").replace(" ", "").replace("\u00a0", "")
    if not s or s == "-" or s == "/":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def _find_data_file():
    filename = "来塔物资全年出库决算分项.txt"
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        p = os.path.join(data_dir, filename)
        if os.path.exists(p):
            return p
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    project_root = os.path.dirname(base_dir)
    for d in [project_root, base_dir]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None


def _parse_outbound_file(filepath: str) -> list[dict]:
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip 2 header rows
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 10:
            continue

        team = parts[0].strip() if len(parts) > 0 else ""
        apply_date = _parse_date(parts[1]) if len(parts) > 1 else None
        material_type = parts[2].strip() if len(parts) > 2 else ""
        material_code = parts[3].strip() if len(parts) > 3 else ""
        material_name = parts[4].strip() if len(parts) > 4 else ""
        specification = parts[5].strip() if len(parts) > 5 else ""
        unit = parts[6].strip() if len(parts) > 6 else ""
        quantity = _parse_number(parts[7]) if len(parts) > 7 else None
        unit_price = _parse_number(parts[8]) if len(parts) > 8 else None
        amount = _parse_number(parts[9]) if len(parts) > 9 else None
        usage_unit = parts[10].strip() if len(parts) > 10 else ""
        project_name = parts[11].strip() if len(parts) > 11 else ""

        if not material_name:
            continue

        records.append({
            "team": team,
            "apply_date": apply_date,
            "material_type": material_type,
            "material_code": material_code,
            "material_name": material_name,
            "specification": specification,
            "unit": unit,
            "quantity": quantity,
            "unit_price": unit_price,
            "amount": amount,
            "usage_unit": usage_unit,
            "project_name": project_name,
        })

    return records


async def seed_warehouse_outbound(db: AsyncSession):
    """Parse outbound file and insert warehouse outbound records."""
    result = await db.execute(select(WarehouseOutbound).limit(1))
    if result.scalar_one_or_none():
        return

    filepath = _find_data_file()
    if not filepath:
        print("[WARN] 来塔物资全年出库决算分项.txt not found, skipping")
        return

    records = _parse_outbound_file(filepath)
    for rec in records:
        db.add(WarehouseOutbound(**rec))

    await db.flush()
    total_amount = sum(r["amount"] or 0 for r in records)
    print(f"[OK] Seeded: {len(records)} warehouse outbound records, total {total_amount:.2f} 元")
