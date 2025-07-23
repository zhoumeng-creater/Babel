"""孤独症儿童AI模拟实验平台主程序"""
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
st.set_page_config(page_title="孤独症儿童AI模拟实验平台 - 医学标准版", layout="wide")

# 初始化session state
if 'experiment_records' not in st.session_state:
    st.session_state.experiment_records = []
if 'current_batch_results' not in st.session_state:
    st.session_state.current_batch_results = []
if 'experiment_progress' not in st.session_state:
    st.session_state.experiment_progress = {'current': 0, 'total': 0}

# 主页面
st.title("🏥 孤独症儿童AI模拟实验平台 - 医学标准版")
st.markdown("**基于DSM-5诊断标准和权威评估量表（CARS、ABC、SCQ、M-CHAT等）**")

# 侧边栏导航
st.sidebar.title("🔍 导航")
page = st.sidebar.selectbox("选择功能页面", [
    "临床快速评估", "批量临床研究", "个性化评估设计", 
    "临床数据分析", "评估记录管理", "📊 临床报告中心"
])

# 页面路由
if page == "临床快速评估":
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
    
    # 显示严重程度分布
    import pandas as pd
    import numpy as np
    severities = [r.get('template', '自定义') for r in st.session_state.experiment_records]
    severity_counts = pd.Series(severities).value_counts()
    st.sidebar.write("**严重程度分布:**")
    for severity, count in severity_counts.items():
        short_name = severity.split('（')[0] if '（' in severity else severity
        st.sidebar.write(f"- {short_name}: {count}")
    
    # 核心症状统计
    all_core_scores = []
    for r in st.session_state.experiment_records:
        core_score = (r['evaluation_scores']['社交互动质量'] + 
                     r['evaluation_scores']['沟通交流能力'] + 
                     r['evaluation_scores']['刻板重复行为']) / 3
        all_core_scores.append(core_score)
    
    avg_core = np.mean(all_core_scores)
    st.sidebar.metric("平均核心症状严重度", f"{avg_core:.2f}/5")
    
    if avg_core >= 4.0:
        st.sidebar.error("整体评估显示重度症状")
    elif avg_core >= 3.0:
        st.sidebar.warning("整体评估显示中度症状")
    else:
        st.sidebar.success("整体评估显示轻度症状")
        
else:
    st.sidebar.write("暂无评估数据")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ 医学标准说明")
st.sidebar.markdown("""
**评估标准**: DSM-5孤独症谱系障碍诊断标准

**核心症状**:
- A. 社交沟通缺陷
- B. 刻板重复行为模式

**参考量表**:
- CARS: 儿童孤独症评定量表
- ABC: 孤独症行为量表  
- SCQ: 社交沟通问卷
- M-CHAT: 修订版孤独症筛查量表

**严重程度分级**:
1. 需要支持（轻度）
2. 需要大量支持（中度）
3. 需要非常大量支持（重度）
""")

if not EXCEL_AVAILABLE:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 功能提示")
    st.sidebar.warning("Excel功能不可用")
    st.sidebar.markdown("要启用专业Excel报告功能，请运行：")
    st.sidebar.code("pip install openpyxl")
    st.sidebar.markdown("目前可使用CSV和JSON格式导出临床数据。")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ API限制说明")
st.sidebar.markdown("""
**当前API限制**: 每分钟3次请求

**对评估影响**:
- 临床快速评估: 立即完成
- 批量临床研究: 每个评估间隔25秒

**建议**:
- 批量研究选择适当规模
- 可分批次进行大样本研究
- 保持网络连接稳定
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏥 临床应用建议")
st.sidebar.markdown("""
**筛查应用**:
- 快速识别可能的孤独症特征
- 辅助临床诊断决策

**干预规划**:
- 基于评估结果制定个体化干预
- 监测干预效果

**研究用途**:
- 症状严重度量化
- 干预前后对比
- 群体特征分析

**注意事项**:
- 本工具仅供辅助参考
- 不能替代专业临床诊断
- 建议结合其他评估工具
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

**🏥 医学标准**: 严格遵循DSM-5诊断标准，参考权威评估量表  
**🔬 科学评估**: 基于循证实践的评估指标和评分标准  
**📊 专业报告**: 生成符合临床要求的专业评估报告  
**🎯 个体化**: 支持个性化配置和定制化评估设计

**💡 使用提示**: 
- 建议先进行'临床快速评估'熟悉平台功能
- 使用'批量临床研究'获取统计学有效的数据
- 在'📊 临床报告中心'下载完整的专业报告
- 所有评估结果仅供临床参考，不能替代专业诊断

**⚠️ 重要声明**: 本平台仅供学术研究和临床辅助使用，不能替代专业医师的临床诊断。
""")

st.markdown("*基于DSM-5标准 | 参考CARS、ABC、SCQ、M-CHAT等权威量表 | 医学标准版 v1.0*")