import re
import json
from typing import Any, Dict, List, Optional, Callable, Tuple


class DependencyManager:
    """依赖管理器，处理测试用例之间的依赖关系和数据传递"""

    def __init__(self):
        """初始化依赖管理器"""
        self.context: Dict[str, Any] = {}
        self.executed_cases: Dict[str, Dict[str, Any]] = {}

    def add_to_context(self, key: str, value: Any):
        """
        添加数据到上下文

        Args:
            key: 键名
            value: 值
        """
        self.context[key] = value

    def get_from_context(self, key: str, default: Any = None) -> Any:
        """
        从上下文获取数据

        Args:
            key: 键名
            default: 默认值

        Returns:
            对应的值
        """
        return self.context.get(key, default)

    def clear_context(self):
        """清空上下文"""
        self.context.clear()

    def store_case_result(self, case_id: str, result: Dict[str, Any]):
        """
        存储测试用例结果

        Args:
            case_id: 测试用例ID
            result: 测试结果
        """
        self.executed_cases[case_id] = result

    def get_case_result(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        获取测试用例结果

        Args:
            case_id: 测试用例ID

        Returns:
            测试用例结果
        """
        return self.executed_cases.get(case_id)

    def extract_data(self, response: Dict[str, Any], extract_config: Dict[str, str]) -> Dict[str, Any]:
        """
        从响应中提取数据

        Args:
            response: 响应数据
            extract_config: 提取配置 {变量名: 路径表达式}

        Returns:
            提取的数据字典
        """
        extracted = {}

        for var_name, path in extract_config.items():
            try:
                value = self._extract_by_path(response, path)
                extracted[var_name] = value
                self.add_to_context(var_name, value)
            except Exception as e:
                extracted[var_name] = None

        return extracted

    def _extract_by_path(self, response: Dict[str, Any], path: str) -> Any:
        """
        根据路径表达式提取数据

        Args:
            response: 响应数据
            path: 路径表达式

        Returns:
            提取的值
        """
        if path.startswith('$'):
            path = path[1:]

        if path.startswith('.'):
            path = path[1:]

        if path.startswith('response.'):
            path = path[9:]
        elif path.startswith('body.'):
            path = path[5:]

        body = response.get('body', {})
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                pass

        return self._get_nested_value(body, path)

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """
        获取嵌套字典的值

        Args:
            data: 字典数据
            path: 路径表达式

        Returns:
            路径对应的值
        """
        if not path:
            return data

        keys = []
        parts = re.split(r'\.', path)

        for part in parts:
            match = re.match(r'(\w+)\[(\d+)\]', part)
            if match:
                keys.append(match.group(1))
                keys.append(int(match.group(2)))
            else:
                keys.append(part)

        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int) and key < len(current):
                current = current[key]
            else:
                return None

        return current

    def resolve_dependencies(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析测试用例的依赖

        Args:
            test_case: 测试用例数据

        Returns:
            解析后的测试用例
        """
        resolved_case = test_case.copy()

        depends_on = test_case.get('depends_on', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]

        for dep_case_id in depends_on:
            dep_result = self.get_case_result(dep_case_id)
            if dep_result:
                resolved_case = self._merge_dependency_data(resolved_case, dep_result)

        resolved_case = self._replace_placeholders(resolved_case)

        return resolved_case

    def _merge_dependency_data(self, current_case: Dict[str, Any], dep_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并依赖数据到当前测试用例

        Args:
            current_case: 当前测试用例
            dep_result: 依赖测试用例结果

        Returns:
            合并后的测试用例
        """
        response = dep_result.get('response', {})
        extract_config = dep_result.get('extract', {})

        if extract_config:
            extracted = self.extract_data(response, extract_config)
            for key, value in extracted.items():
                self.add_to_context(key, value)

        return current_case

    def _replace_placeholders(self, data: Any) -> Any:
        """
        替换数据中的占位符

        Args:
            data: 待替换的数据

        Returns:
            替换后的数据
        """
        if isinstance(data, str):
            return self._replace_string_placeholders(data)
        elif isinstance(data, dict):
            return {k: self._replace_placeholders(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_placeholders(item) for item in data]
        else:
            return data

    def _replace_string_placeholders(self, s: str) -> Any:
        """
        替换字符串中的占位符

        Args:
            s: 待替换的字符串

        Returns:
            替换后的值
        """
        pattern = r'\$\{([^}]+)\}'
        matches = list(re.finditer(pattern, s))

        if not matches:
            return s

        if len(matches) == 1 and matches[0].group(0) == s:
            var_name = matches[0].group(1)
            return self.get_from_context(var_name, s)

        def replace_match(match):
            var_name = match.group(1)
            value = self.get_from_context(var_name, match.group(0))
            return str(value)

        return re.sub(pattern, replace_match, s)

    def check_dependencies_met(self, test_case: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        检查依赖是否满足

        Args:
            test_case: 测试用例

        Returns:
            (是否满足, 未满足的依赖列表)
        """
        depends_on = test_case.get('depends_on', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]

        missing_deps = []
        for dep_case_id in depends_on:
            dep_result = self.get_case_result(dep_case_id)
            if dep_result is None:
                missing_deps.append(dep_case_id)
            elif not dep_result.get('success', False):
                missing_deps.append(f"{dep_case_id}(执行失败)")

        return len(missing_deps) == 0, missing_deps

    def get_execution_order(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据依赖关系确定测试用例执行顺序

        Args:
            test_cases: 测试用例列表

        Returns:
            排序后的测试用例列表
        """
        case_map = {case['id']: case for case in test_cases}
        case_ids = list(case_map.keys())

        ordered = []
        visited = set()
        visiting = set()

        def visit(case_id: str):
            if case_id in visiting:
                raise ValueError(f"检测到循环依赖: {case_id}")
            if case_id in visited:
                return

            visiting.add(case_id)

            case = case_map.get(case_id)
            if case:
                depends_on = case.get('depends_on', [])
                if isinstance(depends_on, str):
                    depends_on = [depends_on]

                for dep_id in depends_on:
                    if dep_id in case_ids:
                        visit(dep_id)

            visiting.remove(case_id)
            visited.add(case_id)
            if case:
                ordered.append(case)

        for case_id in case_ids:
            if case_id not in visited:
                visit(case_id)

        return ordered

    def reset(self):
        """重置依赖管理器状态"""
        self.clear_context()
        self.executed_cases.clear()
