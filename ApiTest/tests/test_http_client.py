import pytest
import json
from unittest.mock import Mock, patch
from core.http_client import HttpClient


class TestHttpClient:
    """HTTP客户端单元测试"""

    @pytest.fixture
    def client(self):
        return HttpClient()

    def test_initialization_default(self):
        """测试默认初始化"""
        client = HttpClient()
        assert client.base_url == ''
        assert client.timeout == 30
        assert client.last_response is None
        assert client.last_request_time == 0

    def test_initialization_with_params(self):
        """测试带参数初始化"""
        client = HttpClient(base_url='https://example.com', timeout=60)
        assert client.base_url == 'https://example.com'
        assert client.timeout == 60

    def test_set_base_url(self, client):
        """测试设置基础URL"""
        client.set_base_url('https://api.example.com')
        assert client.base_url == 'https://api.example.com'

    def test_set_timeout(self, client):
        """测试设置超时"""
        client.set_timeout(10)
        assert client.timeout == 10

    def test_set_default_headers(self, client):
        """测试设置默认请求头"""
        headers = {'User-Agent': 'TestAgent', 'Content-Type': 'application/json'}
        client.set_default_headers(headers)
        assert 'User-Agent' in client.session.headers

    def test_build_url_with_base(self, client):
        """测试带base_url构建URL"""
        client.set_base_url('https://example.com')
        url = client._build_url('/api/test')
        assert url == 'https://example.com/api/test'

    def test_build_url_without_base(self, client):
        """测试不带base_url构建URL"""
        url = client._build_url('https://example.com/api/test')
        assert url == 'https://example.com/api/test'

    def test_build_url_with_override_base(self, client):
        """测试覆盖基础URL"""
        client.set_base_url('https://default.com')
        url = client._build_url('/api/test', 'https://override.com')
        assert url == 'https://override.com/api/test'

    def test_get_request_success(self, client):
        """测试GET请求成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_response.text = json.dumps({'success': True})
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.get('https://example.com/api/test')
            assert result['success'] is True
            assert result['response']['status_code'] == 200

    def test_post_request_with_json(self, client):
        """测试POST请求带JSON"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 1, 'name': 'test'}
        mock_response.text = json.dumps({'id': 1, 'name': 'test'})
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.post('https://example.com/api/test', json={'name': 'test'})
            assert result['success'] is True
            assert result['response']['status_code'] == 201

    def test_put_request(self, client):
        """测试PUT请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'updated': True}
        mock_response.text = json.dumps({'updated': True})
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.put('https://example.com/api/test/1')
            assert result['success'] is True

    def test_delete_request(self, client):
        """测试DELETE请求"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_response.text = ''
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.delete('https://example.com/api/test/1')
            assert result['success'] is True

    def test_patch_request(self, client):
        """测试PATCH请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'patched': True}
        mock_response.text = json.dumps({'patched': True})
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.patch('https://example.com/api/test/1')
            assert result['success'] is True

    def test_request_with_params(self, client):
        """测试带参数的请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_response.text = json.dumps({'data': 'test'})
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.request('GET', 'https://example.com/api', params={'key': 'value'})
            assert result['success'] is True

    def test_request_with_headers(self, client):
        """测试带请求头的请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.text = '{}'
        mock_response.headers = {}
        mock_response.cookies = {}

        with patch.object(client.session, 'request', return_value=mock_response):
            result = client.request('GET', 'https://example.com/api', headers={'X-Test': 'value'})
            assert result['success'] is True

    def test_request_failure(self, client):
        """测试请求失败"""
        from requests.exceptions import RequestException

        with patch.object(client.session, 'request', side_effect=RequestException('Connection error')):
            result = client.request('GET', 'https://example.com/api')
            assert result['success'] is False
            assert 'error' in result

    def test_parse_response_body_json(self, client):
        """测试解析JSON响应体"""
        mock_response = Mock()
        mock_response.json.return_value = {'key': 'value'}
        result = client._parse_response_body(mock_response)
        assert result == {'key': 'value'}

    def test_parse_response_body_text(self, client):
        """测试解析文本响应体"""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError('No JSON')
        mock_response.text = 'Plain text'
        result = client._parse_response_body(mock_response)
        assert result == 'Plain text'

    def test_context_manager(self):
        """测试上下文管理器"""
        with HttpClient() as client:
            assert client is not None
        assert client.session is not None

    def test_close(self, client):
        """测试关闭会话"""
        client.close()
