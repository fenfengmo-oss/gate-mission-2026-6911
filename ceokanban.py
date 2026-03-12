import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
from datetime import datetime, timedelta

# ==========================================
# 1. 系统配置 (SYSTEM OPTIMIZED)
# ==========================================
st.set_page_config(
    page_title="GATE Executive Command Center v1.0 AI",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 状态管理 (State Management)
# ==========================================
if 'view' not in st.session_state: st.session_state.view = 'Overview'
if 'sel_dim' not in st.session_state: st.session_state.sel_dim = None
if 'sel_uid' not in st.session_state: st.session_state.sel_uid = None
if 'sel_reg' not in st.session_state: st.session_state.sel_reg = 'All'
if 'sel_dept' not in st.session_state: st.session_state.sel_dept = 'All'
if 'list_type' not in st.session_state: st.session_state.list_type = None 
if 'risk_factor_filter' not in st.session_state: st.session_state.risk_factor_filter = None 
if 'lang' not in st.session_state: st.session_state.lang = 'CN' # Default Language

def goto(view, uid=None, l_type=None, r_factor=None, dim=None):
    st.session_state.view = view
    if uid: st.session_state.sel_uid = uid
    if l_type: st.session_state.list_type = l_type
    if r_factor: st.session_state.risk_factor_filter = r_factor
    if dim: st.session_state.sel_dim = dim
    st.rerun()

# ==========================================
# 3. 翻译字典 (Translation)
# ==========================================
TRANS = {
    'CN': {
        'title': "GATE 全球人才指挥舱", 'mode': "CEO 智能决策视图", 
        'btn_back': "⬅️ 返回", 'btn_home': "↩️ 返回首页",
        'kpi_hc': "在职人数", 'kpi_cost': "人力成本(亿)", 'kpi_util': "工时饱和度", 'kpi_risk': "极高风险", 'kpi_hippo': "高潜人才",
        # Dimensions
        'dim_1': "📈 战略与资本", 'desc_1': "人效ROI · 成本结构 · 离岸外包",
        'dim_2': "💎 人才与绩效", 'desc_2': "9宫格 · 绩效分布 · 核心人才",
        'dim_3': "⏳ 远程与效能", 'desc_3': "工时饱和度 · 会议负荷 · ONA",
        'dim_4': "⚠️ 风险归因", 'desc_4': "离职预测 · 风险因子 · 预警",
        'dim_5': "🎯 招聘与配置", 'desc_5': "渠道质量 · 招聘漏斗 · Offer",
        'dim_6': "💰 人效与成本", 'desc_6': "薪酬带宽 · 人均产出 · 利润",
        'dim_7': "🌈 文化与多元化", 'desc_7': "DEI · 敬业度 · eNPS",
        'dim_8': "📚 培训与成长", 'desc_8': "技能覆盖 · 领导力 · 学习",
        'dim_9': "👑 梯队建设", 'desc_9': "继任计划 · 关键岗位 · 造血",
        
        'p_basic': "👤 基础信息", 'p_work': "💼 工作负荷", 'p_perf': "🏆 绩效潜能", 'p_comp': "💰 薪酬福利", 'p_history': "📜 历史记录", 'p_assets': "💻 资产技能",
        'list_risk_header': "🚨 极高风险人员透视", 'list_hipo_header': "💎 高潜人才透视", 
        'list_util_header': "⏳ 工时负荷透视", 'list_all_header': "📋 全员结构分析", 'list_cost_header': "💰 人力成本透视",
        'filter_reg': "区域筛选", 'filter_dept': "部门筛选", 'search_ph': "🔍 搜索员工姓名或ID...",
        'insight_risk': "点击热力图区块可筛选特定风险因子的人员名单。",
        'nav_prompt': "请选择分析维度 (Select Dimension)",
        
        # Charts Titles & Insights
        't1_c1': "全球人才密度分布", 'i1_c1': "关注高成本低产出区域，评估离岸外包机会。",
        't1_c2': "组织层级穿透", 'i1_c2': "红色越深代表该单元编制/成本压力越大。",
        't1_c3': "区域人效矩阵 (ROI)", 'i1_c3': "右上角为高投产比区域，左下角需战略优化。",
        't1_c4': "战略岗位满足率", 'i1_c4': "关键业务部门编制缺口监控。",
        't1_c5': "组织敏捷度评分", 'i1_c5': "工时方差越小，组织协同一致性越高。",
        't1_c6': "离岸/外包比例", 'i1_c6': "监控成本结构优化进度。",
        
        't2_c1': "人才九宫格 (9-Box)", 'i2_c1': "右上角明星需股权激励，左下角需PIP介入。",
        't2_c2': "薪酬公平性回归", 'i2_c2': "回归线上方为高溢价人员，需核实ROI。",
        't2_c3': "绩效等级分布", 'i2_c3': "检验绩效强制分布执行情况。",
        't2_c4': "高风险者绩效构成", 'i2_c4': "核心资产流失预警。",
        't2_c5': "新人绩效达标速度", 'i2_c5': "评估招聘质量与入职培训有效性。",
        't2_c6': "低绩效人员分布", 'i2_c6': "低绩效人员滞留时间越长，组织代谢越差。",

        't3_c1': "工时饱和度 vs 绩效", 'i3_c1': "识别'低效卷'与'高效做'。",
        't3_c2': "会议负荷分布", 'i3_c2': "异常高值代表协同冗余，需削减会议。",
        't3_c3': "协作网络密度 (ONA)", 'i3_c3': "颜色越深代表跨部门交互成本越高。",
        't3_c4': "深夜/周末加班强度", 'i3_c4': "合规风险与倦怠预警指标。",
        't3_c5': "工具产出效能比", 'i3_c5': "高薪人员是否承担了高负荷与高产出。",
        't3_c6': "审批流程效率", 'i3_c6': "管理层级越高工时越饱和。",

        't4_c1': "风险因子帕累托 (点击下钻)",
        't4_c2': "人才保留矩阵 (Risk vs Perf)", 'i4_c2': "关注右上角：高绩效+高风险的'红旗人才'。",
        't4_c3': "离职原因时序预测", 'i4_c3': "随着司龄增加，风险因子的变化趋势。",
        't4_c4': "薪酬竞争力 vs 风险", 'i4_c4': "低薪酬渗透率是否是离职主因。",
        't4_c5': "管理者影响分析", 'i4_c5': "哪个部门的管理者制造了最多风险？",
        't4_c6': "通勤/远程风险", 'i4_c6': "物理距离对稳定性的影响。",

        't5_c1': "渠道质量四象限", 'i5_c1': "右上角为金牛渠道。",
        't5_c2': "招聘漏斗转化率", 'i5_c2': "关注 Offer-to-Join 放弃率。",
        't5_c3': "试用期流失率", 'i5_c3': "早期甄选失败分析。",
        't5_c4': "面试官绩效产出", 'i5_c4': "哪个部门招的人绩效最好？",
        't5_c5': "Offer 竞争力分析", 'i5_c5': "新人薪酬是否打破了内部平衡。",
        't5_c6': "招聘周期", 'i5_c6': "业务响应速度监控。",

        't6_c1': "人均利润贡献", 'i6_c1': "斜率越陡峭，ROI越高。",
        't6_c2': "薪酬渗透率", 'i6_c2': "中位线过高代表成本压力。",
        't6_c3': "变动薪酬有效性", 'i6_c3': "奖金是否激励了高绩效？",
        't6_c4': "福利成本占比", 'i6_c4': "总体回报包结构分析。",
        't6_c5': "人力资本增值率", 'i6_c5': "每投入1元薪酬带来的利润。",
        't6_c6': "部门成本分布", 'i6_c6': "识别高成本低产出的异常单元。",

        't7_c1': "人口金字塔", 'i7_c1': "评估组织结构年轻化与性别平衡。",
        't7_c2': "eNPS 情绪热力图", 'i7_c2': "识别文化摩擦点。",
        't7_c3': "女性领导力占比", 'i7_c3': "玻璃天花板打破情况。",
        't7_c4': "代际融合度", 'i7_c4': "团队年龄跨度分析。",
        't7_c5': "价值观考核分布", 'i7_c5': "文化软指标落地情况。",
        't7_c6': "内部流动率", 'i7_c6': "人才市场活跃度。",

        't8_c1': "学习-绩效转化矩阵", 'i8_c1': "验证培训投入产出。",
        't8_c2': "关键技能覆盖率", 'i8_c2': "战略技能储备情况。",
        't8_c3': "学习型组织指数", 'i8_c3': "各部门学习氛围对比。",
        't8_c4': "技能缺口分析", 'i8_c4': "现状 vs 战略目标差距。",
        't8_c5': "领导力认证率", 'i8_c5': "管理者持证上岗情况。",
        't8_c6': "培训满意度", 'i8_c6': "课程质量反馈。",

        't9_c1': "继任者健康度", 'i9_c1': "Ready Now > 20% 为健康。",
        't9_c2': "关键岗位覆盖率", 'i9_c2': "关键岗位'裸奔'风险。",
        't9_c3': "关键岗位空缺周期", 'i9_c3': "核心岗位补位速度。",
        't9_c4': "内部提拔 vs 空降", 'i9_c4': "造血能力 vs 输血依赖。",
        't9_c5': "继任者保留率", 'i9_c5': "备胎保留情况。",
        't9_c6': "继任计划执行率", 'i9_c6': "IDP 落实情况。",

        'l_c1': "全员司龄分布", 'li_c1': "关注 1-3 年离职高峰期。",
        'l_c2': "职级金字塔", 'li_c2': "检查组织结构是否过于臃肿。",
        'l_c3': "管理幅度分析", 'li_c3': "管理者带宽分析。",
        'l_c4': "性别多元化", 'li_c4': "ESG 合规监控。",
        'l_c5': "关键人才流失率", 'li_c5': "核心层级稳定性。",
        'l_c6': "编制增长趋势", 'li_c6': "扩张速度分析。",
        
        'lc_c1': "部门成本分布", 'lic_c1': "识别成本中心。",
        'lc_c2': "职级薪酬结构", 'lic_c2': "固定 vs 变动薪酬。",
        'lc_c3': "平均人效趋势", 'lic_c3': "人均产出变化。",
        'lc_c4': "加班费占比", 'lic_c4': "隐性成本分析。",
        'lc_c5': "薪酬带宽红绿灯", 'lic_c5': "识别薪酬倒挂。",
        'lc_c6': "预算执行偏差", 'lic_c6': "实际支出 vs 预算。",

        'lu_c1': "工时-绩效四象限", 'liu_c1': "低效卷 vs 高效做。",
        'lu_c2': "部门热力图", 'liu_c2': "寻找过劳重灾区。",
        'lu_c3': "周末加班强度", 'liu_c3': "倦怠风险预警。",
        'lu_c4': "会议干扰度", 'liu_c4': "管理幅度对工时的影响。",
        'lu_c5': "产出效能比", 'liu_c5': "单位工时产出。",
        'lu_c6': "假期使用率", 'liu_c6': "员工休息情况。",

        'lr_c1': "风险因子帕累托", 'lir_c1': "核心离职原因。",
        'lr_c2': "高危部门分布", 'lir_c2': "风险集中度。",
        'lr_c3': "关键岗位暴露", 'lir_c3': "核心业务线的脆弱性。",
        'lr_c4': "薪酬竞争力分析", 'lir_c4': "钱没给够吗？",
        'lr_c5': "晋升停滞相关性", 'lir_c5': "职业发展瓶颈。",
        'lr_c6': "管理风格风险", 'lir_c6': "低敬业度聚集区。",

        'lh_c1': "能力画像雷达", 'lih_c1': "高潜人才长板分析。",
        'lh_c2': "留存风险预测", 'lih_c2': "多少明星想走？",
        'lh_c3': "晋升速度分析", 'lih_c3': "成长通道通畅度。",
        'lh_c4': "敬业度 (Engagement)", 'lih_c4': "Voice of star employees.",
        'lh_c5': "跨部门轮岗率", 'lih_c5': "复合型人才培养。",
        'lh_c6': "导师配对率", 'lih_c6': "资源投入情况。",
        
        'lrf_header': "⚠️ 风险因子透视: ", 'lrf_c1': "部门分布", 'lirf_c1': "影响范围。", 'lrf_c2': "职级分布", 'lirf_c2': "受影响层级。"
    },
    'EN': {
        'title': "GATE Command Center", 'mode': "CEO Intelligent View", 
        'btn_back': "⬅️ Back", 'btn_home': "↩️ Home",
        'kpi_hc': "Headcount", 'kpi_cost': "Cost (B)", 'kpi_util': "Utilization", 'kpi_risk': "Critical Risk", 'kpi_hippo': "HiPo Count",
        # Dimensions
        'dim_1': "📈 Strategy & Capital", 'desc_1': "ROI · Cost Structure · Offshore",
        'dim_2': "💎 Talent & Perf", 'desc_2': "9-Box · Distribution · Core Talent",
        'dim_3': "⏳ Efficiency & Remote", 'desc_3': "Utilization · Meetings · ONA",
        'dim_4': "⚠️ Risk Attribution", 'desc_4': "Attrition Forecast · Alerts",
        'dim_5': "🎯 Recruit & Staffing", 'desc_5': "Channels · Funnel · Offers",
        'dim_6': "💰 ROI & Cost", 'desc_6': "Pay Bands · Output · Profit",
        'dim_7': "🌈 Culture & DEI", 'desc_7': "Diversity · eNPS · Mobility",
        'dim_8': "📚 L&D & Growth", 'desc_8': "Skills · Leadership · Upskilling",
        'dim_9': "👑 Succession", 'desc_9': "Pipelines · Key Roles · Planning",
        
        'p_basic': "Basic Info", 'p_work': "Workload", 'p_perf': "Performance", 'p_comp': "Compensation", 'p_history': "History", 'p_assets': "Assets",
        'list_risk_header': "🚨 Critical Risk Analysis", 'list_hipo_header': "💎 HiPo Analysis", 
        'list_util_header': "⏳ Workload Analysis", 'list_all_header': "📋 Full Headcount Analysis", 'list_cost_header': "💰 Labor Cost Analysis",
        'filter_reg': "Region", 'filter_dept': "Department", 'search_ph': "🔍 Search Name/ID...",
        'insight_risk': "Click treemap tiles to filter by risk factor.",
        'nav_prompt': "Select Dimension for Deep Dive",
        
        # Chart Titles (Same as before)
        't1_c1': "Global Talent Density", 'i1_c1': "Focus on high cost/low output regions. Evaluate offshore options.",
        't1_c2': "Org Level Sunburst", 'i1_c2': "Darker red indicates higher cost/headcount pressure.",
        't1_c3': "Region ROI Matrix", 'i1_c3': "Top-right is high ROI. Bottom-left needs optimization.",
        't1_c4': "Strategic Role Fill Rate", 'i1_c4': "Monitor key department headcount gaps.",
        't1_c5': "Org Agility Score", 'i1_c5': "Lower util variance means better alignment.",
        't1_c6': "Offshore/Outsource Ratio", 'i1_c6': "Monitor cost structure optimization.",

        't2_c1': "Talent 9-Box Grid", 'i2_c1': "Top-right needs equity incentives. Bottom-left needs PIP.",
        't2_c2': "Pay Equity Regression", 'i2_c2': "Above line = high premium. Check ROI.",
        't2_c3': "Performance Distribution", 'i2_c3': "Check forced distribution compliance.",
        't2_c4': "High Performer Attrition", 'i2_c4': "Alert for core asset loss.",
        't2_c5': "Time to Productivity", 'i2_c5': "Assess hire quality and onboarding.",
        't2_c6': "Low Perf Resolution Time", 'i2_c6': "Longer retention of low performers = poor metabolism.",

        't3_c1': "Utilization vs Performance", 'i3_c1': "Identify 'Low Eff/High Grind' vs 'High Output'.",
        't3_c2': "Meeting Load Distribution", 'i3_c2': "High values indicate collaboration overhead.",
        't3_c3': "Collaboration Network (ONA)", 'i3_c3': "Darker colors = higher cross-dept interaction cost.",
        't3_c4': "Late Night/Weekend OT", 'i3_c4': "Compliance risk and burnout alert.",
        't3_c5': "Tool Efficiency Ratio", 'i3_c5': "Are high salaries justified by high output?",
        't3_c6': "Approval Efficiency", 'i3_c6': "Higher levels typically have higher utilization.",

        't4_c1': "Risk Factor Pareto (Click)",
        't4_c2': "Retention Matrix (Risk vs Perf)", 'i4_c2': "Focus Top-Right: High Perf + High Risk.",
        't4_c3': "Attrition Reason Forecast", 'i4_c3': "Risk factor trends as tenure increases.",
        't4_c4': "Compa-Ratio vs Risk", 'i4_c4': "Is low pay the main driver?",
        't4_c5': "Manager Impact Analysis", 'i4_c5': "Which dept managers drive the most risk?",
        't4_c6': "Commute/Remote Risk", 'i4_c6': "Impact of physical distance on stability.",

        't5_c1': "Channel Quality Matrix", 'i5_c1': "Top-Right is the Cash Cow channel.",
        't5_c2': "Recruitment Funnel", 'i5_c2': "Monitor Offer-to-Join drop-off rates.",
        't5_c3': "Probation Failure Rate", 'i5_c3': "Early selection failure analysis.",
        't5_c4': "Interviewer Efficacy", 'i5_c4': "Which dept hires the best performers?",
        't5_c5': "Offer Competitiveness", 'i5_c5': "Are new hires breaking internal equity?",
        't5_c6': "Hiring Cycle Time", 'i5_c6': "Business response speed monitor.",

        't6_c1': "Profit per Capita", 'i6_c1': "Steeper slope = Higher ROI.",
        't6_c2': "Compa-Ratio Distribution", 'i6_c2': "High median indicates cost pressure.",
        't6_c3': "Variable Pay Efficacy", 'i6_c3': "Does bonus correlate with high performance?",
        't6_c4': "Benefit Cost Ratio", 'i6_c4': "Total Rewards structure analysis.",
        't6_c5': "Human Capital Value Add", 'i6_c5': "Profit generated per $1 salary invested.",
        't6_c6': "Dept Cost Treemap", 'i6_c6': "Identify high cost / low output units.",

        't7_c1': "Population Pyramid", 'i7_c1': "Assess age structure and gender balance.",
        't7_c2': "eNPS Heatmap", 'i7_c2': "Identify cultural friction points.",
        't7_c3': "Female Leadership Ratio", 'i7_c3': "Glass ceiling analysis.",
        't7_c4': "Generational Diversity", 'i7_c4': "Team age span analysis.",
        't7_c5': "Value Assessment Dist", 'i7_c5': "Cultural soft-metric implementation.",
        't7_c6': "Internal Mobility Rate", 'i7_c6': "Internal talent market activity.",

        't8_c1': "Learning-Performance Matrix", 'i8_c1': "Validate training ROI.",
        't8_c2': "Key Skill Coverage", 'i8_c2': "Strategic skill reserve status.",
        't8_c3': "Learning Org Index", 'i8_c3': "Dept learning atmosphere comparison.",
        't8_c4': "Skill Gap Analysis", 'i8_c4': "Current vs Strategic Goal gap.",
        't8_c5': "Leadership Cert Rate", 'i8_c5': "Manager qualification status.",
        't8_c6': "Training Satisfaction", 'i8_c6': "Course quality feedback.",

        't9_c1': "继任者健康度", 'i9_c1': "Ready Now > 20% 为健康。",
        't9_c2': "关键岗位覆盖率", 'i9_c2': "关键岗位'裸奔'风险。",
        't9_c3': "关键岗位空缺周期", 'i9_c3': "核心岗位补位速度。",
        't9_c4': "内部提拔 vs 空降", 'i9_c4': "造血能力 vs 输血依赖。",
        't9_c5': "继任者保留率", 'i9_c5': "备胎保留情况。",
        't9_c6': "继任计划执行率", 'i9_c6': "IDP 落实情况。",

        'l_c1': "Tenure Distribution", 'li_c1': "Watch for 1-3 year exit peak.",
        'l_c2': "Level Pyramid", 'li_c2': "Check for organizational bloating.",
        'l_c3': "Span of Control", 'li_c3': "Manager bandwidth analysis.",
        'l_c4': "Gender Diversity", 'li_c4': "ESG compliance monitor.",
        'l_c5': "Key Talent Attrition", 'li_c5': "Core level stability.",
        'l_c6': "Headcount Growth", 'li_c6': "Expansion speed analysis.",
        
        'lc_c1': "Dept Cost Dist", 'lic_c1': "Identify cost centers.",
        'lc_c2': "Level Pay Structure", 'lic_c2': "Fixed vs Variable pay.",
        'lc_c3': "Avg Productivity Trend", 'lic_c3': "Output per capita trend.",
        'lc_c4': "Overtime Cost Ratio", 'lic_c4': "Hidden cost analysis.",
        'lc_c5': "Pay Band Traffic Light", 'lic_c5': "Identify pay inversion.",
        'lc_c6': "Budget Variance", 'lic_c6': "Actual vs Budget.",

        'lu_c1': "Util-Perf Quadrant", 'liu_c1': "Low Eff vs High Output.",
        'lu_c2': "Dept Heatmap", 'liu_c2': "Locate burnout zones.",
        'lu_c3': "Weekend OT Intensity", 'liu_c3': "Burnout risk alert.",
        'lu_c4': "Meeting Interference", 'liu_c4': "Span of control impact on util.",
        'lu_c5': "Output Efficiency Ratio", 'liu_c5': "Output per unit of work.",
        'lu_c6': "Leave Utilization", 'liu_c6': "Employee rest status.",

        'lr_c1': "Risk Factor Pareto", 'lir_c1': "Core attrition reasons.",
        'lr_c2': "High Risk Depts", 'lir_c2': "Risk concentration.",
        'lr_c3': "Key Role Exposure", 'lir_c3': "Vulnerability of core lines.",
        'lr_c4': "Pay Competitiveness", 'lir_c4': "Is money the issue?",
        'lr_c5': "Promotion Stagnation", 'lir_c5': "Career bottlenecks.",
        'lr_c6': "Management Style Risk", 'lir_c6': "Low engagement clusters.",

        'lh_c1': "Capability Radar", 'lih_c1': "HiPo strength analysis.",
        'lh_c2': "Retention Risk Forecast", 'lih_c2': "How many stars want to leave?",
        'lh_c3': "Promotion Velocity", 'lih_c3': "Growth channel fluidity.",
        'lh_c4': "Engagement", 'lih_c4': "Voice of star employees.",
        'lh_c5': "Cross-Dept Rotation", 'lih_c5': "Compound talent development.",
        'lh_c6': "Mentor Match Rate", 'lih_c6': "Resource investment status.",
        
        'lrf_header': "⚠️ Risk Factor View: ", 'lrf_c1': "Dept Dist", 'lirf_c1': "Impact Scope.", 'lrf_c2': "Level Dist", 'lirf_c2': "Impacted Levels."
    }
}
def T(key): return TRANS[st.session_state.lang].get(key, key)

def get_axis_map():
    mapping = {
        'Region':'区域', 'Dept':'部门', 'Level':'职级', 'Salary':'年薪(万)', 'Perf':'绩效等级', 
        'Risk':'风险', 'Util':'饱和度', 'Tenure':'司龄', 'Age':'年龄', 'Span':'管理幅度',
        'Cost_per_Hire':'单人招聘成本', 'Quality_of_Hire':'招聘质量', 'Recruit_Source':'渠道',
        'Train_Hours':'培训时长', 'Perf_Score':'绩效分', 'ROI_Ratio':'人效ROI',
        'Compa_Ratio':'薪酬渗透率', 'Bonus_Val':'奖金', 'Stock_Val':'股票', 'eNPS':'满意度',
        'Engagement':'敬业度', 'OT_Hours':'加班时长', 'Vacancy_Days':'空缺天数',
        'Risk_Score': '风险分', 'count': '人数', 'Factor': '风险因子'
    }
    return mapping if st.session_state.lang == 'CN' else {}

# --- CSS: GATE Design System 2.2 (Floating Button & Cards) ---
st.markdown("""
<style>
    /* 1. Global Reset & Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root {
        --bg-color: #F8FAFC; --card-bg: #FFFFFF;
        --text-primary: #1E293B; --text-secondary: #64748B;
        --brand-blue: #2563EB; --brand-light: #EFF6FF;
        --border-color: #E2E8F0;
        --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    }
    .stApp { background-color: var(--bg-color); font-family: "Inter", sans-serif; color: var(--text-primary); }
    .block-container { padding-top: 5rem !important; padding-bottom: 2rem !important; max-width: 100% !important; }
    header[data-testid="stHeader"], footer { display: none; }

    /* 2. Top Nav */
    .nav-header {
        background: rgba(255, 255, 255, 0.90); backdrop-filter: blur(12px);
        padding: 0 24px; border-bottom: 1px solid var(--border-color);
        position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
        display: flex; justify-content: space-between; align-items: center; height: 60px;
    }
    .nav-title { font-size: 16px; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 8px; }
    .nav-tag { background: #3B82F6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; box-shadow: 0 2px 5px rgba(59,130,246,0.3); }

    /* 3. KPI Cards */
    div.stButton > button {
        width: 100%; min-height: 72px !important; padding: 12px 16px !important;
        background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px;
        text-align: left; display: flex; flex-direction: column; justify-content: center;
        box-shadow: var(--shadow-xs); transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover { border-color: var(--brand-blue); transform: translateY(-2px); box-shadow: var(--shadow-sm); z-index: 10; }
    div.stButton > button p { color: var(--text-primary); font-family: "Inter", sans-serif !important; font-size: 14px !important; line-height: 1.4 !important; }

    /* 5. Chart Box */
    .chart-box { background: transparent; border: none; padding: 0; margin-bottom: 16px; }
    
    /* 6. Expert Insight */
    .expert-insight { background: rgba(241, 245, 249, 0.8); border-left: 3px solid var(--brand-blue); padding: 10px 14px; margin-top: 8px; border-radius: 0 4px 4px 0; font-size: 12px; color: var(--text-secondary); }
    .insight-title { font-weight: 700; color: var(--brand-blue); margin-right: 6px; font-size: 11px; text-transform: uppercase; }

    /* 7. Profile Card */
    .profile-card { background: white; border-radius: 12px; border: 1px solid var(--border-color); padding: 24px; margin-bottom: 24px; box-shadow: var(--shadow-xs); }
    .profile-section-header { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px; text-transform: uppercase; }
    .profile-label { font-size: 11px; color: #94A3B8; margin-bottom: 2px; }
    .profile-text { font-size: 14px; color: var(--text-primary); font-weight: 500; margin-bottom: 12px; }
    .tag-critical { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; padding: 2px 10px; border-radius: 100px; font-weight: 700; font-size: 11px; }

    /* 8. Floating Right-Side Back Button (Crucial Fix) */
    div.stButton.fixed-back-btn > button {
        position: fixed !important;
        right: 24px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 999999 !important;
        width: auto !important;
        height: auto !important;
        padding: 12px 20px !important;
        border-radius: 100px !important; /* Pill shape */
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
        color: var(--brand-blue) !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px);
    }
    div.stButton.fixed-back-btn > button:hover {
        background-color: #F8FAFC !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15) !important;
        transform: translateY(-50%) scale(1.05) !important;
    }
    
    /* v1.0 Smart Insight Card */
    .smart-insight-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #DBEAFE;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }
    .smart-insight-card::before {
        content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #2563EB;
    }
    .smart-header { font-size: 14px; font-weight: 700; color: #1E3A8A; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .smart-row { display: flex; gap: 12px; margin-bottom: 8px; font-size: 13px; line-height: 1.5; align-items: flex-start; }
    .smart-icon { min-width: 20px; font-size: 16px; }
    .smart-label { font-weight: 600; color: #3B82F6; margin-right: 4px; min-width: 35px;}
    .smart-text { color: #334155; }

    /* Hide Plotly Modebar & Adjust Inputs */
    .modebar { display: none !important; }
    div[data-baseweb="select"] > div { background-color: white; border-color: var(--border-color); border-radius: 6px; }
    .stTextInput input { border-radius: 6px; border-color: var(--border-color); }
    div[data-testid="stRadio"] { margin-top: 0px; }
    
    .dim-header {
        font-size: 20px; font-weight: 700; color: var(--text-primary); 
        margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);
        display: flex; align-items: center; gap: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 数据生成引擎
# ==========================================
@st.cache_data(ttl=3600)
def generate_data(lang='CN', n=2000):
    regions = {
        'APAC': {'cn':'亚太区', 'en':'APAC', 'lat':31.2, 'lon':121.4},
        'NA':   {'cn':'北美区', 'en':'North America', 'lat':37.7, 'lon':-122.4},
        'EMEA': {'cn':'欧非区', 'en':'EMEA', 'lat':51.5, 'lon':-0.1},
        'LATAM':{'cn':'拉美区', 'en':'LATAM', 'lat':-23.5, 'lon':-46.6}
    }
    depts = ['R&D', 'Sales', 'Product', 'Supply Chain', 'HR', 'Finance']
    levels = ['L1','L2','L3','L4','L5','L6','L7']
    
    # --- PERFORMANCE CONFIGURATION (STRICTLY ADJUSTED) ---
    perf_grades = ['SS','S','A+','A','B+','B','B-','C','D']
    perf_probs = [0.01, 0.04, 0.10, 0.15, 0.10, 0.35, 0.10, 0.05, 0.10] # Sum=1.0. SS+S=0.05.
    
    # --- PERFORMANCE SCORE MAPPING (UPDATED FOR NEW GRADES) ---
    score_map = {
        'SS': 5.0, 'S': 4.5,
        'A+': 4.2, 'A': 4.0,
        'B+': 3.5, 'B': 3.0, 'B-': 2.5,
        'C': 2.0, 'D': 1.0
    }
    
    skill_pool = ['Python', 'Java', 'PMP', 'AWS Arch', 'React', 'SQL', 'Tableau', 'CFA', 'Scrum Master', 'Docker', 'K8s', 'Go', 'Figma']
    sources = ['Referral', 'LinkedIn', 'Agency', 'Internal', 'Campus']
    
    data = []
    name_key = 'cn' if lang == 'CN' else 'en'
    
    for i in range(n):
        r_code = np.random.choice(list(regions.keys()), p=[0.4, 0.3, 0.2, 0.1])
        reg = regions[r_code][name_key]
        dept = np.random.choice(depts)
        lvl = np.random.choice(levels, p=[0.15, 0.25, 0.25, 0.15, 0.1, 0.08, 0.02])
        base = {'L1':30,'L2':50,'L3':80,'L4':150,'L5':280,'L6':500,'L7':1000}[lvl]
        salary = int(base * random.uniform(0.9, 1.3))
        
        # Apply the new distribution
        grade = np.random.choice(perf_grades, p=perf_probs)
        score = score_map[grade]
        
        util = min(1.6, round(np.random.normal(1.0, 0.15), 2))
        
        risk_s = 0; factors = []
        if grade in ['C','D']: risk_s+=40; factors.append("Low Perf")
        if util > 1.2: risk_s+=25; factors.append("Overworked")
        if salary < base*0.95: risk_s+=30; factors.append("Underpaid")
        if entropy := round(random.uniform(2.0, 9.0), 1) > 8.0: risk_s+=20; factors.append("High Entropy")
        risk_l = "Critical" if risk_s>=60 else ("High" if risk_s>=30 else "Low")
        
        ot_hours = int(np.random.normal(10, 5)) + (10 if util>1.1 else 0)
        span = random.randint(3, 15) if lvl >= 'L4' else 0
        engage = random.randint(1, 100)
        flight_risk = random.randint(1, 100)
        compa = round(salary / base, 2)
        qoh = random.randint(60, 100)
        cph = random.randint(10, 50)
        profit = int(salary * random.uniform(2.0, 8.0))
        roi = round((profit - salary)/salary, 2)
        vac_days = random.randint(0, 90)
        source = random.choice(sources)
        user_skills = ", ".join(random.sample(skill_pool, random.randint(1, 3)))
        
        data.append({
            "ID": f"G-{1000+i}", "Name": f"User_{i}", 
            "Region": reg, "Dept": dept, "Level": lvl,
            "Salary": salary, "Perf": grade, "Perf_Score": score, "Potential": random.choice([1,2,3,4,5]),
            "Util": util, "Risk_Level": risk_l, "Risk_Score": risk_s, "Risk_Factors": ", ".join(factors),
            "Tenure": round(random.uniform(0.5, 12), 1), "Age": random.randint(22, 55),
            "OT_Hours": ot_hours, "Span": span, "Engagement": engage, "Flight_Risk": flight_risk,
            "Gender": random.choice(['Male','Female']), "Recruit_Source": source,
            "Training_Hours": random.randint(0, 100), "Compa_Ratio": compa, "Quality_of_Hire": qoh, "Cost_per_Hire": cph,
            "Profit": profit, "ROI_Ratio": roi, "Vacancy_Days": vac_days, "eNPS": random.randint(-50, 100),
            "Last_Bonus": int(salary * 0.2), "Stock_Options": int(salary * 0.5) if lvl>'L4' else 0,
            "Successor_Status": random.choice(["Ready Now", "Ready 1-2Y", "None"]) if lvl > 'L4' else "N/A",
            "Certifications": user_skills,
            "Join_Date": (datetime.now() - timedelta(days=random.randint(100, 3000))).strftime("%Y-%m-%d"),
            "Email": f"user_{i}@gate.com", "Phone": "+86-139-0000-0000", "University": "Tsinghua", "Major": "CS",
            "Review_Note": "Key contributor.", "Laptop": "MacBook Pro", "Children": random.randint(0,2),
            "Project_A": "Project Alpha", "Project_B": "Project Beta", "Entropy": entropy, 
            "Marital": random.choice(["Single", "Married"]),
            "Lat": regions[r_code]['lat']+np.random.normal(0,1), "Lon": regions[r_code]['lon']+np.random.normal(0,1),
            "Headcount_Val": 1
        })
    return pd.DataFrame(data)

df_master = generate_data(st.session_state.lang)

# ==========================================
# 5. 顶部控制台
# ==========================================
st.markdown('<div class="nav-spacer"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="nav-header">
    <div class="nav-title">
        🦅 {T('title')} 
        <span class="nav-tag">v1.0 AI-Core</span>
    </div>
    <div style="font-size:13px; color:#64748B; font-weight:500;">{T('mode')}</div>
</div>
""", unsafe_allow_html=True)

def handle_search():
    term = st.session_state.search_query
    if term:
        res = df_master[df_master['Name'].str.contains(term, case=False) | df_master['ID'].str.contains(term, case=False)]
        if not res.empty:
            st.session_state.sel_uid = res.iloc[0]['ID']
            st.session_state.view = 'Profile'
            st.session_state.search_query = ""

c1, c2, c3, c4 = st.columns([1, 1, 0.8, 2], gap="small", vertical_alignment="bottom")

with c1:
    regions = ['All'] + list(df_master['Region'].unique())
    st.selectbox(T('filter_reg'), regions, key='sel_reg') 

with c2:
    current_reg = st.session_state.sel_reg
    if current_reg != 'All': 
        depts = ['All'] + list(df_master[df_master['Region']==current_reg]['Dept'].unique())
    else: 
        depts = ['All'] + list(df_master['Dept'].unique())
    if st.session_state.sel_dept not in depts: st.session_state.sel_dept = 'All'
    st.selectbox(T('filter_dept'), depts, key='sel_dept')

with c3:
    def on_lang_change():
        sel = st.session_state.lang_select
        st.session_state.lang = 'CN' if sel == '中文' else 'EN'

    idx = 0 if st.session_state.lang == 'CN' else 1
    
    st.radio(
        "Language", 
        ['中文', 'English'], 
        index=idx,
        horizontal=True, 
        label_visibility="collapsed", 
        key='lang_select',
        on_change=on_lang_change
    )

with c4:
    st.text_input(T('search_ph'), label_visibility="collapsed", placeholder=T('search_ph'), key="search_query", on_change=handle_search)

# Context Filtering
df_ctx = df_master.copy()
if st.session_state.sel_reg != 'All': df_ctx = df_ctx[df_ctx['Region'] == st.session_state.sel_reg]
if st.session_state.sel_dept != 'All': df_ctx = df_ctx[df_ctx['Dept'] == st.session_state.sel_dept]

# --- FORCE ORDER FOR PERFORMANCE GRADES ---
perf_order_asc = ['D', 'C', 'B-', 'B', 'B+', 'A', 'A+', 'S', 'SS']

def render_kpi_card(label, value, filter_type=None):
    btn_label = f"{label}\n{value}" 
    if st.button(btn_label, key=f"kpi_{label}", use_container_width=True):
        if filter_type: goto('List', l_type=filter_type)

def update_fig(fig, title=None):
    axis_map = get_axis_map()
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#1E293B", family="Inter", weight=600)),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=10, color="#64748B"),
        margin=dict(l=10, r=10, t=35, b=10),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter", bordercolor="#E2E8F0"),
        clickmode='event+select',
        dragmode='zoom', 
        autosize=True,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10))
    )
    fig.for_each_xaxis(lambda axis: axis.update(
        title_text=axis_map.get(axis.title.text, axis.title.text) if axis.title.text else None,
        showgrid=True, gridcolor="#F1F5F9", zeroline=False
    ))
    fig.for_each_yaxis(lambda axis: axis.update(
        title_text=axis_map.get(axis.title.text, axis.title.text) if axis.title.text else None,
        showgrid=True, gridcolor="#F1F5F9", zeroline=False
    ))
    return fig

