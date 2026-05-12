import pytest

from core.variable_engine import VariableEngine


class TestVariableEngine:
    """变量引擎单元测试"""

    @pytest.fixture
    def engine(self):
        return VariableEngine()

    def test_set_and_get_variable(self, engine):
        engine.set_variable('name', 'test')
        assert engine.get_variable('name') == 'test'

    def test_get_nonexistent_variable(self, engine):
        assert engine.get_variable('nonexistent') is None
        assert engine.get_variable('nonexistent', 'default') == 'default'

    def test_set_variables(self, engine):
        engine.set_variables({'a': 1, 'b': 2})
        assert engine.get_variable('a') == 1
        assert engine.get_variable('b') == 2

    def test_clear_variables(self, engine):
        engine.set_variable('x', 100)
        engine.clear_variables()
        assert engine.get_variable('x') is None

    def test_parse_value_simple(self, engine):
        engine.set_variable('name', 'Alice')
        result = engine.parse_value('Hello ${name}!')
        assert 'Hello Alice!' in result

    def test_parse_dict(self, engine):
        engine.set_variable('id', 123)
        data = {
            'user': '${id}',
            'info': {
                'name': 'User ${id}'
            }
        }
        result = engine.parse_value(data)
        assert result['user'] == 123
        assert result['info']['name'] == 'User 123'

    def test_parse_list(self, engine):
        engine.set_variable('val', 'test')
        data = ['${val}', 'static', '${val}_x']
        result = engine.parse_value(data)
        assert result[0] == 'test'
        assert result[2] == 'test_x'

    def test_random_int_function(self, engine):
        result = engine._random_int(1, 10)
        assert 1 <= result <= 10

    def test_random_string_function(self, engine):
        result = engine._random_string(8)
        assert len(result) == 8
        assert result.isalnum()

    def test_timestamp_function(self, engine):
        result = engine._timestamp()
        assert isinstance(result, int)
        assert result > 0

    def test_increment_function(self, engine):
        first = engine._increment()
        second = engine._increment()
        assert second == first + 1

    def test_uuid_function(self, engine):
        uuid_str = engine._generate_uuid()
        assert len(uuid_str) == 36
        assert '-' in uuid_str

    def test_register_function(self, engine):
        def custom_func(x):
            return x * 2
        engine.register_function('double', custom_func)
        assert 'double' in engine.functions

    def test_full_variable_match(self, engine):
        engine.set_variable('number', 42)
        result = engine._parse_string('${number}')
        assert result == 42

    def test_parse_args(self, engine):
        args_str = '"hello", 123, 3.14'
        args = engine._parse_args(args_str)
        assert args == ['hello', 123, 3.14]

    def test_is_float(self, engine):
        assert engine._is_float('3.14') is True
        assert engine._is_float('123') is True
        assert engine._is_float('abc') is False

    def test_call_function_unknown(self, engine):
        result = engine._call_function('unknown_func', [])
        assert 'unknown_func' in result

    def test_parse_test_case(self, engine):
        test_case = {
            'id': 'test_001',
            'variables': {
                'user_id': '${random_int(1,100)}'
            },
            'request': {
                'url': '/api/users/${user_id}'
            },
            'assertions': []
        }
        result = engine.parse_test_case(test_case)
        assert 'user_id' in engine.variables
        assert '/api/users/' in result['request']['url']

    def test_faker_functions(self, engine):
        name = engine.functions['name']()
        assert isinstance(name, str)
        assert len(name) > 0

        email = engine.functions['email']()
        assert '@' in email
