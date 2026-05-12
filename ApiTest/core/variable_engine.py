import re
import random
import string
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Callable
from faker import Faker


class VariableEngine:
    """变量解析引擎，支持变量替换和函数生成测试数据"""

    def __init__(self):
        """初始化变量引擎"""
        self.variables: Dict[str, Any] = {}
        self.faker = Faker('zh_CN')
        self._init_builtin_functions()

    def _init_builtin_functions(self):
        """初始化内置函数"""
        self.functions = {
            'random_int': self._random_int,
            'random_string': self._random_string,
            'random_float': self._random_float,
            'random_choice': self._random_choice,
            'uuid': self._generate_uuid,
            'timestamp': self._timestamp,
            'datetime': self._datetime,
            'date': self._date,
            'today': self._today,
            'future_date': self._future_date,
            'past_date': self._past_date,
            'name': self.faker.name,
            'phone': self.faker.phone_number,
            'email': self.faker.email,
            'address': self.faker.address,
            'city': self.faker.city,
            'company': self.faker.company,
            'job': self.faker.job,
            'text': self.faker.text,
            'sentence': self.faker.sentence,
            'word': self.faker.word,
            'url': self.faker.url,
            'ipv4': self.faker.ipv4,
            'user_name': self.faker.user_name,
            'password': self.faker.password,
            'credit_card': self.faker.credit_card_number,
            'inc': self._increment
        }
        self._counter = 0

    def set_variable(self, name: str, value: Any):
        """
        设置变量

        Args:
            name: 变量名
            value: 变量值
        """
        self.variables[name] = value

    def set_variables(self, variables: Dict[str, Any]):
        """
        批量设置变量

        Args:
            variables: 变量字典
        """
        self.variables.update(variables)

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        获取变量值

        Args:
            name: 变量名
            default: 默认值

        Returns:
            变量值
        """
        return self.variables.get(name, default)

    def clear_variables(self):
        """清空所有变量"""
        self.variables.clear()
        self._counter = 0

    def _random_int(self, min_val: int = 0, max_val: int = 100) -> int:
        """生成随机整数"""
        return random.randint(int(min_val), int(max_val))

    def _random_string(self, length: int = 8) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=int(length)))

    def _random_float(self, min_val: float = 0, max_val: float = 1, precision: int = 2) -> float:
        """生成随机浮点数"""
        return round(random.uniform(float(min_val), float(max_val)), int(precision))

    def _random_choice(self, *args) -> Any:
        """从列表中随机选择"""
        return random.choice(list(args))

    def _generate_uuid(self) -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    def _timestamp(self, unit: str = 's') -> int:
        """生成时间戳"""
        if unit == 'ms':
            return int(time.time() * 1000)
        return int(time.time())

    def _datetime(self, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """生成当前时间字符串"""
        return datetime.now().strftime(format_str)

    def _date(self, format_str: str = '%Y-%m-%d') -> str:
        """生成当前日期字符串"""
        return datetime.now().strftime(format_str)

    def _today(self, format_str: str = '%Y-%m-%d') -> str:
        """生成今天日期"""
        return datetime.now().strftime(format_str)

    def _future_date(self, days: int = 7, format_str: str = '%Y-%m-%d') -> str:
        """生成未来日期"""
        return (datetime.now() + timedelta(days=int(days))).strftime(format_str)

    def _past_date(self, days: int = 7, format_str: str = '%Y-%m-%d') -> str:
        """生成过去日期"""
        return (datetime.now() - timedelta(days=int(days))).strftime(format_str)

    def _increment(self, start: int = 1, step: int = 1) -> int:
        """生成递增数字"""
        self._counter += int(step)
        return int(start) + self._counter - int(step)

    def register_function(self, name: str, func: Callable):
        """
        注册自定义函数

        Args:
            name: 函数名
            func: 函数对象
        """
        self.functions[name] = func

    def parse_value(self, value: Any) -> Any:
        """
        解析值中的变量和函数

        Args:
            value: 待解析的值

        Returns:
            解析后的值
        """
        if isinstance(value, str):
            return self._parse_string(value)
        elif isinstance(value, dict):
            return {k: self.parse_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.parse_value(item) for item in value]
        else:
            return value

    def _parse_string(self, s: str) -> Any:
        """
        解析字符串中的变量和函数

        Args:
            s: 待解析的字符串

        Returns:
            解析后的值
        """
        result = s

        var_pattern = r'\$\{([^}]+)\}'
        func_pattern = r'\$\{(\w+)\(([^)]*)\)\}'

        var_matches = list(re.finditer(var_pattern, s))
        func_matches = list(re.finditer(func_pattern, s))

        if not var_matches and not func_matches:
            return s

        func_full_match = re.match(r'^\$\{(\w+)\(([^)]*)\)\}$', s)
        if func_full_match:
            func_name = func_full_match.group(1)
            args_str = func_full_match.group(2)
            args = self._parse_args(args_str)
            return self._call_function(func_name, args)

        var_full_match = re.match(r'^\$\{(\w+)\}$', s)
        if var_full_match:
            var_name = var_full_match.group(1)
            return self.get_variable(var_name, s)

        result = re.sub(func_pattern, lambda m: str(self._call_function(m.group(1), self._parse_args(m.group(2)))), result)

        result = re.sub(var_pattern, lambda m: str(self.get_variable(m.group(1), m.group(0))), result)

        return result

    def _parse_args(self, args_str: str) -> list:
        """
        解析函数参数

        Args:
            args_str: 参数字符串

        Returns:
            参数列表
        """
        if not args_str.strip():
            return []

        args = []
        current = ''
        in_quotes = False
        quote_char = None
        i = 0

        while i < len(args_str):
            char = args_str[i]

            if char in '"\'' and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == ',' and not in_quotes:
                args.append(current.strip())
                current = ''
            else:
                current += char

            i += 1

        if current.strip():
            args.append(current.strip())

        parsed_args = []
        for arg in args:
            arg = arg.strip()
            if arg.startswith(('"', "'")) and arg.endswith(arg[0]):
                parsed_args.append(arg[1:-1])
            elif arg.isdigit():
                parsed_args.append(int(arg))
            elif self._is_float(arg):
                parsed_args.append(float(arg))
            else:
                parsed_args.append(arg)

        return parsed_args

    def _is_float(self, s: str) -> bool:
        """判断字符串是否为浮点数"""
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _call_function(self, func_name: str, args: list) -> Any:
        """
        调用函数

        Args:
            func_name: 函数名
            args: 参数列表

        Returns:
            函数返回值
        """
        if func_name in self.functions:
            try:
                return self.functions[func_name](*args)
            except Exception as e:
                return f"ERROR:{func_name}({','.join(map(str, args))})"
        return f"${{{func_name}({','.join(map(str, args))})"

    def parse_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析测试用例中的所有变量

        Args:
            test_case: 测试用例字典

        Returns:
            解析后的测试用例
        """
        parsed = test_case.copy()

        if 'variables' in parsed:
            for key, value in parsed['variables'].items():
                parsed['variables'][key] = self.parse_value(value)
            self.set_variables(parsed['variables'])

        if 'request' in parsed:
            parsed['request'] = self.parse_value(parsed['request'])

        if 'assertions' in parsed:
            parsed['assertions'] = self.parse_value(parsed['assertions'])

        return parsed
