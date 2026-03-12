import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
import hashlib
from datetime import datetime, timedelta

# ==========================================
# 1. 系统配置 (SYSTEM CONFIG)
# ==========================================
st.set_page_config(
    page_title="GATE Executive Command Center v21.0",
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
# 全局筛选状态
if 'filter_company' not in st.session_state: st.session_state.filter_company = 'All'
if 'filter_role' not in st.session_state: st.session_state.filter_role = 'All'
if 'filter_region' not in st.session_state: st.session_state.filter_region = 'All'
# 对比维度专用状态
if 'compare_companies' not in st.session_state: st.session_state.compare_companies = []
if 'compare_roles' not in st.session_state: st.session_state.compare_roles = []

def change_view(target_view, uid=None, dim=None, list_filters=None):
    st.session_state.view = target_view
    if uid: st.session_state.sel_uid = uid
    if dim: st.session_state.sel_dim = dim
    if list_filters: 
        if 'Company' in list_filters: st.session_state.filter_company = list_filters['Company']
        if 'Role' in list_filters: st.session_state.filter_role = list_filters['Role']

def go_back_callback():
    if st.session_state.view == 'Profile':
        if st.session_state.sel_dim: change_view('Dimension_View')
        else: change_view('List')
    elif st.session_state.view in ['Dimension_View', 'List']:
        change_view('Overview')
    else:
        change_view('Overview')

def go_home_callback():
    change_view('Overview')

# ==========================================
# 3. GATE Design System (World-Class UX Injection)
# ==========================================
st.markdown("""
<style>
    /* -------------------------------------- */
    /* 1. Typography & Reset (Inter Font)     */
    /* -------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-body: #F8FAFC; 
        --bg-card: #FFFFFF;
        --primary-500: #2563EB; /* Brand Blue */
        --primary-600: #1D4ED8;
        --slate-50: #F8FAFC;
        --slate-100: #F1F5F9;
        --slate-200: #E2E8F0;
        --slate-400: #94A3B8;
        --slate-500: #64748B;
        --slate-800: #1E293B;
        --slate-900: #0F172A;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --radius-md: 0.75rem;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: var(--bg-body); color: var(--slate-900); }
    
    /* Optimize Container */
    .block-container { 
        padding-top: 5.5rem !important; 
        padding-bottom: 4rem !important; 
        max-width: 98% !important;
    }

    /* -------------------------------------- */
    /* 2. Glassmorphism Navigation            */
    /* -------------------------------------- */
    .nav-header {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--slate-200);
        position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
        display: flex; justify-content: space-between; align-items: center; 
        height: 72px; padding: 0 40px;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    .nav-title { 
        font-size: 20px; font-weight: 800; letter-spacing: -0.5px;
        color: var(--slate-900); display: flex; align-items: center; gap: 16px; 
    }
    .nav-tag { 
        background: linear-gradient(135deg, #3B82F6, #2563EB); 
        color: white; padding: 4px 12px; border-radius: 999px; 
        font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3);
    }
    .nav-status {
        font-family: 'Inter'; font-size: 12px; color: var(--slate-500); 
        font-weight: 600; background: var(--slate-100); 
        padding: 6px 16px; border-radius: 6px;
    }

    /* -------------------------------------- */
    /* 3. High-End Button/Card Interaction    */
    /* -------------------------------------- */
    /* Override Streamlit Buttons to look like Interactive Cards */
    div.stButton > button {
        width: 100%; min-height: 88px !important; padding: 20px 24px !important;
        background-color: var(--bg-card); 
        border: 1px solid var(--slate-200); 
        border-radius: var(--radius-md);
        text-align: left; display: flex; flex-direction: column; justify-content: center;
        box-shadow: var(--shadow-sm); 
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        color: var(--slate-800);
    }
    div.stButton > button:hover { 
        border-color: var(--primary-500); 
        transform: translateY(-3px); 
        box-shadow: var(--shadow-lg);
        background-color: #FFFFFF;
        z-index: 10;
    }
    div.stButton > button:active { transform: translateY(-1px); }
    
    /* Specific styling for small control buttons */
    div[data-testid="column"] div.stButton > button {
        min-height: auto !important;
    }

    /* -------------------------------------- */
    /* 4. Chart & Content Containers          */
    /* -------------------------------------- */
    .chart-box { 
        background: var(--bg-card); border-radius: var(--radius-md); 
        padding: 24px; margin-bottom: 24px; 
        border: 1px solid var(--slate-200); 
        box-shadow: var(--shadow-sm);
        height: 100%; display: flex; flex-direction: column;
        transition: box-shadow 0.3s ease;
    }
    .chart-box:hover { box-shadow: var(--shadow-md); }
    
    .chart-title { 
        font-size: 15px; font-weight: 700; color: var(--slate-900); 
        margin-bottom: 16px; display: flex; align-items: center;
    }
    .chart-title::before {
        content: ''; display: inline-block; width: 4px; height: 16px;
        background: var(--primary-500); margin-right: 12px; border-radius: 2px;
    }
    
    .expert-insight { 
        background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF;
        padding: 12px 16px; margin-top: 16px; border-radius: 8px; 
        font-size: 13px; line-height: 1.6; font-weight: 500;
        display: flex; gap: 8px;
    }
    
    .chart-legend {
        margin-top: 8px; padding: 12px 16px; 
        background: var(--slate-50); border-radius: 8px;
        font-size: 12px; color: var(--slate-500); line-height: 1.5; 
    }

    /* -------------------------------------- */
    /* 5. Smart Executive Summary Card        */
    /* -------------------------------------- */
    .smart-insight-card {
        background: #FFFFFF; 
        border: 1px solid var(--slate-200); 
        border-radius: 16px; padding: 32px; margin-bottom: 40px;
        box-shadow: var(--shadow-md); 
        border-left: 6px solid var(--primary-500);
        position: relative; overflow: hidden;
    }
    .smart-insight-card::after {
        content: ""; position: absolute; top:0; right:0; width: 200px; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(37,99,235,0.03));
        pointer-events: none;
    }
    .smart-header { 
        font-size: 14px; letter-spacing: 1px; text-transform: uppercase;
        font-weight: 800; color: var(--primary-600); margin-bottom: 20px; 
        display: flex; align-items: center; gap: 10px; 
    }
    .smart-row { 
        display: flex; gap: 16px; margin-bottom: 14px; 
        font-size: 14px; line-height: 1.6; color: var(--slate-800); 
        align-items: flex-start;
    }
    .smart-icon {
        flex-shrink: 0; width: 24px; height: 24px; 
        display: flex; align-items: center; justify-content: center;
        background: var(--slate-100); border-radius: 50%; font-size: 14px;
    }

    /* -------------------------------------- */
    /* 6. KPI Stats Cards                     */
    /* -------------------------------------- */
    .kpi-card {
        background: white; border: 1px solid var(--slate-200); border-radius: 12px; padding: 20px;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: var(--primary-500); }
    .kpi-label { color: var(--slate-500); font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { color: var(--slate-900); font-size: 28px; font-weight: 800; margin-top: 8px; letter-spacing: -1px; }
    .kpi-sub { color: var(--primary-600); font-size: 12px; font-weight: 600; margin-top: 6px; display: flex; align-items: center; gap: 4px; }

    /* -------------------------------------- */
    /* 7. Floating Action Buttons (Refined)   */
    /* -------------------------------------- */
    .float-btn {
        position: fixed !important; right: 0px !important; width: 56px !important; z-index: 9999999 !important;
        border-radius: 12px 0 0 12px !important; 
        writing-mode: vertical-rl !important; text-orientation: upright !important;
        font-weight: 700 !important; letter-spacing: 4px !important; font-size: 11px !important;
        box-shadow: -4px 8px 20px rgba(0,0,0,0.15) !important; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        padding: 24px 0 !important; display: flex !important; align-items: center !important; justify-content: center !important;
        min-height: 140px !important; border: none !important;
    }
    .float-btn:hover { padding-right: 24px !important; width: 72px !important; transform: translateX(-4px); }
    
    .float-btn-back { top: 35% !important; background: var(--slate-800) !important; color: white !important; }
    .float-btn-home { top: 52% !important; background: var(--primary-500) !important; color: white !important; }
    .float-btn p { margin: 0 !important; color: white !important; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 鲁棒 ETL 引擎
# ==========================================
@st.cache_data
def load_and_process_data():
    frames = []
    
    def clean_money(val):
        if pd.isna(val): return 0
        s = str(val).strip().lower()
        if s in ['hidden', '不适用', '-', '', 'nan', 'none']: return 0
        try:
            if '-' in s:
                parts = s.split('-')
                v1 = clean_money(parts[0])
                v2 = clean_money(parts[1])
                return (v1+v2)/2 if v1>0 and v2>0 else v1
            mul = 10000 if '万' in s else 1
            matches = re.findall(r"(\d+\.?\d*)", s.replace(',', ''))
            return float(matches[0]) * mul if matches else 0
        except: return 0

    def clean_date(val, capture_time=None):
        s = str(val).strip()
        base = pd.to_datetime(capture_time) if pd.notnull(capture_time) else datetime.now()
        try:
            if 'days ago' in s:
                days = int(re.search(r'(\d+)', s).group(1))
                return base - timedelta(days=days)
            if 'today' in s.lower(): return base
            return pd.to_datetime(s, errors='coerce')
        except: return pd.NaT

    try:
        try: df1 = pd.read_csv('crypto_companies_salary_latest.csv')
        except: df1 = pd.read_csv('crypto_companies_salary_latest.csv', encoding='gbk')
        df1['Source'] = 'Latest'
        map1 = {'总薪酬USD':'Total', '基本工资':'Base', '股票(年)':'Stock', '奖金':'Bonus', 
                '日期':'Date', '公司':'Company', '职位':'Role', '总计工作年数':'YOE', 
                '地区':'Region', '地点':'Location', '级别名称':'Level', '标签':'Tags', 'Source_URL': 'URL'}
        df1.rename(columns={k:v for k,v in map1.items() if k in df1.columns}, inplace=True)
        frames.append(df1)
    except: pass

    try:
        try: df2 = pd.read_csv('crypto_companies_salary.csv')
        except: df2 = pd.read_csv('crypto_companies_salary.csv', encoding='gbk')
        df2['Source'] = 'General'
        map2 = {'总计':'Total', '基本工资':'Base', '股票':'Stock', '奖金':'Bonus', 
                '公司':'Company', '职位':'Role', '地区':'Region', '级别名称':'Level', 'Source_URL': 'URL'}
        df2.rename(columns={k:v for k,v in map2.items() if k in df2.columns}, inplace=True)
        frames.append(df2)
    except: pass

    if not frames: return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)

    for col in ['Total', 'Base', 'Stock', 'Bonus', 'Company', 'Role', 'Region', 'Location', 'YOE', 'Date', 'Tags', 'Level', 'URL', 'Capture_Time']:
        if col not in df.columns: df[col] = np.nan
    
    df['UID'] = [hashlib.md5(f"{r['Company']}{r['Role']}{i}".encode()).hexdigest()[:8] for i, r in df.iterrows()]
    
    for c in ['Total', 'Base', 'Stock', 'Bonus']:
        df[f'{c}_Clean'] = df[c].apply(clean_money)
    
    df['Final_Comp'] = np.where(df['Total_Clean']>0, df['Total_Clean'], df['Base_Clean']+df['Stock_Clean']+df['Bonus_Clean'])
    df['YOE_Clean'] = df['YOE'].apply(lambda x: clean_money(str(x).replace('年','')))
    df['Date_Clean'] = df.apply(lambda x: clean_date(x['Date'], x.get('Capture_Time')), axis=1)
    
    df['Equity_Ratio'] = df['Stock_Clean'] / df['Final_Comp'].replace(0, 1)
    df['Hourly_Rate'] = df['Final_Comp'] / 2000
    df['Net_Pay_Est'] = df['Final_Comp'] * 0.7
    
    def extract_skills(tags_str):
        if pd.isna(tags_str): return []
        return [t.strip() for t in str(tags_str).split(',') if t.strip()]
    df['Skills_List'] = df['Tags'].apply(extract_skills)

    def norm_geo(row):
        txt = (str(row.get('Region','')) + str(row.get('Location',''))).lower()
        if 'singapore' in txt: return 'Singapore'
        if 'united states' in txt or 'ny' in txt or 'ca' in txt or 'san francisco' in txt: return 'USA'
        if 'remote' in txt: return 'Remote'
        if 'hong kong' in txt: return 'Hong Kong'
        if 'uk' in txt or 'london' in txt: return 'UK'
        return 'Global'
    df['Region_Group'] = df.apply(norm_geo, axis=1)
    
    def norm_role(r):
        s = str(r).lower()
        if 'engineer' in s or 'developer' in s or '开发' in s: return 'Engineering'
        if 'product' in s or '产品' in s: return 'Product'
        if 'design' in s or '设计' in s: return 'Design'
        if 'data' in s or 'analy' in s: return 'Data'
        return 'Other'
    df['Role_Group'] = df['Role'].apply(norm_role)

    return df

df_master = load_and_process_data()
df_skills = df_master.explode('Skills_List')
df_skills = df_skills[df_skills['Skills_List'].notna()]
df_skills = df_skills[df_skills['Skills_List'] != '']

# ==========================================
# 5. 智能归因引擎
# ==========================================
def get_crypto_insight(context, df):
    if df.empty: return {'obs':"暂无数据", 'dia':"需补充数据源", 'act':"请清除筛选条件"}
    avg = df['Final_Comp'].median()
    res = {'obs':"", 'dia':"", 'act':""}
    
    if context == 'Overview':
        res['obs'] = f"**[样本监测]** 实时追踪 `{len(df)}` 个薪酬数据点。全市场中位数 `${avg:,.0f}`。"
        res['dia'] = "**[市场特征]** 数据呈现明显的分层结构。Tier 1 交易所与 DAO 组织的薪酬体系差异显著。"
        res['act'] = "**[操作建议]** 探索下方的 **'⚔️ 竞对深度对标'** 模块，进行 Company vs Company 的精确比对。"
    elif context == 'dim_compare':
        res['obs'] = f"**[对标状态]** 正在对比 `{len(df['Company'].unique())}` 家公司的 `{len(df)}` 个 Offer。"
        res['dia'] = "**[差异分析]** 箱线图的上限代表了该公司的最高支付意愿，下限代表起薪门槛。请注意各公司在同一岗位上的定价断层。"
        res['act'] = "**[决策辅助]** 利用上方的控制器切换对标公司和岗位。点击图表中的点可直接查看对应的 JD/Offer 详情。"
    else:
        res['obs'] = f"**[当前维度]** 有效样本 N=`{len(df)}`。该维度下的薪酬峰值为 `${df['Final_Comp'].max():,.0f}`。"
        res['dia'] = "**[分布诊断]** 请注意图表中的异常高值点，它们通常代表了该细分领域的定价天花板。"
        res['act'] = "**[交互提示]** 所有的柱状图和散点图均支持点击交互，可直接穿透至原始数据列表。"
    return res

# ==========================================
# 6. UI 渲染：顶部导航 & 筛选器
# ==========================================
st.markdown('<div class="nav-spacer" style="height: 80px;"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="nav-header">
    <div class="nav-title">
        🦅 GATE Command Center
        <span class="nav-tag">v21.0 Battle Mode</span>
    </div>
    <div class="nav-status">VIEW: {st.session_state.view}</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.view in ['Overview', 'List']:
    with st.container():
        st.write("") 
        f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.5, 1])
        all_comps = ['All'] + sorted(df_master['Company'].dropna().astype(str).unique().tolist())
        all_roles = ['All'] + sorted(df_master['Role'].dropna().astype(str).unique().tolist())
        all_regions = ['All'] + sorted(df_master['Region_Group'].dropna().unique().tolist())
        with f1: sel_comp = st.selectbox("🏢 公司 / Company", all_comps, index=all_comps.index(st.session_state.filter_company) if st.session_state.filter_company in all_comps else 0)
        with f2: sel_role = st.selectbox("🧑‍💻 职位 / Role", all_roles, index=all_roles.index(st.session_state.filter_role) if st.session_state.filter_role in all_roles else 0)
        with f3: sel_region = st.selectbox("🌍 区域 / Region", all_regions, index=all_regions.index(st.session_state.filter_region) if st.session_state.filter_region in all_regions else 0)
        with f4:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True) 
            if st.button("🔄 Reset Filter", use_container_width=True):
                st.session_state.filter_company = 'All'; st.session_state.filter_role = 'All'; st.session_state.filter_region = 'All'; st.rerun()
        if sel_comp != st.session_state.filter_company: st.session_state.filter_company = sel_comp; st.rerun()
        if sel_role != st.session_state.filter_role: st.session_state.filter_role = sel_role; st.rerun()
        if sel_region != st.session_state.filter_region: st.session_state.filter_region = sel_region; st.rerun()
    st.markdown("---")

df_ctx = df_master.copy()
if st.session_state.filter_company != 'All': df_ctx = df_ctx[df_ctx['Company'] == st.session_state.filter_company]
if st.session_state.filter_role != 'All': df_ctx = df_ctx[df_ctx['Role'] == st.session_state.filter_role]
if st.session_state.filter_region != 'All': df_ctx = df_ctx[df_ctx['Region_Group'] == st.session_state.filter_region]

# ==========================================
# 7. 增强组件渲染
# ==========================================
def render_kpi_card(label, value, sub_text=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

def render_chart_box(title, fig, insight, explanation, chart_key, height=380):
    st.markdown(f"<div class='chart-box'><div class='chart-title'>{title}</div>", unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # World-Class Plotly Configuration (Visual Overhaul)
    # ----------------------------------------------------
    fig.update_layout(
        font=dict(family="Inter, sans-serif", size=11, color="#64748B"),
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor="#E2E8F0", 
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#F1F5F9", 
            gridwidth=1, 
            zeroline=False, 
            tickfont=dict(color="#94A3B8")
        ),
        hoverlabel=dict(
            bgcolor="white", 
            bordercolor="#E2E8F0", 
            font_size=12, 
            font_family="Inter, sans-serif"
        ),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=10)
        ),
        colorway=["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#1E40AF"] # GATE Brand Blues
    )
    
    event = st.plotly_chart(
        fig,
        use_container_width=True, 
        on_select="rerun", 
        selection_mode="points", 
        key=f"chart_{chart_key}",
        config={'displayModeBar': False}
    )
    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        if 'customdata' in point: change_view('Profile', uid=point['customdata'][0])
        elif 'label' in point: change_view('List', list_filters={'Company': point['label']})
        elif 'x' in point: change_view('List', list_filters={'Company': point['x']})
    
    st.markdown(f"""
    <div class='expert-insight'><span>💡</span> <span>{insight}</span></div>
    <div class='chart-legend'><strong>图表说明：</strong>{explanation}</div>
    </div>
    """, unsafe_allow_html=True)

def render_smart_insight(data, title):
    st.markdown(f"""
    <div class="smart-insight-card">
        <div class="smart-header"><span>⚡ AI DIAGNOSTIC - {title}</span></div>
        <div class="smart-row"><div class="smart-icon">👁️</div><div>{data['obs']}</div></div>
        <div class="smart-row"><div class="smart-icon">🧬</div><div>{data['dia']}</div></div>
        <div class="smart-row"><div class="smart-icon">🚀</div><div>{data['act']}</div></div>
    </div>
    """, unsafe_allow_html=True)

def render_dim_card(key, title, desc, icon):
    # CSS hack included in global styles to target these buttons specifically if needed
    st.button(f"{icon} {title}\n{desc}", key=f"dim_{key}", use_container_width=True, on_click=change_view, args=('Dimension_View', None, key))

def render_floating_buttons():
    st.button("↩ RETURN", key="btn_float_back", on_click=go_back_callback)
    st.button("🏠 HOME", key="btn_float_home", on_click=go_home_callback)
    st.markdown("""
    <script>
        const observer_float = new MutationObserver((mutations) => {
            const buttons = parent.document.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.innerText.includes("RETURN") && !btn.classList.contains("float-btn")) {
                    btn.classList.add("float-btn", "float-btn-back");
                    btn.innerHTML = "<p>↩ 返回上级</p>"; 
                }
                if (btn.innerText.includes("HOME") && !btn.classList.contains("float-btn")) {
                    btn.classList.add("float-btn", "float-btn-home");
                    btn.innerHTML = "<p>🏠 返回主页</p>";
                }
            });
        });
        observer_float.observe(parent.document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# 8. 核心视图路由
# ==========================================

# --- A. Overview ---
if st.session_state.view == 'Overview':
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: render_kpi_card("有效样本 (N)", len(df_ctx), "Validated Offers")
    with k2: render_kpi_card("中位年薪 (P50)", f"${df_ctx['Final_Comp'].median():,.0f}", "Market Benchmark")
    with k3: render_kpi_card("时薪估算 (Hourly)", f"${df_ctx['Hourly_Rate'].mean():.1f}", "Approx Rate")
    with k4: render_kpi_card("最高年薪 (Max)", f"${df_ctx['Final_Comp'].max():,.0f}", "Talent Ceiling")
    with k5: render_kpi_card("变异系数 (CV)", f"{df_ctx['Final_Comp'].std() / df_ctx['Final_Comp'].mean():.2f}", "Market Volatility")

    si = get_crypto_insight('Overview', df_ctx)
    render_smart_insight(si, "EXECUTIVE SUMMARY")

    st.markdown("#### 🔭 ANALYTIC DIMENSIONS ")
    
    # New Comparison Module at Top
    st.markdown("##### ⚔️ COMPETITOR BATTLE (HEAD-TO-HEAD)")
    c_battle = st.container()
    with c_battle:
        render_dim_card('dim_compare', '竞对深度对标', 'Company vs Company Battle', '⚔️')
    
    st.markdown("##### 📊 STANDARD DIMENSIONS")
    d1, d2, d3, d4, d5, d6 = st.columns(6)
    with d1: render_dim_card('dim_market', '市场竞争格局', 'Share', '🏦')
    with d2: render_dim_card('dim_structure', '薪酬结构工程', 'Mix', '💰')
    with d3: render_dim_card('dim_levels', '职级架构分析', 'Levels', '🪜')
    with d4: render_dim_card('dim_equity', '股权激励透视', 'Equity', '📜')
    with d5: render_dim_card('dim_geo', '地理与远程', 'Geo', '🌍')
    with d6: render_dim_card('dim_skills', '技能与技术栈', 'Skills', '⚡')
    
    d7, d8, d9, d10, d11, d12 = st.columns(6)
    with d7: render_dim_card('dim_talent', '岗位效能对比', 'Role', '🎯')
    with d8: render_dim_card('dim_trends', '时间趋势雷达', 'Trend', '📈')
    with d9: render_dim_card('dim_outliers', '异常值监测', 'Outliers', '🚨')
    with d10: render_dim_card('dim_efficiency', '薪酬效能比', 'ROI', '⚖️')
    with d11: render_dim_card('dim_hourly', '时薪真实价值', 'Hourly', '⏱️')
    with d12: render_dim_card('dim_inflation', '职级通胀诊断', 'Inflation', '🎈')

    d13, d14, d15, d16, d17, d18 = st.columns(6)
    with d13: render_dim_card('dim_tiering', '公司分层定位', 'Tiering', '🏆')
    with d14: render_dim_card('dim_velocity', '招聘速度监测', 'Velocity', '🐆')
    with d15: render_dim_card('dim_netpay', '净收入估算', 'Net Pay', '💸')
    with d16: render_dim_card('dim_clusters', '标签聚类分析', 'Clusters', '🕸️')
    with d17: render_dim_card('dim_benchmark', '对标偏离度', 'Vs Avg', '📏')
    with d18: render_dim_card('dim_health', '数据健康度', 'Quality', '🏥')

    st.markdown("---")
    st.button("📋 Access Full Data List", key="go_list_main", use_container_width=True, on_click=change_view, args=('List',))

# --- B. Dimension View (With Comparison Engine) ---
elif st.session_state.view == 'Dimension_View':
    
    render_floating_buttons() 
    curr_dim = st.session_state.sel_dim
    titles = {
        'dim_compare': '⚔️ 竞对深度对标 (Competitor Battle)',
        'dim_market':'🏦 市场竞争格局', 'dim_structure':'💰 薪酬结构工程', 'dim_levels':'🪜 职级架构分析', 
        'dim_equity':'📜 股权激励透视', 'dim_geo':'🌍 地理与远程策略', 'dim_trends':'📈 时间趋势雷达',
        'dim_skills':'⚡ 技能与技术栈', 'dim_talent':'🎯 岗位效能对比', 'dim_outliers':'🚨 异常值监测',
        'dim_efficiency':'⚖️ 薪酬效能比', 'dim_hourly':'⏱️ 时薪真实价值', 'dim_inflation':'🎈 职级通胀诊断',
        'dim_tiering':'🏆 公司分层定位', 'dim_velocity':'🐆 招聘速度监测', 'dim_netpay':'💸 净收入估算',
        'dim_clusters':'🕸️ 标签聚类分析', 'dim_benchmark':'📏 对标偏离度', 'dim_health':'🏥 数据健康度'
    }
    
    st.markdown(f"## {titles.get(curr_dim, 'Dimension Analysis')}")
    
    # ---------------- D19: Competitor Battle (NEW) ----------------
    if curr_dim == 'dim_compare':
        # Local Controller
        with st.container():
            st.markdown("### 🎛️ BATTLE CONTROLLER")
            cc1, cc2 = st.columns(2)
            all_c = sorted(df_master['Company'].dropna().unique().tolist())
            all_r = sorted(df_master['Role'].dropna().unique().tolist())
            
            with cc1:
                sel_comps = st.multiselect("选择对标公司 (Select Companies)", all_c, default=all_c[:2] if len(all_c)>1 else all_c, key='cmp_c')
            with cc2:
                sel_roles = st.multiselect("选择对标岗位 (Select Roles - Optional)", all_r, default=[], key='cmp_r')
            
            # Filter Data (Use df_master to ignore global filter)
            df_battle = df_master[df_master['Company'].isin(sel_comps)] if sel_comps else df_master
            if sel_roles: df_battle = df_battle[df_battle['Role'].isin(sel_roles)]
        
        si_dim = get_crypto_insight(curr_dim, df_battle)
        render_smart_insight(si_dim, "HEAD-TO-HEAD ANALYSIS")
        
        c1, c2 = st.columns(2); c3, c4 = st.columns(2); c5, c6 = st.columns(2)
        
        with c1: render_chart_box("全维薪酬擂台 (Box Battle)", px.box(df_battle, x='Company', y='Final_Comp', color='Company', points='all', custom_data=['UID']), "展示各公司薪酬的天花板与地板。", 
            "**箱体**代表中位数与四分位范围，**散点**代表具体Offer。可直观对比谁家的薪酬带宽更宽、上限更高。", "bt1")
        
        # Role Pricing
        role_stats = df_battle.groupby(['Company','Role'])['Final_Comp'].median().reset_index()
        # Filter for roles present in at least 2 companies for better comparison if possible, else show all top
        top_roles_battle = df_battle['Role'].value_counts().head(10).index
        role_stats = role_stats[role_stats['Role'].isin(top_roles_battle)]
        with c2: render_chart_box("核心岗位定价 PK", px.bar(role_stats, x='Final_Comp', y='Role', color='Company', barmode='group', orientation='h'), "同岗位谁给的钱多？", 
            "分组条形图。**Y轴**为热门岗位，**条形长度**为中位薪酬。同一岗位的不同颜色条形直接对比各家出价。", "bt2")
            
        with c3: render_chart_box("经验回报率曲线 (Pay vs YOE)", px.scatter(df_battle, x='YOE_Clean', y='Final_Comp', color='Company', trendline='lowess'), "谁家更尊重资历？", 
            "**斜率**越陡峭，说明随着工龄增长，薪酬涨幅越快。趋势线位于上方的公司在同等经验下给薪更高。", "bt3")
            
        # Seniority Premium
        df_battle['Is_Senior'] = df_battle['Role'].astype(str).str.contains('Senior|Lead|Staff|Manager', case=False)
        senior_pay = df_battle[df_battle['Is_Senior']].groupby('Company')['Final_Comp'].median().reset_index()
        with c4: render_chart_box("高级职级溢价 (Senior Premium)", px.bar(senior_pay, x='Company', y='Final_Comp', color='Company'), "Senior Title 含金量对比。", 
            "仅统计带有 Senior/Lead/Staff 等关键词的岗位。展示各家公司对**高阶人才**的定价水位。", "bt4")
            
        with c5: render_chart_box("现金/期权结构战 (Mix Battle)", px.bar(df_battle.groupby('Company')[['Base_Clean','Stock_Clean']].mean().reset_index(), x='Company', y=['Base_Clean','Stock_Clean']), "现金为王还是期权画饼？", 
            "堆叠柱状图。**蓝色**通常为底薪，**红色/绿色**为股票。可识别哪家公司更倾向于给现金（风险低），哪家给期权（杠杆高）。", "bt5")
            
        with c6: render_chart_box("时薪效能对决 (Hourly Efficiency)", px.box(df_battle, x='Company', y='Hourly_Rate', color='Company'), "剥离加班因素后的真实时薪。", 
            "假设年均工作2000小时计算出的时薪。如果某公司总包高但时薪低，说明可能存在**严重的加班文化**。", "bt6")

    # ---------------- Standard Dimensions ----------------
    else:
        si_dim = get_crypto_insight(curr_dim, df_ctx)
        render_smart_insight(si_dim, titles.get(curr_dim).split(' ')[1])
        
        layout_2col = ['dim_trends', 'dim_geo', 'dim_skills', 'dim_clusters', 'dim_velocity', 'dim_outliers']
        if curr_dim in layout_2col:
            c1, c2 = st.columns(2); c3, c4 = st.columns(2); c5, c6 = st.columns(2)
        else:
            c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)

        if curr_dim == 'dim_market':
            p50 = df_ctx.groupby('Company')['Final_Comp'].median().reset_index().sort_values('Final_Comp').tail(15)
            with c1: render_chart_box("Top 15 中位薪酬", px.bar(p50, x='Final_Comp', y='Company', orientation='h', color='Final_Comp'), "头部溢价。", "Y轴为公司，X轴为薪酬中位数。", "m1")
            with c2: render_chart_box("市场份额", px.pie(df_ctx, names='Company', hole=0.6), "头部效应。", "样本量占比。", "m2")
            with c3: render_chart_box("薪酬带宽", px.box(df_ctx, x='Company', y='Final_Comp'), "内部差异。", "箱线图展示分布。", "m3")
            with c4: render_chart_box("直方图分布", px.histogram(df_ctx, x='Final_Comp', nbins=40, color='Company'), "右偏分布。", "薪酬区间分布。", "m4")
            df_s = df_ctx.sort_values('Final_Comp'); df_s['CP'] = np.linspace(0,1,len(df_s)); df_s['CC'] = df_s['Final_Comp'].cumsum()/df_s['Final_Comp'].sum()
            with c5: render_chart_box("不平等曲线", px.line(df_s, x='CP', y='CC'), "贫富差距。", "洛伦兹曲线。", "m5")
            with c6: render_chart_box("分层定位", px.scatter(df_ctx, x='Company', y='Final_Comp', color='Role_Group'), "人才侧重。", "公司与薪酬定位。", "m6")

        elif curr_dim == 'dim_hourly':
            with c1: render_chart_box("时薪分布", px.histogram(df_ctx, x='Hourly_Rate', nbins=30), "分布。", "基于2000小时计算。", "h1")
            with c2: render_chart_box("公司平均时薪", px.bar(df_ctx.groupby('Company')['Hourly_Rate'].mean().reset_index(), x='Company', y='Hourly_Rate'), "价值。", "平均时薪。", "h2")
            with c3: render_chart_box("时薪 vs 总薪", px.scatter(df_ctx, x='Final_Comp', y='Hourly_Rate'), "相关性。", "线性关系。", "h3")
            with c4: render_chart_box("岗位时薪排行", px.box(df_ctx, x='Hourly_Rate', y='Role'), "高单价。", "岗位时薪分布。", "h4")
            with c5: render_chart_box("时薪热力", px.density_heatmap(df_ctx, x='YOE_Clean', y='Hourly_Rate'), "兑换率。", "经验与时薪。", "h5")
            with c6: render_chart_box("低时薪陷阱", px.scatter(df_ctx[df_ctx['Hourly_Rate']<50], x='Company', y='Hourly_Rate'), "低效能。", "低于$50的数据。", "h6")

        elif curr_dim == 'dim_tiering':
            meds = df_ctx.groupby('Company')['Final_Comp'].median()
            q33 = meds.quantile(0.33); q66 = meds.quantile(0.66)
            df_ctx['Tier'] = df_ctx['Company'].map(lambda x: 'Tier 1' if meds.get(x,0)>q66 else 'Tier 2' if meds.get(x,0)>q33 else 'Tier 3')
            with c1: render_chart_box("分层金字塔", px.pie(df_ctx, names='Tier'), "占比。", "各层级占比。", "ti1")
            with c2: render_chart_box("层级薪酬带宽", px.box(df_ctx, x='Tier', y='Final_Comp'), "差距。", "层级分布。", "ti2")
            with c3: render_chart_box("Tier 1 列表", px.bar(df_ctx[df_ctx['Tier']=='Tier 1'].groupby('Company')['Final_Comp'].median().reset_index(), x='Company', y='Final_Comp'), "头部。", "第一梯队。", "ti3")
            with c4: render_chart_box("层级技能偏好", px.histogram(df_ctx, x='Tier', color='Role_Group'), "结构。", "人才结构。", "ti4")
            with c5: render_chart_box("层级流动性", px.scatter(df_ctx.groupby(['Tier','Role']).size().reset_index(name='c'), x='Tier', y='Role', size='c'), "分布。", "岗位气泡。", "ti5")
            with c6: render_chart_box("层级股票比例", px.box(df_ctx, x='Tier', y='Equity_Ratio'), "激励。", "期权占比。", "ti6")

        elif curr_dim == 'dim_trends':
            trend = df_ctx.dropna(subset=['Date_Clean']).sort_values('Date_Clean')
            with c1: render_chart_box("Offer 时间轴", px.scatter(trend, x='Date_Clean', y='Final_Comp', color='Company'), "密集期。", "时间分布。", "tr1")
            trend['MA'] = trend['Final_Comp'].rolling(10).mean()
            with c2: render_chart_box("趋势移动平均", px.line(trend, x='Date_Clean', y='MA'), "走势。", "MA10线。", "tr2")
            with c3: render_chart_box("月度中位薪酬", px.bar(trend.groupby(trend['Date_Clean'].dt.to_period('M').astype(str))['Final_Comp'].median().reset_index(), x='Date_Clean', y='Final_Comp'), "波动。", "月度统计。", "tr3")
            with c4: render_chart_box("招聘总量累积", px.line(trend, x='Date_Clean', y=range(1, len(trend)+1)), "增速。", "累积数量。", "tr4")
            with c5: render_chart_box("公司活跃分布", px.scatter(trend, x='Date_Clean', y='Company'), "节奏。", "招聘时间点。", "tr5")
            with c6: render_chart_box("资历要求变化", px.scatter(trend, x='Date_Clean', y='YOE_Clean', trendline='lowess'), "变化。", "年限趋势。", "tr6")

        elif curr_dim == 'dim_skills':
            if df_skills.empty: st.warning("No Data")
            else:
                top = df_skills['Skills_List'].value_counts().head(20).reset_index()
                with c1: render_chart_box("Top 20 技能", px.bar(top, x='count', y='Skills_List', orientation='h'), "热门。", "频次排行。", "sk1")
                with c2: render_chart_box("技能 Treemap", px.treemap(top, path=['Skills_List'], values='count'), "权重。", "矩形树图。", "sk2")
                with c3: render_chart_box("技能-职能", px.scatter(df_skills.groupby(['Role_Group','Skills_List']).size().reset_index(name='c').nlargest(40,'c'), x='Role_Group', y='Skills_List', size='c'), "绑定。", "气泡图。", "sk3")
                pay = df_skills.groupby('Skills_List')['Final_Comp'].median().nlargest(15).reset_index()
                with c4: render_chart_box("高薪技能", px.bar(pay, x='Skills_List', y='Final_Comp'), "含金量。", "中位薪酬。", "sk4")
                with c5: render_chart_box("资深技能", px.bar(df_skills.groupby('Skills_List')['YOE_Clean'].mean().nlargest(15).reset_index(), x='Skills_List', y='YOE_Clean'), "沉淀。", "平均年限。", "sk5")
                with c6: render_chart_box("稀缺技能", px.bar(df_skills['Skills_List'].value_counts().tail(20).reset_index(), x='count', y='Skills_List'), "蓝海。", "长尾技能。", "sk6")
                
        elif curr_dim == 'dim_clusters':
             if df_skills.empty: st.warning("No Data")
             else:
                top_tags = df_skills['Skills_List'].value_counts().head(20).index
                df_s_filt = df_skills[df_skills['Skills_List'].isin(top_tags)]
                with c1: render_chart_box("标签共现", px.scatter(df_s_filt, x='Company', y='Skills_List'), "指纹。", "使用情况。", "cl1")
                with c2: render_chart_box("组合价值", px.box(df_s_filt, x='Skills_List', y='Final_Comp'), "定价。", "薪酬分布。", "cl2")
                with c3: render_chart_box("流向映射", px.parallel_categories(df_s_filt, dimensions=['Role_Group', 'Skills_List']), "路径。", "桑基图。", "cl3")
                with c4: render_chart_box("全景 Treemap", px.treemap(df_skills['Skills_List'].value_counts().reset_index().head(30), path=['Skills_List'], values='count'), "生态。", "全景图。", "cl4")
                with c5: render_chart_box("技术栈偏好", px.histogram(df_s_filt, x='Company', color='Skills_List'), "构成。", "堆叠图。", "cl5")
                with c6: render_chart_box("稀缺扫描", px.bar(df_skills['Skills_List'].value_counts().tail(20).reset_index(), x='count', y='Skills_List'), "长尾。", "低频词。", "cl6")
        
        else:
            with c1: render_chart_box("通用分布", px.histogram(df_ctx, x='Final_Comp', color='Company'), "Dist.", "分布。", "g1")
            with c2: render_chart_box("通用箱线", px.box(df_ctx, x='Company', y='Final_Comp'), "Box.", "带宽。", "g2")
            with c3: render_chart_box("通用散点", px.scatter(df_ctx, x='YOE_Clean', y='Final_Comp'), "Scatter.", "散点。", "g3")
            with c4: render_chart_box("通用排行", px.bar(df_ctx.groupby('Company')['Final_Comp'].mean().reset_index(), x='Company', y='Final_Comp'), "Bar.", "排行。", "g4")
            with c5: render_chart_box("通用趋势", px.line(df_ctx.sort_values('Date_Clean'), x='Date_Clean', y='Final_Comp'), "Line.", "趋势。", "g5")
            with c6: render_chart_box("通用热力", px.density_heatmap(df_ctx, x='YOE_Clean', y='Final_Comp'), "Heat.", "热力。", "g6")

