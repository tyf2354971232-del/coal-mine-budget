"""Civil construction sub-project data from 土建工程概算表 (total 9,035.35万元)."""


def get_civil_subprojects() -> list[dict]:
    """Return a list of civil construction sub-projects from 土建工程概算表."""
    return [
        # 已完工程 - 一 提升系统(已完) 1,253.58万元
        {
            "name": "主井井架维修加固",
            "category": "土建工程",
            "allocated_budget": 202.50,
            "description": "主井井架维修加固",
        },
        {
            "name": "主井提升机房",
            "category": "土建工程",
            "allocated_budget": 204.58,
            "description": "主井提升机房",
        },
        {
            "name": "新增主井提升机房配电室",
            "category": "土建工程",
            "allocated_budget": 42.12,
            "description": "新增主井提升机房配电室",
        },
        {
            "name": "新建副井井架",
            "category": "土建工程",
            "allocated_budget": 534.46,
            "description": "新建副井井架",
        },
        {
            "name": "新建副井提升机房",
            "category": "土建工程",
            "allocated_budget": 224.88,
            "description": "新建副井提升机房",
        },
        {
            "name": "新建副井提升机房配电室",
            "category": "土建工程",
            "allocated_budget": 45.05,
            "description": "新建副井提升机房配电室",
        },
        # 二 地面生产系统(已完) 751.95万元
        {
            "name": "新建副井井口房",
            "category": "土建工程",
            "allocated_budget": 279.37,
            "description": "新建副井井口房",
        },
        {
            "name": "筛分楼",
            "category": "土建工程",
            "allocated_budget": 334.44,
            "description": "筛分楼",
        },
        {
            "name": "煤场(已完)",
            "category": "土建工程",
            "allocated_budget": 138.14,
            "description": "煤场(已完)",
        },
        # 三 供电系统(已完) 375.35万元
        {
            "name": "新建6KV变电所",
            "category": "土建工程",
            "allocated_budget": 70.57,
            "description": "新建6KV变电所",
        },
        {
            "name": "110KV变电站",
            "category": "土建工程",
            "allocated_budget": 304.78,
            "description": "110KV变电站(含主控室、6KV配电室、辅助用房、场内道路硬化、排水沟、围墙大门)",
        },
        # 四 地面运输(已完) 697.00万元
        {
            "name": "场外道路",
            "category": "土建工程",
            "allocated_budget": 311.62,
            "description": "场外道路",
        },
        {
            "name": "窄轨铁路",
            "category": "土建工程",
            "allocated_budget": 145.46,
            "description": "窄轨铁路",
        },
        {
            "name": "运煤道路",
            "category": "土建工程",
            "allocated_budget": 239.93,
            "description": "运煤道路",
        },
        # 五 室外给排水及供热 119.06万元
        {
            "name": "锅炉房",
            "category": "土建工程",
            "allocated_budget": 119.06,
            "description": "锅炉房",
        },
        # 六 辅助厂房及仓库 884.56万元
        {
            "name": "新建综机车间",
            "category": "土建工程",
            "allocated_budget": 459.86,
            "description": "新建综机车间",
        },
        {
            "name": "室外龙门吊车基础",
            "category": "土建工程",
            "allocated_budget": 52.02,
            "description": "室外龙门吊车基础",
        },
        {
            "name": "综机广场硬化",
            "category": "土建工程",
            "allocated_budget": 144.84,
            "description": "综机广场硬化",
        },
        {
            "name": "电机车充电室",
            "category": "土建工程",
            "allocated_budget": 22.88,
            "description": "电机车充电室",
        },
        {
            "name": "电机车充电室配电房",
            "category": "土建工程",
            "allocated_budget": 9.24,
            "description": "电机车充电室配电房",
        },
        {
            "name": "材料库(电缆、配件)",
            "category": "土建工程",
            "allocated_budget": 58.08,
            "description": "材料库(电缆、配件)",
        },
        {
            "name": "简易材料大棚",
            "category": "土建工程",
            "allocated_budget": 137.64,
            "description": "简易材料大棚",
        },
        # 七 行政福利设施 2,334.15万元
        {
            "name": "新建灯房浴室联合建筑",
            "category": "土建工程",
            "allocated_budget": 1560.04,
            "description": "新建灯房浴室联合建筑",
        },
        {
            "name": "滤油池",
            "category": "土建工程",
            "allocated_budget": 11.22,
            "description": "滤油池",
        },
        {
            "name": "临时澡堂",
            "category": "土建工程",
            "allocated_budget": 36.30,
            "description": "临时澡堂",
        },
        {
            "name": "职工宿舍6栋",
            "category": "土建工程",
            "allocated_budget": 601.44,
            "description": "职工宿舍6栋",
        },
        {
            "name": "厂区大门",
            "category": "土建工程",
            "allocated_budget": 78.86,
            "description": "厂区大门",
        },
        {
            "name": "公共卫生间",
            "category": "土建工程",
            "allocated_budget": 26.23,
            "description": "公共卫生间",
        },
        {
            "name": "化粪池",
            "category": "土建工程",
            "allocated_budget": 20.06,
            "description": "化粪池",
        },
        # 八 场地设施(已完) 1,216.22万元
        {
            "name": "场内道路",
            "category": "土建工程",
            "allocated_budget": 242.68,
            "description": "场内道路",
        },
        {
            "name": "排水沟",
            "category": "土建工程",
            "allocated_budget": 111.30,
            "description": "排水沟",
        },
        {
            "name": "综合支架(钢结构)",
            "category": "土建工程",
            "allocated_budget": 151.20,
            "description": "综合支架(钢结构)",
        },
        {
            "name": "工广围挡",
            "category": "土建工程",
            "allocated_budget": 68.31,
            "description": "工广围挡",
        },
        {
            "name": "矿井水再利用工程",
            "category": "土建工程",
            "allocated_budget": 315.42,
            "description": "矿井水再利用工程",
        },
        {
            "name": "主副井广场硬化",
            "category": "土建工程",
            "allocated_budget": 67.98,
            "description": "主副井广场硬化",
        },
        {
            "name": "综合楼广场改造",
            "category": "土建工程",
            "allocated_budget": 68.81,
            "description": "综合楼广场改造",
        },
        {
            "name": "新建停车场",
            "category": "土建工程",
            "allocated_budget": 190.51,
            "description": "新建停车场",
        },
        # 九 环境保护及三废处理(已完) 476.67万元
        {
            "name": "饮用水设备",
            "category": "土建工程",
            "allocated_budget": 291.47,
            "description": "饮用水设备",
        },
        {
            "name": "矿井水处理",
            "category": "土建工程",
            "allocated_budget": 150.47,
            "description": "矿井水处理",
        },
        {
            "name": "厂区外污水管网",
            "category": "土建工程",
            "allocated_budget": 34.73,
            "description": "厂区外污水管网",
        },
        # 未完工程 - 一 通风系统 152.43万元
        {
            "name": "新建回风井通风机设备基础及风道",
            "category": "土建工程",
            "allocated_budget": 119.40,
            "description": "新建回风井通风机设备基础及风道",
        },
        {
            "name": "防爆盖基础",
            "category": "土建工程",
            "allocated_budget": 2.25,
            "description": "防爆盖基础",
        },
        {
            "name": "通风机房配电室值班室",
            "category": "土建工程",
            "allocated_budget": 30.78,
            "description": "通风机房配电室值班室",
        },
        # 二 地面生产系统(未完) 631.39万元
        {
            "name": "上筛分楼皮带走廊",
            "category": "土建工程",
            "allocated_budget": 109.50,
            "description": "上筛分楼皮带走廊",
        },
        {
            "name": "去储煤场皮带走廊",
            "category": "土建工程",
            "allocated_budget": 262.50,
            "description": "去储煤场皮带走廊",
        },
        {
            "name": "出筛分楼运矸皮带走廊",
            "category": "土建工程",
            "allocated_budget": 52.50,
            "description": "出筛分楼运矸皮带走廊",
        },
        {
            "name": "转载点一",
            "category": "土建工程",
            "allocated_budget": 67.60,
            "description": "转载点一",
        },
        {
            "name": "卸载点(煤)",
            "category": "土建工程",
            "allocated_budget": 71.73,
            "description": "卸载点(煤)",
        },
        {
            "name": "卸载点(矸石)",
            "category": "土建工程",
            "allocated_budget": 67.56,
            "description": "卸载点(矸石)",
        },
        # 三 安全技术及控制系统 143.00万元
        {
            "name": "新建制氮站及大棚(后期)",
            "category": "土建工程",
            "allocated_budget": 85.00,
            "description": "新建制氮站及大棚(后期)",
        },
        {
            "name": "新建制氮站配电房(后期)",
            "category": "土建工程",
            "allocated_budget": 58.00,
            "description": "新建制氮站配电房(后期)",
        },
    ]
