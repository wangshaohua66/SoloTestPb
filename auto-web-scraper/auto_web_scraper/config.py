"""
配置管理模块
负责加载和管理采集配置
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import yaml
import json


@dataclass
class SelectorConfig:
    """
    选择器配置类
    用于定义数据提取规则
    """
    name: str
    selector: str
    selector_type: str = "css"
    attribute: Optional[str] = None
    is_list: bool = False
    default_value: Any = None


@dataclass
class LoginConfig:
    """
    登录配置类
    用于配置需要认证的页面采集
    """
    login_url: str
    username: str
    password: str
    username_field: str = "username"
    password_field: str = "password"
    submit_field: Optional[str] = None
    extra_fields: Dict[str, str] = field(default_factory=dict)
    success_indicator: str = ""


@dataclass
class PaginationConfig:
    """
    分页配置类
    用于配置自动分页采集
    """
    enabled: bool = False
    selector: str = ""
    selector_type: str = "css"
    max_pages: int = 10
    next_page_pattern: str = ""
    page_param_name: str = "page"
    start_page: int = 1


@dataclass
class RequestConfig:
    """
    请求配置类
    用于配置HTTP请求参数
    """
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    allow_redirects: bool = True


@dataclass
class RateLimitConfig:
    """
    速率限制配置类
    用于配置请求间隔避免封禁
    """
    min_delay: float = 1.0
    max_delay: float = 3.0
    random_delay: bool = True
    concurrency: int = 1


@dataclass
class ProxyConfig:
    """
    代理配置类
    用于配置代理IP轮换
    """
    enabled: bool = False
    proxies: List[str] = field(default_factory=list)
    rotation_strategy: str = "round_robin"
    test_url: str = "https://httpbin.org/ip"
    test_timeout: int = 5


@dataclass
class ExportConfig:
    """
    导出配置类
    用于配置数据导出格式
    """
    formats: List[str] = field(default_factory=lambda: ["json"])
    output_dir: str = "./output"
    filename_prefix: str = "scraped_data"
    encoding: str = "utf-8"


@dataclass
class ScraperConfig:
    """
    采集器总配置类
    整合所有配置项
    """
    name: str = "default"
    start_urls: List[str] = field(default_factory=list)
    selectors: List[SelectorConfig] = field(default_factory=list)
    login: Optional[LoginConfig] = None
    pagination: PaginationConfig = field(default_factory=PaginationConfig)
    request: RequestConfig = field(default_factory=RequestConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    retry_times: int = 3
    retry_delay: float = 2.0


class ConfigLoader:
    """
    配置加载器
    支持从YAML或JSON文件加载配置
    """

    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> ScraperConfig:
        """
        从字典创建配置对象

        Args:
            config_dict: 配置字典

        Returns:
            ScraperConfig配置对象
        """
        selectors = [
            SelectorConfig(**sel)
            for sel in config_dict.get("selectors", [])
        ]

        login_config = None
        if "login" in config_dict:
            login_config = LoginConfig(**config_dict["login"])

        pagination_config = PaginationConfig(
            **config_dict.get("pagination", {})
        )
        request_config = RequestConfig(**config_dict.get("request", {}))
        rate_limit_config = RateLimitConfig(
            **config_dict.get("rate_limit", {})
        )
        proxy_config = ProxyConfig(**config_dict.get("proxy", {}))
        export_config = ExportConfig(**config_dict.get("export", {}))

        return ScraperConfig(
            name=config_dict.get("name", "default"),
            start_urls=config_dict.get("start_urls", []),
            selectors=selectors,
            login=login_config,
            pagination=pagination_config,
            request=request_config,
            rate_limit=rate_limit_config,
            proxy=proxy_config,
            export=export_config,
            retry_times=config_dict.get("retry_times", 3),
            retry_delay=config_dict.get("retry_delay", 2.0),
        )

    @staticmethod
    def from_yaml(file_path: str) -> ScraperConfig:
        """
        从YAML文件加载配置

        Args:
            file_path: YAML文件路径

        Returns:
            ScraperConfig配置对象
        """
        with open(file_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return ConfigLoader.from_dict(config_dict)

    @staticmethod
    def from_json(file_path: str) -> ScraperConfig:
        """
        从JSON文件加载配置

        Args:
            file_path: JSON文件路径

        Returns:
            ScraperConfig配置对象
        """
        with open(file_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        return ConfigLoader.from_dict(config_dict)
