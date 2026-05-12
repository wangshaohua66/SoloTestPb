import pytest
import os
import tempfile
import yaml

from core.config_parser import ConfigParser


class TestConfigParser:
    """配置解析器单元测试"""

    @pytest.fixture
    def parser(self):
        return ConfigParser()

    @pytest.fixture
    def temp_yaml_file(self):
        content = """
- id: test_case_1
  name: 测试用例1
  description: 这是一个测试用例
  tags: [smoke, regression]
  enabled: true
  request:
    method: GET
    url: https://httpbin.org/get
    headers:
      Content-Type: application/json
  assertions:
    - type: status_code
      expected: 200

- id: test_case_2
  name: 测试用例2
  request:
    method: POST
    url: https://httpbin.org/post
    json:
      key: value
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(content)
            filename = f.name
        yield filename
        os.unlink(filename)

    def test_parse_file(self, parser, temp_yaml_file):
        cases = parser.parse_file(temp_yaml_file)
        assert len(cases) == 2
        assert cases[0]['id'] == 'test_case_1'
        assert cases[0]['name'] == '测试用例1'
        assert cases[0]['request']['method'] == 'GET'

    def test_parse_directory(self, parser):
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                content = f"""
- id: case_{i}
  name: 测试用例{i}
  request:
    method: GET
    url: https://httpbin.org/get
"""
                with open(os.path.join(tmpdir, f'test_{i}.yaml'), 'w', encoding='utf-8') as f:
                    f.write(content)

            cases = parser.parse_directory(tmpdir)
            assert len(cases) == 3

    def test_file_not_found(self, parser):
        with pytest.raises(FileNotFoundError):
            parser.parse_file('nonexistent.yaml')

    def test_directory_not_found(self, parser):
        with pytest.raises(NotADirectoryError):
            parser.parse_directory('nonexistent_dir')

    def test_get_test_case_by_id(self, parser, temp_yaml_file):
        parser.parse_file(temp_yaml_file)
        case = parser.get_test_case_by_id('test_case_1')
        assert case is not None
        assert case['id'] == 'test_case_1'

    def test_get_test_case_not_found(self, parser):
        case = parser.get_test_case_by_id('nonexistent')
        assert case is None

    def test_get_test_cases_by_tag(self, parser, temp_yaml_file):
        parser.parse_file(temp_yaml_file)
        cases = parser.get_test_cases_by_tag('smoke')
        assert len(cases) >= 1

    def test_get_all_test_cases(self, parser, temp_yaml_file):
        parser.parse_file(temp_yaml_file)
        all_cases = parser.get_all_test_cases()
        assert len(all_cases) == 2

    def test_clear(self, parser, temp_yaml_file):
        parser.parse_file(temp_yaml_file)
        parser.clear()
        assert len(parser.get_all_test_cases()) == 0

    def test_single_case_yaml(self, parser):
        content = """
id: single_case
name: 单个用例
request:
  method: GET
  url: https://httpbin.org/get
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(content)
            filename = f.name

        try:
            cases = parser.parse_file(filename)
            assert len(cases) == 1
            assert cases[0]['id'] == 'single_case'
        finally:
            os.unlink(filename)

    def test_case_with_test_cases_key(self, parser):
        content = """
test_cases:
  - id: nested_case_1
    name: 嵌套用例1
    request:
      method: GET
      url: https://httpbin.org/get
  - id: nested_case_2
    name: 嵌套用例2
    request:
      method: POST
      url: https://httpbin.org/post
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(content)
            filename = f.name

        try:
            cases = parser.parse_file(filename)
            assert len(cases) == 2
        finally:
            os.unlink(filename)

    def test_default_values(self, parser):
        content = """
- id: minimal_case
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(content)
            filename = f.name

        try:
            cases = parser.parse_file(filename)
            assert len(cases) == 1
            case = cases[0]
            assert case['enabled'] is True
            assert case['tags'] == []
            assert case['timeout'] == 30
            assert case['request']['method'] == 'GET'
        finally:
            os.unlink(filename)
