"""JSON导入器实现"""
import json
import datetime
from typing import List, Dict, Any, Tuple, Union
from .base_importer import BaseImporter, ImportError


class JSONImporter(BaseImporter):
    """JSON文件导入器"""
    
    def parse_file(self, file_content: Union[bytes, str], **kwargs) -> List[Dict[str, Any]]:
        """
        解析JSON文件内容
        
        Args:
            file_content: 文件内容（字节或字符串）
            **kwargs: 额外参数
                
        Returns:
            解析后的记录列表
        """
        try:
            # 处理不同类型的输入
            if isinstance(file_content, bytes):
                content_str = file_content.decode('utf-8')
            else:
                content_str = file_content
            
            # 解析JSON
            data = json.loads(content_str)
            
            # 处理不同的JSON结构
            if isinstance(data, list):
                # 直接是记录列表
                records = data
            elif isinstance(data, dict):
                # 可能是包装的数据结构
                if 'records' in data:
                    records = data['records']
                elif 'data' in data:
                    records = data['data']
                elif 'experiments' in data:
                    records = data['experiments']
                elif 'observations' in data:
                    records = data['observations']
                else:
                    # 单个记录
                    records = [data]
            else:
                raise ImportError("不支持的JSON数据结构")
            
            # 转换日期字符串
            for record in records:
                self._convert_datetime_fields(record)
            
            return records
            
        except json.JSONDecodeError as e:
            raise ImportError(f"JSON解析错误: {str(e)}")
        except Exception as e:
            raise ImportError(f"文件处理错误: {str(e)}")
    
    def validate_structure(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证JSON数据结构
        
        Args:
            data: 数据列表
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        if not data:
            errors.append("JSON数据为空")
            return False, errors
        
        # 检查每条记录的结构
        for idx, record in enumerate(data):
            if not isinstance(record, dict):
                errors.append(f"第{idx + 1}条记录不是有效的对象")
                continue
            
            # 检查必需字段
            record_errors = self._validate_record_structure(record, idx + 1)
            errors.extend(record_errors)
            
            if len(errors) > 20:  # 限制错误数量
                errors.append("错误过多，停止验证...")
                break
        
        return len(errors) == 0, errors
    
    def _validate_record_structure(self, record: Dict[str, Any], row_num: int) -> List[str]:
        """验证单条记录的结构"""
        errors = []
        
        # 检查时间戳
        if 'timestamp' not in record and '评估时间' not in record and '观察时间' not in record:
            errors.append(f"第{row_num}条记录缺少时间信息")
        
        # 根据评估类型检查必需字段
        if self.assessment_type == 'autism':
            if 'scene' not in record and '评估情境' not in record:
                errors.append(f"第{row_num}条记录缺少评估情境")
        else:
            if 'scene' not in record and '观察情境' not in record:
                errors.append(f"第{row_num}条记录缺少观察情境")
        
        return errors
    
    def _convert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换JSON记录为标准格式
        
        Args:
            record: JSON记录
            
        Returns:
            转换后的记录
        """
        # JSON格式通常已经是标准格式，主要处理兼容性
        converted = record.copy()
        
        # 确保有评估类型
        if 'assessment_type' not in converted:
            converted['assessment_type'] = self.assessment_type
        
        # 处理时间戳
        if 'timestamp' not in converted:
            # 尝试从其他字段获取
            for field in ['评估时间', '观察时间', 'created_at', 'date']:
                if field in record:
                    timestamp = self._parse_timestamp_flexible(record[field])
                    if timestamp:
                        converted['timestamp'] = timestamp
                        break
        
        # 处理不同版本的字段名
        self._normalize_field_names(converted)
        
        return converted
    
    def _convert_datetime_fields(self, obj: Any) -> Any:
        """递归转换日期时间字段"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['timestamp', 'created_at', 'updated_at', '评估时间', '观察时间']:
                    obj[key] = self._parse_timestamp_flexible(value)
                elif isinstance(value, (dict, list)):
                    self._convert_datetime_fields(value)
        elif isinstance(obj, list):
            for item in obj:
                self._convert_datetime_fields(item)
        return obj
    
    def _parse_timestamp_flexible(self, value: Any) -> datetime.datetime:
        """灵活解析时间戳"""
        if isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, str):
            # ISO格式
            if 'T' in value:
                try:
                    # 处理带时区的ISO格式
                    if '+' in value or value.endswith('Z'):
                        # 简单处理：去掉时区信息
                        value = value.split('+')[0].split('Z')[0]
                    return datetime.datetime.fromisoformat(value)
                except:
                    pass
            # 尝试父类的解析方法
            return self._parse_timestamp(value)
        elif isinstance(value, (int, float)):
            # Unix时间戳
            try:
                return datetime.datetime.fromtimestamp(value)
            except:
                pass
        
        return datetime.datetime.now()
    
    def _normalize_field_names(self, record: Dict[str, Any]):
        """标准化字段名称"""
        # 字段映射表
        field_mappings = {
            # 通用字段
            '评估ID': 'experiment_id',
            '观察ID': 'observation_id',
            '评估情境': 'scene',
            '观察情境': 'scene',
            '观察活动': 'activity',
            '触发因素': 'trigger',
            '情境触发': 'trigger',
            '备注': 'notes',
            '配置类型': 'template',
            '年龄发展阶段': 'template',
            
            # ABC相关
            'ABC总分': 'abc_total_score',
            'ABC严重程度': 'abc_severity',
            
            # DSM-5相关
            'DSM5核心症状均分': 'dsm5_core_average'
        }
        
        # 应用映射
        for old_name, new_name in field_mappings.items():
            if old_name in record and new_name not in record:
                record[new_name] = record[old_name]
                # 可选：删除旧字段名
                # del record[old_name]
        
        # 处理嵌套结构
        if 'child_profile' in record and isinstance(record['child_profile'], dict):
            self._normalize_child_profile(record['child_profile'])
    
    def _normalize_child_profile(self, profile: Dict[str, Any]):
        """标准化儿童档案字段"""
        profile_mappings = {
            '发展阶段特征': 'stage_characteristics',
            '发展重点': 'development_focus',
            '语言发展配置': 'language_development',
            '社交技能配置': 'social_skills',
            '认知能力配置': 'cognitive_ability',
            '情绪调节配置': 'emotional_regulation',
            '运动技能配置': 'motor_skills',
            '独立性配置': 'independence_level',
            '典型兴趣描述': 'typical_interests'
        }
        
        for cn_name, en_name in profile_mappings.items():
            if cn_name in profile and en_name not in profile:
                profile[en_name] = profile[cn_name]