"""Installation engineering sub-project data from 机电设备及安装工程概算表 (total: 14,293.29万元)."""


def get_installation_subprojects() -> list[dict]:
    """Return a list of installation engineering sub-projects from 机电设备及安装工程概算表."""
    return [
        # 已完工程 0.90万元
        {
            "name": "通信调度(已完): 调度通信系统",
            "category": "安装工程",
            "allocated_budget": 0.90,
            "description": "已完工程-调度通信系统",
        },
        # 一 井筒 1,618.35万元
        {
            "name": "主井井筒装备",
            "category": "安装工程",
            "allocated_budget": 498.14,
            "description": "井筒-主井井筒装备安装",
        },
        {
            "name": "副井井筒装备",
            "category": "安装工程",
            "allocated_budget": 414.89,
            "description": "井筒-副井井筒装备安装",
        },
        {
            "name": "主井井筒管路",
            "category": "安装工程",
            "allocated_budget": 55.69,
            "description": "井筒-主井井筒管路安装",
        },
        {
            "name": "副井井筒管路",
            "category": "安装工程",
            "allocated_budget": 249.63,
            "description": "井筒-副井井筒管路安装",
        },
        {
            "name": "井筒其他",
            "category": "安装工程",
            "allocated_budget": 400.00,
            "description": "井筒-其他装备安装",
        },
        # 二 井底车场巷道及硐室 410.19万元
        {
            "name": "副井(+740水平)车场连接处装备安装",
            "category": "安装工程",
            "allocated_budget": 153.48,
            "description": "井底车场巷道及硐室-副井+740水平车场连接处",
        },
        {
            "name": "副井(+810水平)车场连接处装备安装",
            "category": "安装工程",
            "allocated_budget": 132.96,
            "description": "井底车场巷道及硐室-副井+810水平车场连接处",
        },
        {
            "name": "主井井底装载装备安装",
            "category": "安装工程",
            "allocated_budget": 123.74,
            "description": "井底车场巷道及硐室-主井井底装载装备",
        },
        # 三 采区 1,844.21万元
        {
            "name": "810水平大巷带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 64.68,
            "description": "采区-810水平大巷带式输送机",
        },
        {
            "name": "下探巷17带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 40.72,
            "description": "采区-下探巷17带式输送机",
        },
        {
            "name": "810主井联巷带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 15.51,
            "description": "采区-810主井联巷带式输送机",
        },
        {
            "name": "810煤仓下山带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 27.71,
            "description": "采区-810煤仓下山带式输送机",
        },
        {
            "name": "11021风巷带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 108.87,
            "description": "采区-11021风巷带式输送机",
        },
        {
            "name": "11021机巷带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 108.87,
            "description": "采区-11021机巷带式输送机",
        },
        {
            "name": "11021切眼带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 24.21,
            "description": "采区-11021切眼带式输送机",
        },
        {
            "name": "轨道上山提升机设备安装",
            "category": "安装工程",
            "allocated_budget": 31.23,
            "description": "采区-轨道上山提升机",
        },
        {
            "name": "采区运输下山带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 136.39,
            "description": "采区-运输下山带式输送机",
        },
        {
            "name": "一采区运输转载巷带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 79.63,
            "description": "采区-一采区运输转载巷带式输送机",
        },
        {
            "name": "采区煤仓清仓设备安装",
            "category": "安装工程",
            "allocated_budget": 10.26,
            "description": "采区-煤仓清仓设备",
        },
        {
            "name": "采区煤仓仓下给煤机装载硐室设备安装",
            "category": "安装工程",
            "allocated_budget": 36.75,
            "description": "采区-煤仓仓下给煤机装载硐室",
        },
        {
            "name": "一采区运输石门带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 73.74,
            "description": "采区-一采区运输石门带式输送机",
        },
        {
            "name": "箕斗装载带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 52.10,
            "description": "采区-箕斗装载带式输送机",
        },
        {
            "name": "轨道下山架空乘人装置设备安装",
            "category": "安装工程",
            "allocated_budget": 156.95,
            "description": "采区-轨道下山架空乘人装置",
        },
        {
            "name": "11021采面设备安装",
            "category": "安装工程",
            "allocated_budget": 533.98,
            "description": "采区-11021采面设备",
        },
        {
            "name": "11021机巷掘进工作面设备",
            "category": "安装工程",
            "allocated_budget": 151.74,
            "description": "采区-11021机巷掘进工作面设备",
        },
        {
            "name": "11021风巷掘进工作面设备",
            "category": "安装工程",
            "allocated_budget": 157.26,
            "description": "采区-11021风巷掘进工作面设备",
        },
        {
            "name": "风机维修设备安装",
            "category": "安装工程",
            "allocated_budget": 33.60,
            "description": "采区-风机维修设备",
        },
        # 四 提升系统 530.22万元
        {
            "name": "主井提升机房设备安装",
            "category": "安装工程",
            "allocated_budget": 104.97,
            "description": "提升系统-主井提升机房",
        },
        {
            "name": "副井提升机房设备安装",
            "category": "安装工程",
            "allocated_budget": 414.10,
            "description": "提升系统-副井提升机房",
        },
        {
            "name": "回风斜井临时提升机房设备安装",
            "category": "安装工程",
            "allocated_budget": 11.15,
            "description": "提升系统-回风斜井临时提升机房",
        },
        # 五 排水系统 615.42万元
        {
            "name": "井底车场排水泵房设备安装",
            "category": "安装工程",
            "allocated_budget": 79.86,
            "description": "排水系统-井底车场排水泵房",
        },
        {
            "name": "一采区中部水泵房设备安装",
            "category": "安装工程",
            "allocated_budget": 138.06,
            "description": "排水系统-一采区中部水泵房",
        },
        {
            "name": "采区排水泵房设备安装(后期)",
            "category": "安装工程",
            "allocated_budget": 365.37,
            "description": "排水系统-采区排水泵房(后期)",
        },
        {
            "name": "井下临时排水工程设备安装",
            "category": "安装工程",
            "allocated_budget": 32.13,
            "description": "排水系统-井下临时排水工程",
        },
        # 六 通风系统 376.19万元
        {
            "name": "投产时主立井安装临时通风机",
            "category": "安装工程",
            "allocated_budget": 35.11,
            "description": "通风系统-主立井临时通风机",
        },
        {
            "name": "后期回风斜井安装永久通风机",
            "category": "安装工程",
            "allocated_budget": 339.71,
            "description": "通风系统-回风斜井永久通风机",
        },
        {
            "name": "斜井自复式防爆门",
            "category": "安装工程",
            "allocated_budget": 1.36,
            "description": "通风系统-斜井自复式防爆门",
        },
        # 七 压风系统 303.00万元
        {
            "name": "压风系统机械设备安装",
            "category": "安装工程",
            "allocated_budget": 263.17,
            "description": "压风系统-机械设备安装",
        },
        {
            "name": "压风系统电气设备安装",
            "category": "安装工程",
            "allocated_budget": 39.83,
            "description": "压风系统-电气设备安装",
        },
        # 八 地面生产系统 646.52万元
        {
            "name": "副井井口装备安装",
            "category": "安装工程",
            "allocated_budget": 113.99,
            "description": "地面生产系统-副井井口装备",
        },
        {
            "name": "主井井口装备安装",
            "category": "安装工程",
            "allocated_budget": 28.94,
            "description": "地面生产系统-主井井口装备",
        },
        {
            "name": "主井井口受煤仓设备安装",
            "category": "安装工程",
            "allocated_budget": 41.01,
            "description": "地面生产系统-主井井口受煤仓",
        },
        {
            "name": "仓下转载带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 5.61,
            "description": "地面生产系统-仓下转载带式输送机",
        },
        {
            "name": "上筛分楼带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 12.90,
            "description": "地面生产系统-上筛分楼带式输送机",
        },
        {
            "name": "筛分楼设备安装",
            "category": "安装工程",
            "allocated_budget": 246.94,
            "description": "地面生产系统-筛分楼设备",
        },
        {
            "name": "去储煤场带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 13.10,
            "description": "地面生产系统-去储煤场带式输送机",
        },
        {
            "name": "出筛分楼运矸带式输送机设备安装",
            "category": "安装工程",
            "allocated_budget": 5.03,
            "description": "地面生产系统-出筛分楼运矸带式输送机",
        },
        {
            "name": "配电及控制(地面生产)",
            "category": "安装工程",
            "allocated_budget": 178.99,
            "description": "地面生产系统-配电及控制",
        },
        # 九 安全及监控系统 1,168.98万元
        {
            "name": "防尘隔爆设施",
            "category": "安装工程",
            "allocated_budget": 1.22,
            "description": "安全及监控-防尘隔爆设施",
        },
        {
            "name": "井下消防洒水管路",
            "category": "安装工程",
            "allocated_budget": 250.87,
            "description": "安全及监控-井下消防洒水管路",
        },
        {
            "name": "井下清水管路",
            "category": "安装工程",
            "allocated_budget": 52.33,
            "description": "安全及监控-井下清水管路",
        },
        {
            "name": "井下安全监控设备安装",
            "category": "安装工程",
            "allocated_budget": 24.29,
            "description": "安全及监控-井下安全监控设备",
        },
        {
            "name": "地面制氮站机械设备安装",
            "category": "安装工程",
            "allocated_budget": 293.29,
            "description": "安全及监控-地面制氮站机械设备",
        },
        {
            "name": "井下灌浆站机械设备安装",
            "category": "安装工程",
            "allocated_budget": 99.65,
            "description": "安全及监控-井下灌浆站机械设备",
        },
        {
            "name": "井下制氮站机械设备安装",
            "category": "安装工程",
            "allocated_budget": 364.09,
            "description": "安全及监控-井下制氮站机械设备",
        },
        {
            "name": "通风安全及地测",
            "category": "安装工程",
            "allocated_budget": 83.25,
            "description": "安全及监控-通风安全及地测",
        },
        # 十 通信调度及计算中心 254.98万元
        {
            "name": "井上下调度通信系统",
            "category": "安装工程",
            "allocated_budget": 173.58,
            "description": "通信调度-井上下调度通信系统",
        },
        {
            "name": "中心机房信息基础设施",
            "category": "安装工程",
            "allocated_budget": 5.04,
            "description": "通信调度-中心机房信息基础设施",
        },
        {
            "name": "办公网络系统",
            "category": "安装工程",
            "allocated_budget": 15.63,
            "description": "通信调度-办公网络系统",
        },
        {
            "name": "智慧大屏系统",
            "category": "安装工程",
            "allocated_budget": 3.29,
            "description": "通信调度-智慧大屏系统",
        },
        {
            "name": "地面安防系统",
            "category": "安装工程",
            "allocated_budget": 14.72,
            "description": "通信调度-地面安防系统",
        },
        {
            "name": "4G基站建设",
            "category": "安装工程",
            "allocated_budget": 5.95,
            "description": "通信调度-4G基站建设",
        },
        {
            "name": "SD-WAN系统",
            "category": "安装工程",
            "allocated_budget": 5.56,
            "description": "通信调度-SD-WAN系统",
        },
        {
            "name": "物流仓储系统",
            "category": "安装工程",
            "allocated_budget": 5.56,
            "description": "通信调度-物流仓储系统",
        },
        {
            "name": "智能会议系统",
            "category": "安装工程",
            "allocated_budget": 14.59,
            "description": "通信调度-智能会议系统",
        },
        {
            "name": "智慧园区系统",
            "category": "安装工程",
            "allocated_budget": 4.91,
            "description": "通信调度-智慧园区系统",
        },
        {
            "name": "井下工业视频",
            "category": "安装工程",
            "allocated_budget": 6.16,
            "description": "通信调度-井下工业视频",
        },
        # 十一 供电系统 4,652.24万元
        {
            "name": "地面工广110kV变电站电气设备安装",
            "category": "安装工程",
            "allocated_budget": 1039.80,
            "description": "供电系统-地面工广110kV变电站",
        },
        {
            "name": "110kV电源线路",
            "category": "安装工程",
            "allocated_budget": 536.06,
            "description": "供电系统-110kV电源线路",
        },
        {
            "name": "地面工广临时6kV电源线路",
            "category": "安装工程",
            "allocated_budget": 197.60,
            "description": "供电系统-地面工广临时6kV电源线路",
        },
        {
            "name": "井底车场中央变电所电气设备安装",
            "category": "安装工程",
            "allocated_budget": 136.18,
            "description": "供电系统-井底车场中央变电所",
        },
        {
            "name": "810井底车场变电所电气设备安装",
            "category": "安装工程",
            "allocated_budget": 51.57,
            "description": "供电系统-810井底车场变电所",
        },
        {
            "name": "进风井下井电缆",
            "category": "安装工程",
            "allocated_budget": 424.89,
            "description": "供电系统-进风井下井电缆",
        },
        {
            "name": "宿舍区箱变",
            "category": "安装工程",
            "allocated_budget": 50.86,
            "description": "供电系统-宿舍区箱变",
        },
        {
            "name": "工广动照网",
            "category": "安装工程",
            "allocated_budget": 249.20,
            "description": "供电系统-工广动照网",
        },
        {
            "name": "井下动力网",
            "category": "安装工程",
            "allocated_budget": 636.21,
            "description": "供电系统-井下动力网",
        },
        {
            "name": "风井工广6kV电源线路",
            "category": "安装工程",
            "allocated_budget": 97.67,
            "description": "供电系统-风井工广6kV电源线路",
        },
        {
            "name": "110KV降压站EPC",
            "category": "安装工程",
            "allocated_budget": 1232.19,
            "description": "供电系统-110KV降压站EPC",
        },
        # 十二 地面运输 51.24万元
        {
            "name": "地面运输机械设备",
            "category": "安装工程",
            "allocated_budget": 17.87,
            "description": "地面运输-机械设备",
        },
        {
            "name": "地面运输配电及控制",
            "category": "安装工程",
            "allocated_budget": 33.36,
            "description": "地面运输-配电及控制",
        },
        # 十三 室外给排水及供热 1,391.63万元
        {
            "name": "纯净水水处理厂",
            "category": "安装工程",
            "allocated_budget": 81.33,
            "description": "室外给排水及供热-纯净水水处理厂",
        },
        {
            "name": "矿井尾矿水设备安装",
            "category": "安装工程",
            "allocated_budget": 5.31,
            "description": "室外给排水及供热-矿井尾矿水设备",
        },
        {
            "name": "生产消防泵房设备安装",
            "category": "安装工程",
            "allocated_budget": 183.39,
            "description": "室外给排水及供热-生产消防泵房设备",
        },
        {
            "name": "室外工程",
            "category": "安装工程",
            "allocated_budget": 87.20,
            "description": "室外给排水及供热-室外工程",
        },
        {
            "name": "水源",
            "category": "安装工程",
            "allocated_budget": 624.94,
            "description": "室外给排水及供热-水源设备",
        },
        {
            "name": "厂区外污水管网",
            "category": "安装工程",
            "allocated_budget": 44.20,
            "description": "室外给排水及供热-厂区外污水管网",
        },
        {
            "name": "锅炉房设备安装",
            "category": "安装工程",
            "allocated_budget": 152.71,
            "description": "室外给排水及供热-锅炉房设备",
        },
        {
            "name": "主井空气加热室设备安装",
            "category": "安装工程",
            "allocated_budget": 105.25,
            "description": "室外给排水及供热-主井空气加热室",
        },
        {
            "name": "副井空气加热室设备安装",
            "category": "安装工程",
            "allocated_budget": 107.29,
            "description": "室外给排水及供热-副井空气加热室",
        },
        # 十四 辅助厂房及仓库 13.97万元
        {
            "name": "综机车间设备工具及材料",
            "category": "安装工程",
            "allocated_budget": 13.97,
            "description": "辅助厂房及仓库-综机车间设备工具及材料",
        },
        # 利旧设备安装 415.28万元
        {
            "name": "利旧设备安装",
            "category": "安装工程",
            "allocated_budget": 415.28,
            "description": "利旧设备安装费用总计",
        },
    ]
