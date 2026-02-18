"""Seed data initialization - creates project, categories, sub-projects, and users."""
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.project import Project, SubProject
from app.models.budget import BudgetCategory, CostItem
from app.utils.security import hash_password

from app.services.seed_mining_data import get_mining_subprojects
from app.services.seed_civil_data import get_civil_subprojects
from app.services.seed_installation_data import get_installation_subprojects
from app.services.seed_other_data import get_other_subprojects
from app.services.seed_equipment_data import get_equipment_items, EQUIPMENT_GROUP_TO_L2
from app.services.seed_reuse_equipment import get_reuse_equipment


async def seed_initial_data(db: AsyncSession):
    """Initialize the database with real project data if empty."""
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        return

    # ── Users ──
    users = [
        User(username="admin", full_name="系统管理员", password_hash=hash_password("admin123"), role="admin", department="信息技术部"),
        User(username="leader", full_name="矿领导", password_hash=hash_password("leader123"), role="leader", department="矿领导层"),
        User(username="engineer", full_name="工程部员工", password_hash=hash_password("eng123"), role="department", department="工程部"),
        User(username="viewer", full_name="普通员工", password_hash=hash_password("view123"), role="viewer", department="综合办"),
    ]
    db.add_all(users)

    # ── Project ──
    project = Project(
        name="平煤神马塔能伊斯法拉公司煤矿（原舒拉8号井）技术改造项目",
        description="根据平煤神马集团批复，项目建设总投资56397.84万元的技术改造工程",
        total_budget=56397.84,
        reserve_rate=0.07,
        start_date=datetime.date(2025, 3, 1),
        end_date=datetime.date(2027, 12, 31),
        status="in_progress",
    )
    db.add(project)
    await db.flush()

    # ── L1 Budget Categories ──
    l1_data = [
        ("矿建工程", "MJ", 13176.53, 1),
        ("土建工程", "TJ", 9035.35, 2),
        ("安装工程", "AZ", 14293.29, 3),
        ("设备购置", "SB", 14116.51, 4),
        ("其他费用", "QT", 4574.25, 5),
        ("工程预备费", "YB", 1201.91, 6),
    ]
    l1_cats = {}
    for name, code, amount, order in l1_data:
        cat = BudgetCategory(name=name, code=code, level=1, budget_amount=amount, sort_order=order)
        db.add(cat)
        await db.flush()
        l1_cats[code] = cat

    # ── L2 Budget Categories ──
    l2_map = {}

    # 矿建工程 L2
    mj_l2 = [
        ("井底车场巷道及硐室", "MJ-01", 716.86, 1),
        ("采区", "MJ-02", 11529.94, 2),
        ("排水系统", "MJ-03", 772.58, 3),
        ("供电系统", "MJ-04", 157.15, 4),
    ]
    for name, code, amount, order in mj_l2:
        c = BudgetCategory(name=name, code=code, level=2, parent_id=l1_cats["MJ"].id, budget_amount=amount, sort_order=order)
        db.add(c)
        await db.flush()
        l2_map[code] = c

    # 土建工程 L2
    tj_l2 = [
        ("提升系统", "TJ-01", 1253.58, 1),
        ("地面生产系统", "TJ-02", 1383.34, 2),
        ("供电系统", "TJ-03", 375.35, 3),
        ("地面运输", "TJ-04", 697.00, 4),
        ("室外给排水及供热", "TJ-05", 119.06, 5),
        ("辅助厂房及仓库", "TJ-06", 884.56, 6),
        ("行政福利设施", "TJ-07", 2334.15, 7),
        ("场地设施", "TJ-08", 1216.22, 8),
        ("环境保护及三废处理", "TJ-09", 476.67, 9),
        ("通风系统", "TJ-10", 152.43, 10),
        ("安全技术及控制系统", "TJ-11", 143.00, 11),
    ]
    for name, code, amount, order in tj_l2:
        c = BudgetCategory(name=name, code=code, level=2, parent_id=l1_cats["TJ"].id, budget_amount=amount, sort_order=order)
        db.add(c)
        await db.flush()
        l2_map[code] = c

    # 安装工程 L2
    az_l2 = [
        ("井筒", "AZ-01", 1618.35, 1),
        ("井底车场巷道及硐室", "AZ-02", 410.19, 2),
        ("采区", "AZ-03", 1844.21, 3),
        ("提升系统", "AZ-04", 530.22, 4),
        ("排水系统", "AZ-05", 615.42, 5),
        ("通风系统", "AZ-06", 376.19, 6),
        ("压风系统", "AZ-07", 303.00, 7),
        ("地面生产系统", "AZ-08", 646.52, 8),
        ("安全及监控系统", "AZ-09", 1168.98, 9),
        ("通信调度及计算中心", "AZ-10", 255.88, 10),
        ("供电系统", "AZ-11", 4652.24, 11),
        ("地面运输", "AZ-12", 51.24, 12),
        ("室外给排水及供热", "AZ-13", 1391.63, 13),
        ("辅助厂房及仓库", "AZ-14", 13.97, 14),
        ("利旧设备安装", "AZ-15", 415.28, 15),
    ]
    for name, code, amount, order in az_l2:
        c = BudgetCategory(name=name, code=code, level=2, parent_id=l1_cats["AZ"].id, budget_amount=amount, sort_order=order)
        db.add(c)
        await db.flush()
        l2_map[code] = c

    # 设备购置 L2
    sb_l2 = [
        ("操车及装载设备", "SB-01", 0, 1),
        ("带式输送机设备", "SB-02", 0, 2),
        ("采掘设备", "SB-03", 0, 3),
        ("提升设备", "SB-04", 0, 4),
        ("排水设备", "SB-05", 0, 5),
        ("通风设备", "SB-06", 0, 6),
        ("压风设备", "SB-07", 0, 7),
        ("供电设备", "SB-08", 0, 8),
        ("安全监控设备", "SB-09", 0, 9),
        ("通信信息设备", "SB-10", 0, 10),
        ("地面生产设备", "SB-11", 0, 11),
        ("其他设备及工器具", "SB-12", 0, 12),
    ]
    sb_group_totals = {}
    for item in get_equipment_items():
        g = item["group"]
        sb_group_totals[g] = sb_group_totals.get(g, 0) + item["budget_amount"]

    group_name_to_l2_code = EQUIPMENT_GROUP_TO_L2
    for name, code, _, order in sb_l2:
        for gname, gcode in group_name_to_l2_code.items():
            if gcode == code:
                amount = round(sb_group_totals.get(gname, 0), 2)
                break
        else:
            amount = 0
        c = BudgetCategory(name=name, code=code, level=2, parent_id=l1_cats["SB"].id, budget_amount=amount, sort_order=order)
        db.add(c)
        await db.flush()
        l2_map[code] = c

    # 其他费用 L2
    qt_l2 = [
        ("建设管理费", "QT-01", 1829.25, 1),
        ("勘察设计费", "QT-02", 1180.00, 2),
        ("国内运费及清关费", "QT-03", 1500.00, 3),
        ("临时设施费", "QT-04", 65.00, 4),
        ("安全评价费", "QT-05", 0, 5),
        ("应急预案编制费", "QT-06", 10.00, 6),
    ]
    for name, code, amount, order in qt_l2:
        c = BudgetCategory(name=name, code=code, level=2, parent_id=l1_cats["QT"].id, budget_amount=amount, sort_order=order)
        db.add(c)
        await db.flush()
        l2_map[code] = c

    await db.flush()

    # ── Sub-projects ──
    all_sp_data = []
    all_sp_data.extend(get_mining_subprojects())
    all_sp_data.extend(get_civil_subprojects())
    all_sp_data.extend(get_installation_subprojects())
    all_sp_data.extend(get_other_subprojects())

    cat_name_map = {
        "矿建工程": "矿建工程",
        "土建工程": "土建工程",
        "安装工程": "安装工程",
        "其他费用": "其他费用",
    }

    sp_objects = {}
    for i, sp_data in enumerate(all_sp_data):
        sp = SubProject(
            project_id=project.id,
            name=sp_data["name"],
            category=sp_data["category"],
            allocated_budget=sp_data["allocated_budget"],
            actual_spent=0,
            progress_percent=0,
            status="not_started",
            planned_start=datetime.date(2025, 3, 1),
            planned_end=datetime.date(2027, 12, 31),
            description=sp_data.get("description", ""),
            sort_order=i + 1,
        )
        db.add(sp)
        await db.flush()
        sp_objects[sp_data["name"]] = sp

    # Create a virtual sub-project for equipment purchase
    equipment_sp = SubProject(
        project_id=project.id,
        name="设备购置",
        category="设备购置",
        allocated_budget=14116.51,
        actual_spent=0,
        progress_percent=0,
        status="not_started",
        planned_start=datetime.date(2025, 3, 1),
        planned_end=datetime.date(2027, 12, 31),
        description="全部设备采购（含357+项设备明细）",
        sort_order=len(all_sp_data) + 1,
    )
    db.add(equipment_sp)
    await db.flush()

    # Create sub-project for reuse equipment installation
    reuse_sp = SubProject(
        project_id=project.id,
        name="利旧设备安装",
        category="安装工程",
        allocated_budget=415.28,
        actual_spent=0,
        progress_percent=0,
        status="not_started",
        planned_start=datetime.date(2025, 6, 1),
        planned_end=datetime.date(2027, 6, 30),
        description="33条利旧设备安装工程",
        sort_order=len(all_sp_data) + 2,
    )
    db.add(reuse_sp)
    await db.flush()

    # ── Equipment CostItems ──
    eq_items = get_equipment_items()
    for item in eq_items:
        l2_code = EQUIPMENT_GROUP_TO_L2.get(item["group"])
        cat_id = l2_map[l2_code].id if l2_code and l2_code in l2_map else None
        ci = CostItem(
            sub_project_id=equipment_sp.id,
            category_id=cat_id,
            name=item["name"],
            budget_amount=item["budget_amount"],
            actual_amount=0,
            unit=item.get("unit", ""),
            quantity=item.get("quantity", 1),
            unit_price=item.get("unit_price", 0),
            note=item.get("model", ""),
        )
        db.add(ci)

    # ── Reuse Equipment CostItems ──
    reuse_cat_id = l2_map.get("AZ-15")
    reuse_cat_id = reuse_cat_id.id if reuse_cat_id else None
    for item in get_reuse_equipment():
        ci = CostItem(
            sub_project_id=reuse_sp.id,
            category_id=reuse_cat_id,
            name=f"[利旧]{item['name']}",
            budget_amount=item.get("install_fee", 0),
            actual_amount=0,
            unit="台/套",
            quantity=item.get("quantity", 1),
            unit_price=item.get("install_fee", 0) / max(1, item.get("quantity", 1)),
            note=f"{item['model']} 原值:{item.get('original_value', 0)}万 净值:{item.get('net_value', 0)}万",
        )
        db.add(ci)

    await db.flush()
    print(f"[OK] Seeded: {len(all_sp_data)+2} sub-projects, {len(eq_items)} equipment items, {len(get_reuse_equipment())} reuse items")
