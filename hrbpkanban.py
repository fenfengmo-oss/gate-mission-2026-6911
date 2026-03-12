import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random
from datetime import datetime, timedelta

# ==========================================
# 0. 依赖检查与配置
# ==========================================
try:
    import statsmodels
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

st.set_page_config(
    page_title="GATE BP-Link Ultra v4.0 AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 1. 状态管理 & 语言设置
# ==========================================
if 'view' not in st.session_state: st.session_state.view = 'Overview'
if 'sel_dim' not in st.session_state: st.session_state.sel_dim = None
if 'sel_uid' not in st.session_state: st.session_state.sel_uid = None
if 'sel_team' not in st.session_state: st.session_state.sel_team = 'All'
if 'sel_level' not in st.session_state: st.session_state.sel_level = []
if 'lang' not in st.session_state: st.session_state.lang = 'CN' 
if 'search_input' not in st.session_state: st.session_state.search_input = ""

def goto(view, uid=None, dim=None):
    st.session_state.view = view
    if uid: st.session_state.sel_uid = uid
    if dim: st.session_state.sel_dim = dim
    st.rerun()

# --- 翻译字典 (Translation Dictionary) ---
TRANS = {
    'CN': {
        # --- 全局/Global ---
        'title': "GATE BP-Link Ultra", 'subtitle': "HRBP 智能战略视图 v4.0",
        'coverage': "覆盖人数", 'search_ph': "🔍 搜索员工姓名或ID (回车跳转)...",
        'filter_bu': "业务单元", 'filter_lvl': "职级筛选", 'home': "↩️ 返回首页",
        
        # --- 核心 KPIs ---
        'kpi_hc': "在职人数", 'kpi_sal': "平均年薪", 'kpi_perf': "平均绩效", 'kpi_risk': "高风险人数", 'kpi_hipo': "高潜占比",

        # --- 维度导航 ---
        'dim_org': "📊 组织效能", 'desc_org': "管理幅度 · 层级 · 成本",
        'dim_talent': "🦁 人才盘点", 'desc_talent': "九宫格 · 高潜 · 继任",
        'dim_risk': "🚨 离职风控", 'desc_risk': "流失预测 · 预警",
        'dim_comp': "💰 薪酬回报", 'desc_comp': "公平性 · 带宽 · 结构",
        'dim_recruit': "🧲 招聘配置", 'desc_recruit': "漏斗 · 效率 · 渠道",
        'dim_train': "🌱 培训发展", 'desc_train': "技能 · 投入产出",
        'dim_dei': "⚖️ 多元共融", 'desc_dei': "多样性 · 包容性",
        'dim_perf': "🎯 绩效管理", 'desc_perf': "OKR · 绩效校准",
        'dim_lead': "👑 领导力", 'desc_lead': "管理者效能 · 梯队",
        'dim_plan': "📉 预算规划", 'desc_plan': "编制预测 · 成本",

        # --- 通用 UI ---
        'header_pillars': "战略支柱分析 (点击进入详情)", 'header_quick': "快捷入口",
        'btn_list': "📋 查看全员列表", 'btn_rand': "👤 随机档案",
        'p_perf_pot': "绩效与潜能", 'p_eng_growth': "敬业度与成长", 'p_history': "历史记录",
        'lbl_perf': "绩效等级", 'lbl_pot': "潜能等级", 'lbl_hipo': "高潜状态",
        'lbl_mgr': "管理者评分", 'lbl_okr': "OKR完成率", 'lbl_skill': "技能缺口",
        'lbl_join': "入职日期", 'lbl_tenure': "司龄(年)", 'lbl_src': "招聘渠道", 'lbl_risk': "风险标签",
        'smart_obs': "现象 (Obs)", 'smart_dia': "归因 (Diag)", 'smart_act': "行动 (Act)",

        # ================= 图表标题与洞察 (Charts & Insights) =================
        'ct_span': "管理幅度分布 (Span of Control)", 'in_span': "监控管理幅度异常（>15人或<3人），识别团队拥堵或资源浪费。",
        'ct_layer': "职级层级分布", 'in_layer': "检查组织是否过于臃肿，警惕中高层（P7/P8）比例失衡。",
        'ct_cost_dist': "人力成本投入分布", 'in_cost_dist': "分析各业务单元的薪酬资源投入占比，确保好钢用在刀刃上。",
        'ct_tenure': "司龄结构分析", 'in_tenure': "观察组织代谢率，识别老龄化团队或流动性过高的团队。",
        'ct_revenue': "人效贡献矩阵 (Salary vs Perf)", 'in_revenue': "识别高薪低产出（右上角）与低薪高产出（左下角）人员。",
        'ct_flat': "组织扁平度指数", 'in_flat': "对比各部门层级复杂度，推动组织扁平化改革。",

        'ct_9box': "九宫格人才分布 (9-Box Grid)", 'in_9box': "核心视图：识别超级明星（右上）与待提升者（左下）。气泡大小代表薪酬。",
        'ct_hipo_den': "高潜人才密度 (HiPo Density)", 'in_hipo_den': "各团队高潜人才浓度对比，监控创新核心驱动力。",
        'ct_bench': "板凳深度 (Succession Bench)", 'in_bench': "高潜力（Potential > 4）人才储备库分布，评估继任安全性。",
        'ct_corr': "绩效-潜能相关性热力图", 'in_corr': "验证人才识别标准的一致性，避免'唯绩效论'。",
        'ct_velocity': "人才成长速度 (晋升/司龄)", 'in_velocity': "识别快速晋升者（Fast-trackers），高潜往往具备更陡峭的成长曲线。",
        'ct_skill_rad': "关键能力雷达图 (Skill Profile)", 'in_skill_rad': "组织整体能力短板扫描，指导招聘与培训重心。",

        'ct_risk_dist': "离职风险评分分布", 'in_risk_dist': "全员风险模型概览，右侧长尾部分为重点关注的高危人群。",
        'ct_regret': "遗憾离职预警 (Regret Loss)", 'in_regret': "聚焦高潜/核心人才的离职风险，此处亮点即为必须挽留的对象。",
        'ct_inv': "薪酬倒挂风险 (Pay Inversion)", 'in_inv': "监控低职级薪酬高于高职级，或新人倒挂老人的异常点。",
        'ct_mgr_attr': "管理者与下属风险归因", 'in_mgr_attr': "分析管理者评分低是否直接导致了下属的高离职风险。",
        'ct_burn': "职业倦怠曲线 (Tenure vs Risk)", 'in_burn': "识别'三年之痒'或特定司龄段的离职高峰期。",
        'ct_impact': "高危人员业务影响分布", 'in_impact': "若高风险人员离职，对哪些业务单元冲击最大？",

        'ct_pen': "薪酬渗透率分布 (Compa-Ratio)", 'in_pen': "分析员工薪酬在宽带中的位置，识别红点（>1.2）与绿点（<0.8）。",
        'ct_equity': "内部公平性回归分析", 'in_equity': "检查同一职级下，性别或其他因素是否导致了显著的薪酬差异。",
        'ct_sens': "薪酬-绩效敏感度 (Pay-for-Perf)", 'in_sens': "高绩效是否真的拿到了高薪酬？检验激励机制的有效性。",
        'ct_comp_ext': "外部竞争力指数 (CR by Team)", 'in_comp_ext': "各团队薪酬中位值与市场（Compa-Ratio）的对比。",
        'ct_cost_str': "薪酬成本结构 (Treemap)", 'in_cost_str': "直观展示薪酬包是如何被各团队和职级切分的。",
        'ct_new_old': "新老员工薪酬倒挂", 'in_new_old': "监控'倒挂'现象：同职级下，新人薪酬是否显著高于老员工。",

        'ct_funnel': "招聘转化漏斗", 'in_funnel': "从申请到入职的全流程转化率，识别流程瓶颈。",
        'ct_chan_qual': "渠道质量分析 (Cost vs Quality)", 'in_chan_qual': "寻找高性价比渠道（低成本、高质量 hire）。",
        'ct_time': "招聘周期 (Time to Fill)", 'in_time': "各部门平均到岗时间监控，预警招聘迟滞。",
        'ct_prob': "试用期绩效分布", 'in_prob': "入职<1年员工的绩效表现，衡量'人岗匹配度'。",
        'ct_int_eff': "面试官有效性分析", 'in_int_eff': "各团队招聘进来的人才平均质量（QoH），评估面试官眼光。",
        'ct_sup': "人才供给结构", 'in_sup': "当前在职员工的来源渠道构成。",

        'ct_gap': "技能缺口热力图", 'in_gap': "各团队急需补充的关键技能领域（红色高亮）。",
        'ct_roi': "培训 ROI 分析 (Hours vs Perf)", 'in_roi': "投入更多培训时长是否带来了更高的绩效产出？",
        'ct_cert': "专业认证持有率", 'in_cert': "团队专业资质的密度分布。",
        'ct_learn': "学习型组织指数", 'in_learn': "员工年均培训时长分布，衡量学习氛围。",
        'ct_succ_r': "继任者准备度 (P8/P9)", 'in_succ_r': "关键岗位（P8+）继任者的技能缺口状况。",
        'ct_res': "培训资源投入分布", 'in_res': "培训预算和时间资源主要流向了哪些职级？",

        'ct_gen': "性别层级分布", 'in_gen': "监控'玻璃天花板'现象：高层级中女性占比是否急剧下降。",
        'ct_pay_eq': "同岗同酬分析", 'in_pay_eq': "同一职级下的性别薪酬差异箱线图。",
        'ct_age': "团队年龄结构", 'in_age': "识别团队是趋于年轻化（活力）还是老龄化（经验/僵化）。",
        'ct_hipo_div': "高潜人才多样性", 'in_hipo_div': "未来的领导梯队（HiPo）中，性别/背景的分布情况。",
        'ct_prom_eq': "晋升公平性 (Tenure by Gender)", 'in_prom_eq': "不同性别员工获得同等职级所需的平均年限。",
        'ct_inc': "包容性指数 (Manager Rating)", 'in_inc': "各团队管理者评分均值，作为包容性文化的代理指标。",

        'ct_dist': "绩效正态分布检验", 'in_dist': "检查是否存在'满分通胀'或'强制分布'过严的情况。",
        'ct_okr': "OKR 完成率概览", 'in_okr': "战略目标的达成情况与执行力透视。",
        'ct_feed': "持续反馈关联度", 'in_feed': "反馈频率（Feedback Count）与最终绩效的相关性。",
        'ct_pip': "绩效改进计划 (PIP) 预警", 'in_pip': "低绩效人员（<2.5）在各团队的占比。",
        'ct_cal': "绩效校准分析 (Calibration)", 'in_cal': "各团队绩效中位数对比，识别评分过松或过严的Manager。",
        'ct_align': "目标-结果一致性", 'in_align': "OKR完成率高但绩效低（或反之）的异常点分析。",

        'ct_eff': "管理者效能分布", 'in_eff': "通过下属评分和团队产出衡量的管理者综合效能。",
        'ct_up': "向上反馈与离职风险", 'in_up': "差劲的管理者（低分）是否导致了团队的高风险？",
        'ct_pipe': "领导梯队储备 (Pipeline)", 'in_pipe': "P7+ 资深员工储备量，衡量未来管理者的供给能力。",
        'ct_style': "管理风格热力图", 'in_style': "各团队管理者评分的聚集趋势。",
        'ct_inv_l': "领导力培养投入", 'in_inv_l': "中高层管理者接受培训的时长分布。",
        'ct_high': "高地占领 (High Ground)", 'in_high': "管理者自身的绩效 vs 团队目标的达成率。",

        'ct_fc': "薪酬成本预测 (Forecast)", 'in_fc': "基于当前编制的年度薪酬总包预测。",
        'ct_hc': "人力增长趋势", 'in_hc': "历史入职与编制增长曲线，辅助Headcount规划。",
        'ct_roi_p': "人力资本回报 (HC ROI)", 'in_roi_p': "薪酬投入与OKR产出的散点关系。",
        'ct_var': "薪酬方差分析", 'in_var': "各职级薪酬波动范围，用于预算控制。",
        'ct_rec_b': "预计招聘成本预算", 'in_rec_b': "基于历史 Cost-per-hire 的未来招聘预算预估。",
        'ct_repl': "离职置换成本预估", 'in_repl': "假设当前人员离职，所需的重置成本（通常为年薪的 50%-200%）。"
    },
    'EN': {
        'title': "GATE BP-Link Ultra", 'subtitle': "HRBP Intelligent View v4.0",
        'coverage': "Lives Covered", 'search_ph': "🔍 Search Name or ID (Enter to Go)...",
        'filter_bu': "Business Unit", 'filter_lvl': "Job Level", 'home': "↩️ Home",
        'kpi_hc': "Headcount", 'kpi_sal': "Avg Salary", 'kpi_perf': "Avg Perf", 'kpi_risk': "Risk Count", 'kpi_hipo': "HiPo %",
        'dim_org': "📊 Org Health", 'desc_org': "Span · Layers · Cost",
        'dim_talent': "🦁 Talent Review", 'desc_talent': "9-Box · HiPo · Succession",
        'dim_risk': "🚨 Retention Risk", 'desc_risk': "Attrition Forecast · Alerts",
        'dim_comp': "💰 Total Rewards", 'desc_comp': "Equity · Bandwidth · Structure",
        'dim_recruit': "🧲 Talent Acquisition", 'desc_recruit': "Funnel · Efficiency · Channels",
        'dim_train': "🌱 L&D", 'desc_train': "Skills Gap · ROI",
        'dim_dei': "⚖️ DEI", 'desc_dei': "Diversity · Inclusion",
        'dim_perf': "🎯 Performance", 'desc_perf': "OKR · Calibration",
        'dim_lead': "👑 Leadership", 'desc_lead': "Effectiveness · Pipeline",
        'dim_plan': "📉 Workforce Planning", 'desc_plan': "Headcount · Cost Forecast",
        'header_pillars': "Strategic Pillars (Deep Dive)", 'header_quick': "Quick Access",
        'btn_list': "📋 Employee Directory", 'btn_rand': "👤 Random Profile",
        'p_perf_pot': "Performance & Potential", 'p_eng_growth': "Engagement & Growth", 'p_history': "History & Status",
        'lbl_perf': "Performance", 'lbl_pot': "Potential", 'lbl_hipo': "HiPo Status",
        'lbl_mgr': "Manager Rating", 'lbl_okr': "OKR Completion", 'lbl_skill': "Skill Gap",
        'lbl_join': "Join Date", 'lbl_tenure': "Tenure (Yrs)", 'lbl_src': "Source", 'lbl_risk': "Risk Flags",
        'smart_obs': "Obs", 'smart_dia': "Diag", 'smart_act': "Act",
        # English charts... (省略以节省空间，Key ID保持一致即可)
        'ct_span': "Span of Control", 'in_span': "Monitor outliers: Teams with >15 or <3 direct reports.",
        'ct_layer': "Organizational Layering", 'in_layer': "Check for organizational bloating.",
        'ct_cost_dist': "Headcount Cost Dist", 'in_cost_dist': "Analyze budget allocation across business units.",
        'ct_tenure': "Tenure Structure", 'in_tenure': "Analyze organizational metabolism.",
        'ct_revenue': "Efficiency Matrix (Sal vs Perf)", 'in_revenue': "Identify High-Cost/Low-Output vs. Low-Cost/High-Output.",
        'ct_flat': "Org Flatness Index", 'in_flat': "Compare reporting complexity.",
        'ct_9box': "9-Box Talent Grid", 'in_9box': "Core View: Identify Star Performers vs. Underperformers.",
        'ct_hipo_den': "HiPo Density", 'in_hipo_den': "Compare concentration of HiPo talent.",
        'ct_bench': "Succession Bench Strength", 'in_bench': "Distribution of employees with Potential > 4.",
        'ct_corr': "Perf-Potential Correlation", 'in_corr': "Verify consistency.",
        'ct_velocity': "Talent Velocity", 'in_velocity': "Identify 'Fast-trackers'.",
        'ct_skill_rad': "Critical Skill Radar", 'in_skill_rad': "Scan organizational skill gaps.",
        'ct_risk_dist': "Attrition Risk Score Dist", 'in_risk_dist': "Overview of retention risk.",
        'ct_regret': "Regret Loss Alert", 'in_regret': "Focus on HiPo/Critical talent with high risk scores.",
        'ct_inv': "Pay Inversion Risk", 'in_inv': "Detect anomalies where junior levels earn more than seniors.",
        'ct_mgr_attr': "Manager-Driven Risk", 'in_mgr_attr': "Correlate low manager ratings with flight risk.",
        'ct_burn': "Tenure Burnout Curve", 'in_burn': "Identify risk peaks at specific tenure milestones.",
        'ct_impact': "Risk Impact Analysis", 'in_impact': "Which business units suffer most?",
        'ct_pen': "Compa-Ratio Penetration", 'in_pen': "Analyze pay band distribution.",
        'ct_equity': "Internal Equity Regression", 'in_equity': "Check for unexplained pay gaps.",
        'ct_sens': "Pay-for-Performance Sensitivity", 'in_sens': "Are high performers paid more?",
        'ct_comp_ext': "External Competitiveness", 'in_comp_ext': "Median Compa-Ratio by team.",
        'ct_cost_str': "Cost Structure (Treemap)", 'in_cost_str': "Visualizing how the salary budget is sliced.",
        'ct_new_old': "New Hire vs. Veteran Pay", 'in_new_old': "Monitor 'Inversion'.",
        'ct_funnel': "Acquisition Funnel", 'in_funnel': "Conversion rates.",
        'ct_chan_qual': "Channel ROI (Cost vs QoH)", 'in_chan_qual': "Identify high-value channels.",
        'ct_time': "Time-to-Fill Heatmap", 'in_time': "Monitor hiring velocity.",
        'ct_prob': "Probation Performance", 'in_prob': "Performance of new hires.",
        'ct_int_eff': "Interviewer Effectiveness", 'in_int_eff': "Average Quality of Hire (QoH).",
        'ct_sup': "Talent Supply Source", 'in_sup': "Composition of current workforce origin.",
        'ct_gap': "Skill Gap Heatmap", 'in_gap': "Critical skill shortages by team.",
        'ct_roi': "L&D ROI Analysis", 'in_roi': "Does more training correlate with higher performance?",
        'ct_cert': "Certification Density", 'in_cert': "Proportion of team members with certifications.",
        'ct_learn': "Learning Organization Index", 'in_learn': "Distribution of learning hours.",
        'ct_succ_r': "Succession Readiness (P8+)", 'in_succ_r': "Skill gap analysis for successors.",
        'ct_res': "Training Resource Allocation", 'in_res': "Where are L&D budget/hours going?",
        'ct_gen': "Gender by Level", 'in_gen': "Monitor 'Glass Ceiling' effects.",
        'ct_pay_eq': "Equal Pay Analysis", 'in_pay_eq': "Pay gap boxplot.",
        'ct_age': "Age Demographics", 'in_age': "Team age structure.",
        'ct_hipo_div': "HiPo Diversity", 'in_hipo_div': "Composition of leadership pipeline.",
        'ct_prom_eq': "Promotion Equity", 'in_prom_eq': "Average tenure required for promotion.",
        'ct_inc': "Inclusion Index", 'in_inc': "Manager ratings as proxy.",
        'ct_dist': "Performance Distribution", 'in_dist': "Check for 'Grade Inflation'.",
        'ct_okr': "OKR Completion Rate", 'in_okr': "Strategic execution.",
        'ct_feed': "Feedback Correlation", 'in_feed': "Feedback vs Performance.",
        'ct_pip': "PIP Risk Monitor", 'in_pip': "Underperformers percentage.",
        'ct_cal': "Performance Calibration", 'in_cal': "Identify lenient/strict managers.",
        'ct_align': "Goal-Result Alignment", 'in_align': "High OKR but Low Perf?",
        'ct_eff': "Manager Effectiveness", 'in_eff': "Composite score.",
        'ct_up': "Upward Feedback Risk", 'in_up': "Manager rating vs risk.",
        'ct_pipe': "Leadership Pipeline", 'in_pipe': "Volume of P7+ talent.",
        'ct_style': "Management Style Heatmap", 'in_style': "Clustering of manager ratings.",
        'ct_inv_l': "Leadership Investment", 'in_inv_l': "Training hours for leaders.",
        'ct_high': "High Ground", 'in_high': "Manager Perf vs Team OKR.",
        'ct_fc': "Cost Forecast", 'in_fc': "Projected annual salary spend.",
        'ct_hc': "Headcount Growth Trend", 'in_hc': "Historical growth curve.",
        'ct_roi_p': "Human Capital ROI Proxy", 'in_roi_p': "Salary Spend vs. OKR Output.",
        'ct_var': "Compensation Variance", 'in_var': "Pay range spreads.",
        'ct_rec_b': "Recruitment Budget Est.", 'in_rec_b': "Forecasted hiring costs.",
        'ct_repl': "Replacement Cost Risk", 'in_repl': "Estimated cost to replace."
    }
}

def T(key):
    return TRANS[st.session_state.lang].get(key, key)

# ==========================================
# 2. CSS: GATE Design System
# ==========================================
st.markdown("""
<style>
    /* Global Font & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root { --bg-color: #F8FAFC; --card-bg: #FFFFFF; --text-primary: #1E293B; --brand-blue: #4F46E5; }
    .stApp { background-color: var(--bg-color); font-family: "Inter", sans-serif; color: var(--text-primary); }
    .block-container { padding-top: 5rem !important; padding-bottom: 2rem !important; }
    header[data-testid="stHeader"], footer { display: none; }

    /* Top Navigation */
    .nav-header {
        background: rgba(255, 255, 255, 0.90); backdrop-filter: blur(12px);
        padding: 0 24px; border-bottom: 1px solid #E2E8F0;
        position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
        display: flex; justify-content: space-between; align-items: center; height: 60px;
    }
    .nav-title { font-size: 18px; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 10px; }
    .nav-tag { background: #EEF2FF; color: var(--brand-blue); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }

    /* Cards & Buttons */
    div.stButton > button {
        width: 100%; min-height: 72px !important; padding: 12px 16px !important;
        background-color: white; border: 1px solid #E2E8F0; border-radius: 8px;
        text-align: left; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    div.stButton > button:hover { border-color: var(--brand-blue); transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div.stButton > button p { color: #1E293B; font-size: 14px !important; font-weight: 600; }

    /* Chart Containers */
    .chart-box { background: transparent; padding: 0; margin-bottom: 16px; }
    .expert-insight { background: rgba(241, 245, 249, 0.8); border-left: 3px solid var(--brand-blue); padding: 8px 12px; margin-top: 8px; border-radius: 0 4px 4px 0; font-size: 12px; color: #64748B; }
    .insight-title { font-weight: 700; color: var(--brand-blue); margin-right: 6px; font-size: 11px; text-transform: uppercase; }

    /* Profile Card */
    .profile-card { background: white; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .tag-critical { background: #FEF2F2; color: #DC2626; padding: 2px 10px; border-radius: 100px; font-weight: 700; font-size: 11px; }

    /* Floating Back Button */
    div.stButton.fixed-back-btn > button {
        position: fixed !important; right: 24px !important; top: 50% !important;
        transform: translateY(-50%) !important; z-index: 999999 !important;
        width: auto !important; height: auto !important; padding: 12px 20px !important;
        border-radius: 100px !important; background: white !important; color: var(--brand-blue) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
    }

    /* v4.0 Smart Insight Card */
    .smart-insight-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
        border: 1px solid #E0E7FF;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }
    .smart-insight-card::before { content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #4F46E5; }
    .smart-header { font-size: 14px; font-weight: 700; color: #312E81; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .smart-row { display: flex; gap: 12px; margin-bottom: 8px; font-size: 13px; line-height: 1.5; align-items: flex-start; }
    .smart-icon { min-width: 20px; font-size: 16px; }
    .smart-label { font-weight: 600; color: #4F46E5; margin-right: 4px; min-width: 40px; }
    .smart-text { color: #334155; }

    /* Input Styling */
    div[data-baseweb="select"] > div { background-color: white; border-radius: 6px; }
    .dim-header { font-size: 24px; font-weight: 700; color: #0F172A; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. Data Engine
# ==========================================
@st.cache_data
def generate_mega_data(n=1200):
    teams = ['Platform Eng', 'AI Research', 'Core Product', 'Growth', 'Enterprise Sales', 'Customer Success']
    levels = ['P5', 'P6', 'P7', 'P8', 'P9']
    genders = ['Male', 'Female']
    sources = ['LinkedIn', 'Referral', 'Agency', 'Campus', 'Internal']
    
    data = []
    current_date = datetime.now()
    
    for i in range(n):
        team = np.random.choice(teams)
        lvl = np.random.choice(levels, p=[0.15, 0.4, 0.3, 0.1, 0.05])
        gender = np.random.choice(genders, p=[0.6, 0.4])
        
        base_ref = {'P5':30, 'P6':50, 'P7':85, 'P8':140, 'P9':220}[lvl]
        base_pay = base_ref * random.uniform(0.85, 1.25)
        compa = base_pay / base_ref
        
        perf = min(5.0, max(1.0, np.random.normal(3.5, 0.8)))
        pot = min(5.0, max(1.0, np.random.normal(3.2, 0.9)))
        
        tenure = round(random.uniform(0.1, 10.0), 1)
        age = 22 + int(tenure) + {'P5':0,'P6':3,'P7':6,'P8':10,'P9':15}[lvl] + random.randint(0,5)
        
        recruit_cost = random.randint(20, 150)
        time_to_fill = random.randint(15, 90)
        interview_score = random.randint(3, 5) + random.random()
        
        train_hrs = random.randint(0, 80)
        skills_gap = random.choice(['Low', 'Medium', 'High', 'Critical'])
        certifications = random.randint(0, 5)
        okr_progress = random.uniform(0.3, 1.2)
        feedback_freq = random.randint(0, 12)
        manager_rating = min(5.0, max(1.0, np.random.normal(4.0, 0.7)))
        
        risk_flags = []
        if compa < 0.9: risk_flags.append('Underpaid')
        if tenure > 3 and lvl in ['P5','P6']: risk_flags.append('Stagnated')
        if manager_rating < 3.0: risk_flags.append('Bad Manager')
        risk_score = len(risk_flags) * 20 + (100 - okr_progress*80) * 0.2
        risk_score = min(100, max(0, int(risk_score)))
        
        data.append({
            "ID": f"E{1000+i}", "Name": f"User_{i}", "Team": team, "Level": lvl, "Gender": gender,
            "Age": age, "Tenure": tenure, "Salary": int(base_pay), "Compa_Ratio": round(compa, 2),
            "Perf": round(perf, 1), "Potential": round(pot, 1),
            "Recruit_Source": np.random.choice(sources), "Cost_Per_Hire": recruit_cost, "Time_to_Fill": time_to_fill,
            "Quality_of_Hire": round(interview_score, 1),
            "Training_Hours": train_hrs, "Skill_Gap": skills_gap, "Certifications": certifications,
            "OKR_Completion": round(okr_progress, 2), "Feedback_Count": feedback_freq,
            "Manager_Rating": round(manager_rating, 1),
            "Risk_Score": risk_score, "Is_HiPo": (perf>4 and pot>4),
            "Join_Date": (current_date - timedelta(days=int(tenure*365))).strftime("%Y-%m-%d"),
            "Risk_Flags": ", ".join(risk_flags) if risk_flags else "None"
        })
        
    return pd.DataFrame(data)

df_master = generate_mega_data()

# ==========================================
# 4. 辅助函数 (已修复点击跳转)
# ==========================================
def get_trendline_params():
    return {"trendline": "ols"} if HAS_STATSMODELS else {}

def render_chart_box(title, fig, insight):
    with st.container():
        st.markdown(f"<div class='chart-box'>", unsafe_allow_html=True)
        
        # 1. 强制配置点击事件
        fig.update_layout(
            title=dict(text=title, font=dict(size=14, color="#1E293B", family="Inter", weight=600)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=11, color="#64748B"),
            margin=dict(l=10, r=10, t=40, b=10),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter", bordercolor="#E2E8F0"),
            height=320, 
            dragmode='zoom',
            clickmode='event+select' # 允许点击
        )
        fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", zeroline=False)

        unique_key = f"{title}_{st.session_state.view}_{st.session_state.lang}" 
        
        # 2. 捕获点击事件
        event = st.plotly_chart(
            fig, 
            use_container_width=True, 
            on_select="rerun", 
            selection_mode="points", 
            key=unique_key, 
            config={'displayModeBar': False}
        )
        
        # 3. 处理跳转逻辑
        if event and event.selection and len(event.selection.points) > 0:
            point = event.selection.points[0]
            # 尝试获取 customdata (通常是 ID)
            if 'customdata' in point and point['customdata']:
                # Plotly 可能返回 list 或 scalar
                val = point['customdata'][0] if isinstance(point['customdata'], list) else point['customdata']
                # 校验 ID 格式避免误触
                if isinstance(val, str) and val.startswith('E'):
                    goto('Profile', uid=val)
        
        st.markdown(f"<div class='expert-insight'><span class='insight-title'>INSIGHT</span>{insight}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Smart Insight Logic (AI)
def get_smart_insight(dim, df):
    is_cn = st.session_state.lang == 'CN'
    res = {
        'obs': "📊 **[数据监测]** 各项核心指标处于正常波动范围。",
        'dia': "🔍 **[归因分析]** 暂未发现显著的结构性异常。",
        'act': "⚡ **[行动建议]** 建议维持现有策略，持续关注趋势。"
    } if is_cn else {
        'obs': "Data Monitor: Metrics are within normal range.",
        'dia': "Diagnosis: No structural anomalies detected.",
        'act': "Action: Maintain current strategy."
    }

    if df.empty: return res

    if dim == 'Org':
        p8_plus = len(df[df['Level'].isin(['P8','P9'])])
        ratio = p8_plus / len(df)
        if ratio > 0.2:
            res['obs'] = f"📊 **[结构监测]** 组织呈现明显'头重脚轻'趋势，P8+ 高职级人员占比达 `{ratio:.1%}` (基准 < 15%)。" if is_cn else f"Top-heavy Alert: P8+ ratio at `{ratio:.1%}` (Benchmark < 15%)."
            res['dia'] = "🔍 **[效能归因]** 指挥层级过厚，导致决策链条冗长，且挤压了 P5/P6 一线执行层的薪酬预算空间。" if is_cn else "Decision latency due to bloated leadership layer; squeezing budget for execution layer."
            res['act'] = "⚡ **[BP 策略]** 1. 冻结非关键业务 P7+ 招聘；2. 启动 **'Spans & Layers'** 诊断，目标压降 1 层汇报关系。" if is_cn else "1. Freeze non-critical P7+ hiring. 2. Launch 'Spans & Layers' audit to flatten structure."
    elif dim == 'Talent':
        rate = len(df[df['Is_HiPo']]) / len(df)
        if rate < 0.1:
            res['obs'] = f"📊 **[人才密度]** 团队高潜人才 (HiPo) 浓度仅为 `{rate:.1%}`，远低于创新型组织 15-20% 的水位。" if is_cn else f"Low Talent Density: HiPo rate at `{rate:.1%}` (Target 15-20%)."
            res['dia'] = "🔍 **[识别归因]** 人才盘点标准可能过严，或外部招聘并未有效引入'抬高均值'的种子选手。" if is_cn else "Stringent identification criteria or failure to hire 'bar-raisers'."
            res['act'] = "⚡ **[BP 策略]** 1. 重新校准 Talent Review 标准；2. 建立 **'高潜护城河'** 计划，对现有 HiPo 实施 1:1 导师制。" if is_cn else "1. Recalibrate Talent Review standards. 2. Launch Mentorship program for existing HiPos."
    elif dim == 'Risk':
        crit_risk = len(df[df['Risk_Score'] > 80])
        if crit_risk > 5:
            res['obs'] = f"📊 **[预警监测]** 模型识别出 `{crit_risk}` 名极高风险人员 (Risk > 80)，其中包含多名核心骨干。" if is_cn else f"Alert: `{crit_risk}` Critical Risk employees identified, including key contributors."
            res['dia'] = "🔍 **[离职归因]** 主要驱动因素为 **'薪酬倒挂'** (Compa-Ratio < 0.9) 叠加 **'职业倦怠'** (Tenure > 4年)。" if is_cn else "Drivers: Pay Inversion (CR < 0.9) combined with Tenure Fatigue (> 4yrs)."
            res['act'] = "⚡ **[BP 策略]** 1. 生成 **'遗憾离职白名单'**；2. 申请专项留任包 (Retention Bonus)；3. 安排 Skip-level 访谈。" if is_cn else "1. Generate 'Regret Loss List'. 2. Apply for Retention Bonus. 3. Schedule Skip-level interviews."
    elif dim == 'Comp':
        new_sal = df[df['Tenure']<1]['Salary'].mean()
        old_sal = df[df['Tenure']>3]['Salary'].mean()
        if old_sal > 0 and new_sal > old_sal * 1.1:
            res['obs'] = f"📊 **[公平性监测]** 出现显著'薪酬倒挂'：入职 < 1 年新人平均薪酬比 3 年以上老员工高出 `{(new_sal/old_sal - 1):.1%}`。" if is_cn else f"Pay Inversion: New hires paid `{(new_sal/old_sal - 1):.1%}` more than 3yr+ veterans."
            res['dia'] = "🔍 **[C&B 归因]** 外部市场薪酬通胀速度快于内部调薪预算，导致老员工价值被相对低估，引发公平感危机。" if is_cn else "External market inflation outpacing internal merit budget, eroding veteran equity."
            res['act'] = "⚡ **[BP 策略]** 1. 针对高绩效老员工进行 **'市场修正调薪'** (Market Adjustment)；2. 优化 Total Rewards 沟通。" if is_cn else "1. Apply Market Adjustment for high-perf veterans. 2. Communicate Total Rewards value."
    elif dim == 'Recruit':
        avg_qoh = df['Quality_of_Hire'].mean()
        if avg_qoh < 3.8:
             res['obs'] = f"📊 **[质量监测]** 近期招聘质量 (QoH) 下滑至 `{avg_qoh:.1f}`，且试用期离职率呈现上升趋势。" if is_cn else f"Quality Dip: QoH dropped to `{avg_qoh:.1f}` with rising probation attrition."
             res['dia'] = "🔍 **[招聘归因]** 面试官标准松动，为追求 'Time-to-Fill' 牺牲了人才质量，特别是急招岗位。" if is_cn else "Lowered hiring bar to meet Time-to-Fill targets, compromising quality."
             res['act'] = "⚡ **[BP 策略]** 1. 实施 **'Bar Raiser'** (一票否决) 机制；2. 冻结 QoH 低于 3.5 的面试官资格并进行再培训。" if is_cn else "1. Implement Bar Raiser mechanism. 2. Retrain interviewers with low QoH scores."

    return res

DIM_DEFINITIONS = {
    "Org": ("dim_org", "desc_org"),
    "Talent": ("dim_talent", "desc_talent"),
    "Risk": ("dim_risk", "desc_risk"),
    "Comp": ("dim_comp", "desc_comp"),
    "Recruit": ("dim_recruit", "desc_recruit"),
    "Train": ("dim_train", "desc_train"),
    "DEI": ("dim_dei", "desc_dei"),
    "Perf": ("dim_perf", "desc_perf"),
    "Lead": ("dim_lead", "desc_lead"),
    "Plan": ("dim_plan", "desc_plan")
}

# ==========================================
# 5. 顶部导航栏 (Top Nav)
# ==========================================
st.markdown('<div class="nav-spacer"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="nav-header">
    <div class="nav-title">
        ⚡ {T('title')}
        <span class="nav-tag">{T('subtitle')}</span>
    </div>
    <div style="font-size:13px; color:#64748B; font-weight:500;">{T('coverage')}: 1,200</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1, 1, 0.4, 1.5], gap="small", vertical_alignment="bottom")
with c1:
    teams = ['All'] + list(df_master['Team'].unique())
    st.selectbox(T('filter_bu'), teams, key='sel_team')
with c2:
    levels = df_master['Level'].unique()
    st.multiselect(T('filter_lvl'), levels, default=[], key='sel_level', placeholder="All Levels")
with c3:
    lang_val = st.radio("Language", ["CN", "EN"], horizontal=True, label_visibility="collapsed", key='lang_toggle')
    if lang_val != st.session_state.lang:
        st.session_state.lang = lang_val
        st.rerun()
with c4:
    def handle_search():
        if st.session_state.search_input:
            term = st.session_state.search_input.strip()
            res = df_master[df_master['Name'].str.contains(term, case=False) | df_master['ID'].str.contains(term, case=False)]
            if not res.empty:
                st.session_state.sel_uid = res.iloc[0]['ID']
                st.session_state.view = 'Profile'
                st.session_state.search_input = "" 
    st.text_input("Search", placeholder=T('search_ph'), label_visibility="collapsed", key="search_input", on_change=handle_search)

# Filter Data
df_ctx = df_master.copy()
if st.session_state.sel_team != 'All': df_ctx = df_ctx[df_ctx['Team'] == st.session_state.sel_team]
if st.session_state.sel_level: df_ctx = df_ctx[df_ctx['Level'].isin(st.session_state.sel_level)]

if df_ctx.empty:
    st.warning("⚠️ No data available.")
    st.stop()

# ==========================================
# 6. 视图路由
# ==========================================

# --- A. Overview ---
if st.session_state.view == 'Overview':
    k1, k2, k3, k4, k5 = st.columns(5, gap="small")
    with k1: 
        if st.button(f"{T('kpi_hc')}\n{len(df_ctx)}", key="btn_kpi_hc", use_container_width=True): goto('Dimension_View', dim='Org')
    with k2: 
        if st.button(f"{T('kpi_sal')}\n¥{int(df_ctx['Salary'].mean())}k", key="btn_kpi_sal", use_container_width=True): goto('Dimension_View', dim='Comp')
    with k3: 
        if st.button(f"{T('kpi_perf')}\n{df_ctx['Perf'].mean():.2f}", key="btn_kpi_perf", use_container_width=True): goto('Dimension_View', dim='Perf')
    with k4: 
        if st.button(f"{T('kpi_risk')}\n{len(df_ctx[df_ctx['Risk_Score']>60])}", key="btn_kpi_risk", use_container_width=True): goto('Dimension_View', dim='Risk')
    with k5: 
        if st.button(f"{T('kpi_hipo')}\n{len(df_ctx[df_ctx['Is_HiPo']])/len(df_ctx)*100:.1f}%", key="btn_kpi_hipo", use_container_width=True): goto('Dimension_View', dim='Talent')
    
    st.markdown("---")
    st.markdown(f"#### {T('header_pillars')}")

    cols = st.columns(3)
    for idx, (key, (label_key, desc_key)) in enumerate(DIM_DEFINITIONS.items()):
        with cols[idx % 3]:
            if st.button(f"{T(label_key)}\n{T(desc_key)}", key=f"btn_{key}", use_container_width=True):
                goto('Dimension_View', dim=key)

    st.markdown(f"#### {T('header_quick')}")
    l1, l2 = st.columns(2)
    with l1: 
        if st.button(T('btn_list'), use_container_width=True): goto('List')
    with l2:
        rand_id = df_ctx.sample(1).iloc[0]['ID']
        if st.button(T('btn_rand'), use_container_width=True): goto('Profile', uid=rand_id)


# --- B. Dimension View ---
elif st.session_state.view == 'Dimension_View':
    
    if st.button(T('home'), key="btn_back_dim", type="secondary"): goto('Overview')
    st.components.v1.html(f"<script>const buttons = window.parent.document.querySelectorAll('button'); buttons.forEach(btn => {{ if (btn.innerText.includes('{T('home')}')) {{ btn.parentElement.classList.add('fixed-back-btn'); }} }});</script>", height=0)

    curr_dim = st.session_state.sel_dim
    title_key = DIM_DEFINITIONS.get(curr_dim, (curr_dim, ""))[0]
    st.markdown(f"<div class='dim-header'>{T(title_key)}</div>", unsafe_allow_html=True)

    dff = df_ctx 
    si = get_smart_insight(curr_dim, dff)
    st.markdown(f"""
    <div class="smart-insight-card">
        <div class="smart-header"><span>⚡ SMART INSIGHT (v4.0 Alpha) - HRBP Edition</span></div>
        <div class="smart-row"><div class="smart-icon">👁️</div><div><span class="smart-label">{T('smart_obs')}:</span><span class="smart-text">{si['obs']}</span></div></div>
        <div class="smart-row"><div class="smart-icon">🧬</div><div><span class="smart-label">{T('smart_dia')}:</span><span class="smart-text">{si['dia']}</span></div></div>
        <div class="smart-row"><div class="smart-icon">⚡</div><div><span class="smart-label">{T('smart_act')}:</span><span class="smart-text">{si['act']}</span></div></div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Org
    if curr_dim == "Org":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_span'), px.histogram(dff, x="Team", color="Level", barmode="group"), T('in_span'))
        with c2: render_chart_box(T('ct_layer'), px.histogram(dff, y="Level", category_orders={"Level":['P9','P8','P7','P6','P5']}), T('in_layer'))
        with c3: render_chart_box(T('ct_cost_dist'), px.pie(dff, names="Team", values="Salary", hole=0.4), T('in_cost_dist'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_tenure'), px.box(dff, x="Team", y="Tenure", color="Team", custom_data=['ID']), T('in_tenure'))
        with c5: render_chart_box(T('ct_revenue'), px.scatter(dff, x="Salary", y="Perf", color="Team", custom_data=['ID']), T('in_revenue'))
        with c6: render_chart_box(T('ct_flat'), px.bar(dff.groupby('Team')['Level'].nunique().reset_index(), x='Team', y='Level'), T('in_flat'))

    # 2. Talent
    elif curr_dim == "Talent":
        c1, c2, c3 = st.columns(3)
        # 核心：添加 custom_data=['ID']
        with c1: render_chart_box(T('ct_9box'), px.scatter(dff, x="Perf", y="Potential", color="Team", size="Salary", custom_data=['ID']), T('in_9box'))
        with c2: render_chart_box(T('ct_hipo_den'), px.bar(dff.groupby('Team')['Is_HiPo'].mean().reset_index(), x='Team', y='Is_HiPo'), T('in_hipo_den'))
        with c3: render_chart_box(T('ct_bench'), px.histogram(dff[dff['Potential']>4], x='Team'), T('in_bench'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_corr'), px.density_heatmap(dff, x="Perf", y="Potential", nbinsx=10, nbinsy=10, color_continuous_scale='Blues'), T('in_corr'))
        with c5: render_chart_box(T('ct_velocity'), px.scatter(dff, x="Tenure", y="Level", color="Is_HiPo", custom_data=['ID']), T('in_velocity'))
        with c6: render_chart_box(T('ct_skill_rad'), px.line_polar(r=[80, 70, 60, 90, 50], theta=['Tech','Lead','Biz','Strat','Agile'], line_close=True), T('in_skill_rad'))

    # 3. Risk
    elif curr_dim == "Risk":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_risk_dist'), px.histogram(dff, x="Risk_Score", color="Team"), T('in_risk_dist'))
        with c2: render_chart_box(T('ct_regret'), px.scatter(dff[dff['Is_HiPo']], x="Risk_Score", y="Salary", color="Team", custom_data=['ID']), T('in_regret'))
        with c3: render_chart_box(T('ct_inv'), px.box(dff, x="Level", y="Compa_Ratio", custom_data=['ID']), T('in_inv'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_mgr_attr'), px.scatter(dff, x="Manager_Rating", y="Risk_Score", custom_data=['ID'], **get_trendline_params()), T('in_mgr_attr'))
        with c5: render_chart_box(T('ct_burn'), px.line(dff.groupby('Tenure')['Risk_Score'].mean().reset_index(), x='Tenure', y='Risk_Score'), T('in_burn'))
        with c6: render_chart_box(T('ct_impact'), px.pie(dff[dff['Risk_Score']>80], names='Team'), T('in_impact'))

    # 4. Comp
    elif curr_dim == "Comp":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_pen'), px.histogram(dff, x="Compa_Ratio", color="Level", nbins=20), T('in_pen'))
        with c2: 
            dff['Level_Num'] = dff['Level'].astype(str).str.extract(r'(\d+)').astype(int)
            render_chart_box(T('ct_equity'), px.scatter(dff, x="Level_Num", y="Salary", color="Gender", custom_data=['ID'], **get_trendline_params()), T('in_equity'))
        with c3: render_chart_box(T('ct_sens'), px.box(dff, x="Perf", y="Salary", custom_data=['ID']), T('in_sens'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_comp_ext'), px.bar(dff.groupby('Team')['Compa_Ratio'].mean().reset_index(), x='Team', y='Compa_Ratio'), T('in_comp_ext'))
        with c5: render_chart_box(T('ct_cost_str'), px.treemap(dff, path=['Team', 'Level'], values='Salary'), T('in_cost_str'))
        with c6: render_chart_box(T('ct_new_old'), px.scatter(dff, x="Tenure", y="Salary", color="Level", custom_data=['ID']), T('in_new_old'))

    # 5. Recruit
    elif curr_dim == "Recruit":
        c1, c2, c3 = st.columns(3)
        rec_funnel = pd.DataFrame({'Stage':['Apply','Screen','Interview','Offer','Accept','Onboard'], 'Count':[1000,400,150,50,40,38]})
        with c1: render_chart_box(T('ct_funnel'), px.funnel(rec_funnel, x='Count', y='Stage'), T('in_funnel'))
        with c2: render_chart_box(T('ct_chan_qual'), px.scatter(dff, x="Cost_Per_Hire", y="Quality_of_Hire", color="Recruit_Source", custom_data=['ID']), T('in_chan_qual'))
        with c3: render_chart_box(T('ct_time'), px.histogram(dff, x="Time_to_Fill", color="Team"), T('in_time'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_prob'), px.pie(dff[dff['Tenure']<1], names='Perf'), T('in_prob'))
        with c5: render_chart_box(T('ct_int_eff'), px.bar(dff.groupby('Team')['Quality_of_Hire'].mean().reset_index(), x='Team', y='Quality_of_Hire'), T('in_int_eff'))
        with c6: render_chart_box(T('ct_sup'), px.pie(dff, names='Recruit_Source'), T('in_sup'))

    # 6. Train
    elif curr_dim == "Train":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_gap'), px.density_heatmap(dff, x="Team", y="Skill_Gap"), T('in_gap'))
        with c2: render_chart_box(T('ct_roi'), px.scatter(dff, x="Training_Hours", y="Perf", color="Level", custom_data=['ID']), T('in_roi'))
        with c3: render_chart_box(T('ct_cert'), px.bar(dff.groupby('Team')['Certifications'].mean().reset_index(), x='Team', y='Certifications'), T('in_cert'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_learn'), px.histogram(dff, x="Training_Hours"), T('in_learn'))
        with c5: render_chart_box(T('ct_succ_r'), px.pie(dff[dff['Level'].isin(['P8','P9'])], names='Skill_Gap'), T('in_succ_r'))
        with c6: render_chart_box(T('ct_res'), px.bar(dff.groupby('Level')['Training_Hours'].sum().reset_index(), x='Level', y='Training_Hours'), T('in_res'))

    # 7. DEI
    elif curr_dim == "DEI":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_gen'), px.histogram(dff, x="Level", color="Gender", barmode="group"), T('in_gen'))
        with c2: render_chart_box(T('ct_pay_eq'), px.box(dff, x="Level", y="Salary", color="Gender", custom_data=['ID']), T('in_pay_eq'))
        with c3: render_chart_box(T('ct_age'), px.histogram(dff, x="Age", color="Team"), T('in_age'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_hipo_div'), px.pie(dff[dff['Is_HiPo']], names='Gender'), T('in_hipo_div'))
        with c5: render_chart_box(T('ct_prom_eq'), px.bar(dff.groupby('Gender')['Tenure'].mean().reset_index(), x='Gender', y='Tenure'), T('in_prom_eq'))
        with c6: render_chart_box(T('ct_inc'), px.bar(dff.groupby('Team')['Manager_Rating'].mean().reset_index(), x='Team', y='Manager_Rating'), T('in_inc'))

    # 8. Perf
    elif curr_dim == "Perf":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_dist'), px.histogram(dff, x="Perf", color="Team", marginal="box"), T('in_dist'))
        with c2: render_chart_box(T('ct_okr'), px.bar(dff.groupby('Team')['OKR_Completion'].mean().reset_index(), x='Team', y='OKR_Completion'), T('in_okr'))
        with c3: render_chart_box(T('ct_feed'), px.scatter(dff, x="Feedback_Count", y="Perf", custom_data=['ID']), T('in_feed'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_pip'), px.pie(dff[dff['Perf']<2.5], names='Team'), T('in_pip'))
        with c5: render_chart_box(T('ct_cal'), px.box(dff, x="Team", y="Perf", custom_data=['ID']), T('in_cal'))
        with c6: render_chart_box(T('ct_align'), px.scatter(dff, x="OKR_Completion", y="Perf", custom_data=['ID']), T('in_align'))

    # 9. Lead
    elif curr_dim == "Lead":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_eff'), px.histogram(dff, x="Manager_Rating", nbins=10), T('in_eff'))
        with c2: render_chart_box(T('ct_up'), px.scatter(dff, x="Manager_Rating", y="Risk_Score", custom_data=['ID'], **get_trendline_params()), T('in_up'))
        with c3: render_chart_box(T('ct_pipe'), px.bar(dff[dff['Level']>'P7'].groupby('Team').size().reset_index(), x='Team', y=0), T('in_pipe'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_style'), px.density_heatmap(dff, x="Team", y="Manager_Rating"), T('in_style'))
        with c5: render_chart_box(T('ct_inv_l'), px.bar(dff[dff['Level']>'P6'].groupby('Level')['Training_Hours'].mean().reset_index(), x='Level', y='Training_Hours'), T('in_inv_l'))
        with c6: render_chart_box(T('ct_high'), px.box(dff, x="Manager_Rating", y="OKR_Completion", custom_data=['ID']), T('in_high'))

    # 10. Plan
    elif curr_dim == "Plan":
        c1, c2, c3 = st.columns(3)
        with c1: render_chart_box(T('ct_fc'), px.bar(dff.groupby('Team')['Salary'].sum().reset_index(), x='Team', y='Salary'), T('in_fc'))
        df_growth = dff.sort_values('Join_Date')
        df_growth['Cumulative_Headcount'] = range(1, len(df_growth) + 1)
        with c2: render_chart_box(T('ct_hc'), px.line(df_growth, x='Join_Date', y='Cumulative_Headcount'), T('in_hc'))
        with c3: render_chart_box(T('ct_roi_p'), px.scatter(dff, x="Salary", y="OKR_Completion", color="Team", custom_data=['ID']), T('in_roi_p'))
        c4, c5, c6 = st.columns(3)
        with c4: render_chart_box(T('ct_var'), px.pie(dff, names='Level', values='Salary'), T('in_var'))
        with c5: render_chart_box(T('ct_rec_b'), px.bar(dff.groupby('Team')['Cost_Per_Hire'].sum().reset_index(), x='Team', y='Cost_Per_Hire'), T('in_rec_b'))
        with c6: render_chart_box(T('ct_repl'), px.histogram(dff, x="Salary", title="Assuming 6mo Replacement Cost"), T('in_repl'))

# --- C. List View ---
elif st.session_state.view == 'List':
    if st.button(T('home'), key="btn_back_list", type="secondary"): goto('Overview')
    st.components.v1.html(f"<script>const buttons = window.parent.document.querySelectorAll('button'); buttons.forEach(btn => {{ if (btn.innerText.includes('{T('home')}')) {{ btn.parentElement.classList.add('fixed-back-btn'); }} }});</script>", height=0)

    st.markdown(f"## {T('btn_list')}")
    cols = ['ID', 'Name', 'Team', 'Level', 'Salary', 'Perf', 'Risk_Score', 'Is_HiPo']
    event = st.dataframe(df_ctx[cols], selection_mode="single-row", on_select="rerun", use_container_width=True, height=600)
    if len(event.selection.rows) > 0:
        target_uid = df_ctx.iloc[event.selection.rows[0]]['ID']
        goto('Profile', uid=target_uid)

# --- D. Profile View ---
elif st.session_state.view == 'Profile':
    if st.button(T('home'), key="btn_back_profile", type="secondary"): goto('Overview')
    st.components.v1.html(f"<script>const buttons = window.parent.document.querySelectorAll('button'); buttons.forEach(btn => {{ if (btn.innerText.includes('{T('home')}')) {{ btn.parentElement.classList.add('fixed-back-btn'); }} }});</script>", height=0)

    uid = st.session_state.sel_uid
    rec = df_master[df_master['ID']==uid].iloc[0]

    st.markdown(f"""
    <div class="profile-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <h1 style="margin:0; font-size:24px; color:#1E293B;">{rec['Name']}</h1>
                <p style="color:#64748B; margin-top:4px; font-size:13px;">{rec['ID']} | {rec['Team']} | {rec['Level']}</p>
            </div>
            <div style="text-align:right">
                <h2 style="color:#0F172A; margin:0; font-size:24px;">¥{rec['Salary']}k</h2>
                <span class="tag-critical" style="display:inline-block; margin-top:6px;">Risk Score: {rec['Risk_Score']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**{T('p_perf_pot')}**")
        st.metric(T('lbl_perf'), rec['Perf'])
        st.metric(T('lbl_pot'), rec['Potential'])
        st.info(f"{T('lbl_hipo')}: {'Yes 🌟' if rec['Is_HiPo'] else 'No'}")
    
    with c2:
        st.markdown(f"**{T('p_eng_growth')}**")
        st.metric(T('lbl_mgr'), rec['Manager_Rating'])
        st.metric(T('lbl_okr'), f"{rec['OKR_Completion']*100:.0f}%")
        st.write(f"**{T('lbl_skill')}:** {rec['Skill_Gap']}")

    with c3:
        st.markdown(f"**{T('p_history')}**")
        st.write(f"**{T('lbl_join')}:** {rec['Join_Date']}")
        st.write(f"**{T('lbl_tenure')}:** {rec['Tenure']}")
        st.write(f"**{T('lbl_src')}:** {rec['Recruit_Source']}")
        st.write(f"**{T('lbl_risk')}:** {rec['Risk_Flags']}")