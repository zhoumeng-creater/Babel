"""孤独症评估数据导入页面"""
import streamlit as st
import pandas as pd
from typing import Optional
import datetime

from common.importer import get_importer, ImportStatus
from common.data_storage_manager import DataStorageManager


def page_data_import():
    """数据导入页面"""
    st.header("📥 数据导入")
    st.markdown("导入历史评估数据，支持CSV、JSON、Excel和ZIP格式")
    
    # 初始化数据管理器
    storage_manager = DataStorageManager(assessment_type='autism')
    
    # 显示当前数据统计
    col1, col2, col3 = st.columns(3)
    summary = storage_manager.get_import_summary()
    
    with col1:
        st.metric("总记录数", summary['total_records'])
    with col2:
        st.metric("导入记录", summary['imported_records'])
    with col3:
        st.metric("本地记录", summary['native_records'])
    
    if summary['last_import']:
        st.info(f"最后导入时间: {summary['last_import'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.divider()
    
    # 文件上传区域
    st.subheader("📤 选择要导入的文件")
    
    uploaded_file = st.file_uploader(
        "拖拽文件到此处或点击浏览",
        type=['csv', 'json', 'xlsx', 'xls', 'zip'],
        help="支持CSV、JSON、Excel和ZIP压缩包格式"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        file_info = {
            'filename': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**文件信息:**")
            st.write(f"- 文件名: {file_info['filename']}")
            st.write(f"- 大小: {_format_file_size(file_info['size'])}")
            st.write(f"- 类型: {file_info['type']}")
        
        with col2:
            # 导入选项
            st.write("**导入选项:**")
            merge_strategy = st.selectbox(
                "数据合并策略",
                options=['append', 'skip_duplicates', 'replace'],
                format_func=lambda x: {
                    'append': '追加所有数据',
                    'skip_duplicates': '跳过重复记录',
                    'replace': '替换现有数据'
                }[x],
                help="选择如何处理导入的数据"
            )
            
            if merge_strategy == 'replace':
                st.warning("⚠️ 替换模式将清空所有现有数据！")
        
        # 导入按钮
        if st.button("🚀 开始导入", type="primary"):
            process_import(uploaded_file, merge_strategy, storage_manager)
    
    # 导入帮助
    with st.expander("❓ 导入帮助"):
        st.markdown("""
        ### 支持的文件格式
        
        1. **CSV文件** (.csv)
           - 支持UTF-8、GBK等常见编码
           - 自动识别分隔符
           - 可包含孤独症评估的各种数据
        
        2. **JSON文件** (.json)
           - 支持单条或多条记录
           - 保留完整的数据结构
           - 适合程序间数据交换
        
        3. **Excel文件** (.xlsx, .xls)
           - 支持多工作表
           - 自动识别数据类型
           - 适合批量数据管理
        
        4. **ZIP压缩包** (.zip)
           - 可包含多个文件
           - 支持混合格式
           - 适合完整项目导入
        
        ### 数据格式要求
        
        - 必需字段：`评估时间`/`timestamp`、`评估情境`/`scene`
        - 支持统一评估、ABC评估、DSM-5评估等多种格式
        - 自动识别并转换不同版本的数据
        
        ### 合并策略说明
        
        - **追加所有数据**：将导入的数据全部添加到现有数据后面
        - **跳过重复记录**：自动检测并跳过相似的记录
        - **替换现有数据**：清空现有数据，只保留导入的数据
        """)


def process_import(uploaded_file, merge_strategy: str, storage_manager: DataStorageManager):
    """处理文件导入"""
    try:
        # 获取文件扩展名
        file_ext = uploaded_file.name.split('.')[-1].lower()
        
        # 获取对应的导入器
        importer_class = get_importer(file_ext)
        importer = importer_class(assessment_type='autism')
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 读取文件内容
        status_text.text("正在读取文件...")
        progress_bar.progress(20)
        
        file_content = uploaded_file.read()
        
        # 导入数据
        status_text.text("正在解析数据...")
        progress_bar.progress(40)
        
        result = importer.import_data(file_content)
        
        # 检查导入结果
        if result.status == ImportStatus.FAILED:
            progress_bar.progress(100)
            st.error("❌ 导入失败")
            
            # 显示错误信息
            if result.errors:
                st.write("**错误详情:**")
                for error in result.errors[:10]:  # 最多显示10个错误
                    st.write(f"- 行{error.get('row', 'N/A')}: {error['message']}")
                if len(result.errors) > 10:
                    st.write(f"...还有{len(result.errors) - 10}个错误")
            return
        
        # 合并数据
        status_text.text("正在合并数据...")
        progress_bar.progress(60)
        
        merged_count, conflicts = storage_manager.merge_imported_data(
            result.records, 
            merge_strategy
        )
        
        # 完成
        progress_bar.progress(100)
        status_text.empty()
        
        # 显示结果
        if result.status == ImportStatus.SUCCESS:
            st.success(f"✅ 成功导入 {merged_count} 条记录")
        elif result.status == ImportStatus.PARTIAL:
            st.warning(f"⚠️ 部分导入成功: {merged_count}/{result.total_count} 条记录")
        
        # 显示详细信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("解析记录", result.total_count)
        with col2:
            st.metric("成功导入", merged_count)
        with col3:
            st.metric("跳过/失败", result.failed_count + result.skipped_count)
        
        # 显示冲突信息
        if conflicts:
            with st.expander(f"⚠️ 发现 {len(conflicts)} 个冲突"):
                for conflict in conflicts[:20]:
                    st.write(f"- {conflict}")
                if len(conflicts) > 20:
                    st.write(f"...还有{len(conflicts) - 20}个冲突")
        
        # 显示警告信息
        if result.warnings:
            with st.expander(f"⚠️ {len(result.warnings)} 个警告"):
                for warning in result.warnings[:20]:
                    st.write(f"- {warning}")
        
        # 显示元数据
        if result.metadata:
            with st.expander("📊 导入元数据"):
                if 'files_processed' in result.metadata:
                    st.write(f"**处理的文件:** {', '.join(result.metadata['files_processed'])}")
                if 'files_skipped' in result.metadata:
                    st.write(f"**跳过的文件:** {', '.join(result.metadata['files_skipped'])}")
        
        # 刷新页面以显示新数据
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 导入过程中发生错误: {str(e)}")
        st.exception(e)


def _format_file_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"