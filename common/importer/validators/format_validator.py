"""文件格式验证器"""
import os
import mimetypes
import zipfile
import io
from typing import Dict, Any, Optional
from . import ValidationResult


class FormatValidator:
    """文件格式验证器"""
    
    def __init__(self):
        # 文件大小限制
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_zip_size = 100 * 1024 * 1024  # 100MB
        
        # 支持的文件类型
        self.allowed_extensions = {
            '.csv': ['text/csv', 'application/csv', 'text/plain'],
            '.json': ['application/json', 'text/json', 'text/plain'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.xls': ['application/vnd.ms-excel'],
            '.zip': ['application/zip', 'application/x-zip-compressed'],
            '.txt': ['text/plain']
        }
        
        # 危险文件扩展名
        self.dangerous_extensions = [
            '.exe', '.dll', '.bat', '.cmd', '.sh', '.ps1',
            '.vbs', '.js', '.jar', '.app', '.deb', '.rpm'
        ]
    
    def validate(self, file_info: Dict[str, Any]) -> ValidationResult:
        """
        验证文件格式
        
        Args:
            file_info: 包含文件信息的字典
                - filename: 文件名
                - size: 文件大小（字节）
                - content: 文件内容（可选）
                - mimetype: MIME类型（可选）
        
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()
        
        # 验证文件名
        if 'filename' not in file_info:
            result.add_error("缺少文件名")
            return result
        
        filename = file_info['filename']
        
        # 验证文件扩展名
        self._validate_extension(filename, result)
        
        # 验证文件大小
        if 'size' in file_info:
            self._validate_size(file_info['size'], filename, result)
        
        # 验证MIME类型
        if 'mimetype' in file_info:
            self._validate_mimetype(filename, file_info['mimetype'], result)
        
        # 验证文件内容（如果提供）
        if 'content' in file_info and file_info['content']:
            self._validate_content(filename, file_info['content'], result)
        
        return result
    
    def _validate_extension(self, filename: str, result: ValidationResult):
        """验证文件扩展名"""
        # 获取文件扩展名
        ext = self._get_extension(filename)
        
        if not ext:
            result.add_error("文件缺少扩展名")
            return
        
        # 检查危险扩展名
        if ext.lower() in self.dangerous_extensions:
            result.add_error(f"不允许的文件类型: {ext}")
            return
        
        # 检查支持的扩展名
        if ext.lower() not in self.allowed_extensions:
            result.add_error(
                f"不支持的文件类型: {ext}. "
                f"支持的类型: {', '.join(self.allowed_extensions.keys())}"
            )
    
    def _validate_size(self, size: int, filename: str, result: ValidationResult):
        """验证文件大小"""
        ext = self._get_extension(filename).lower()
        
        # ZIP文件有更大的限制
        if ext == '.zip':
            max_size = self.max_zip_size
        else:
            max_size = self.max_file_size
        
        if size > max_size:
            result.add_error(
                f"文件大小超过限制: {self._format_size(size)} "
                f"(最大: {self._format_size(max_size)})"
            )
        elif size == 0:
            result.add_error("文件为空")
        elif size < 10:  # 小于10字节
            result.add_warning("文件大小异常小，可能为空文件")
    
    def _validate_mimetype(self, filename: str, mimetype: str, result: ValidationResult):
        """验证MIME类型"""
        ext = self._get_extension(filename).lower()
        
        if ext in self.allowed_extensions:
            allowed_mimes = self.allowed_extensions[ext]
            
            # 标准化MIME类型
            mimetype = mimetype.lower().split(';')[0].strip()
            
            if mimetype not in allowed_mimes:
                # 某些系统可能返回不同的MIME类型，给出警告而非错误
                result.add_warning(
                    f"MIME类型不匹配: {mimetype} "
                    f"(预期: {', '.join(allowed_mimes)})"
                )
    
    def _validate_content(self, filename: str, content: bytes, result: ValidationResult):
        """验证文件内容"""
        ext = self._get_extension(filename).lower()
        
        # 检查文件签名
        if not self._check_file_signature(content, ext, result):
            return
        
        # 特定类型的内容验证
        if ext == '.zip':
            self._validate_zip_content(content, result)
        elif ext == '.json':
            self._validate_json_content(content, result)
        elif ext == '.csv':
            self._validate_csv_content(content, result)
    
    def _check_file_signature(self, content: bytes, ext: str, result: ValidationResult) -> bool:
        """检查文件签名"""
        if len(content) < 4:
            result.add_error("文件内容太小，无法验证")
            return False
        
        # 文件签名映射
        signatures = {
            '.zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
            '.xlsx': [b'PK\x03\x04'],  # XLSX也是ZIP格式
            '.xls': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],  # OLE2
            '.json': [b'{', b'['],  # JSON可能以{或[开头
        }
        
        if ext in signatures:
            valid = any(content.startswith(sig) for sig in signatures[ext])
            if not valid and ext not in ['.json', '.csv', '.txt']:
                result.add_error(f"文件内容与扩展名不匹配: {ext}")
                return False
        
        return True
    
    def _validate_zip_content(self, content: bytes, result: ValidationResult):
        """验证ZIP文件内容"""
        try:
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_file:
                # 检查ZIP文件完整性
                bad_file = zip_file.testzip()
                if bad_file:
                    result.add_error(f"ZIP文件损坏: {bad_file}")
                    return
                
                # 检查压缩包内的文件
                file_list = zip_file.namelist()
                
                if not file_list:
                    result.add_error("ZIP文件为空")
                    return
                
                # 检查是否有危险文件
                for filename in file_list:
                    ext = self._get_extension(filename).lower()
                    if ext in self.dangerous_extensions:
                        result.add_error(f"ZIP包含危险文件: {filename}")
                
                # 统计文件类型
                file_types = {}
                for filename in file_list:
                    if not filename.endswith('/'):  # 忽略目录
                        ext = self._get_extension(filename).lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                
                # 添加信息
                result.add_info(
                    f"ZIP包含 {len(file_list)} 个文件: " +
                    ", ".join(f"{count}个{ext}文件" for ext, count in file_types.items())
                )
                
        except zipfile.BadZipFile:
            result.add_error("无效的ZIP文件格式")
        except Exception as e:
            result.add_error(f"ZIP文件验证失败: {str(e)}")
    
    def _validate_json_content(self, content: bytes, result: ValidationResult):
        """验证JSON文件内容"""
        try:
            import json
            
            # 尝试解析JSON
            text = content.decode('utf-8')
            data = json.loads(text)
            
            # 检查数据结构
            if isinstance(data, dict):
                result.add_info(f"JSON对象包含 {len(data)} 个键")
            elif isinstance(data, list):
                result.add_info(f"JSON数组包含 {len(data)} 个元素")
            else:
                result.add_warning("JSON数据既不是对象也不是数组")
            
        except UnicodeDecodeError:
            result.add_error("JSON文件编码错误（需要UTF-8）")
        except json.JSONDecodeError as e:
            result.add_error(f"JSON格式错误: {str(e)}")
        except Exception as e:
            result.add_error(f"JSON验证失败: {str(e)}")
    
    def _validate_csv_content(self, content: bytes, result: ValidationResult):
        """验证CSV文件内容"""
        # 检查BOM
        if content.startswith(b'\xef\xbb\xbf'):
            result.add_info("检测到UTF-8 BOM")
        
        # 尝试检测编码
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        detected_encoding = None
        
        for encoding in encodings:
            try:
                content.decode(encoding)
                detected_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if not detected_encoding:
            result.add_error("无法检测CSV文件编码")
        else:
            result.add_info(f"CSV文件编码: {detected_encoding}")
    
    def _get_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1]
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"