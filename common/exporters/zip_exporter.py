"""ZIP包导出模块"""
import io
import zipfile


def create_zip_package(files_dict):
    """
    创建ZIP压缩包
    
    Args:
        files_dict: 字典，键为文件名，值为文件内容（字符串或字节）
    
    Returns:
        bytes: ZIP文件的字节数据
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files_dict.items():
            if isinstance(content, str):
                content = content.encode('utf-8')
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()