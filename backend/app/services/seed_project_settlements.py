"""Seed settlement/expenditure data for 矿建工程, 安装工程, 设备购置, 其他费用.

All amounts in 万元 unless otherwise noted.
"""
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import SubProject
from app.models.budget import BudgetCategory, Expenditure

# ── 矿建工程 决算数据 (total spent: 6979.47 万元) ──
MINING_SETTLEMENT_DATA = [
    {
        "name": "+810m水平回风大巷",
        "budget": 3600,
        "spent": 3600,
        "sub_project_match": "810水平回风大巷(维修)",
        "l2_code": "MJ-02",
    },
    {
        "name": "回风斜井",
        "budget": 780,
        "spent": 780,
        "sub_project_match": "回风斜井(维修)",
        "l2_code": "MJ-02",
    },
    {
        "name": "+878-810m回风斜巷",
        "budget": 546,
        "spent": 526,
        "sub_project_match": "878-810回风斜巷 α=30°",
        "l2_code": "MJ-02",
    },
    {
        "name": "+810m运输大巷",
        "budget": 1275,
        "spent": 1255,
        "sub_project_match": "810运输大巷(维修)",
        "l2_code": "MJ-02",
    },
    {
        "name": "+878m片盘联巷",
        "budget": 198,
        "spent": 188,
        "sub_project_match": "878片盘联巷",
        "l2_code": "MJ-02",
    },
    {
        "name": "+810m大巷至装载硐室",
        "budget": 307.5,
        "spent": 299.47,
        "sub_project_match": "井底车场(维修)",
        "l2_code": "MJ-01",
    },
    {
        "name": "+810m主井底向副井绕巷",
        "budget": 247.5,
        "spent": 212.5,
        "sub_project_match": "810至878回风联巷(维修)",
        "l2_code": "MJ-01",
    },
    {
        "name": "风井联巷20",
        "budget": 133.5,
        "spent": 118.5,
        "sub_project_match": "铺轨",
        "l2_code": "MJ-02",
    },
]

# ── 安装工程 决算数据 ──
INSTALLATION_SETTLEMENT_DATA = [
    {
        "name": "降压站",
        "budget": 3525.9,
        "spent": 2955.04,
        "sub_project_match": "110KV降压站EPC",
        "l2_code": "AZ-11",
    },
]

# ── 设备购置 决算数据 ──
EQUIPMENT_SETTLEMENT_DATA = [
    {
        "name": "设备购置",
        "budget": 1216,
        "spent": 1304.28,
        "sub_project_match": "设备购置",
        "l1_code": "SB",
    },
]

# ── 其他基建 决算数据 (total budget: 3060, spent: 1612, balance: 1448) ──
OTHER_SETTLEMENT_DATA = [
    {
        "name": "建设单位管理费",
        "spent": 1440,
        "sub_project_match": "建设单位管理费",
        "l2_code": "QT-01",
    },
    {
        "name": "其他基建-设备",
        "spent": 172,
        "sub_project_match": "国内运费、国际运费及清关等费用",
        "l2_code": "QT-03",
    },
]


async def seed_project_settlements(db: AsyncSession):
    """Create expenditure records for mining, installation, equipment, and other settlements."""
    check = await db.execute(
        select(Expenditure).where(Expenditure.source == "mining_settlement").limit(1)
    )
    if check.scalar_one_or_none():
        return

    sp_result = await db.execute(select(SubProject))
    sp_map = {sp.name: sp for sp in sp_result.scalars().all()}

    cat_result = await db.execute(select(BudgetCategory))
    all_cats = cat_result.scalars().all()
    l2_code_map = {cat.code: cat for cat in all_cats if cat.level == 2}
    l1_code_map = {cat.code: cat for cat in all_cats if cat.level == 1}

    record_date = datetime.date(2025, 12, 31)
    exp_count = 0

    # ── 矿建工程 ──
    for item in MINING_SETTLEMENT_DATA:
        sp = sp_map.get(item["sub_project_match"])
        if not sp:
            continue
        l2_cat = l2_code_map.get(item["l2_code"])
        amount = item["spent"]

        sp.actual_spent = round(amount, 2)
        if amount >= item.get("budget", amount):
            sp.status = "completed"
            sp.progress_percent = 100
        else:
            sp.status = "in_progress"
            sp.progress_percent = round(amount / item["budget"] * 100, 1) if item.get("budget") else 0

        expenditure = Expenditure(
            sub_project_id=sp.id,
            category_id=l2_cat.id if l2_cat else None,
            record_date=record_date,
            amount=amount,
            description=f"矿建决算-{item['name']}",
            source="mining_settlement",
        )
        db.add(expenditure)
        exp_count += 1

    # ── 安装工程 ──
    for item in INSTALLATION_SETTLEMENT_DATA:
        sp = sp_map.get(item["sub_project_match"])
        if not sp:
            continue
        l2_cat = l2_code_map.get(item["l2_code"])
        amount = item["spent"]

        sp.actual_spent = round(amount, 2)
        sp.status = "in_progress"
        sp.progress_percent = round(amount / item["budget"] * 100, 1) if item.get("budget") else 0

        expenditure = Expenditure(
            sub_project_id=sp.id,
            category_id=l2_cat.id if l2_cat else None,
            record_date=record_date,
            amount=amount,
            description=f"安装决算-{item['name']}",
            source="installation_settlement",
        )
        db.add(expenditure)
        exp_count += 1

    # ── 设备购置 ──
    for item in EQUIPMENT_SETTLEMENT_DATA:
        sp = sp_map.get(item["sub_project_match"])
        if not sp:
            continue
        l1_cat = l1_code_map.get(item.get("l1_code"))
        amount = item["spent"]

        sp.actual_spent = round(amount, 2)
        sp.status = "in_progress"
        sp.progress_percent = round(amount / sp.allocated_budget * 100, 1) if sp.allocated_budget > 0 else 0

        expenditure = Expenditure(
            sub_project_id=sp.id,
            category_id=l1_cat.id if l1_cat else None,
            record_date=record_date,
            amount=amount,
            description=f"设备决算-{item['name']}",
            source="equipment_settlement",
        )
        db.add(expenditure)
        exp_count += 1

    # ── 其他费用 ──
    for item in OTHER_SETTLEMENT_DATA:
        sp = sp_map.get(item["sub_project_match"])
        if not sp:
            continue
        l2_cat = l2_code_map.get(item.get("l2_code"))
        amount = item["spent"]

        sp.actual_spent = round(amount, 2)
        sp.status = "in_progress"
        sp.progress_percent = round(amount / sp.allocated_budget * 100, 1) if sp.allocated_budget > 0 else 0

        expenditure = Expenditure(
            sub_project_id=sp.id,
            category_id=l2_cat.id if l2_cat else None,
            record_date=record_date,
            amount=amount,
            description=f"其他决算-{item['name']}",
            source="other_settlement",
        )
        db.add(expenditure)
        exp_count += 1

    await db.flush()

    mining_total = sum(i["spent"] for i in MINING_SETTLEMENT_DATA)
    install_total = sum(i["spent"] for i in INSTALLATION_SETTLEMENT_DATA)
    equip_total = sum(i["spent"] for i in EQUIPMENT_SETTLEMENT_DATA)
    other_total = sum(i["spent"] for i in OTHER_SETTLEMENT_DATA)
    print(
        f"[OK] Seeded project settlements: {exp_count} expenditures "
        f"(矿建 {mining_total:.2f}, 安装 {install_total:.2f}, "
        f"设备 {equip_total:.2f}, 其他 {other_total:.2f} 万元)"
    )