# --- C. List View ---
elif st.session_state.view == 'List':
    render_floating_buttons()
    st.markdown("## 📋 深度数据列表")
    event = st.dataframe(
        df_ctx[['Company', 'Role', 'Final_Comp', 'Base_Clean', 'Stock_Clean', 'YOE_Clean', 'Level', 'Location', 'Date_Clean', 'URL', 'UID']],
        column_config={
            "Final_Comp": st.column_config.NumberColumn("Total($)", format="$%d"),
            "URL": st.column_config.LinkColumn("Source", display_text="🔗 点击校对")
        },
        use_container_width=True, on_select="rerun", selection_mode="single-row", height=700
    )
    if len(event.selection.rows) > 0: change_view('Profile', uid=df_ctx.iloc[event.selection.rows[0]]['UID'])

# --- D. Profile View ---
elif st.session_state.view == 'Profile':
    render_floating_buttons()
    uid = st.session_state.sel_uid
    row = df_master[df_master['UID'] == uid].iloc[0]
    st.markdown(f"""
    <div style="background:white; border-radius:16px; border:1px solid #E2E8F0; padding:32px; margin-bottom:24px; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
        <h1 style="margin:0; font-size:32px; font-weight:800; color:#0F172A;">{row['Role']}</h1>
        <div style="color:#64748B; font-size:14px; margin-top:8px; font-weight:500;">🏢 {row['Company']}  |  📍 {row['Location']}</div>
        <h2 style="color:#2563EB; margin-top:16px; font-size:28px; font-weight:700;">${row['Final_Comp']:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.write("**Comp Details**", row[['Base_Clean','Stock_Clean','Bonus_Clean','Equity_Ratio']].to_dict())
    with c2: st.write("**Context**", row[['YOE_Clean','Level','Date_Clean','Source']].to_dict())
    
    if pd.notna(row.get('URL')) and str(row['URL']).startswith('http'):
        st.markdown(f"""
        <a href="{row['URL']}" target="_blank" style="display:block; margin-top:24px; background:#2563EB; color:white; text-align:center; padding:16px; border-radius:12px; text-decoration:none; font-weight:700; transition:all 0.2s; box-shadow: 0 4px 6px rgba(37,99,235,0.2);">
            🔗 前往原始网页校对数据 (Verify on Source)
        </a>
        """, unsafe_allow_html=True)