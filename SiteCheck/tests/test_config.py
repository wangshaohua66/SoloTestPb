"""
配置管理模块测试
"""

import pytest
import os
import tempfile
import yaml
from src.config import Config


class TestConfig:
    """
    Config类测试
    """

    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        config_data = {
            'sites': [
                {
                    'name': '测试站点1',
                    'url': 'https://example1.com',
                    'priority': 1,
                    'check_interval': 60
                },
                {
                    'name': '测试站点2',
                    'url': 'https://example2.com',
                    'priority': 2,
                    'check_interval': 120
                }
            ],
            'notifications': {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.example.com'
                }
            },
            'ssl': {
                'check_enabled': True,
                'alert_days_before_expiry': 30
            },
            'report': {
                'generate_interval': 86400,
                'output_dir': './reports'
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/test.log'
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
            temp_path = f.name

        yield temp_path

        os.unlink(temp_path)

    def test_load_config_success(self, temp_config_file):
        """测试成功加载配置文件"""
        config = Config(temp_config_file)
        assert config is not None

    def test_load_config_file_not_found(self):
        """测试配置文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            Config('non_existent_config.yaml')

    def test_get_sites(self, temp_config_file):
        """测试获取站点列表"""
        config = Config(temp_config_file)
        sites = config.get_sites()

        assert len(sites) == 2
        assert sites[0]['priority'] == 1
        assert sites[1]['priority'] == 2

    def test_get_notifications(self, temp_config_file):
        """测试获取通知配置"""
        config = Config(temp_config_file)
        notifications = config.get_notifications()
        assert 'email' in notifications

    def test_get_ssl_config(self, temp_config_file):
        """测试获取SSL配置"""
        config = Config(temp_config_file)
        ssl_config = config.get_ssl_config()
        assert ssl_config['check_enabled'] is True
        assert ssl_config['alert_days_before_expiry'] == 30

    def test_get_report_config(self, temp_config_file):
        """测试获取报告配置"""
        config = Config(temp_config_file)
        report_config = config.get_report_config()
        assert report_config['generate_interval'] == 86400
        assert report_config['output_dir'] == './reports'

    def test_empty_sites(self, temp_config_file):
        """测试空站点列表"""
        import yaml
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_data['sites'] = []
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        config = Config(temp_config_file)
        sites = config.get_sites()
        assert len(sites) == 0

    def test_get_empty_notifications(self, temp_config_file):
        """测试获取空通知配置"""
        import yaml
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_data['notifications'] = {}
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        config = Config(temp_config_file)
        notifications = config.get_notifications()
        assert notifications == {}

    def test_get_empty_ssl_config(self, temp_config_file):
        """测试获取空SSL配置"""
        import yaml
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_data['ssl'] = {}
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        config = Config(temp_config_file)
        ssl_config = config.get_ssl_config()
        assert ssl_config == {}

    def test_get_empty_report_config(self, temp_config_file):
        """测试获取空报告配置"""
        import yaml
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_data['report'] = {}
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        config = Config(temp_config_file)
        report_config = config.get_report_config()
        assert report_config == {}

    def test_get_empty_logging_config(self, temp_config_file):
        """测试获取空日志配置"""
        import yaml
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_data['logging'] = {}
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        config = Config(temp_config_file)
        logging_config = config.get_logging_config()
        assert logging_config == {}

    def test_setup_logging(self, temp_config_file):
        """测试日志系统设置"""
        from src.config import setup_logging
        import logging
        
        config = Config(temp_config_file)
        
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers.copy()
        
        setup_logging(config)
        
        assert len(root_logger.handlers) >= 2

    def test_setup_logging_with_empty_config(self, temp_config_file):
        """测试使用空配置设置日志系统"""
        from src.config import setup_logging
        import yaml
        import logging
        
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        config_data['logging'] = {}
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        config = Config(temp_config_file)
        setup_logging(config)
        
        assert True
