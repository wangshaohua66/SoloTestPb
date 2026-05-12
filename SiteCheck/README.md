# 网站健康检测工具

一个用于自动化检测网站可用性的工具，定期检测网站状态并在异常时发送告警通知。

## 功能特性

1. **HTTP/HTTPS协议检测**：记录响应时间和状态码
2. **多站点配置**：支持配置多个检测站点，按优先级排序
3. **检测频率配置**：可设置检测间隔
4. **SSL证书检测**：SSL证书有效期检测和过期提醒
5. **告警通知**：异常时支持邮件和Webhook两种告警方式
6. **统计报告**：生成网站可用性统计报告，包含响应时间趋势图

## 技术栈

- 编程语言：Python 3
- HTTP库：requests
- 调度：APScheduler
- 图表：matplotlib
- 测试框架：pytest + Allure

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `config.yaml.example` 为 `config.yaml` 并修改配置：

```yaml
sites:
  - name: 示例网站
    url: https://example.com
    priority: 1
    check_interval: 60

notifications:
  email:
    enabled: true
    smtp_server: smtp.example.com
    smtp_port: 587
    username: your_email@example.com
    password: your_password
    recipients:
      - admin@example.com

  webhook:
    enabled: true
    url: https://webhook.example.com/alert
    method: POST

ssl:
  check_enabled: true
  alert_days_before_expiry: 30

report:
  generate_interval: 86400
  output_dir: ./reports
```

## 运行

```bash
python main.py
```

## 测试

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## 代码规范

遵循PEP8代码规范。
