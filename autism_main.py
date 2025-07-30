"""孤独症儿童AI模拟实验平台主程序 - 支持ABC量表和DSM-5双标准"""
import streamlit as st

# 导入通用模块
from common.config import EXCEL_AVAILABLE
from common.ui_components import display_sidebar_stats

# 导入孤独症专用模块
from autism.ui_pages import (
    page_quick_assessment,
    page_batch_research,
    page_custom_assessment,
    page_data_analysis,
    page_records_management
)

# 页面配置
st.set_page_config(page_title="孤独症儿童AI模拟实验平台 - 双标准版", layout="wide")

# 初始化session state
if 'experiment_records' not in st.session_state:
    st.session_state.experiment_records = []
if 'current_batch_results' not in st.session_state:
    st.session_state.current_batch_results = []
if 'experiment_progress' not in st.session_state:
    st.session_state.experiment_progress = {'current': 0, 'total': 0}

# 主页面
st.title("🏥 孤独症儿童AI模拟实验平台 - 双标准版")
st.markdown("**基于ABC孤独症行为量表和DSM-5诊断标准的综合评估系统**")

# 侧边栏导航
st.sidebar.title("🔍 导航")
page = st.sidebar.selectbox("选择功能页面", [
    "快速临床评估", "批量临床研究", "个性化评估设计", 
    "临床数据分析", "评估记录管理", "📊 临床报告中心"
])

# 页面路由
if page == "快速临床评估":
    page_quick_assessment()
elif page == "批量临床研究":
    page_batch_research()
elif page == "个性化评估设计":
    page_custom_assessment()
elif page == "临床数据分析":
    page_data_analysis()
elif page == "评估记录管理":
    page_records_management()
elif page == "📊 临床报告中心":
    # 导入报告页面（这个页面会比较大，单独导入）
    from autism.report_center import page_report_center
    page_report_center()

# 侧边栏额外信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 评估统计")
if st.session_state.experiment_records:
    st.sidebar.metric("评估总数", len(st.session_state.experiment_records))
    recent_record = st.session_state.experiment_records[-1]
    st.sidebar.write(f"最近评估: {recent_record['timestamp'].strftime('%m-%d %H:%M')}")
    
    # 分别统计两种标准的数据
    import pandas as pd
    import numpy as np
    
    abc_records = [r for r in st.session_state.experiment_records if r.get('assessment_standard', 'ABC') == 'ABC']
    dsm5_records = [r for r in st.session_state.experiment_records if r.get('assessment_standard', 'ABC') == 'DSM5']
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("ABC评估", len(abc_records))
    with col2:
        st.metric("DSM-5评估", len(dsm5_records))
    
    # ABC评估统计
    if abc_records:
        total_scores = [r['abc_total_score'] for r in abc_records]
        avg_score = np.mean(total_scores)
        st.sidebar.write(f"**ABC平均总分**: {avg_score:.1f}")
    
    # DSM-5评估统计
    if dsm5_records:
        core_severities = []
        for r in dsm5_records:
            core_severity = (r['evaluation_scores'].get('社交互动质量', 0) + 
                           r['evaluation_scores'].get('沟通交流能力', 0) + 
                           r['evaluation_scores'].get('刻板重复行为', 0)) / 3
            core_severities.append(core_severity)
        if core_severities:
            avg_core = np.mean(core_severities)
            st.sidebar.write(f"**DSM-5平均核心症状**: {avg_core:.2f}/5")
    
    # 综合判断
    if abc_records and len(abc_records) > len(dsm5_records):
        if avg_score >= 67:
            st.sidebar.error("ABC评估显示孤独症阳性为主")
        elif avg_score >= 53:
            st.sidebar.warning("ABC评估显示轻度孤独症为主")
        else:
            st.sidebar.info("ABC评估处于边缘或正常范围")
    elif dsm5_records:
        if avg_core >= 4.0:
            st.sidebar.error("DSM-5评估显示重度症状为主")
        elif avg_core >= 3.0:
            st.sidebar.warning("DSM-5评估显示中度症状为主")
        else:
            st.sidebar.info("DSM-5评估显示轻度症状为主")
        
