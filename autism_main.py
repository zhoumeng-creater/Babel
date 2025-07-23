"""孤独症儿童AI模拟实验平台主程序 - 基于ABC量表"""
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
st.set_page_config(page_title="孤独症儿童AI模拟实验平台 - ABC量表版", layout="wide")

# 初始化session state
if 'experiment_records' not in st.session_state:
    st.session_state.experiment_records = []
if 'current_batch_results' not in st.session_state:
    st.session_state.current_batch_results = []
if 'experiment_progress' not in st.session_state:
    st.session_state.experiment_progress = {'current': 0, 'total': 0}

# 主页面
st.title("🏥 孤独症儿童AI模拟实验平台 - ABC量表版")
st.markdown("**基于ABC孤独症行为量表（Autism Behavior Checklist）的专业评估系统**")

# 侧边栏导航
st.sidebar.title("🔍 导航")
page = st.sidebar.selectbox("选择功能页面", [
    "快速ABC评估", "批量ABC研究", "个性化评估设计", 
    "ABC数据分析", "评估记录管理", "📊 ABC报告中心"
])

# 页面路由
if page == "快速ABC评估":
    page_quick_assessment()
elif page == "批量ABC研究":
    page_batch_research()
elif page == "个性化评估设计":
    page_custom_assessment()
elif page == "ABC数据分析":
    page_data_analysis()
elif page == "评估记录管理":
    page_records_management()
elif page == "📊 ABC报告中心":
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
    
    # 显示ABC总分分布
    import pandas as pd
    import numpy as np
    total_scores = [r['abc_total_score'] for r in st.session_state.experiment_records]
    avg_score = np.mean(total_scores)
    st.sidebar.metric("平均ABC总分", f"{avg_score:.1f}")
    
    # 显示严重程度分布
    severities = [r['abc_severity'] for r in st.session_state.experiment_records]
    severity_counts = pd.Series(severities).value_counts()
    st.sidebar.write("**严重程度分布:**")
    for severity, count in severity_counts.items():
        st.sidebar.write(f"- {severity}: {count}")
    
    # 判断整体情况
    if avg_score >= 67:
        st.sidebar.error("整体评估显示孤独症阳性")
    elif avg_score >= 53:
        st.sidebar.warning("整体评估显示轻度孤独症")
    elif avg_score >= 40:
        st.sidebar.info("整体评估处于边缘状态")
    else:
        st.sidebar.success("整体评估未达孤独症标准")
        
else:
    st.sidebar.write("暂无评估数据")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ ABC量表说明")
st.sidebar.markdown("""
**评估工具**: ABC孤独症行为量表

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

**权重范围**: 1-4分/项
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
- 快速ABC评估: 立即完成
- 批量ABC研究: 每个评估间隔25秒

**建议**:
- 批量研究选择适当规模
- 可分批次进行大样本研究
- 保持网络连接稳定
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏥 临床应用建议")
st.sidebar.markdown("""
**筛查应用**:
- ABC总分初步筛查
- 识别高危儿童
- 转诊专业评估

**评估应用**:
- 各领域详细评估
- 行为特征分析
- 严重程度分级

**干预规划**:
- 基于领域得分制定方案
- 针对高频行为干预
- 定期评估监测进展

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

**🏥 专业标准**: 严格遵循ABC孤独症行为量表，57项行为评估  
**🔬 科学评估**: 基于行为观察的量化评分系统  
**📊 专业报告**: 生成符合临床要求的ABC评估报告  
**🎯 个体化**: 支持个性化配置和定制化评估设计

**💡 使用提示**: 
- 建议先进行'快速ABC评估'熟悉平台功能
- 使用'批量ABC研究'获取统计学有效的数据
- 在'📊 ABC报告中心'下载完整的专业报告
- 所有评估结果仅供临床参考，不能替代专业诊断

**⚠️ 重要声明**: 本平台仅供学术研究和临床辅助使用，不能替代专业医师的临床诊断。
""")

st.markdown("*基于ABC孤独症行为量表 | 57项行为评估 | ABC量表版 v1.0*")