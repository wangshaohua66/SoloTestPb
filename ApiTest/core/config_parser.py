import yaml
import os
from typing import List, Dict, Any


class ConfigParser:
    """YAML配置解析器，负责读取和解析测试用例配置文件"""

    def __init__(self):
        """初始化配置解析器"""
        self.test_cases = []

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析单个YAML测试用例文件

        Args:
            file_path: YAML文件路径

        Returns:
            解析后的测试用例列表

        Raises:
            FileNotFoundError: 文件不存在时抛出
            yaml.YAMLError: YAML解析错误时抛出
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"测试用例文件不存在: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"YAML解析错误: {str(e)}")

        cases = self._parse_test_cases(data, file_path)
        self.test_cases.extend(cases)
        return cases

    def parse_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """
        解析目录下所有YAML测试用例文件

        Args:
            dir_path: 目录路径

        Returns:
            解析后的所有测试用例列表

        Raises:
            NotADirectoryError: 目录不存在时抛出
        """
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"目录不存在: {dir_path}")

        all_cases = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(('.yml', '.yaml')):
                    file_path = os.path.join(root, file)
                    cases = self.parse_file(file_path)
                    all_cases.extend(cases)

        return all_cases

    def _parse_test_cases(self, data: Any, file_path: str) -> List[Dict[str, Any]]:
        """
        解析测试用例数据

        Args:
            data: YAML加载的数据
            file_path: 源文件路径

        Returns:
            标准化的测试用例列表
        """
        cases = []

        if not data:
            return cases

        if isinstance(data, list):
            for idx, item in enumerate(data):
                case = self._normalize_test_case(item, file_path, idx)
                cases.append(case)
        elif isinstance(data, dict):
            if 'test_cases' in data:
                for idx, item in enumerate(data['test_cases']):
                    case = self._normalize_test_case(item, file_path, idx)
                    cases.append(case)
            else:
                case = self._normalize_test_case(data, file_path, 0)
                cases.append(case)

        return cases

    def _normalize_test_case(self, case_data: Dict[str, Any], file_path: str, index: int) -> Dict[str, Any]:
        """
        标准化测试用例格式

        Args:
            case_data: 原始测试用例数据
            file_path: 源文件路径
            index: 测试用例在文件中的索引

        Returns:
            标准化的测试用例字典
        """
        case_id = case_data.get('id', f"{os.path.basename(file_path)}_case_{index}")
        case_name = case_data.get('name', case_data.get('description', f"测试用例_{case_id}"))

        normalized = {
            'id': case_id,
            'name': case_name,
            'description': case_data.get('description', ''),
            'file_path': file_path,
            'enabled': case_data.get('enabled', True),
            'tags': case_data.get('tags', []),
            'priority': case_data.get('priority', 'medium'),
            'request': self._normalize_request(case_data.get('request', {})),
            'assertions': case_data.get('assertions', []),
            'variables': case_data.get('variables', {}),
            'depends_on': case_data.get('depends_on', []),
            'extract': case_data.get('extract', {}),
            'timeout': case_data.get('timeout', 30)
        }

        return normalized

    def _normalize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化请求配置

        Args:
            request_data: 原始请求配置

        Returns:
            标准化的请求配置字典
        """
        method = request_data.get('method', 'GET').upper()

        normalized = {
            'method': method,
            'url': request_data.get('url', ''),
            'base_url': request_data.get('base_url', ''),
            'headers': request_data.get('headers', {}),
            'params': request_data.get('params', {}),
            'data': request_data.get('data', {}),
            'json': request_data.get('json', {}),
            'files': request_data.get('files', {}),
            'auth': request_data.get('auth'),
            'verify': request_data.get('verify', True),
            'allow_redirects': request_data.get('allow_redirects', True)
        }

        return normalized

    def get_test_case_by_id(self, case_id: str) -> Dict[str, Any]:
        """
        根据ID获取测试用例

        Args:
            case_id: 测试用例ID

        Returns:
            测试用例字典，未找到时返回None
        """
        for case in self.test_cases:
            if case['id'] == case_id:
                return case
        return None

    def get_test_cases_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        根据标签筛选测试用例

        Args:
            tag: 标签名称

        Returns:
            匹配的测试用例列表
        """
        return [case for case in self.test_cases if tag in case['tags']]

    def get_all_test_cases(self) -> List[Dict[str, Any]]:
        """
        获取所有已加载的测试用例

        Returns:
            所有测试用例列表
        """
        return self.test_cases.copy()

    def clear(self):
        """清空已加载的测试用例"""
        self.test_cases = []
