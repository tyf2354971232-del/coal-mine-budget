"""Seed data for civil engineering settlement (土建工程决算).

Source: 按审核金额的80%开票入账金额 table (图1).
Total: 27,674,649.32 元
"""
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import SubProject
from app.models.budget import BudgetCategory, Expenditure
from app.models.procurement import CivilSettlement

# sub-project name -> L2 budget category code (土建工程 children)
_SP_TO_L2_CODE = {
    "主井井架维修加固": "TJ-01",
    "主井提升机房": "TJ-01",
    "新增主井提升机房配电室": "TJ-01",
    "新建副井井架": "TJ-01",
    "新建副井提升机房": "TJ-01",
    "新建副井提升机房配电室": "TJ-01",
    "新建副井井口房": "TJ-02",
    "筛分楼": "TJ-02",
    "煤场(已完)": "TJ-02",
    "新建6KV变电所": "TJ-03",
    "110KV变电站": "TJ-03",
    "场外道路": "TJ-04",
    "窄轨铁路": "TJ-04",
    "运煤道路": "TJ-04",
    "锅炉房": "TJ-05",
    "新建综机车间": "TJ-06",
    "室外龙门吊车基础": "TJ-06",
    "综机广场硬化": "TJ-06",
    "电机车充电室": "TJ-06",
    "电机车充电室配电房": "TJ-06",
    "材料库(电缆、配件)": "TJ-06",
    "简易材料大棚": "TJ-06",
    "新建灯房浴室联合建筑": "TJ-07",
    "滤油池": "TJ-07",
    "临时澡堂": "TJ-07",
    "职工宿舍6栋": "TJ-07",
    "厂区大门": "TJ-07",
    "公共卫生间": "TJ-07",
    "化粪池": "TJ-07",
    "场内道路": "TJ-08",
    "排水沟": "TJ-08",
    "综合支架(钢结构)": "TJ-08",
    "工广围挡": "TJ-08",
    "矿井水再利用工程": "TJ-08",
    "主副井广场硬化": "TJ-08",
    "综合楼广场改造": "TJ-08",
    "新建停车场": "TJ-08",
    "饮用水设备": "TJ-09",
    "矿井水处理": "TJ-09",
    "厂区外污水管网": "TJ-09",
    "新建回风井通风机设备基础及风道": "TJ-10",
    "防爆盖基础": "TJ-10",
    "通风机房配电室值班室": "TJ-10",
    "上筛分楼皮带走廊": "TJ-02",
    "去储煤场皮带走廊": "TJ-02",
    "出筛分楼运矸皮带走廊": "TJ-02",
    "转载点一": "TJ-02",
    "卸载点(煤)": "TJ-02",
    "卸载点(矸石)": "TJ-02",
    "新建制氮站及大棚(后期)": "TJ-11",
    "新建制氮站配电房(后期)": "TJ-11",
}

