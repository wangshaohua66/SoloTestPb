# 服务器资源监控工具 - 系统设计文档

## 1. 项目概述

### 1.1 项目目标
开发一个功能完整的服务器资源监控工具，能够实时监控CPU、内存、磁盘、网络等系统资源，支持告警通知和报告生成功能。

### 1.2 功能清单
- ✅ 实时CPU监控（支持多核）
- ✅ 实时内存监控（物理+虚拟）
- ✅ 磁盘使用率和IO监控
- ✅ 网络流量监控
- ✅ 阈值告警和邮件通知
- ✅ 历史趋势报告生成
- ✅ 可配置的采集间隔（最小1秒）

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    命令行入口 (main.py)                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   主监控器 (monitor.py)                   │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Config      │  │  DataStore   │  │ AlertManager │  │
│  │  配置管理    │  │  数据存储    │  │  告警管理    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼───────┐ ┌──────▼───────┐
│   CPU监控     │ │  内存监控    │ │  磁盘监控    │
│ cpu_monitor   │ │memory_monitor│ │disk_monitor  │
└───────────────┘ └───────────────┘ └───────────────┘
                                                          
┌─────────────────────────────────────────────────────────┐
├───────────────┐ ┌───────────────┐ ┌────────────────────┐│
│  网络监控     │ │  邮件通知     │ │  报告生成          ││
│network_monitor│ │email_notifier │ │report_generator    ││
└───────────────┘ └───────────────┘ └────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

#### 配置管理模块 (config.py)
- 加载和保存配置文件
- 提供配置项的访问接口
- 支持默认配置和用户配置的合并

#### 数据存储模块 (core/data_store.py)
- 统一管理所有监控数据
- 实现数据保留机制
- 提供数据查询接口

#### CPU监控模块 (core/cpu_monitor.py)
- 采集CPU使用率（整体+各核心）
- 维护历史数据
- 提供CPU信息查询

#### 内存监控模块 (core/memory_monitor.py)
- 采集物理内存使用率
- 采集虚拟内存（交换空间）使用率
- 维护历史数据

#### 磁盘监控模块 (core/disk_monitor.py)
- 采集各分区磁盘使用率
- 采集磁盘IO速度（读写）
- 维护历史数据

#### 网络监控模块 (core/network_monitor.py)
- 采集各网卡网络流量
- 计算上传/下载速度
- 维护历史数据

#### 告警管理模块 (notifier/alert_manager.py)
- 检查各项指标是否超过阈值
- 管理告警历史
- 实现告警冷却机制

#### 邮件通知模块 (notifier/email_notifier.py)
- 发送告警邮件
- 支持SMTP/TLS配置
- 测试邮件服务器连接

#### 报告生成模块 (reporter/report_generator.py)
- 生成历史趋势图表
- 生成HTML格式报告
- 支持定时报告生成

## 3. 数据结构设计

### 3.1 CPU数据结构
```python
{
    "timestamp": float,       # 时间戳
    "overall": float,         # 整体CPU使用率(%)
    "per_cpu": List[float],   # 各核心使用率(%)
    "cpu_count": int,         # 逻辑CPU数量
    "cpu_count_physical": int,# 物理CPU数量
    "avg": float,             # 平均使用率
    "max": float,             # 最大使用率
    "min": float              # 最小使用率
}
```

### 3.2 内存数据结构
```python
{
    "timestamp": float,       # 时间戳
    "virtual": {
        "total": int,         # 总内存
        "available": int,     # 可用内存
        "used": int,          # 已用内存
        "free": int,          # 空闲内存
        "percent": float,     # 使用率(%)
        "used_gb": float,     # 已用(GB)
        "total_gb": float,    # 总计(GB)
        "available_gb": float # 可用(GB)
    },
    "swap": {
        "total": int,         # 总交换空间
        "used": int,          # 已用交换空间
        "free": int,          # 空闲交换空间
        "percent": float,     # 使用率(%)
        "used_gb": float,     # 已用(GB)
        "total_gb": float     # 总计(GB)
    }
}
```

### 3.3 磁盘数据结构
```python
{
    "timestamp": float,       # 时间戳
    "usage": {
        "device": {           # 设备名
            "mountpoint": str,    # 挂载点
            "fstype": str,        # 文件系统类型
            "total": int,         # 总容量
            "used": int,          # 已用
            "free": int,          # 空闲
            "percent": float,     # 使用率(%)
            "used_gb": float,     # 已用(GB)
            "total_gb": float,    # 总计(GB)
            "free_gb": float      # 空闲(GB)
        }
    },
    "io": {
        "device": {           # 设备名
            "read_speed": float,     # 读速度(bytes/s)
            "write_speed": float,    # 写速度(bytes/s)
            "read_speed_mb": float,  # 读速度(MB/s)
            "write_speed_mb": float, # 写速度(MB/s)
            "total_read_bytes": int, # 总读字节
            "total_write_bytes": int # 总写字节
        }
    },
    "max_percent": float      # 最大分区使用率(%)
}
```

### 3.4 网络数据结构
```python
{
    "timestamp": float,       # 时间戳
    "io": {
        "interfaces": {
            "nic_name": {      # 网卡名
                "upload_speed": float,     # 上传速度(bytes/s)
                "download_speed": float,   # 下载速度(bytes/s)
                "upload_speed_mb": float,  # 上传速度(MB/s)
                "download_speed_mb": float, # 下载速度(MB/s)
                "total_upload": int,       # 总上传字节
                "total_download": int,     # 总下载字节
                "packets_sent": int,       # 发送数据包数
                "packets_recv": int        # 接收数据包数
            }
        },
        "total_upload_speed": float,      # 总上传速度(bytes/s)
        "total_download_speed": float,    # 总下载速度(bytes/s)
        "total_upload_speed_mb": float,   # 总上传速度(MB/s)
        "total_download_speed_mb": float  # 总下载速度(MB/s)
    }
}
```

