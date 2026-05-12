import pytest

from core.assertion_engine import AssertionEngine


class TestAssertionEngine:
    """断言引擎单元测试"""

    @pytest.fixture
    def engine(self):
        return AssertionEngine()

    @pytest.fixture
    def sample_response(self):
        return {
            'status_code': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': 'abc123'
            },
            'body': {
                'success': True,
                'data': {
                    'id': 123,
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'items': [1, 2, 3]
                },
                'message': 'OK'
            },
            'response_time_ms': 150
        }

    def test_assert_status_code_success(self, engine, sample_response):
        assertions = [{'type': 'status_code', 'expected': 200}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True
        assert results[0]['passed'] is True

    def test_assert_status_code_failure(self, engine, sample_response):
        assertions = [{'type': 'status_code', 'expected': 500}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is False

    def test_assert_status_code_list(self, engine, sample_response):
        assertions = [{'type': 'status_code', 'expected': [200, 201]}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_body_contains(self, engine, sample_response):
        assertions = [{'type': 'body', 'expected': 'Test User'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_json_path(self, engine, sample_response):
        assertions = [
            {'type': 'json_path', 'path': 'data.id', 'expected': 123},
            {'type': 'json_path', 'path': 'data.name', 'expected': 'Test User'}
        ]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_response_time(self, engine, sample_response):
        assertions = [{'type': 'response_time', 'max': 500}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_response_time_failure(self, engine, sample_response):
        assertions = [{'type': 'response_time', 'max': 100}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is False

    def test_assert_equals(self, engine, sample_response):
        assertions = [
            {'type': 'equals', 'key': 'success', 'expected': True},
            {'type': 'equals', 'key': 'message', 'expected': 'OK'}
        ]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_contains(self, engine, sample_response):
        assertions = [{'type': 'contains', 'expected': 'email'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_not_contains(self, engine, sample_response):
        assertions = [{'type': 'not_contains', 'expected': 'error'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_exists(self, engine, sample_response):
        assertions = [{'type': 'exists', 'key': 'data.id'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_not_exists(self, engine, sample_response):
        assertions = [{'type': 'not_exists', 'key': 'data.error'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_type(self, engine, sample_response):
        assertions = [
            {'type': 'type', 'key': 'data.id', 'expected': 'int'},
            {'type': 'type', 'key': 'data.name', 'expected': 'string'}
        ]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_greater_than(self, engine, sample_response):
        assertions = [{'type': 'greater_than', 'key': 'data.id', 'expected': 100}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_less_than(self, engine, sample_response):
        assertions = [{'type': 'less_than', 'key': 'data.id', 'expected': 200}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_assert_regex(self, engine, sample_response):
        assertions = [{'type': 'regex', 'pattern': r'\w+@\w+\.\w+'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True

    def test_unknown_assertion_type(self, engine, sample_response):
        assertions = [{'type': 'unknown_type', 'expected': 'value'}]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is False

    def test_multiple_assertions(self, engine, sample_response):
        assertions = [
            {'type': 'status_code', 'expected': 200},
            {'type': 'response_time', 'max': 500},
            {'type': 'json_path', 'path': 'data.id', 'expected': 123}
        ]
        all_passed, results = engine.assert_all(assertions, sample_response)
        assert all_passed is True
        assert len(results) == 3

    def test_get_nested_value(self, engine, sample_response):
        result = engine._get_nested_value(sample_response['body'], 'data.items[1]')
        assert result == 2

    def test_get_nested_value_not_found(self, engine, sample_response):
        result = engine._get_nested_value(sample_response['body'], 'data.nonexistent')
        assert result is None

    def test_assert_with_exception(self, engine):
        assertions = [{'type': 'status_code', 'expected': 200}]
        all_passed, results = engine.assert_all(assertions, {})
        assert all_passed is False
