"""Seed data initialization - creates default project, categories, and admin user."""
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.project import Project, SubProject
from app.models.budget import BudgetCategory
from app.utils.security import hash_password


async def seed_initial_data(db: AsyncSession):
    """Initialize the database with default data if empty."""
    # Check if data already exists
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        return  # Already seeded

    # 1. Create default admin user
    admin = User(
        username="admin",
        full_name="系统管理员",
        password_hash=hash_password("admin123"),
        role="admin",
        department="信息技术部",
    )
    leader = User(
        username="leader",
        full_name="矿领导",
        password_hash=hash_password("leader123"),
        role="leader",
        department="矿领导层",
    )
    dept_user = User(
        username="engineer",
        full_name="工程部员工",
        password_hash=hash_password("eng123"),
        role="department",
        department="工程部",
    )
    viewer = User(
        username="viewer",
        full_name="普通员工",
        password_hash=hash_password("view123"),
        role="viewer",
        department="综合办",
    )
    db.add_all([admin, leader, dept_user, viewer])

    # 2. Create main project
    project = Project(
        name="平煤神马塔能伊斯法拉公司煤矿（原舒拉8号井）技术改造项目",
        description="根据平煤神马集团批复，项目建设总投资56397.84万元的技术改造工程",
        total_budget=56397.84,
        reserve_rate=0.07,
        start_date=datetime.date(2025, 3, 1),
        end_date=datetime.date(2026, 3, 1),
        status="in_progress",
    )
    db.add(project)
    await db.flush()

    # 3. Create budget categories (Level 1 - 一级科目)
    categories_l1 = [
        BudgetCategory(name="矿建工程费", code="MJ", level=1, budget_amount=13176.53, sort_order=1),
        BudgetCategory(name="土建工程费", code="TJ", level=1, budget_amount=9035.35, sort_order=2),
        BudgetCategory(name="安装工程费", code="AZ", level=1, budget_amount=14293.29, sort_order=3),
        BudgetCategory(name="设备购置费", code="SB", level=1, budget_amount=14116.51, sort_order=4),
        BudgetCategory(name="其他费用", code="QT", level=1, budget_amount=4574.25, sort_order=5),
        BudgetCategory(name="预备费", code="YB", level=1, budget_amount=1201.91, sort_order=6),
    ]
    db.add_all(categories_l1)
    await db.flush()

    # 4. Create level 2 categories (示例二级科目)
    cat_map = {c.code: c for c in categories_l1}

    l2_categories = [
        # 矿建工程费下
        BudgetCategory(name="主井筒改造", code="MJ-01", level=2, parent_id=cat_map["MJ"].id, budget_amount=3500, sort_order=1),
        BudgetCategory(name="副井筒改造", code="MJ-02", level=2, parent_id=cat_map["MJ"].id, budget_amount=2800, sort_order=2),
        BudgetCategory(name="巷道掘进", code="MJ-03", level=2, parent_id=cat_map["MJ"].id, budget_amount=3200, sort_order=3),
        BudgetCategory(name="通风系统", code="MJ-04", level=2, parent_id=cat_map["MJ"].id, budget_amount=1876.53, sort_order=4),
        BudgetCategory(name="排水系统", code="MJ-05", level=2, parent_id=cat_map["MJ"].id, budget_amount=1800, sort_order=5),
        # 土建工程费下
        BudgetCategory(name="工业场地建筑", code="TJ-01", level=2, parent_id=cat_map["TJ"].id, budget_amount=3200, sort_order=1),
        BudgetCategory(name="办公及生活设施", code="TJ-02", level=2, parent_id=cat_map["TJ"].id, budget_amount=2100, sort_order=2),
        BudgetCategory(name="道路及运输设施", code="TJ-03", level=2, parent_id=cat_map["TJ"].id, budget_amount=1835.35, sort_order=3),
        BudgetCategory(name="环保设施", code="TJ-04", level=2, parent_id=cat_map["TJ"].id, budget_amount=1900, sort_order=4),
        # 安装工程费下
        BudgetCategory(name="采掘设备安装", code="AZ-01", level=2, parent_id=cat_map["AZ"].id, budget_amount=4500, sort_order=1),
        BudgetCategory(name="提升运输设备安装", code="AZ-02", level=2, parent_id=cat_map["AZ"].id, budget_amount=3200, sort_order=2),
        BudgetCategory(name="供电系统安装", code="AZ-03", level=2, parent_id=cat_map["AZ"].id, budget_amount=3500, sort_order=3),
        BudgetCategory(name="通讯监控系统安装", code="AZ-04", level=2, parent_id=cat_map["AZ"].id, budget_amount=3093.29, sort_order=4),
        # 设备购置费下
        BudgetCategory(name="采掘设备", code="SB-01", level=2, parent_id=cat_map["SB"].id, budget_amount=5000, sort_order=1),
        BudgetCategory(name="提升运输设备", code="SB-02", level=2, parent_id=cat_map["SB"].id, budget_amount=3500, sort_order=2),
        BudgetCategory(name="供电设备", code="SB-03", level=2, parent_id=cat_map["SB"].id, budget_amount=2800, sort_order=3),
        BudgetCategory(name="安全监测设备", code="SB-04", level=2, parent_id=cat_map["SB"].id, budget_amount=2816.51, sort_order=4),
        # 其他费用下
        BudgetCategory(name="设计咨询费", code="QT-01", level=2, parent_id=cat_map["QT"].id, budget_amount=1200, sort_order=1),
        BudgetCategory(name="建设管理费", code="QT-02", level=2, parent_id=cat_map["QT"].id, budget_amount=1500, sort_order=2),
        BudgetCategory(name="生产准备费", code="QT-03", level=2, parent_id=cat_map["QT"].id, budget_amount=1074.25, sort_order=3),
        BudgetCategory(name="其他专项费用", code="QT-04", level=2, parent_id=cat_map["QT"].id, budget_amount=800, sort_order=4),
    ]
    db.add_all(l2_categories)
    await db.flush()

    # 5. Create level 3 categories (三级科目 - 通用支出类型)
    l3_names = [
        ("人员工资", "RY"), ("材料费", "CL"), ("机械使用费", "JX"),
        ("运输费", "YS"), ("管理费", "GL"), ("临时设施费", "LS"),
    ]
    for l2_cat in l2_categories:
        for i, (name, code) in enumerate(l3_names):
            l3 = BudgetCategory(
                name=name,
                code=f"{l2_cat.code}-{code}",
                level=3,
                parent_id=l2_cat.id,
                budget_amount=round(l2_cat.budget_amount / len(l3_names), 2),
                sort_order=i + 1,
            )
            db.add(l3)

    # 6. Create sample sub-projects (30+ items as specified)
    sub_projects_data = [
        # 矿建工程
        ("主井筒改造工程", "矿建工程费", 3500, "2025-03-01", "2025-08-30"),
        ("副井筒改造工程", "矿建工程费", 2800, "2025-03-15", "2025-09-30"),
        ("主运输巷道掘进", "矿建工程费", 1600, "2025-04-01", "2025-10-31"),
        ("回风巷道掘进", "矿建工程费", 1600, "2025-04-15", "2025-11-15"),
        ("通风系统改造", "矿建工程费", 1876.53, "2025-05-01", "2025-10-31"),
        ("排水系统升级", "矿建工程费", 1800, "2025-05-15", "2025-11-30"),
        # 土建工程
        ("选煤厂房建设", "土建工程费", 1800, "2025-03-01", "2025-09-30"),
        ("机修车间建设", "土建工程费", 1400, "2025-04-01", "2025-09-30"),
        ("办公楼改造", "土建工程费", 1200, "2025-05-01", "2025-10-31"),
        ("职工宿舍改造", "土建工程费", 900, "2025-05-15", "2025-10-15"),
        ("矿区道路建设", "土建工程费", 1000, "2025-03-15", "2025-08-31"),
        ("运输通道建设", "土建工程费", 835.35, "2025-04-01", "2025-09-30"),
        ("污水处理设施", "土建工程费", 1000, "2025-06-01", "2025-11-30"),
        ("粉尘治理设施", "土建工程费", 900, "2025-06-15", "2025-12-15"),
        # 安装工程
        ("综采设备安装", "安装工程费", 2500, "2025-06-01", "2025-10-31"),
        ("掘进设备安装", "安装工程费", 2000, "2025-06-15", "2025-11-15"),
        ("主井提升机安装", "安装工程费", 1800, "2025-07-01", "2025-11-30"),
        ("皮带运输机安装", "安装工程费", 1400, "2025-07-15", "2025-12-15"),
        ("35kV变电所安装", "安装工程费", 2000, "2025-05-01", "2025-09-30"),
        ("井下供电系统安装", "安装工程费", 1500, "2025-06-01", "2025-10-31"),
        ("安全监控系统安装", "安装工程费", 1593.29, "2025-07-01", "2025-12-31"),
        ("通讯调度系统安装", "安装工程费", 1500, "2025-08-01", "2026-01-31"),
        # 设备购置
        ("综采成套设备采购", "设备购置费", 3000, "2025-03-01", "2025-06-30"),
        ("掘进机组采购", "设备购置费", 2000, "2025-03-15", "2025-06-30"),
        ("主井提升设备采购", "设备购置费", 2000, "2025-04-01", "2025-07-31"),
        ("皮带运输设备采购", "设备购置费", 1500, "2025-04-15", "2025-08-31"),
        ("变压器及开关柜采购", "设备购置费", 1600, "2025-03-01", "2025-06-30"),
        ("电缆电线采购", "设备购置费", 1200, "2025-03-15", "2025-07-31"),
        ("瓦斯监测系统采购", "设备购置费", 1500, "2025-04-01", "2025-07-31"),
        ("人员定位系统采购", "设备购置费", 1316.51, "2025-04-15", "2025-08-31"),
        # 其他费用
        ("初步设计及施工图设计", "其他费用", 1200, "2025-02-01", "2025-04-30"),
        ("工程监理", "其他费用", 800, "2025-03-01", "2026-03-01"),
        ("建设单位管理费", "其他费用", 700, "2025-03-01", "2026-03-01"),
        ("生产准备及培训", "其他费用", 1074.25, "2025-10-01", "2026-02-28"),
        ("环评及安评", "其他费用", 400, "2025-02-15", "2025-05-31"),
        ("联合试运转", "其他费用", 400, "2025-12-01", "2026-02-28"),
    ]

    for i, (name, category, budget, start, end) in enumerate(sub_projects_data):
        sp = SubProject(
            project_id=project.id,
            name=name,
            category=category,
            allocated_budget=budget,
            actual_spent=0,
            progress_percent=0,
            status="not_started",
            planned_start=datetime.date.fromisoformat(start),
            planned_end=datetime.date.fromisoformat(end),
            sort_order=i + 1,
        )
        db.add(sp)

    await db.flush()
    print("[OK] Initial data seeded successfully")
