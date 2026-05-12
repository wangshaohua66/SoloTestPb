import pytest
from core.dependency_manager import DependencyManager


class TestDependencyManager:
    """依赖管理器单元测试"""

    @pytest.fixture
    def manager(self):
        return DependencyManager()

    def test_initialization(self, manager):
        """测试初始化"""
        assert manager.context == {}
        assert manager.executed_cases == {}

    def test_add_to_context(self, manager):
        """测试添加数据到上下文"""
        manager.add_to_context('key1', 'value1')
        assert manager.context['key1'] == 'value1'

    def test_get_from_context_existing(self, manager):
        """测试从上下文获取存在的数据"""
        manager.add_to_context('test_key', 'test_value')
        value = manager.get_from_context('test_key')
        assert value == 'test_value'

    def test_get_from_context_missing(self, manager):
        """测试从上下文获取不存在的数据"""
        value = manager.get_from_context('nonexistent')
        assert value is None

    def test_get_from_context_with_default(self, manager):
        """测试从上下文获取数据带默认值"""
        value = manager.get_from_context('nonexistent', 'default')
        assert value == 'default'

    def test_clear_context(self, manager):
        """测试清空上下文"""
        manager.add_to_context('key1', 'value1')
        manager.add_to_context('key2', 'value2')
        manager.clear_context()
        assert manager.context == {}

    def test_store_case_result(self, manager):
        """测试存储测试用例结果"""
        result = {'success': True, 'response': {'status_code': 200}}
        manager.store_case_result('case_1', result)
        assert 'case_1' in manager.executed_cases
        assert manager.executed_cases['case_1'] == result

    def test_get_case_result_existing(self, manager):
        """测试获取存在的测试用例结果"""
        result = {'success': True}
        manager.store_case_result('case_1', result)
        retrieved = manager.get_case_result('case_1')
        assert retrieved == result

    def test_get_case_result_missing(self, manager):
        """测试获取不存在的测试用例结果"""
        result = manager.get_case_result('nonexistent')
        assert result is None

    def test_extract_data_simple(self, manager):
        """测试简单提取数据"""
        response = {
            'body': {
                'token': 'abc123',
                'user': {'id': 1, 'name': 'test'}
            }
        }
        extract_config = {
            'auth_token': 'token',
            'user_id': 'user.id'
        }
        extracted = manager.extract_data(response, extract_config)
        assert extracted['auth_token'] == 'abc123'

    def test_extract_data_nested(self, manager):
        """测试嵌套提取数据"""
        response = {
            'body': {
                'data': {
                    'items': [{'id': 1}, {'id': 2}]
                }
            }
        }
        extract_config = {
            'first_item_id': 'data.items[0].id'
        }
        extracted = manager.extract_data(response, extract_config)
        assert extracted['first_item_id'] == 1

    def test_extract_data_updates_context(self, manager):
        """测试提取数据更新上下文"""
        response = {'body': {'token': 'xyz789'}}
        extract_config = {'token': 'token'}
        manager.extract_data(response, extract_config)
        assert manager.context['token'] == 'xyz789'

    def test_check_dependencies_met_all_met(self, manager):
        """测试所有依赖满足"""
        manager.store_case_result('case_1', {'success': True})
        test_case = {'depends_on': ['case_1']}
        met, missing = manager.check_dependencies_met(test_case)
        assert met is True
        assert missing == []

    def test_check_dependencies_met_missing(self, manager):
        """测试依赖缺失"""
        test_case = {'depends_on': ['nonexistent_case']}
        met, missing = manager.check_dependencies_met(test_case)
        assert met is False
        assert 'nonexistent_case' in missing[0]

    def test_check_dependencies_met_failed(self, manager):
        """测试依赖用例执行失败"""
        manager.store_case_result('case_1', {'success': False})
        test_case = {'depends_on': ['case_1']}
        met, missing = manager.check_dependencies_met(test_case)
        assert met is False
        assert 'case_1' in missing[0]

    def test_check_dependencies_met_string_dep(self, manager):
        """测试字符串形式的依赖"""
        manager.store_case_result('case_1', {'success': True})
        test_case = {'depends_on': 'case_1'}
        met, missing = manager.check_dependencies_met(test_case)
        assert met is True

    def test_check_dependencies_met_no_deps(self, manager):
        """测试无依赖的情况"""
        test_case = {}
        met, missing = manager.check_dependencies_met(test_case)
        assert met is True
        assert missing == []

    def test_get_execution_order_simple(self, manager):
        """测试简单的执行顺序"""
        cases = [
            {'id': 'case_1', 'depends_on': []},
            {'id': 'case_2', 'depends_on': ['case_1']}
        ]
        ordered = manager.get_execution_order(cases)
        assert ordered[0]['id'] == 'case_1'
        assert ordered[1]['id'] == 'case_2'

    def test_get_execution_order_chain(self, manager):
        """测试链式依赖的执行顺序"""
        cases = [
            {'id': 'case_3', 'depends_on': ['case_2']},
            {'id': 'case_1', 'depends_on': []},
            {'id': 'case_2', 'depends_on': ['case_1']}
        ]
        ordered = manager.get_execution_order(cases)
        assert ordered[0]['id'] == 'case_1'
        assert ordered[1]['id'] == 'case_2'
        assert ordered[2]['id'] == 'case_3'

    def test_get_execution_order_circular_dependency(self, manager):
        """测试循环依赖检测"""
        cases = [
            {'id': 'case_1', 'depends_on': ['case_2']},
            {'id': 'case_2', 'depends_on': ['case_1']}
        ]
        with pytest.raises(ValueError, match='循环依赖'):
            manager.get_execution_order(cases)

    def test_replace_placeholders_string(self, manager):
        """测试替换字符串占位符"""
        manager.add_to_context('name', 'Alice')
        result = manager._replace_placeholders('Hello ${name}!')
        assert 'Hello Alice!' in result

    def test_replace_placeholders_full_match(self, manager):
        """测试完整匹配的占位符替换"""
        manager.add_to_context('value', 42)
        result = manager._replace_placeholders('${value}')
        assert result == 42

    def test_replace_placeholders_dict(self, manager):
        """测试替换字典中的占位符"""
        manager.add_to_context('id', 123)
        data = {'user': 'User ${id}'}
        result = manager._replace_placeholders(data)
        assert result['user'] == 'User 123'

    def test_replace_placeholders_list(self, manager):
        """测试替换列表中的占位符"""
        manager.add_to_context('val', 'test')
        data = ['${val}', 'static']
        result = manager._replace_placeholders(data)
        assert result[0] == 'test'

    def test_resolve_dependencies(self, manager):
        """测试解析依赖"""
        manager.store_case_result('case_1', {'success': True, 'extract': {}, 'response': {'body': {}}})
        manager.add_to_context('token', 'abc123')
        test_case = {
            'id': 'case_2',
            'depends_on': ['case_1'],
            'request': {'url': '/api/${token}'}
        }
        resolved = manager.resolve_dependencies(test_case)
        assert 'url' in resolved['request']

    def test_reset(self, manager):
        """测试重置状态"""
        manager.add_to_context('key', 'value')
        manager.store_case_result('case_1', {'success': True})
        manager.reset()
        assert manager.context == {}
        assert manager.executed_cases == {}

    def test_get_nested_value_simple(self, manager):
        """测试获取简单嵌套值"""
        data = {'a': {'b': {'c': 'value'}}}
        result = manager._get_nested_value(data, 'a.b.c')
        assert result == 'value'

    def test_get_nested_value_array(self, manager):
        """测试获取数组中的值"""
        data = {'items': [{'id': 1}, {'id': 2}]}
        result = manager._get_nested_value(data, 'items[1].id')
        assert result == 2

    def test_get_nested_value_not_found(self, manager):
        """测试获取不存在的嵌套值"""
        data = {'a': 1}
        result = manager._get_nested_value(data, 'a.b.c')
        assert result is None
