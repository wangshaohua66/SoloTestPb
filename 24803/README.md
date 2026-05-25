# 分布式任务调度系统

基于 Go + Gin 构建的分布式任务调度系统，支持定时任务管理、执行、监控等功能。

## 功能特性

- **任务管理**：任务的动态创建、更新、删除
- **Cron 表达式**：支持标准的 6 字段 Cron 表达式（含秒级）
- **任务类型**：支持 HTTP 请求、Shell 脚本、数据库操作
- **任务依赖**：支持任务间依赖关系，A 任务成功后触发 B 任务
- **重试机制**：任务失败自动重试，最多 3 次
- **限流熔断**：内置限流和熔断器，防止任务堆积
- **Webhook 回调**：任务执行完成后回调通知
- **标签分类**：支持按标签分类和搜索任务
- **执行日志**：详细的任务执行日志，包含耗时、返回结果
- **审计日志**：所有操作均记录审计日志

## 技术栈

- **Web 框架**：Gin
- **配置管理**：Viper
- **日志**：Zap + Lumberjack
- **数据校验**：Validator
- **ORM**：GORM
- **数据库**：SQLite（默认）/ MySQL
- **Cron 解析**：robfig/cron
- **限流**：golang.org/x/time/rate
- **熔断**：sony/gobreaker

## 项目结构

```
.
├── cmd/
│   └── server/          # 主程序入口
├── internal/
│   ├── config/          # 配置管理
│   ├── handlers/        # API 处理器
│   ├── middleware/      # 中间件
│   ├── models/          # 数据模型
│   └── services/        # 业务逻辑
├── pkg/
│   ├── errors/          # 错误定义
│   ├── utils/           # 工具函数
│   └── validator/       # 自定义验证器
├── config.yaml          # 配置文件
├── go.mod
└── README.md
```

## 快速开始

### 编译

```bash
go build -o bin/task-scheduler ./cmd/server
```

### 运行

```bash
./bin/task-scheduler
```

或直接运行：

```bash
go run ./cmd/server
```

### 配置

修改 `config.yaml` 文件：

```yaml
server:
  port: 8080
  mode: debug

database:
  driver: sqlite
  dsn: task_scheduler.db

log:
  level: info
  filename: logs/task-scheduler.log

scheduler:
  max_concurrent_tasks: 10
  default_timeout: 300
  max_retry_count: 3
```

## API 接口

所有接口需要在 Header 中携带 `Authorization` 字段（当前为简单验证，非空即可）。

### 任务管理

#### 创建任务

```
POST /api/v1/tasks
Content-Type: application/json

{
  "name": "测试任务",
  "description": "任务描述",
  "type": "http",
  "cron_expression": "*/5 * * * * *",
  "params": "{\"url\":\"https://example.com\",\"method\":\"GET\"}",
  "timeout": 300,
  "max_retry_count": 3,
  "retry_interval": 60,
  "tags": [{"name": "测试"}],
  "dependencies": [],
  "webhook_url": "https://example.com/webhook",
  "circuit_breaker": true
}
```

#### 任务类型参数说明

**HTTP 任务** (`type: http`):
```json
{
  "url": "https://example.com/api",
  "method": "POST",
  "headers": {"Content-Type": "application/json"},
  "body": {"key": "value"}
}
```

**Shell 任务** (`type: shell`):
```json
{
  "command": "echo Hello World",
  "args": [],
  "shell": "/bin/bash"
}
```

**数据库任务** (`type: database`):
```json
{
  "dsn": "user:password@tcp(localhost:3306)/dbname",
  "driver": "mysql",
  "sql": "SELECT * FROM users",
  "args": [],
  "query_type": "query"
}
```

#### 更新任务

```
PUT /api/v1/tasks/:id
```

#### 删除任务

```
DELETE /api/v1/tasks/:id
```

#### 获取任务详情

```
GET /api/v1/tasks/:id
```

#### 获取任务列表

```
GET /api/v1/tasks?page=1&page_size=10&keyword=测试&status=pending&tag_ids=xxx
```

#### 更新任务状态

```
PATCH /api/v1/tasks/:id/status
Content-Type: application/json

{
  "status": "paused"
}
```

状态值：`pending`, `running`, `paused`, `cancelled`

#### 手动触发任务

```
POST /api/v1/tasks/:id/trigger
```

#### 获取任务执行日志

```
GET /api/v1/tasks/:id/logs?page=1&page_size=10
```

### Cron 验证

```
POST /api/v1/cron/validate
Content-Type: application/json

{
  "expression": "*/5 * * * * *"
}
```

### 标签管理

#### 创建标签

```
POST /api/v1/tags
Content-Type: application/json

{
  "name": "重要",
  "color": "#ef4444"
}
```

#### 获取标签列表

```
GET /api/v1/tags
```

#### 更新标签

```
PUT /api/v1/tags/:id
```

#### 删除标签

```
DELETE /api/v1/tags/:id
```

## Cron 表达式

支持 6 字段格式（含秒）：

```
┌───────────── 秒 (0 - 59)
│ ┌───────────── 分钟 (0 - 59)
│ │ ┌───────────── 小时 (0 - 23)
│ │ │ ┌───────────── 日 (1 - 31)
│ │ │ │ ┌───────────── 月 (1 - 12)
│ │ │ │ │ ┌───────────── 星期 (0 - 6) (星期日=0)
│ │ │ │ │ │
│ │ │ │ │ │
* * * * * *
```

示例：
- `*/5 * * * * *` - 每 5 秒执行
- `0 * * * * *` - 每分钟执行
- `0 0 2 * * *` - 每天凌晨 2 点执行
- `0 0 0 1 * *` - 每月 1 号凌晨执行

## 任务依赖

通过 `dependencies` 字段指定依赖任务 ID 数组，依赖任务执行成功后才会触发当前任务。

## 限流熔断

- **限流**：通过 `max_concurrent_tasks` 配置最大并发任务数
- **熔断**：设置 `circuit_breaker: true` 开启熔断器，连续失败超过阈值后自动熔断

## Webhook 回调

任务执行完成后会向 `webhook_url` 发送 POST 请求，包含以下数据：

```json
{
  "task_id": "任务ID",
  "task_name": "任务名称",
  "status": "success/failed",
  "start_time": "开始时间",
  "end_time": "结束时间",
  "duration_ms": 1234,
  "result": "执行结果",
  "error": "错误信息"
}
```
