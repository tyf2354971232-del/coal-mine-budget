"""Other costs sub-project data from 工程建设其它费用概算表 (total: 4,574.25万元)."""


def get_other_subprojects() -> list[dict]:
    """Return a list of other costs sub-projects from 工程建设其它费用概算表."""
    return [
        # 一 建设管理费 1,829.25万元
        {
            "name": "建设单位管理费",
            "category": "其他费用",
            "allocated_budget": 1649.25,
            "description": "含管理人员工资924.00、图纸翻译费2.00、起重设备运营和维护许可费5.00、安保服务费72.00、办理工作签证费用462.00、办公用品及其他17.25、安全生产标准化100.00、矿井各类证照办理服务费用67.00",
        },
        {
            "name": "工程监理费",
            "category": "其他费用",
            "allocated_budget": 180.00,
            "description": "工程监理费",
        },
        # 四 勘察设计费 1,180.00万元
        {
            "name": "勘察费",
            "category": "其他费用",
            "allocated_budget": 180.00,
            "description": "勘察费(暂估)",
        },
        {
            "name": "工程设计费",
            "category": "其他费用",
            "allocated_budget": 1000.00,
            "description": "工程设计费",
        },
        # 九 安全生产应急救援预案编制评 10.00万元
        {
            "name": "安全生产应急救援预案编制评估",
            "category": "其他费用",
            "allocated_budget": 10.00,
            "description": "安全生产应急救援预案编制评估",
        },
        # 十 临时设施费 65.00万元
        {
            "name": "临时设施费",
            "category": "其他费用",
            "allocated_budget": 15.00,
            "description": "临时设施费",
        },
        {
            "name": "固体废物处理费用",
            "category": "其他费用",
            "allocated_budget": 50.00,
            "description": "固体废物处理费用",
        },
        # 十五 国内运费、国际运费及清关等费用 1,500.00万元
        {
            "name": "国内运费、国际运费及清关等费用",
            "category": "其他费用",
            "allocated_budget": 1500.00,
            "description": "国内运费、国际运费及清关等费用",
        },
    ]
