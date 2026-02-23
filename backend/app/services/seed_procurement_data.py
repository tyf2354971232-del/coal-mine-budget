"""Seed data for Tajikistan procurement records (塔国采购物资决算分项).

Parses 12 monthly txt files from project root directory.
Total: 34,920,691.80 索莫尼 (2025年1-12月)
"""
import os
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.procurement import ProcurementRecord, ProcurementMonthlySummary

MONTHLY_TOTALS_SOMONI = {
    1: 461410.65,
    2: 434575.65,
    3: 839301.50,
    4: 369855.85,
    5: 2610990.90,
    6: 553355.00,
    7: 1550071.40,
    8: 2976305.27,
    9: 1818037.45,
    10: 8483008.83,
    11: 5088279.35,
    12: 9735499.95,
}

MONTH_NAMES = {
    1: "1月", 2: "2月", 3: "3月", 4: "4月",
    5: "5月", 6: "6月", 7: "7月", 8: "8月",
    9: "9月", 10: "10月", 11: "11月", 12: "12月",
}


def _parse_number(s: str):
    """Parse a number string, handling commas and whitespace."""
    if not s:
        return None
    s = s.strip().replace(",", "").replace(" ", "").replace("\u00a0", "")
    if not s or s == "-":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _find_data_file(month: int):
    """Locate the monthly procurement txt file."""
    filename = f"集团域外企业物资采购情况统计表{MONTH_NAMES[month]}.txt"
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


def _parse_monthly_file(filepath: str, month: int) -> list[dict]:
    """Parse a single monthly procurement txt file."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_rows = 4
    for line in lines[header_rows:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 10:
            continue

        seq_str = parts[0].strip()
        if not seq_str or not re.match(r"^\d+$", seq_str):
            if "合计" in line or "填报人" in line or "联系电话" in line:
                continue
            continue

        seq = int(seq_str)
        material_name = parts[2].strip() if len(parts) > 2 else ""
        specification = parts[3].strip() if len(parts) > 3 else ""
        plan_price = _parse_number(parts[4]) if len(parts) > 4 else None
        plan_quantity = _parse_number(parts[5]) if len(parts) > 5 else None
        unit = parts[6].strip() if len(parts) > 6 else ""
        purchase_unit_price_somoni = _parse_number(parts[7]) if len(parts) > 7 else None
        purchase_method = parts[8].strip() if len(parts) > 8 else ""
        payment_method = parts[9].strip() if len(parts) > 9 else ""
        purchase_quantity = _parse_number(parts[10]) if len(parts) > 10 else None
        purchase_amount_somoni = _parse_number(parts[11]) if len(parts) > 11 else None
        stock_quantity = _parse_number(parts[12]) if len(parts) > 12 else None
        unit_price_rmb = _parse_number(parts[13]) if len(parts) > 13 else None
        amount_rmb = _parse_number(parts[14]) if len(parts) > 14 else None
        usage_unit = parts[15].strip() if len(parts) > 15 else ""
        project_name = parts[16].strip() if len(parts) > 16 else ""

        if not material_name:
            continue

        records.append({
            "month": month,
            "seq": seq,
            "material_name": material_name,
            "specification": specification,
            "unit": unit,
            "plan_price": plan_price,
            "plan_quantity": plan_quantity,
            "purchase_unit_price_somoni": purchase_unit_price_somoni,
            "purchase_method": purchase_method,
            "payment_method": payment_method,
            "purchase_quantity": purchase_quantity,
            "purchase_amount_somoni": purchase_amount_somoni,
            "stock_quantity": stock_quantity,
            "unit_price_rmb": unit_price_rmb,
            "amount_rmb": amount_rmb,
            "usage_unit": usage_unit,
            "project_name": project_name,
        })

    return records


async def seed_procurement_data(db: AsyncSession):
    """Parse 12 monthly files and insert procurement records + monthly summaries."""
    result = await db.execute(select(ProcurementMonthlySummary).limit(1))
    if result.scalar_one_or_none():
        return

    # Monthly summaries
    for month, total in MONTHLY_TOTALS_SOMONI.items():
        db.add(ProcurementMonthlySummary(month=month, amount_somoni=total))

    # Parse each monthly file
    total_records = 0
    for month in range(1, 13):
        filepath = _find_data_file(month)
        if not filepath:
            print(f"[WARN] Procurement file for month {month} not found, skipping")
            continue

        records = _parse_monthly_file(filepath, month)
        for rec in records:
            db.add(ProcurementRecord(**rec))
        total_records += len(records)
        print(f"  Month {month}: {len(records)} records from {os.path.basename(filepath)}")

    await db.flush()
    print(f"[OK] Seeded: 12 monthly summaries, {total_records} procurement detail records")
