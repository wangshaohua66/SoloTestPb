import re
import json
from typing import Any, Dict, List, Tuple, Optional


class AssertionEngine:
    """断言引擎，支持多种类型的响应断言"""

    def __init__(self):
        """初始化断言引擎"""
        self.assertion_types = {
            'status_code': self._assert_status_code,
            'status': self._assert_status_code,
            'body': self._assert_body,
            'json': self._assert_json,
            'json_path': self._assert_json_path,
            'headers': self._assert_headers,
            'header': self._assert_headers,
            'response_time': self._assert_response_time,
            'contains': self._assert_contains,
            'not_contains': self._assert_not_contains,
            'equals': self._assert_equals,
            'not_equals': self._assert_not_equals,
            'greater_than': self._assert_greater_than,
            'less_than': self._assert_less_than,
            'regex': self._assert_regex,
            'exists': self._assert_exists,
            'not_exists': self._assert_not_exists,
            'type': self._assert_type
        }

    def assert_all(self, assertions: List[Dict[str, Any]], response: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        执行所有断言

        Args:
            assertions: 断言列表
            response: 响应数据

        Returns:
            (是否全部通过, 断言结果列表)
        """
        results = []
        all_passed = True

        for assertion in assertions:
            passed, result = self._execute_assertion(assertion, response)
            results.append(result)
            if not passed:
                all_passed = False

        return all_passed, results

    def _execute_assertion(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        执行单个断言

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 断言结果字典)
        """
        assertion_type = assertion.get('type', assertion.get('assertion', ''))
        expected = assertion.get('expected', assertion.get('value'))
        actual = assertion.get('actual', '')
        message = assertion.get('message', f'{assertion_type}断言失败')

        result = {
            'type': assertion_type,
            'expected': expected,
            'actual': None,
            'passed': False,
            'message': message
        }

        try:
            if assertion_type not in self.assertion_types:
                result['message'] = f'不支持的断言类型: {assertion_type}'
                return False, result

            passed, actual_value = self.assertion_types[assertion_type](assertion, response)
            result['actual'] = actual_value
            result['passed'] = passed

            if not passed:
                result['message'] = f'{message} - 预期: {expected}, 实际: {actual_value}'

            return passed, result

        except Exception as e:
            result['message'] = f'断言执行异常: {str(e)}'
            return False, result

    def _assert_status_code(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, int]:
        """
        断言状态码

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际状态码)
        """
        expected = assertion.get('expected', assertion.get('value', 200))
        actual = response.get('status_code', 0)

        if isinstance(expected, list):
            return actual in expected, actual
        return actual == expected, actual

    def _assert_body(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        断言响应体内容

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际响应体)
        """
        expected = assertion.get('expected', assertion.get('value', ''))
        actual = response.get('body', response.get('text', ''))

        if isinstance(actual, (dict, list)):
            actual_str = json.dumps(actual, ensure_ascii=False)
        else:
            actual_str = str(actual)

        return str(expected) in actual_str, actual_str

    def _assert_json(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言JSON响应

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value'))
        key = assertion.get('key', assertion.get('path', ''))
        body = response.get('body', {})

        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return False, body

        if key:
            actual = self._get_nested_value(body, key)
        else:
            actual = body

        return actual == expected, actual

    def _assert_json_path(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言JSON路径

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value'))
        path = assertion.get('path', assertion.get('json_path', ''))
        body = response.get('body', {})

        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return False, body

        actual = self._get_nested_value(body, path)
        return actual == expected, actual

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """
        获取嵌套字典的值

        Args:
            data: 字典数据
            path: 路径表达式 (如: 'data.user.name' 或 'data.items[0].name')

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

    def _assert_headers(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言响应头

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value'))
        header_name = assertion.get('header', assertion.get('name', ''))
        headers = response.get('headers', {})

        actual = headers.get(header_name)
        return str(actual) == str(expected), actual

    def _assert_response_time(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, int]:
        """
        断言响应时间

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际响应时间)
        """
        max_time = assertion.get('max', assertion.get('expected', assertion.get('value', 1000)))
        actual = response.get('response_time_ms', 0)

        return actual <= max_time, actual

    def _assert_contains(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        断言包含

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value', ''))
        actual = assertion.get('actual', str(response.get('body', response.get('text', ''))))

        return str(expected) in str(actual), actual

    def _assert_not_contains(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        断言不包含

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value', ''))
        actual = assertion.get('actual', str(response.get('body', response.get('text', ''))))

        return str(expected) not in str(actual), actual

    def _assert_equals(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言相等

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value'))
        actual = assertion.get('actual')

        if actual is None:
            key = assertion.get('key', assertion.get('path', ''))
            body = response.get('body', {})
            if key:
                actual = self._get_nested_value(body, key)
            else:
                actual = body

        return actual == expected, actual

    def _assert_not_equals(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言不相等

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value'))
        actual = assertion.get('actual')

        if actual is None:
            key = assertion.get('key', assertion.get('path', ''))
            body = response.get('body', {})
            if key:
                actual = self._get_nested_value(body, key)
            else:
                actual = body

        return actual != expected, actual

    def _assert_greater_than(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言大于

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value', 0))
        actual = assertion.get('actual')

        if actual is None:
            key = assertion.get('key', assertion.get('path', ''))
            body = response.get('body', {})
            if key:
                actual = self._get_nested_value(body, key)
            else:
                actual = 0

        try:
            return float(actual) > float(expected), actual
        except (ValueError, TypeError):
            return False, actual

    def _assert_less_than(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言小于

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        expected = assertion.get('expected', assertion.get('value', 0))
        actual = assertion.get('actual')

        if actual is None:
            key = assertion.get('key', assertion.get('path', ''))
            body = response.get('body', {})
            if key:
                actual = self._get_nested_value(body, key)
            else:
                actual = 0

        try:
            return float(actual) < float(expected), actual
        except (ValueError, TypeError):
            return False, actual

    def _assert_regex(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        断言正则匹配

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        pattern = assertion.get('pattern', assertion.get('expected', assertion.get('value', '')))
        actual = assertion.get('actual', str(response.get('body', response.get('text', ''))))

        try:
            return bool(re.search(str(pattern), str(actual))), actual
        except re.error:
            return False, actual

    def _assert_exists(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言存在

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        key = assertion.get('key', assertion.get('path', ''))
        body = response.get('body', {})

        actual = self._get_nested_value(body, key)
        return actual is not None, actual

    def _assert_not_exists(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        断言不存在

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际值)
        """
        key = assertion.get('key', assertion.get('path', ''))
        body = response.get('body', {})

        actual = self._get_nested_value(body, key)
        return actual is None, actual

    def _assert_type(self, assertion: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        断言类型

        Args:
            assertion: 断言配置
            response: 响应数据

        Returns:
            (是否通过, 实际类型)
        """
        expected_type = assertion.get('expected', assertion.get('value', ''))
        key = assertion.get('key', assertion.get('path', ''))
        body = response.get('body', {})

        if key:
            actual = self._get_nested_value(body, key)
        else:
            actual = body

        actual_type = type(actual).__name__
        type_mapping = {
            'str': 'str', 'string': 'str',
            'int': 'int', 'integer': 'int',
            'float': 'float',
            'bool': 'bool', 'boolean': 'bool',
            'list': 'list', 'array': 'list',
            'dict': 'dict', 'object': 'dict',
            'NoneType': 'None', 'null': 'None'
        }

        expected = type_mapping.get(expected_type, expected_type)
        actual_mapped = type_mapping.get(actual_type, actual_type)

        return expected == actual_mapped, actual_type