CIVIL_SETTLEMENT_DATA = [
    {
        "seq": 1,
        "project_name": "职工宿舍及室外工程",
        "audit_amount": 8634188.70,
        "settlement_amount": 6907350.95,
        "payment_plan": 8645938.27,
        "somoni_amount": 1133.57,
        "somoni_40_percent": 453,
        "feb_plan_somoni": 0,
        "debt_somoni": 680.14,
        "contractor": "项目一",
        "sub_project_names": ["职工宿舍6栋"],
    },
    {
        "seq": 2,
        "project_name": "临时澡堂",
        "audit_amount": 477085.87,
        "settlement_amount": 381668.70,
        "contractor": "项目一",
        "sub_project_names": ["临时澡堂"],
    },
    {
        "seq": 3,
        "project_name": "新建停车场",
        "audit_amount": 1696148.28,
        "settlement_amount": 1356918.62,
        "contractor": "项目一",
        "sub_project_names": ["新建停车场"],
    },
    {
        "seq": 4,
        "project_name": "原水调节池兼消防水池",
        "audit_amount": 1331015.24,
        "settlement_amount": 1064812.19,
        "payment_plan": 11177801.71,
        "somoni_amount": 1465.52,
        "somoni_40_percent": 586,
        "feb_plan_somoni": 500,
        "debt_somoni": 379.31,
        "contractor": "项目二",
        "sub_project_names": ["饮用水设备"],
    },
    {
        "seq": 5,
        "project_name": "矿井水沉淀池",
        "audit_amount": 1097013.88,
        "settlement_amount": 877611.10,
        "contractor": "项目二",
        "sub_project_names": ["矿井水处理"],
    },
    {
        "seq": 6,
        "project_name": "新建泵房配电室",
        "audit_amount": 319294.29,
        "settlement_amount": 255435.43,
        "contractor": "项目二",
        "sub_project_names": ["新增主井提升机房配电室"],
    },
    {
        "seq": 7,
        "project_name": "简易材料大棚",
        "audit_amount": 779862.04,
        "settlement_amount": 623889.63,
        "contractor": "项目二",
        "sub_project_names": ["简易材料大棚"],
    },
    {
        "seq": 8,
        "project_name": "新建灯房浴室联合建筑",
        "audit_amount": 6917318.20,
        "settlement_amount": 5533854.56,
        "contractor": "项目二",
        "sub_project_names": ["新建灯房浴室联合建筑"],
    },
    {
        "seq": 9,
        "project_name": "锅炉房",
        "audit_amount": 911734.26,
        "settlement_amount": 729387.41,
        "contractor": "项目二",
        "sub_project_names": ["锅炉房"],
    },
    {
        "seq": 10,
        "project_name": "公共卫生间及化粪池",
        "audit_amount": 276251.54,
        "settlement_amount": 221001.23,
        "contractor": "项目二",
        "sub_project_names": ["公共卫生间", "化粪池"],
    },
    {
        "seq": 11,
        "project_name": "综机广场硬化及行吊基础",
        "audit_amount": 2339762.70,
        "settlement_amount": 1871810.16,
        "contractor": "项目二",
        "sub_project_names": ["综机广场硬化", "室外龙门吊车基础"],
    },
    {
        "seq": 12,
        "project_name": "场内道路",
        "audit_amount": 1067955.60,
        "settlement_amount": 854364.48,
        "payment_plan": 3702768.46,
        "somoni_amount": 485.47,
        "somoni_40_percent": 194,
        "feb_plan_somoni": 90,
        "debt_somoni": 201.28,
        "contractor": "项目三",
        "sub_project_names": ["场内道路"],
    },
    {
        "seq": 13,
        "project_name": "场外道路",
        "audit_amount": 2521363.33,
        "settlement_amount": 2017090.66,
        "contractor": "项目三",
        "sub_project_names": ["场外道路"],
    },
    {
        "seq": 14,
        "project_name": "综合楼广场改造",
        "audit_amount": 1039141.64,
        "settlement_amount": 831313.31,
        "contractor": "项目三",
        "sub_project_names": ["综合楼广场改造"],
    },
    {
        "seq": 15,
        "project_name": "新建副井井口房",
        "audit_amount": 1337923.79,
        "settlement_amount": 1070339.04,
        "payment_plan": 4148140.88,
        "somoni_amount": 543.86,
        "somoni_40_percent": 218,
        "feb_plan_somoni": 250,
        "debt_somoni": 76.32,
        "contractor": "项目四",
        "sub_project_names": ["新建副井井口房"],
    },
    {
        "seq": 16,
        "project_name": "新建综机车间",
        "audit_amount": 3847252.30,
        "settlement_amount": 3077801.84,
        "contractor": "项目四",
        "sub_project_names": ["新建综机车间"],
    },
]


async def seed_civil_settlement(db: AsyncSession):
    """Insert civil settlement data, update sub-project actual_spent, and create Expenditure records."""
    result = await db.execute(select(CivilSettlement).limit(1))
    if result.scalar_one_or_none():
        return

    sp_result = await db.execute(
        select(SubProject).where(SubProject.category == "土建工程")
    )
    sp_map = {sp.name: sp for sp in sp_result.scalars().all()}

    cat_result = await db.execute(
        select(BudgetCategory).where(BudgetCategory.level == 2)
    )
    l2_code_map = {cat.code: cat for cat in cat_result.scalars().all()}

    count = 0
    exp_count = 0
    for item in CIVIL_SETTLEMENT_DATA:
        linked_sps = [sp_map[n] for n in item["sub_project_names"] if n in sp_map]
        first_sp_id = linked_sps[0].id if linked_sps else None

        record = CivilSettlement(
            seq=item["seq"],
            project_name=item["project_name"],
            audit_amount=item.get("audit_amount"),
            settlement_amount=item["settlement_amount"],
            payment_plan=item.get("payment_plan"),
            somoni_amount=item.get("somoni_amount"),
            somoni_40_percent=item.get("somoni_40_percent"),
            feb_plan_somoni=item.get("feb_plan_somoni"),
            debt_somoni=item.get("debt_somoni"),
            contractor=item.get("contractor"),
            sub_project_id=first_sp_id,
        )
        db.add(record)

        if linked_sps:
            total_budget = sum(sp.allocated_budget for sp in linked_sps) or 1
            for sp in linked_sps:
                ratio = sp.allocated_budget / total_budget
                amount_wan = round(item["settlement_amount"] * ratio / 10000, 2)
                sp.actual_spent = amount_wan
                sp.status = "completed"
                sp.progress_percent = 100

                l2_code = _SP_TO_L2_CODE.get(sp.name)
                l2_cat = l2_code_map.get(l2_code) if l2_code else None

                expenditure = Expenditure(
                    sub_project_id=sp.id,
                    category_id=l2_cat.id if l2_cat else None,
                    record_date=datetime.date(2025, 12, 31),
                    amount=amount_wan,
                    description=f"土建决算-{item['project_name']}({sp.name})",
                    source="settlement_import",
                )
                db.add(expenditure)
                exp_count += 1

        count += 1

    await db.flush()
    total_wan = round(27674649.32 / 10000, 2)
    print(f"[OK] Seeded: {count} civil settlement records, {exp_count} expenditures, total {total_wan} 万元")