def render_chart_box(title, fig, insight, key_suffix=""):
    with st.container():
        st.markdown(f"<div class='chart-box'>", unsafe_allow_html=True)
        unique_key = f"chart_{abs(hash(title + key_suffix + st.session_state.view))}"
        event = st.plotly_chart(
            update_fig(fig, title), 
            use_container_width=True, 
            on_select="rerun", 
            selection_mode="points", 
            key=unique_key,
            config={'displayModeBar': False} 
        )
        if event and event.selection and len(event.selection.points) > 0:
            point = event.selection.points[0]
            if 'customdata' in point and point['customdata']:
                target_uid = point['customdata'][0]
                if isinstance(target_uid, str) and target_uid.startswith('G-'):
                    goto('Profile', uid=target_uid)
            elif 'label' in point:
                if title == T('t4_c1'): 
                     goto('List', l_type='Risk_Factor', r_factor=point['label'])
        st.markdown(f"<div class='expert-insight'><span class='insight-title'>INSIGHT</span>{insight}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def render_dim_card(dim_key, title, desc):
    btn_txt = f"{title}\n{desc}"
    if st.button(btn_txt, key=f"btn_dim_{dim_key}", use_container_width=True):
        goto('Dimension_View', dim=dim_key)

# ==========================================
# 6. 核心黑科技：智能洞察系统逻辑 (AI INSIGHT - UPGRADED)
# ==========================================
def get_global_overview_insight(df):
    """专门针对首页5个核心KPI卡片生成的全局智能分析"""
    is_cn = st.session_state.lang == 'CN'
    
    # 1. 实时计算5个核心指标
    hc_val = len(df)
    cost_val = df['Salary'].sum() / 10000 # 亿
    util_val = df['Util'].mean()
    risk_count = len(df[df['Risk_Level']=='Critical'])
    hipo_count = len(df[df['Perf'].isin(['SS','S','A+'])])
    
    risk_rate = (risk_count / hc_val) * 100 if hc_val > 0 else 0
    hipo_rate = (hipo_count / hc_val) * 100 if hc_val > 0 else 0

    # 2. 逻辑引擎 - 动态生成分析文案
    obs_text, dia_text, act_text = "", "", ""
    
    # 场景判断
    if util_val > 0.98: # 对应截图中的 99%
        obs_text = f"📊 **[数据监测]** 组织工时饱和度高达 `{util_val*100:.0f}%` (警戒线 95%)，系统内无任何缓冲冗余。同时监测到极高风险人数 `{risk_count}` (占比 {risk_rate:.1f}%)，二者呈现强相关性。" if is_cn else f"Observed Saturation at `{util_val*100:.0f}%` (>95%), correlating with `{risk_count}` Critical Risks."
        dia_text = f"🔍 **[HR 专家归因]** 典型的 **'红线运行 (Redlining)'** 状态：过度追求人效导致组织弹性丧失。高潜人才 (HiPo) 在高压环境下出现职业倦怠，离职风险向核心层蔓延。" if is_cn else "Redlining status: Zero organizational slack causing burnout among HiPos and rising attrition risk."
        act_text = f"⚡ **[CEO 指令]** 1. 立即启动 **'熔断机制'**：冻结非核心项目立项；2. 针对 `{hipo_count}` 名高潜人才实施强制休假与留任访谈；3. 释放 5% 编制用于外部外包缓冲。" if is_cn else "1. Trigger 'Circuit Breaker': Freeze non-core projects. 2. Mandate leave for HiPos. 3. Open 5% headcount for contractors."
    
    elif risk_rate > 5.0: # 风险过高
        obs_text = f"📊 **[数据监测]** 极高风险人数达到 `{risk_count}` 人，占比 `{risk_rate:.1f}%`，远超行业健康基准 (2%)。主要集中在 `{df['Dept'].mode()[0]}` 部门。" if is_cn else f"Critical Risk count `{risk_count}` ({risk_rate:.1f}%) exceeds benchmark (2%), centered in `{df['Dept'].mode()[0]}`."
        dia_text = f"🔍 **[HR 专家归因]** **'价值-回报'** 错配：高潜人才占比 `{hipo_rate:.1f}%` 显示人才密度健康，但高风险主要源于现有激励体系未能覆盖高产出群体，导致核心资产动摇。" if is_cn else "Value-Reward Mismatch: Good HiPo density but incentive structure fails to retain top performers."
        act_text = f"⚡ **[CEO 指令]** 1. 授权 CHRO 在 48 小时内对 Top 50 风险人员进行 **'一对一'** 挽留；2. 启动专项 retention bonus 资金池；3. 彻查 `{df['Dept'].mode()[0]}` 管理层风格。" if is_cn else "1. Authorize CHRO for 1-on-1 retention talks within 48h. 2. Activate retention bonus pool. 3. Audit mgmt style."
    
    else: # 默认稳态
        obs_text = f"📊 **[数据监测]** 全局人效与成本结构处于稳态区间。在职 `{hc_val}` 人，人均产出效率维持在基准线以上，高潜人才储备充足 (`{hipo_rate:.1f}%`)。" if is_cn else f"Steady state: Headcount `{hc_val}` with healthy productivity and robust HiPo pipeline (`{hipo_rate:.1f}%`)."
        dia_text = f"🔍 **[HR 专家归因]** 组织处于良性代谢期，但需警惕工时饱和度 (`{util_val*100:.0f}%`) 上升趋势，避免长期疲劳积累。" if is_cn else "Healthy metabolism, but watch rising utilization trend to prevent future burnout."
        act_text = f"⚡ **[CEO 指令]** 维持当前战略节奏，重点优化 `{df['Region'].mode()[0]}` 区域的成本结构，提升 ROI。" if is_cn else "Maintain strategy. Focus on optimizing cost structure in key regions."

    return {'obs': obs_text, 'dia': dia_text, 'act': act_text}

def get_list_view_insight(l_type, df):
    """
    专门针对 'List' 视图（5个核心透视）生成的智能分析。
    l_type: 'Headcount', 'Cost', 'Util', 'Risk', 'HiPo'
    """
    is_cn = st.session_state.lang == 'CN'
    res = {'obs':"", 'dia':"", 'act':""}
    
    if l_type == 'Headcount': # 全员结构分析
        new_hires = len(df[df['Tenure'] < 1])
        avg_tenure = df['Tenure'].mean()
        span_l5 = df[df['Level']=='L5']['Span'].mean()
        
        res['obs'] = f"📊 **[数据监测]** 全员平均司龄 `{avg_tenure:.1f}` 年。入职不满 1 年的新员工占比 `{new_hires/len(df)*100:.1f}%`。L5 级管理者平均管理幅度 (Span) 为 `{span_l5:.1f}`。" if is_cn else f"Avg tenure `{avg_tenure:.1f}` yrs. New hires (<1y) `{new_hires/len(df)*100:.1f}%`. L5 Avg Span `{span_l5:.1f}`."
        if span_l5 < 5:
            res['dia'] = "🔍 **[OD 专家归因]** 组织呈现 **'腰部肥大'** 特征：中层管理幅度过窄 (Span < 5)，导致汇报层级冗余，决策链条过长，存在严重的 'Middle Management Bloat' 风险。" if is_cn else "Middle Management Bloat: Narrow span of control (<5) causing hierarchy redundancy and slow decision making."
            res['act'] = "⚡ **[CEO 指令]** 1. 启动 **'组织扁平化'** 专项：合并编制小于 5 人的微型团队；2. 冻结 L5/L6 级管理岗外部招聘，优先内部提拔高潜 IC (独立贡献者)。" if is_cn else "1. Merge teams < 5 members. 2. Freeze external L5/L6 hiring, prioritize internal IC promotion."
        else:
            res['dia'] = "🔍 **[OD 专家归因]** 组织结构处于快速扩张后的震荡期，新老员工比例适中，但需关注新员工的文化融合问题。" if is_cn else "Organization in post-expansion phase. Watch for cultural integration of new hires."
            res['act'] = "⚡ **[CEO 指令]** 强化 **'导师制 (Mentorship)'** 覆盖率，确保每一位新员工在试用期内都有指定 Mentor。" if is_cn else "Enforce Mentorship program coverage for all new hires."

    elif l_type == 'Cost': # 人力成本透视
        rd_cost = df[df['Dept']=='R&D']['Salary'].sum()
        total_cost = df['Salary'].sum()
        rd_ratio = rd_cost / total_cost * 100
        
        res['obs'] = f"📊 **[数据监测]** R&D 部门消耗了全公司 `{rd_ratio:.1f}%` 的人力成本预算。全员薪酬变动部分 (Bonus) 与绩效评分的相关系数仅为 `0.35` (弱相关)。" if is_cn else f"R&D consumes `{rd_ratio:.1f}%` of budget. Bonus correlation with performance is weak (0.35)."
        res['dia'] = "🔍 **[C&B 专家归因]** **'资源错配风险'**：高成本投入并未精准流向高产出群体。刚性兑付文化导致奖金变成了'延迟发放的固定工资'，失去了激励杠杆作用。" if is_cn else "Resource Misallocation: Fixed cost rigidity is high. Bonuses act as deferred salary rather than performance incentives."
        res['act'] = "⚡ **[CFO 指令]** 1. 下季度实施 **'零基预算 (Zero-Based Budgeting)'**；2. 重构奖金公式，将部门 ROI 系数权重提升至 40%；3. 审计 R&D 部门的人效产出比。" if is_cn else "1. Implement Zero-Based Budgeting. 2. Increase Dept ROI weight in bonus to 40%. 3. Audit R&D ROI."

    elif l_type == 'Util': # 工时负荷透视
        over_users = len(df[df['Util']>1.2])
        weekend_ot = df['OT_Hours'].mean()
        
        res['obs'] = f"📊 **[数据监测]** 监测到 `{over_users}` 名员工处于极度过劳状态 (Util > 120%)，平均周末加班时长达 `{weekend_ot:.1f}` 小时，主要集中在产品交付周期末端。" if is_cn else f"`{over_users}` users at extreme burnout (>120%), avg weekend OT `{weekend_ot:.1f}`h, mostly in delivery cycles."
        res['dia'] = "🔍 **[效能专家归因]** **'伪勤奋与流程内耗'**：高工时主要由跨部门协作摩擦和无效会议驱动，而非核心业务产出。存在用'战术上的勤奋'掩盖'战略上的懒惰'现象。" if is_cn else "False Diligence: High hours driven by friction and meetings, not core output. Tactical busyness masking strategic laziness."
        res['act'] = "⚡ **[COO 指令]** 1. 强制实施 **'深度工作时间 (Deep Work Block)'**：每天 10:00-12:00 禁止会议；2. 对持续 3 周 Util > 1.2 的团队进行强制调休介入。" if is_cn else "1. Mandate 'Deep Work' (No meetings 10-12am). 2. Forced time-off for teams with >3 weeks of high burnout."

    elif l_type == 'Risk': # 极高风险人员透视
        top_factor = df['Risk_Factors'].mode()[0] if not df['Risk_Factors'].empty else "None"
        risk_dept = df['Dept'].value_counts().idxmax()
        
        res['obs'] = f"📊 **[数据监测]** 极高风险人员的首要驱动因子为 `{top_factor}`。风险在 `{risk_dept}` 部门呈现聚集性爆发趋势，单点突破可能引发链式离职反应。" if is_cn else f"Top risk factor: `{top_factor}`. Risk clustering in `{risk_dept}`, threatening chain attrition."
        res['dia'] = f"🔍 **[HRBP 专家归因]** **'核心阵地失守'**：`{risk_dept}` 作为业务关键部门，其核心骨干因 `{top_factor}` 产生集体动摇，说明该领域的竞争对手正在进行针对性挖角或内部管理生态恶化。" if is_cn else f"Core Defense Failure: Key talent in `{risk_dept}` shaking due to `{top_factor}`, indicating targeted poaching or toxic micro-culture."
        res['act'] = f"⚡ **[CEO 指令]** 1. 对 `{risk_dept}` 立即启动 **'薪酬竞争力专项审计'**；2. 建立离职预警 '红名单'，CEO 直接关注 Top 10 核心人才动态。" if is_cn else f"1. Launch Comp Audit for `{risk_dept}`. 2. CEO to monitor Top 10 risk talent directly."

    elif l_type == 'HiPo': # 高潜人才透视
        retention_risk = len(df[df['Flight_Risk']>70])
        promo_rate = len(df[df['Tenure']<2]) / len(df) # 模拟
        
        res['obs'] = f"📊 **[数据监测]** 高潜人才库中，`{retention_risk}` 人存在高离职风险。数据显示，高潜人员的跨部门轮岗率仅为 `12%`，低于行业优秀的 `25%`。" if is_cn else f"`{retention_risk}` HiPos at flight risk. Rotation rate is 12% (Benchmark 25%)."
        res['dia'] = "🔍 **[人才管理专家归因]** **'人才囤积 (Talent Hoarding)'**：部门管理者倾向于将高潜人才'私有化'，阻碍了其在组织内部的流动与成长，导致高潜因发展受限而寻求外部机会。" if is_cn else "Talent Hoarding: Managers locking HiPos in silos, blocking growth and driving external attrition."
        res['act'] = "⚡ **[CHO 指令]** 1. 建立 **'内部人才市场'**，允许高潜人才在服务满 18 个月后单方面发起转岗申请；2. 将'人才输送率'纳入管理者 KPI。" if is_cn else "1. Launch Internal Talent Market allowing unilateral transfer after 18m. 2. Add 'Talent Export Rate' to Manager KPI."

    return res

def get_smart_insight(dim, df):
    is_cn = st.session_state.lang == 'CN'
    
    # 初始化默认值
    res = {
        'obs': "📊 **[数据监测]** 异常值检测算法未发现显著偏离基准的指标。",
        'dia': "🔍 **[归因模型]** 当前维度处于稳态，无需干预。",
        'act': "⚡ **[决策建议]** 建议维持当前管理策略，持续监控下个周期波动。"
    } if is_cn else {
        'obs': "Data Monitor: No significant anomalies detected.",
        'dia': "Diagnosis: Metrics are within baseline thresholds.",
        'act': "Action: Maintain current strategy."
    }
    
    # 逻辑引擎 (Logic Engine)
    if dim == 'dim_1': # 战略与资本 (Strategy) - 严格复刻截图内容
        low_roi_reg = df.groupby('Region')['ROI_Ratio'].mean().idxmin()
        high_cost_dept = df.groupby('Dept')['Salary'].sum().idxmax()
        if low_roi_reg:
            res['obs'] = f"📊 **[数据监测]** 区域人效矩阵显示 `{low_roi_reg}` 区域的人效 ROI 低于全球均值 18%，且 `{high_cost_dept}` 部门的人力成本占比已达预算红线。" if is_cn else f"Observed `{low_roi_reg}` ROI is >18% below avg, with `{high_cost_dept}` hitting budget cap."
            res['dia'] = f"🔍 **[CEO 战略归因]** 组织结构臃肿（L5+ 占比 > 25%）与离岸外包杠杆率过低（< 10%）是导致利润率被侵蚀的核心结构性原因。" if is_cn else "Structural bloat (L5+ >25%) and low offshore leverage (<10%) are eroding margins."
            res['act'] = f"⚡ **[CEO 指令]** 1. 立即冻结 `{low_roi_reg}` 所有 L4+ 招聘；2. 启动 **'Project Move'**，目标在 Q4 前将 15% 的非核心 HC 迁移至低成本中心。" if is_cn else "1. Freeze L4+ hiring in region. 2. Launch 'Project Move' to shift 15% headcount to offshore hubs by Q4."

    elif dim == 'dim_2': # 人才与绩效 (Talent)
        stars = len(df[df['Perf'].isin(['SS','S'])])
        low_perf = len(df[df['Perf'].isin(['C','D'])])
        ratio = round(stars/low_perf, 1) if low_perf > 0 else 0
        if ratio < 3: 
            res['obs'] = f"📊 **[数据监测]** 9宫格分布显示人才密度稀释：明星员工(Star)与低绩效者(Iceberg)的比例仅为 `{ratio}:1` (健康基准 > 3:1)。" if is_cn else f"Talent density alert: Star-to-Iceberg ratio is only `{ratio}:1` (Benchmark > 3:1)."
            res['dia'] = "🔍 **[HR 专家归因]** 绩效区分度失效（Mediocrity Tolerance），导致 '大锅饭' 现象，无法有效激励高潜人才，同时低绩效人员代谢受阻。" if is_cn else "Lack of performance differentiation is causing mediocrity tolerance and failing to incentivize HiPos."
            res['act'] = "⚡ **[OD 专家建议]** 1. 实施 **'强制分布 (Forced Ranking)'** 复核；2. 对 Top 20% 实施股权差异化激励；3. 对持续低绩效者启动 PIP 加速程序。" if is_cn else "1. Enforce Forced Ranking calibration. 2. Differentiate equity for Top 20%. 3. Accelerate PIP for bottom performers."

    elif dim == 'dim_3': # 效能 (Efficiency)
        high_util_dept = df.groupby('Dept')['Util'].mean().idxmax()
        avg_util = df.groupby('Dept')['Util'].mean().max()
        if avg_util > 1.1:
            res['obs'] = f"📊 **[数据监测]** `{high_util_dept}` 部门的平均工时饱和度突破 `{avg_util:.2f}` (警戒线 1.1)，且人均周会议时长超过 15 小时。" if is_cn else f"`{high_util_dept}` utilization hit `{avg_util:.2f}` (Alert > 1.1) with >15h/week meeting load."
            res['dia'] = "🔍 **[效能专家归因]** 典型的 **'协作过载 (Collaboration Overload)'**：碎片化会议导致深度工作时间不足 30%，迫使员工通过延长工时（虚假勤奋）来完成核心产出。" if is_cn else "Collaboration Overload: Fragmented meetings (<30% Deep Work) forcing extended hours for core delivery."
            res['act'] = f"⚡ **[COO 指令]** 1. 在 `{high_util_dept}` 试点 **'无会议周三'**；2. 部署 RPA 机器人接管 20% 的报表类重复性工作；3. 审查 L5+ 管理者的控制幅度 (Span)。" if is_cn else "1. Pilot 'No-Meeting Wednesday'. 2. Deploy RPA for 20% repetitive tasks. 3. Review Span of Control for L5+ managers."

    elif dim == 'dim_4': # 风险 (Risk)
        risk_cnt = len(df[df['Risk_Level']=='Critical'])
        main_factor = df['Risk_Factors'].mode()[0] if not df['Risk_Factors'].empty else "Unknown"
        if risk_cnt > 0:
            res['obs'] = f"📊 **[数据监测]** 预测模型识别出 `{risk_cnt}` 名 '极高风险' 核心人才，主要集中在研发与产品序列，主要风险因子为 `{main_factor}`。" if is_cn else f"Predictive model flagged `{risk_cnt}` Critical Risk core talents, mainly driven by `{main_factor}`."
            res['dia'] = "🔍 **[HRBP 专家归因]** **'高能耗-低回报'** 错配：核心骨干长期承担超额负荷 (Util > 1.2)，但薪酬渗透率 (CR) 滞后于市场 15% 以上，导致外部诱惑抵抗力下降。" if is_cn else "High Burnout/Low Reward Mismatch: Key talent overworked (Util > 1.2) with Compa-Ratio lagging market by >15%."
            res['act'] = "⚡ **[CHRO 建议]** 1. 立即启动 **'关键人才留任访谈 (Stay Interview)'**；2. 开启专项调薪窗口，使用 Retention Bonus (留任奖金) 进行定点防御；3. 强制休假干预。" if is_cn else "1. Launch Stay Interviews immediately. 2. Open off-cycle salary review with Retention Bonuses. 3. Mandate forced leave."

    elif dim == 'dim_5': # 招聘 (Recruiting)
        res['obs'] = f"📊 **[数据监测]** 招聘漏斗显示 'Offer-to-Join' 放弃率在 `{random.randint(15,25)}%` 高位震荡，特别是技术类岗位。" if is_cn else "Offer-to-Join drop-off rate hovering at high levels, esp. for Tech roles."
        res['dia'] = "🔍 **[招聘专家归因]** 雇主品牌竞争力在薪酬谈判阶段疲软，且面试流程过长（平均 `{random.randint(30,45)}` 天），导致在与竞对抢人时处于劣势。" if is_cn else "Weak employer value proposition in offer stage + long cycle time causing loss to competitors."
        res['act'] = "⚡ **[招聘总监建议]** 1. 优化面试流程，承诺 **'48小时反馈制'**；2. 授权 Hiring Manager 在薪酬带宽 75分位内的即时决策权；3. 增加签约奖金 (Sign-on Bonus)。" if is_cn else "1. Optimize process to '48h Feedback'. 2. Authorize Managers for instant decisions within 75th percentile. 3. Add Sign-on Bonuses."

    elif dim == 'dim_6': # 成本 (Cost)
        inv_pay = df[df['Compa_Ratio'] > 1.2]
        cnt = len(inv_pay)
        if cnt > 10:
            res['obs'] = f"📊 **[数据监测]** 薪酬带宽分析发现 `{cnt}` 名员工的薪酬渗透率 (Compa-Ratio) 超过 1.2，即工资已显著高于岗位价值上限。" if is_cn else f"Detected `{cnt}` employees with Compa-Ratio > 1.2 (Overpaid vs Role Value)."
            res['dia'] = "🔍 **[C&B 专家归因]** 存在严重的 **'薪酬倒挂与沉淀'**：部分老员工薪酬随年资自然增长但产出停滞，导致部门薪酬包被低效锁定，挤压了新人的定薪空间。" if is_cn else "Pay Inversion & Stagnation: Legacy high costs/low output locking budget, squeezing cap for new hires."
            res['act'] = "⚡ **[CFO/CHRO 联合建议]** 1. 对 CR > 1.2 人员冻结普调，改用一次性奖金 (Lump Sum)；2. 实施 **'人效清洗'**：要求部门在 Q3 前解决 10% 的低ROI 人力库存。" if is_cn else "1. Freeze base pay for CR > 1.2, use Lump Sum bonuses. 2. Mandate 'ROI Clean-up' of 10% low-efficiency inventory by Q3."
            
    elif dim == 'dim_9': # 继任 (Succession)
        ready_now = len(df[df['Successor_Status']=='Ready Now'])
        total_lead = len(df[df['Level'].isin(['L5','L6','L7'])])
        rate = round(ready_now / total_lead * 100, 1) if total_lead > 0 else 0
        if rate < 15:
            res['obs'] = f"📊 **[数据监测]** 关键岗位继任健康度仅为 `{rate}%` (红线 < 15%)，意味着每 10 个关键岗位中，仅有不到 2 个有即战力备选。" if is_cn else f"Succession Health is critical at `{rate}%` (<15% Red Line). Key roles are exposed."
            res['dia'] = "🔍 **[人才管理专家归因]** **'造血功能衰竭'**：内部提拔率低于 30%，过度依赖外部空降导致文化稀释与磨合成本激增（空降失败率通常 > 40%）。" if is_cn else "Internal Pipeline Failure: Promotion rate < 30%, over-reliance on external hires causing culture dilution and high failure risk."
            res['act'] = "⚡ **[CEO 指令]** 1. 将 **'人才培养指数'** 纳入 L6+ 管理者绩效红线（权重 20%）；2. 启动 **'高潜加速器 (HiPo Accelerator)'** 项目，强制实施跨部门轮岗。" if is_cn else "1. Tie 'Talent Dev Index' to L6+ KPI (20% weight). 2. Launch 'HiPo Accelerator' with mandatory rotation."

    return res

# ==========================================
# 7. 主视图路由 (View Routing)
# ==========================================

# --- A. 指挥舱首页 (Overview) ---
if st.session_state.view == 'Overview':
    
    # 1. 渲染 5 个 KPI 卡片 (对应截图)
    k1, k2, k3, k4, k5 = st.columns(5, gap="small")
    hc = len(df_ctx)
    cost = df_ctx['Salary'].sum() / 10000
    util = df_ctx['Util'].mean()
    risk = len(df_ctx[df_ctx['Risk_Level']=='Critical'])
    hipo = len(df_ctx[df_ctx['Perf'].isin(['SS','S','A+'])])
    
    with k1: render_kpi_card(T('kpi_hc').upper(), f"{hc}", 'Headcount')
    with k2: render_kpi_card(T('kpi_cost').upper(), f"¥{cost:.2f}", 'Cost')
    with k3: render_kpi_card(T('kpi_util').upper(), f"{util*100:.0f}%", 'Util')
    with k4: render_kpi_card(T('kpi_risk').upper(), f"{risk}", 'Risk')
    with k5: render_kpi_card(T('kpi_hippo').upper(), f"{hipo}", 'HiPo')
    
    # 2. 插入全局智能分析模块 (对应截图需求的 5 个核心维度分析)
    si_global = get_global_overview_insight(df_ctx)
    st.markdown(f"""
    <div class="smart-insight-card" style="margin-top: 12px; margin-bottom: 24px;">
        <div class="smart-header">
            <span>⚡ SMART INSIGHT (v1.0 Alpha) - Executive Summary</span>
        </div>
        <div class="smart-row">
            <div class="smart-icon">👁️</div>
            <div><span class="smart-text">{si_global['obs']}</span></div>
        </div>
        <div class="smart-row">
            <div class="smart-icon">🧬</div>
            <div><span class="smart-text">{si_global['dia']}</span></div>
        </div>
        <div class="smart-row">
            <div class="smart-icon">⚡</div>
            <div><span class="smart-text">{si_global['act']}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown(f"#### {T('nav_prompt')}")
    
    g1, g2, g3 = st.columns(3, gap="small")
    with g1:
        render_dim_card('dim_1', T('dim_1'), T('desc_1'))
        render_dim_card('dim_4', T('dim_4'), T('desc_4'))
        render_dim_card('dim_7', T('dim_7'), T('desc_7'))
    with g2:
        render_dim_card('dim_2', T('dim_2'), T('desc_2'))
        render_dim_card('dim_5', T('dim_5'), T('desc_5'))
        render_dim_card('dim_8', T('dim_8'), T('desc_8'))
    with g3:
        render_dim_card('dim_3', T('dim_3'), T('desc_3'))
        render_dim_card('dim_6', T('dim_6'), T('desc_6'))
        render_dim_card('dim_9', T('dim_9'), T('desc_9'))

# --- B. 维度详情视图 (Dimension View) ---
elif st.session_state.view == 'Dimension_View':
    
    if st.button(T('btn_home'), key="btn_back_floating_dim", type="secondary"): 
        goto('Overview')
    
    st.components.v1.html(f"""
    <script>
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {{
            if (btn.innerText.includes('{T('btn_home')}')) {{
                btn.parentElement.classList.add('fixed-back-btn');
            }}
        }});
    </script>
    """, height=0)

    curr_dim = st.session_state.sel_dim
    st.markdown(f"<div class='dim-header'>{T(curr_dim)}</div>", unsafe_allow_html=True)
    
    # --- v1.0 NEW FEATURE: Smart Insight Block ---
    si = get_smart_insight(curr_dim, df_ctx)
    st.markdown(f"""
    <div class="smart-insight-card">
        <div class="smart-header">
            <span>⚡ SMART INSIGHT (v1.0 Alpha) - Multi-Expert View</span>
        </div>
        <div class="smart-row">
            <div class="smart-icon">👁️</div>
            <div><span class="smart-text">{si['obs']}</span></div>
        </div>
        <div class="smart-row">
            <div class="smart-icon">🧬</div>
            <div><span class="smart-text">{si['dia']}</span></div>
        </div>
        <div class="smart-row">
            <div class="smart-icon">⚡</div>
            <div><span class="smart-text">{si['act']}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ---------------------------------------------

    if curr_dim == 'dim_1': 
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('t1_c1'), px.scatter_geo(df_ctx, lat='Lat', lon='Lon', color='Region', size='Salary', projection='natural earth', hover_name='Name', custom_data=['ID'], labels=get_axis_map()), T('i1_c1'))
        with c2: render_chart_box(T('t1_c2'), px.sunburst(df_ctx, path=['Region','Dept'], values='Salary'), T('i1_c2'))
        with c3: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t1_c3'), px.scatter(df_ctx, x='Salary', y='Perf', color='Region', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i1_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t1_c4'), px.bar(df_ctx.groupby('Dept').size().reset_index(), x='Dept', y=0), T('i1_c4'))
        with c5: render_chart_box(T('t1_c5'), px.box(df_ctx, x='Dept', y='Util', points='all', custom_data=['ID']), T('i1_c5'))
        with c6: render_chart_box(T('t1_c6'), px.pie(df_ctx, names='Region', hole=0.6), T('i1_c6'))

    elif curr_dim == 'dim_2': 
        c1, c2, c3 = st.columns(3)
        with c1: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t2_c1'), px.scatter(df_ctx, x='Perf', y='Potential', color='Risk_Level', size_max=15, category_orders={'Perf': perf_order_asc}, hover_name='Name', custom_data=['ID']), T('i2_c1'))
        with c2: render_chart_box(T('t2_c2'), px.scatter(df_ctx, x='Tenure', y='Salary', color='Level', opacity=0.7, hover_name='Name', custom_data=['ID']), T('i2_c2'))
        with c3: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t2_c3'), px.histogram(df_ctx, x='Perf', color='Dept', category_orders={'Perf': perf_order_asc}), T('i2_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: 
            # Replaced Perf_Score with Perf distribution
            render_chart_box(T('t2_c4'), px.histogram(df_ctx[df_ctx['Risk_Level']=='Critical'], x='Dept', color='Perf', category_orders={'Perf': perf_order_asc}), T('i2_c4'))
        with c5: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t2_c5'), px.scatter(df_ctx[df_ctx['Tenure']<1], x='Tenure', y='Perf', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i2_c5'))
        with c6: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t2_c6'), px.histogram(df_ctx[df_ctx['Perf'].isin(['C','D'])], x='Dept', color='Perf', category_orders={'Perf': perf_order_asc}), T('i2_c6'))

    elif curr_dim == 'dim_3': 
        c1, c2, c3 = st.columns(3)
        with c1: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t3_c1'), px.scatter(df_ctx, x='Util', y='Perf', color='Dept', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i3_c1'))
        with c2: render_chart_box(T('t3_c2'), px.box(df_ctx, y='OT_Hours', x='Level', points='all', custom_data=['ID']), T('i3_c2'))
        with c3: render_chart_box(T('t3_c3'), px.density_heatmap(df_ctx, x='Dept', y='Region', z='Util'), T('i3_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t3_c4'), px.histogram(df_ctx, x='OT_Hours', color='Dept'), T('i3_c4'))
        with c5: 
            # Replaced Perf_Score with Perf (removed size mapping)
            render_chart_box(T('t3_c5'), px.scatter(df_ctx, x='Salary', y='Util', color='Perf', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i3_c5'))
        with c6: render_chart_box(T('t3_c6'), px.bar(df_ctx.groupby('Level')['Util'].mean().reset_index(), x='Level', y='Util'), T('i3_c6'))

    elif curr_dim == 'dim_4': 
        c1, c2, c3 = st.columns(3)
        with c1: 
            sub_factors = []
            for rs in df_ctx['Risk_Factors']: sub_factors.extend([x.strip() for x in rs.split(',')])
            df_risk = pd.DataFrame(sub_factors, columns=['F'])['F'].value_counts().reset_index()
            df_risk.columns = ['F','C']
            render_chart_box(T('t4_c1'), px.treemap(df_risk, path=['F'], values='C', color='C', color_continuous_scale='Reds'), T('insight_risk'))
        with c2: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t4_c2'), px.scatter(df_ctx, x='Risk_Score', y='Perf', color='Risk_Level', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i4_c2'))
        with c3: render_chart_box(T('t4_c3'), px.scatter(df_ctx.sort_values('Tenure'), x='Tenure', y='Risk_Score', color='Risk_Level', custom_data=['ID']), T('i4_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t4_c4'), px.box(df_ctx, x='Risk_Level', y='Compa_Ratio', points='all', custom_data=['ID']), T('i4_c4'))
        with c5: render_chart_box(T('t4_c5'), px.histogram(df_ctx[df_ctx['Risk_Level']=='Critical'], x='Dept'), T('i4_c5'))
        with c6: render_chart_box(T('t4_c6'), px.scatter(df_ctx, x='Region', y='Risk_Score', custom_data=['ID']), T('i4_c6'))

    elif curr_dim == 'dim_5': 
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('t5_c1'), px.scatter(df_ctx, x='Cost_per_Hire', y='Quality_of_Hire', color='Recruit_Source', custom_data=['ID']), T('i5_c1'))
        with c2: render_chart_box(T('t5_c2'), px.funnel(pd.DataFrame({'Stg':['Apply','Screen','Interview','Offer','Hire'],'Val':[1000,500,200,80,60]}), y='Stg', x='Val'), T('i5_c2'))
        with c3: render_chart_box(T('t5_c3'), px.pie(df_ctx[df_ctx['Tenure']<0.5], names='Risk_Level'), T('i5_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: 
            # Replaced Perf_Score with Perf distribution
            render_chart_box(T('t5_c4'), px.histogram(df_ctx[df_ctx['Tenure']<1], x='Dept', color='Perf', category_orders={'Perf': perf_order_asc}), T('i5_c4'))
        with c5: render_chart_box(T('t5_c5'), px.box(df_ctx[df_ctx['Tenure']<1], y='Compa_Ratio', points='all', custom_data=['ID']), T('i5_c5'))
        with c6: render_chart_box(T('t5_c6'), px.histogram(df_ctx, x='Tenure'), T('i5_c6'))

    elif curr_dim == 'dim_6': 
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('t6_c1'), px.scatter(df_ctx, x='Salary', y='Profit', color='Dept', custom_data=['ID']), T('i6_c1'))
        with c2: render_chart_box(T('t6_c2'), px.box(df_ctx, x='Level', y='Compa_Ratio', points='all', custom_data=['ID']), T('i6_c2'))
        with c3: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t6_c3'), px.scatter(df_ctx, x='Last_Bonus', y='Perf', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i6_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t6_c4'), px.pie(df_ctx, names='Level', values='Salary'), T('i6_c4'))
        with c5: render_chart_box(T('t6_c5'), px.bar(df_ctx.groupby('Region')['Profit'].sum().reset_index(), x='Region', y='Profit'), T('i6_c5'))
        with c6: render_chart_box(T('t6_c6'), px.treemap(df_ctx, path=['Dept','Level'], values='Salary'), T('i6_c6'))

    elif curr_dim == 'dim_7': 
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('t7_c1'), px.histogram(df_ctx, x='Age', color='Gender'), T('i7_c1'))
        with c2: render_chart_box(T('t7_c2'), px.scatter(df_ctx, x='Tenure', y='Engagement', color='Dept', custom_data=['ID']), T('i7_c2'))
        with c3: render_chart_box(T('t7_c3'), px.pie(df_ctx[df_ctx['Level']>'L4'], names='Gender'), T('i7_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t7_c4'), px.box(df_ctx, x='Dept', y='Age', points='all', custom_data=['ID']), T('i7_c4'))
        with c5: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t7_c5'), px.histogram(df_ctx, x='Perf', category_orders={'Perf': perf_order_asc}), T('i7_c5'))
        with c6: render_chart_box(T('t7_c6'), px.bar(df_ctx.groupby('Region').size().reset_index(), x='Region', y=0), T('i7_c6'))

    elif curr_dim == 'dim_8': 
        c1, c2, c3 = st.columns(3)
        with c1: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('t8_c1'), px.scatter(df_ctx, x='Training_Hours', y='Perf', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('i8_c1'))
        with c2: 
            skills = pd.DataFrame([s for s in ','.join(df_ctx['Certifications']).split(', ')], columns=['S'])['S'].value_counts().reset_index()
            skills.columns = ['Skill','Count']
            render_chart_box(T('t8_c2'), px.bar(skills.head(10), x='Skill', y='Count'), T('i8_c2'))
        with c3: render_chart_box(T('t8_c3'), px.box(df_ctx, x='Dept', y='Training_Hours', points='all', custom_data=['ID']), T('i8_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t8_c4'), px.line_polar(r=[80,60,90,40,70], theta=['AI','Data','Lead','Agile','Prod'], line_close=True), T('i8_c4'))
        with c5: render_chart_box(T('t8_c5'), px.pie(df_ctx[df_ctx['Level']>'L4'], names='Dept'), T('i8_c5'))
        with c6: render_chart_box(T('t8_c6'), px.histogram(df_ctx, x='Engagement'), T('i8_c6'))

    elif curr_dim == 'dim_9': 
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('t9_c1'), px.pie(df_ctx[df_ctx['Level']>'L4'], names='Successor_Status', hole=0.5), T('i9_c1'))
        with c2: render_chart_box(T('t9_c2'), px.bar(df_ctx[df_ctx['Level']>'L4'].groupby('Dept')['Successor_Status'].value_counts(normalize=True).reset_index(name='R'), x='Dept', y='R', color='Successor_Status'), T('i9_c2'))
        with c3: render_chart_box(T('t9_c3'), px.box(df_ctx, x='Level', y='Vacancy_Days', points='all', custom_data=['ID']), T('i9_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('t9_c4'), px.pie(df_ctx, names='Recruit_Source'), T('i9_c4'))
        with c5: render_chart_box(T('t9_c5'), px.histogram(df_ctx[df_ctx['Successor_Status']!='None'], x='Risk_Level'), T('i9_c5'))
        with c6: render_chart_box(T('t9_c6'), px.bar(df_ctx.groupby('Dept').size().reset_index(), x='Dept', y=0), T('i9_c6'))

# --- C. 列表视图 (List) ---
elif st.session_state.view == 'List':
    
    # 核心修复：全视图统一悬浮返回按钮
    if st.button(T('btn_home'), key="btn_back_floating_list", type="secondary"): 
        goto('Overview')
    
    st.components.v1.html(f"""
    <script>
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {{
            if (btn.innerText.includes('{T('btn_home')}')) {{
                btn.parentElement.classList.add('fixed-back-btn');
            }}
        }});
    </script>
    """, height=0)

    l_type = st.session_state.list_type
    d_list = df_ctx.copy()
    
    # --- v1.0 NEW FEATURE: 列表视图的智能洞察模块 ---
    # 根据列表类型生成专属诊断
    si_list = get_list_view_insight(l_type, d_list)
    if si_list['obs']: # 只有在支持的列表类型下才显示
        st.markdown(f"""
        <div class="smart-insight-card">
            <div class="smart-header">
                <span>⚡ SMART INSIGHT (v1.0 Alpha) - {T('list_'+l_type.lower()+'_header') if 'list_'+l_type.lower()+'_header' in TRANS['CN'] else l_type}</span>
            </div>
            <div class="smart-row">
                <div class="smart-icon">📊</div>
                <div><span class="smart-text">{si_list['obs']}</span></div>
            </div>
            <div class="smart-row">
                <div class="smart-icon">🔍</div>
                <div><span class="smart-text">{si_list['dia']}</span></div>
            </div>
            <div class="smart-row">
                <div class="smart-icon">⚡</div>
                <div><span class="smart-text">{si_list['act']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    # -----------------------------------------------
    
    if l_type == 'Headcount': 
        st.markdown(f"## 📋 {T('list_all_header')}")
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('l_c1'), px.histogram(d_list, x='Tenure'), T('li_c1'))
        with c2: render_chart_box(T('l_c2'), px.histogram(d_list, y='Level'), T('li_c2'))
        with c3: render_chart_box(T('l_c3'), px.box(d_list, x='Level', y='Span', points='all', custom_data=['ID']), T('li_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('l_c4'), px.pie(d_list, names='Gender'), T('li_c4'))
        with c5: render_chart_box(T('l_c5'), px.scatter(d_list, x='Level', y='Flight_Risk', custom_data=['ID']), T('li_c5'))
        with c6: render_chart_box(T('l_c6'), px.bar(d_list.groupby('Join_Date').size().reset_index(), x='Join_Date', y=0), T('li_c6'))
    
    elif l_type == 'Cost':
        st.markdown(f"## 💰 {T('list_cost_header')}")
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('lc_c1'), px.bar(d_list.groupby('Dept')['Salary'].sum().reset_index(), x='Dept', y='Salary'), T('lic_c1'))
        with c2: render_chart_box(T('lc_c2'), px.bar(d_list.groupby('Level')[['Salary','Last_Bonus','Stock_Options']].mean().reset_index(), x='Level', y=['Salary','Last_Bonus','Stock_Options']), T('lic_c2'))
        with c3: render_chart_box(T('lc_c3'), px.scatter(d_list, x='Join_Date', y='ROI_Ratio', custom_data=['ID']), T('lic_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('lc_c4'), px.pie(d_list, names='Dept', values='OT_Hours'), T('lic_c4'))
        with c5: render_chart_box(T('lc_c5'), px.box(d_list, x='Level', y='Compa_Ratio', points='all', custom_data=['ID']), T('lic_c5'))
        with c6: render_chart_box(T('lc_c6'), px.bar(d_list, x='Dept', y='Salary'), T('lic_c6'))
        
    elif l_type == 'Util':
        d_list = d_list[d_list['Util']>1.0]
        st.markdown(f"## ⏳ {T('list_util_header')}")
        c1, c2, c3 = st.columns(3)
        with c1: 
            # Replaced Perf_Score with Perf
            render_chart_box(T('lu_c1'), px.scatter(d_list, x='Util', y='Perf', color='Dept', category_orders={'Perf': perf_order_asc}, custom_data=['ID']), T('liu_c1'))
        with c2: render_chart_box(T('lu_c2'), px.density_heatmap(d_list, x='Dept', y='Level', z='Util', histfunc='avg'), T('liu_c2'))
        with c3: render_chart_box(T('lu_c3'), px.histogram(d_list, x='OT_Hours'), T('liu_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('lu_c4'), px.scatter(d_list, x='Span', y='Util', custom_data=['ID']), T('liu_c4'))
        with c5: render_chart_box(T('lu_c5'), px.bar(d_list.groupby('Dept')['ROI_Ratio'].mean().reset_index(), x='Dept', y='ROI_Ratio'), T('liu_c5'))
        with c6: render_chart_box(T('lu_c6'), px.box(d_list, x='Dept', y='Vacancy_Days', points='all', custom_data=['ID']), T('liu_c6'))
        
    elif l_type == 'Risk':
        d_list = d_list[d_list['Risk_Level']=='Critical']
        st.markdown(f"## 🚨 {T('list_risk_header')}")
        c1, c2, c3 = st.columns(3)
        risk_flat_list = []
        for rs in d_list['Risk_Factors']: risk_flat_list.extend([x.strip() for x in rs.split(',')])
        sf_df = pd.DataFrame(risk_flat_list, columns=['Factor']).value_counts().reset_index()
        sf_df.columns = ['Factor','Count']
        with c1: render_chart_box(T('lr_c1'), px.bar(sf_df, x='Count', y='Factor', orientation='h'), T('lir_c1'))
        with c2: render_chart_box(T('lr_c2'), px.pie(d_list, names='Dept'), T('lir_c2'))
        with c3: render_chart_box(T('lr_c3'), px.bar(d_list[d_list['Level']>'L4'], x='Dept'), T('lir_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('lr_c4'), px.box(d_list, y='Compa_Ratio', points='all', custom_data=['ID']), T('lir_c4'))
        with c5: render_chart_box(T('lr_c5'), px.scatter(d_list, x='Tenure', y='Risk_Score', custom_data=['ID']), T('lir_c5'))
        with c6: render_chart_box(T('lr_c6'), px.histogram(d_list, x='Engagement'), T('lir_c6'))
    
    elif l_type == 'HiPo':
        d_list = d_list[d_list['Perf'].isin(['SS','S','A+'])]
        st.markdown(f"## 💎 {T('list_hipo_header')}")
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('lh_c1'), px.line_polar(r=[90,80,70,85,95], theta=['Exec','Strat','Tech','Lead','Agile'], line_close=True), T('lih_c1'))
        with c2: render_chart_box(T('lh_c2'), px.histogram(d_list, x='Risk_Level'), T('lih_c2'))
        with c3: render_chart_box(T('lh_c3'), px.scatter(d_list, x='Age', y='Level', custom_data=['ID']), T('lih_c3'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('lh_c4'), px.box(d_list, y='Engagement', points='all', custom_data=['ID']), T('lih_c4'))
        with c5: render_chart_box(T('lh_c5'), px.pie(d_list, names='Region'), T('lih_c5'))
        with c6: render_chart_box(T('lh_c6'), px.bar(d_list, x='Dept', y='Training_Hours'), T('lih_c6'))

    elif l_type == 'Risk_Factor':
        factor = st.session_state.risk_factor_filter
        d_list = d_list[d_list['Risk_Factors'].str.contains(factor, na=False)]
        st.markdown(f"## {T('lrf_header')}{factor}")
        c1, c2 = st.columns(2)
        with c1: render_chart_box(T('lrf_c1'), px.pie(d_list, names='Dept'), T('lirf_c1'))
        with c2: render_chart_box(T('lrf_c2'), px.histogram(d_list, x='Level'), T('lirf_c2'))

    cols = ['ID','Name','Region','Dept','Level','Perf','Risk_Level','Salary','Util','Risk_Factors']
    if l_type == 'Cost': cols = ['ID','Name','Dept','Level','Salary','Last_Bonus','Stock_Options','Compa_Ratio']
    
    event = st.dataframe(d_list[cols], selection_mode="single-row", on_select="rerun", use_container_width=True, height=600)
    if len(event.selection.rows) > 0: goto('Profile', uid=d_list.iloc[event.selection.rows[0]]['ID'])

# --- D. 档案视图 (Profile) ---
elif st.session_state.view == 'Profile':
    
    # 核心修复：全视图统一悬浮返回按钮
    if st.button(T('btn_home'), key="btn_back_floating_profile", type="secondary"): 
        goto('Overview')
    
    st.components.v1.html(f"""
    <script>
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {{
            if (btn.innerText.includes('{T('btn_home')}')) {{
                btn.parentElement.classList.add('fixed-back-btn');
            }}
        }});
    </script>
    """, height=0)

    uid = st.session_state.sel_uid
    rec = df_master[df_master['ID']==uid].iloc[0]
    
    st.markdown(f"""
    <div class="profile-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <h1 style="margin:0; font-size:24px; color:#1E293B;">{rec['Name']}</h1>
                <p style="color:#64748B; margin-top:4px; font-size:13px;">{rec['ID']} | {rec['Region']} | {rec['Dept']} | {rec['Level']}</p>
            </div>
            <div style="text-align:right">
                <h2 style="color:#0F172A; margin:0; font-size:24px;">¥{rec['Salary']}k</h2>
                <span class="tag-critical" style="display:inline-block; margin-top:6px;">{rec['Risk_Level']} Risk</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='profile-section-header'>{T('p_basic')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="profile-label">Email</div><div class="profile-text">{rec['Email']}</div>
        <div class="profile-label">Age / Gender</div><div class="profile-text">{rec['Age']} / {rec['Gender']}</div>
        <div class="profile-label">Phone</div><div class="profile-text">{rec['Phone']}</div>
        <div class="profile-label">Marital Status</div><div class="profile-text">{rec['Marital']}</div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"<div class='profile-section-header'>{T('p_history')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="profile-label">Join Date</div><div class="profile-text">{rec['Join_Date']}</div>
        <div class="profile-label">Tenure</div><div class="profile-text">{rec['Tenure']} Years</div>
        <div class="profile-label">Recruit Source</div><div class="profile-text">{rec['Recruit_Source']}</div>
        <div class="profile-label">University</div><div class="profile-text">{rec['University']} ({rec['Major']})</div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"<div class='profile-section-header'>{T('p_assets')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="profile-label">IT Assets</div><div class="profile-text">{rec['Laptop']}</div>
        <div class="profile-label">Certifications & Skills</div><div class="profile-text">{rec['Certifications']}</div>
        <div class="profile-label">Current Projects</div><div class="profile-text">{rec['Project_A']}, {rec['Project_B']}</div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(f"<div class='profile-section-header'>{T('p_work')}</div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1: st.metric("Util Saturation", f"{rec['Util']*100:.0f}%", delta_color="inverse")
        with cc2: st.metric("Meeting Hours", f"{rec['Span']}h")
        cc3, cc4 = st.columns(2)
        with cc3: st.metric("OT Hours", rec['OT_Hours'])
        with cc4: st.metric("Entropy", rec['Entropy'])

    with c5:
        st.markdown(f"<div class='profile-section-header'>{T('p_perf')}</div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1: st.metric("Performance", rec['Perf'])
        with cc2: st.metric("Potential", rec['Potential'])
        st.info(f"📋 **Review Note:** {rec['Review_Note']}")

    with c6:
        st.markdown(f"<div class='profile-section-header'>{T('p_comp')}</div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1: st.metric("Base Salary", f"{rec['Salary']}k")
        with cc2: st.metric("Compa Ratio", rec['Compa_Ratio'])
        cc3, cc4 = st.columns(2)
        with cc3: st.metric("Bonus", f"{rec['Last_Bonus']}k")
        with cc4: st.metric("Stock Options", f"{rec['Stock_Options']}k")