else:
    st.sidebar.write("暂无评估数据")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ 评估标准说明")

# 使用tabs展示两种评估标准
tab1, tab2 = st.sidebar.tabs(["ABC量表", "DSM-5标准"])

with tab1:
    st.markdown("""
    **ABC孤独症行为量表**
    
    **量表构成**:
    - 57个行为项目
    - 5个评估领域
    
    **评估领域**:
    - 感觉领域（9项）
    - 交往领域（12项）
    - 躯体运动领域（12项）
    - 语言领域（13项）
    - 社交与自理领域（11项）
    
    **诊断标准**:
    - ≥67分：孤独症
    - 53-66分：轻度孤独症
    - 40-52分：边缘状态
    - <40分：非孤独症
    """)

with tab2:
    st.markdown("""
    **DSM-5诊断标准**
    
    **核心症状** (A+B):
    - A. 社交沟通缺陷
    - B. 刻板重复行为
    
    **严重程度分级**:
    - 需要支持（轻度）
    - 需要大量支持（中度）
    - 需要非常大量支持（重度）
    
    **功能评估**:
    - 社交互动质量
    - 沟通交流能力
    - 感官处理能力
    - 情绪行为调节
    - 认知适应功能
    
    **评分说明**: 1-5分制
    （1=正常，5=严重缺陷）
    """)

if not EXCEL_AVAILABLE:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 功能提示")
    st.sidebar.warning("Excel功能不可用")
    st.sidebar.markdown("要启用专业Excel报告功能，请运行：")
    st.sidebar.code("pip install openpyxl")
    st.sidebar.markdown("目前可使用CSV和JSON格式导出数据。")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ API限制说明")
st.sidebar.markdown("""
**当前API限制**: 每分钟3次请求

**对评估影响**:
- 快速评估: 立即完成
- 批量研究: 每个评估间隔25秒

**建议**:
- 批量研究选择适当规模
- 可分批次进行大样本研究
- 保持网络连接稳定
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏥 临床应用建议")
st.sidebar.markdown("""
**评估选择**:
- ABC量表：适合行为筛查和量化评估
- DSM-5标准：适合诊断分类和支持需求评估
- 建议：结合使用获得综合评估

**筛查应用**:
- 初步筛查高危儿童
- 识别核心症状
- 转诊专业评估

**干预规划**:
- ABC：基于领域得分制定方案
- DSM-5：基于支持需求分级
- 综合：个体化干预计划

**注意事项**:
- 本工具仅供辅助参考
- 不能替代专业诊断
- 建议结合临床观察
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 数据管理")
if st.sidebar.button("🗑️ 清空所有评估数据"):
    if st.sidebar.checkbox("确认清空（此操作不可恢复）"):
        st.session_state.experiment_records = []
        st.sidebar.success("✅ 评估数据已清空")
        st.rerun()

# 页脚
st.markdown("---")
st.markdown("""
### 📋 平台特点

**🏥 双重标准**: 整合ABC孤独症行为量表和DSM-5诊断标准  
**🔬 科学评估**: 行为量化评分与症状严重程度评估相结合  
**📊 专业报告**: 生成符合临床要求的综合评估报告  
**🎯 个体化**: 支持基于两种标准的个性化评估设计

**💡 使用提示**: 
- 建议先进行'快速临床评估'熟悉平台功能
- 使用'批量临床研究'获取统计学有效的数据
- 在'📊 临床报告中心'下载完整的专业报告
- 可以选择单一标准或综合使用两种标准进行评估

**⚠️ 重要声明**: 本平台仅供学术研究和临床辅助使用，不能替代专业医师的临床诊断。
""")

st.markdown("*基于ABC量表 & DSM-5标准 | 综合评估系统 | 双标准版 v2.0*")