### 3.5 告警数据结构
```python
{
    "type": str,              # 告警类型: cpu/memory/disk/network
    "level": str,             # 告警级别: normal/warning
    "threshold": float,       # 阈值
    "current": float,         # 当前值
    "message": str,           # 告警消息
    "timestamp": float        # 时间戳
}
```

## 4. 核心算法设计

### 4.1 IO速度计算算法
```python
# 原理：两次采样之间的数据量差除以时间差
speed = (current_counter - last_counter) / (current_time - last_time)
```

### 4.2 告警冷却算法
```python
# 原理：记录每次告警的时间，相同类型告警在冷却期内不重复发送
if current_time - last_alert_time >= cooldown_period:
    send_alert()
    last_alert_time = current_time
```

### 4.3 数据清理算法
```python
# 原理：定期清理超过保留时间的数据
cutoff_time = current_time - retention_period
data = [item for item in data if item.timestamp >= cutoff_time]
```

## 5. 配置设计

### 5.1 完整配置结构
```json
{
    "interval": 1,                    // 采集间隔（秒）
    "cpu_threshold": 80.0,           // CPU告警阈值
    "memory_threshold": 80.0,        // 内存告警阈值
    "disk_threshold": 85.0,          // 磁盘告警阈值
    "network_threshold": 100.0,      // 网络告警阈值
    "smtp": {
        "enabled": false,             // 邮件通知开关
        "server": "smtp.example.com", // SMTP服务器
        "port": 587,                  // SMTP端口
        "username": "user@example.com", // SMTP用户名
        "password": "password",        // SMTP密码
        "from_email": "monitor@example.com", // 发件人
        "to_emails": ["admin@example.com"], // 收件人列表
        "use_tls": true               // 是否使用TLS
    },
    "report": {
        "enabled": true,              // 报告功能开关
        "interval": 3600,             // 报告生成间隔
        "path": "./reports",          // 报告保存路径
        "format": "html"              // 报告格式
    },
    "data_retention": 86400          // 数据保留时间
}
```

## 6. 接口设计

### 6.1 Config类接口
```python
get(key: str, default: Any = None) -> Any
set(key: str, value: Any) -> None
save() -> None
interval -> int
cpu_threshold -> float
memory_threshold -> float
disk_threshold -> float
network_threshold -> float
```

### 6.2 DataStore类接口
```python
add_cpu_data(data: Dict) -> None
add_memory_data(data: Dict) -> None
add_disk_data(data: Dict) -> None
add_network_data(data: Dict) -> None
get_cpu_data(limit: int = None) -> List[Dict]
get_memory_data(limit: int = None) -> List[Dict]
get_disk_data(limit: int = None) -> List[Dict]
get_network_data(limit: int = None) -> List[Dict]
get_all_data() -> Dict[str, List]
clear_all() -> None
```

### 6.3 AlertManager类接口
```python
check_cpu_alert(cpu_data: Dict) -> Dict
check_memory_alert(memory_data: Dict) -> Dict
check_disk_alert(disk_data: Dict) -> Dict
check_network_alert(network_data: Dict) -> Dict
check_all_alerts(data: Dict) -> List[Dict]
get_alert_history(limit: int = None) -> List[Dict]
clear_alert_history() -> None
set_cooldown_period(seconds: int) -> None
```

### 6.4 EmailNotifier类接口
```python
is_enabled() -> bool
send_alert(alerts: List[Dict]) -> bool
send_report(report_path: str) -> bool
test_connection() -> bool
```

### 6.5 ReportGenerator类接口
```python
generate_report(data_store: DataStore) -> str
```

## 7. 测试策略

### 7.1 单元测试覆盖范围
- ✅ 配置管理模块：配置加载、保存、合并
- ✅ 数据存储模块：数据增删查、数据保留
- ✅ 告警管理模块：阈值检查、冷却机制
- ✅ 邮件通知模块：连接测试、发送逻辑
- ✅ 监控模块：数据采集功能（需实际环境）

### 7.2 集成测试
- 主监控流程测试
- 告警-通知链路测试
- 数据采集-存储-报告链路测试

### 7.3 性能测试
- 最小间隔（1秒）下的CPU占用
- 长时间运行的内存泄漏检查
- 大数据量下的报告生成速度

## 8. 部署说明

### 8.1 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发
python main.py

# 运行测试
pytest
pytest --cov=monitor
```

### 8.2 生产环境
```bash
# Linux系统可配置systemd服务
# 或使用nohup后台运行
nohup python main.py > monitor.log 2>&1 &
```

## 9. 安全考虑

### 9.1 敏感信息保护
- 邮件密码存储在配置文件中，建议配置文件权限设为仅所有者可读
- 生产环境建议使用环境变量存储敏感信息

### 9.2 邮件服务器安全
- 建议使用专用的告警邮箱
- 开启SMTP认证和TLS加密
- 避免使用个人邮箱密码

## 10. 扩展方向

### 10.1 功能扩展
- Web界面展示
- 数据库持久化存储
- 多服务器集中监控
- 更多告警方式（短信、微信等）

### 10.2 性能优化
- 异步数据采集
- 数据压缩存储
- 增量报告生成

### 10.3 兼容性扩展
- 容器化部署（Docker）
- 云平台适配
- 更多操作系统支持
