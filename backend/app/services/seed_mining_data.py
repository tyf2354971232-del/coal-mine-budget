"""Mining construction sub-project data from 矿建工程概算表."""


def get_mining_subprojects() -> list[dict]:
    """Return a list of mining construction sub-projects from 矿建工程概算表 (total 13,176.53万元)."""
    return [
        # 一 井底车场巷道及硐室 - 716.86万元
        {
            "name": "井底车场(维修)",
            "category": "矿建工程",
            "allocated_budget": 716.86,
            "description": "井底车场维修，880m",
        },
        # 二 采区 - 11,529.94万元
        {
            "name": "740运输石门",
            "category": "矿建工程",
            "allocated_budget": 246.89,
            "description": "740运输石门，230m",
        },
        {
            "name": "一采区运输转载巷",
            "category": "矿建工程",
            "allocated_budget": 308.96,
            "description": "一采区运输转载巷，210m",
        },
        {
            "name": "煤仓 D=8m",
            "category": "矿建工程",
            "allocated_budget": 227.64,
            "description": "煤仓 D=8m，30m",
        },
        {
            "name": "煤仓上口设备道",
            "category": "矿建工程",
            "allocated_budget": 91.34,
            "description": "煤仓上口设备道，80m",
        },
        {
            "name": "一采区运输下山",
            "category": "矿建工程",
            "allocated_budget": 457.59,
            "description": "一采区运输下山，406m",
        },
        {
            "name": "下部联巷",
            "category": "矿建工程",
            "allocated_budget": 182.67,
            "description": "下部联巷，180m",
        },
        {
            "name": "740水平轨道石门",
            "category": "矿建工程",
            "allocated_budget": 282.23,
            "description": "740水平轨道石门，280m",
        },
        {
            "name": "740水平轨道大巷(维修)",
            "category": "矿建工程",
            "allocated_budget": 81.49,
            "description": "740水平轨道大巷维修，100m",
        },
        {
            "name": "一采区轨道石门(维修)",
            "category": "矿建工程",
            "allocated_budget": 179.19,
            "description": "一采区轨道石门维修，220m",
        },
        {
            "name": "一采区轨道下山",
            "category": "矿建工程",
            "allocated_budget": 331.15,
            "description": "一采区轨道下山，376m",
        },
        {
            "name": "一采区回风下山",
            "category": "矿建工程",
            "allocated_budget": 331.15,
            "description": "一采区回风下山，376m",
        },
        {
            "name": "轨皮联巷",
            "category": "矿建工程",
            "allocated_budget": 53.63,
            "description": "轨皮联巷，55m",
        },
        {
            "name": "上车场",
            "category": "矿建工程",
            "allocated_budget": 251.00,
            "description": "上车场，140m",
        },
        {
            "name": "绞车房及通道",
            "category": "矿建工程",
            "allocated_budget": 167.05,
            "description": "绞车房及通道，148m",
        },
        {
            "name": "第一中车场",
            "category": "矿建工程",
            "allocated_budget": 343.34,
            "description": "第一中车场，182m",
        },
        {
            "name": "11020风巷",
            "category": "矿建工程",
            "allocated_budget": 2306.58,
            "description": "11020风巷，1476m",
        },
        {
            "name": "11020机巷",
            "category": "矿建工程",
            "allocated_budget": 2543.10,
            "description": "11020机巷，1634m",
        },
        {
            "name": "11020工作面切眼 α=10°",
            "category": "矿建工程",
            "allocated_budget": 277.50,
            "description": "11020工作面切眼 α=10°，150m",
        },
        {
            "name": "810水平回风大巷(维修)",
            "category": "矿建工程",
            "allocated_budget": 1529.75,
            "description": "810水平回风大巷维修，1800m",
        },
        {
            "name": "回风斜井(维修)",
            "category": "矿建工程",
            "allocated_budget": 94.46,
            "description": "回风斜井维修，390m",
        },
        {
            "name": "878-810回风斜巷 α=30°",
            "category": "矿建工程",
            "allocated_budget": 113.10,
            "description": "878-810回风斜巷 α=30°，175m",
        },
        {
            "name": "810运输大巷(维修)",
            "category": "矿建工程",
            "allocated_budget": 609.67,
            "description": "810运输大巷维修，850m",
        },
        {
            "name": "878片盘联巷",
            "category": "矿建工程",
            "allocated_budget": 47.31,
            "description": "878片盘联巷，66m",
        },
        {
            "name": "810至878回风联巷(维修)",
            "category": "矿建工程",
            "allocated_budget": 242.21,
            "description": "810至878回风联巷维修，285m",
        },
        {
            "name": "铺轨",
            "category": "矿建工程",
            "allocated_budget": 230.92,
            "description": "铺轨，4716m",
        },
        # 三 排水系统 - 772.58万元
        {
            "name": "下部排水系统",
            "category": "矿建工程",
            "allocated_budget": 534.19,
            "description": "下部排水系统，170m",
        },
        {
            "name": "740中央泵房(维修)",
            "category": "矿建工程",
            "allocated_budget": 43.02,
            "description": "740中央泵房维修，60m",
        },
        {
            "name": "740水仓",
            "category": "矿建工程",
            "allocated_budget": 195.37,
            "description": "740水仓，100m",
        },
        # 四 供电系统 - 157.15万元
        {
            "name": "上部变电所",
            "category": "矿建工程",
            "allocated_budget": 111.19,
            "description": "上部变电所，58m",
        },
        {
            "name": "井底变电所(维修)",
            "category": "矿建工程",
            "allocated_budget": 45.96,
            "description": "井底变电所维修，60m",
        },
    ]
