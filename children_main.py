"""正常儿童成长发育AI观察平台主程序"""
import streamlit as st

# 导入通用模块
from common.config import EXCEL_AVAILABLE
from common.ui_components import display_sidebar_stats

# 导入儿童发展专用模块
from children.ui_pages import (
    page_quick_observation,
    page_batch_research,
    page_custom_observation,
    page_data_analysis,
    page_records_management
)

# 页面配置
st.set_page_config(page_title="正常儿童成长发育AI观察平台 - 专业版", layout="wide")

# 初始化session state
if 'observation_records' not in st.session_state:
    st.session_state.observation_records = []
if 'current_batch_results' not in st.session_state:
    st.session_state.current_batch_results = []
if 'observation_progress' not in st.session_state:
    st.session_state.observation_progress = {'current': 0, 'total': 0}

# 主页面
st.title("🌟 正常儿童成长发育AI观察平台 - 专业版")
st.markdown("**基于儿童发展心理学理论和多元智能评估框架**")

# 侧边栏导航
st.sidebar.title("🧭 导航")
page = st.sidebar.selectbox("选择功能页面", [
    "快速发育观察", "批量发展研究", "个性化观察设计", 
    "发展数据分析", "观察记录管理", "临床数据导入",
    "📊 发展报告中心"
])

# 页面路由
if page == "快速发育观察":
    page_quick_observation()
elif page == "批量发展研究":
    page_batch_research()
elif page == "个性化观察设计":
    page_custom_observation()
elif page == "发展数据分析":
    page_data_analysis()
elif page == "观察记录管理":
    page_records_management()
elif page == "临床数据导入":
    from autism.pages.data_import_page import page_data_import
elif page == "📊 发展报告中心":
    # 导入报告页面（这个页面会比较大，单独导入）
    from children.report_center import page_report_center
    page_report_center()

# 侧边栏额外信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 观察统计")
if st.session_state.observation_records:
    st.sidebar.metric("观察总数", len(st.session_state.observation_records))
    recent_record = st.session_state.observation_records[-1]
    st.sidebar.write(f"最近观察: {recent_record['timestamp'].strftime('%m-%d %H:%M')}")
    
    # 显示年龄段分布
    import pandas as pd
    import numpy as np
    age_groups = [r.get('template', '自定义') for r in st.session_state.observation_records]
    age_counts = pd.Series(age_groups).value_counts()
    st.sidebar.write("**年龄段分布:**")
    for age_group, count in age_counts.items():
        short_name = age_group.split('期')[0] if '期' in age_group else age_group
        st.sidebar.write(f"- {short_name}: {count}")
    
    # 发展水平统计
    all_development_scores = []
    for r in st.session_state.observation_records:
        development_score = sum(r['evaluation_scores'].values()) / len(r['evaluation_scores'])
        all_development_scores.append(development_score)
    
    avg_development = np.mean(all_development_scores)
    st.sidebar.metric("平均发展指数", f"{avg_development:.2f}/5")
    
    if avg_development >= 4.5:
        st.sidebar.success("整体发展水平优秀")
    elif avg_development >= 4.0:
        st.sidebar.info("整体发展水平良好")
    elif avg_development >= 3.0:
        st.sidebar.warning("整体发展水平一般")
    else:
        st.sidebar.error("整体发展需要关注")
        
else:
    st.sidebar.write("暂无观察数据")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ 理论基础说明")
st.sidebar.markdown("""
**理论基础**: 儿童发展心理学

**核心发展领域**:
- 语言沟通发展
- 社交互动能力
- 认知学习能力

**其他发展领域**:
- 情绪调节发展
- 运动技能发展
- 独立自理能力

**参考理论**:
- 皮亚杰认知发展理论
- 维果茨基社会文化理论  
- 加德纳多元智能理论
- 埃里克森心理社会发展理论

**发展水平分级**:
1. 需要支持（1-2分）
2. 需要关注（2-3分）
3. 一般发展（3-4分）
4. 良好发展（4-5分）
5. 优秀发展（5分）
""")

if not EXCEL_AVAILABLE:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 功能提示")
    st.sidebar.warning("Excel功能不可用")
    st.sidebar.markdown("要启用专业Excel报告功能，请运行：")
    st.sidebar.code("pip install openpyxl")
    st.sidebar.markdown("目前可使用CSV和JSON格式导出发展数据。")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ API限制说明")
st.sidebar.markdown("""
**当前API限制**: 每分钟3次请求

**对观察影响**:
- 快速发育观察: 立即完成
- 批量发展研究: 每个观察间隔25秒

**建议**:
- 批量研究选择适当规模
- 可分批次进行大样本研究
- 保持网络连接稳定
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌟 教育应用建议")
st.sidebar.markdown("""
**家庭教育**:
- 了解儿童发展特点
- 制定个性化教育方案
- 发现儿童优势和潜能

**幼儿园应用**:
- 观察儿童发展状况
- 设计适龄教育活动
- 与家长沟通发展情况

**研究用途**:
- 儿童发展规律研究
- 教育干预效果评估
- 发展里程碑验证

**注意事项**:
- 本工具仅供发展参考
- 不能替代专业发展评估
- 建议结合多种观察方法
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 数据管理")
if st.sidebar.button("🗑️ 清空所有观察数据"):
    if st.sidebar.checkbox("确认清空（此操作不可恢复）"):
        st.session_state.observation_records = []
        st.sidebar.success("✅ 观察数据已清空")
        st.rerun()

# 页脚
st.markdown("---")
st.markdown("""
### 🌟 平台特点

**🎓 科学理论**: 严格遵循儿童发展心理学理论，参考国际发展里程碑  
**🔍 专业观察**: 基于多元智能理论的全面发展评估框架  
**📊 数据驱动**: 生成符合教育研究要求的专业发展报告  
**👨‍👩‍👧‍👦 个性化**: 支持个性化配置和定制化观察设计

**💡 使用提示**: 
- 建议先进行'快速发育观察'熟悉平台功能
- 使用'批量发展研究'获取统计学有效的数据
- 在'📊 发展报告中心'下载完整的专业报告
- 所有观察结果仅供教育参考，建议结合多种评估方法

**⚠️ 重要声明**: 本平台仅供教育研究和儿童发展支持使用，不能替代专业的儿童发展评估。
""")

st.markdown("*基于儿童发展心理学理论 | 参考多元智能和发展里程碑 | 专业版 v1.0*")