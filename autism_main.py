"""孤独症儿童AI模拟实验平台主程序 - 增强版（支持多量表和干预功能）"""
import streamlit as st

# 导入通用模块
from common.config import EXCEL_AVAILABLE
from common.ui_components import display_sidebar_stats

# 导入所有页面功能（包括新增功能）
from autism.pages import (
    # 基础功能
    page_quick_assessment,
    page_batch_research,
    page_custom_assessment,
    page_data_analysis,
    page_records_management,
    # 新增功能
    page_multi_scale_assessment,
    page_intervention_assessment,
    page_score_based_generation
)
from autism.pages.data_import_page import page_data_import

# 导入增强版页面（如果需要替换原有页面）
from autism.pages.quick_assessment_enhanced import page_quick_assessment_enhanced
from autism.pages.batch_research_enhanced import page_batch_research_enhanced

# 页面配置
st.set_page_config(
    page_title="孤独症儿童AI模拟实验平台 - 专业增强版", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'experiment_records' not in st.session_state:
    st.session_state.experiment_records = []
if 'current_batch_results' not in st.session_state:
    st.session_state.current_batch_results = []
if 'experiment_progress' not in st.session_state:
    st.session_state.experiment_progress = {'current': 0, 'total': 0}
if 'intervention_history' not in st.session_state:
    st.session_state.intervention_history = []

# 主页面标题和描述
st.title("🏥 孤独症儿童AI模拟实验平台 - 专业增强版")
st.markdown("**支持ABC、DSM-5、CARS、ASSQ多量表评估 | 干预效果模拟 | 智能对话生成**")

# 显示版本信息
col_v1, col_v2, col_v3, col_v4 = st.columns(4)
with col_v1:
    st.caption("✅ ABC量表")
with col_v2:
    st.caption("✅ DSM-5标准")
with col_v3:
    st.caption("✅ CARS量表")
with col_v4:
    st.caption("✅ ASSQ筛查")

# 侧边栏导航
st.sidebar.title("🔍 功能导航")

# 功能模式选择
mode = st.sidebar.radio(
    "选择功能模式",
    ["标准评估", "增强评估", "干预研究", "数据分析"],
    help="选择不同的功能模式以访问相应的工具"
)

# 根据模式显示不同的页面选项
if mode == "标准评估":
    page = st.sidebar.selectbox("选择评估功能", [
        "快速临床评估（标准版）",
        "批量临床研究（标准版）", 
        "个性化评估设计",
        "临床数据导入"
    ])
elif mode == "增强评估":
    page = st.sidebar.selectbox("选择增强功能", [
        "快速评估（多量表版）",
        "批量研究（多量表版）",
        "多量表综合评估",
        "基于分数生成对话"
    ])
elif mode == "干预研究":
    page = st.sidebar.selectbox("选择干预功能", [
        "干预效果评估",
        "干预策略对比",
        "个性化干预设计"
    ])
else:  # 数据分析
    page = st.sidebar.selectbox("选择分析功能", [
        "临床数据分析",
        "评估记录管理",
        "📊 专业报告中心"
    ])

# 页面路由
if page == "快速临床评估（标准版）":
    page_quick_assessment()
elif page == "批量临床研究（标准版）":
    page_batch_research()
elif page == "快速评估（多量表版）":
    page_quick_assessment_enhanced()
elif page == "批量研究（多量表版）":
    page_batch_research_enhanced()
elif page == "多量表综合评估":
    page_multi_scale_assessment()
elif page == "个性化评估设计":
    page_custom_assessment()
elif page == "临床数据导入":
    page_data_import()
elif page == "干预效果评估":
    page_intervention_assessment()
elif page == "干预策略对比":
    # 这是干预评估页面的另一个入口
    page_intervention_assessment()
elif page == "个性化干预设计":
    # 可以创建新页面或使用现有页面
    page_intervention_assessment()
elif page == "基于分数生成对话":
    page_score_based_generation()
elif page == "临床数据分析":
    page_data_analysis()
elif page == "评估记录管理":
    page_records_management()
elif page == "📊 专业报告中心":
    from autism.report_center import page_report_center
    page_report_center()

# 侧边栏统计信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 评估统计")

if st.session_state.experiment_records:
    st.sidebar.metric("总评估数", len(st.session_state.experiment_records))
    
    # 统计各量表使用情况
    scale_usage = {
        'ABC': 0,
        'DSM-5': 0,
        'CARS': 0,
        'ASSQ': 0
    }
    
    for record in st.session_state.experiment_records:
        if 'abc_evaluation' in record:
            scale_usage['ABC'] += 1
        if 'dsm5_evaluation' in record:
            scale_usage['DSM-5'] += 1
        if 'cars_evaluation' in record:
            scale_usage['CARS'] += 1
        if 'assq_evaluation' in record:
            scale_usage['ASSQ'] += 1
    
    # 显示量表使用统计
    st.sidebar.write("**量表使用情况：**")
    for scale, count in scale_usage.items():
        if count > 0:
            st.sidebar.write(f"• {scale}: {count}次")
    
    # 显示最近评估
    recent_record = st.session_state.experiment_records[-1]
    st.sidebar.write(f"**最近评估：**")
    st.sidebar.caption(f"{recent_record['timestamp'].strftime('%m-%d %H:%M')}")
    
    # 如果有干预历史，显示干预统计
    if st.session_state.intervention_history:
        st.sidebar.markdown("---")
        st.sidebar.write(f"**干预研究：** {len(st.session_state.intervention_history)}次")
else:
    st.sidebar.info("暂无评估数据")
    st.sidebar.caption("请开始您的第一次评估")

# 底部信息
st.sidebar.markdown("---")
st.sidebar.caption("💡 **提示**：")
st.sidebar.caption("• 标准评估：ABC+DSM-5双量表")
st.sidebar.caption("• 增强评估：支持4种量表组合")
st.sidebar.caption("• 干预研究：模拟干预效果")
st.sidebar.caption("• 智能生成：基于分数生成对话")

# 版本信息
st.sidebar.markdown("---")
st.sidebar.caption("版本：v2.0 增强版")
st.sidebar.caption("更新：支持多量表评估和干预功能")