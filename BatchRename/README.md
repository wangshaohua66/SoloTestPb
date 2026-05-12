# 批量文件重命名工具

## 功能概述

一个功能强大的批量文件重命名工具，支持多种命名规则和模式，帮助用户快速整理大量文件。

## 功能特性

1. **按序号批量重命名** - 如 file_001、file_002、file_003
2. **按日期时间戳重命名** - 使用当前日期时间或指定日期格式
3. **查找替换** - 查找并替换文件名中的特定字符
4. **添加前缀/后缀** - 为文件名添加前缀或后缀
5. **正则表达式匹配替换** - 支持复杂的正则匹配和替换
6. **预览功能** - 执行前显示重命名结果
7. **撤销功能** - 可恢复最近一次批量重命名操作

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 按序号重命名

```bash
python -m batch_rename /path/to/files --mode sequence --name "photo" --start 1 --padding 3
# 结果: photo_001.jpg, photo_002.jpg, ...
```

### 2. 按日期时间戳重命名

```bash
python -m batch_rename /path/to/files --mode timestamp
# 使用当前时间戳

python -m batch_rename /path/to/files --mode timestamp --format "%Y%m%d"
# 使用自定义日期格式
```

### 3. 查找替换

```bash
python -m batch_rename /path/to/files --mode replace --find "old" --replace "new"
```

### 4. 添加前缀/后缀

```bash
# 添加前缀
python -m batch_rename /path/to/files --mode prefix --prefix "2024_"

# 添加后缀
python -m batch_rename /path/to/files --mode suffix --suffix "_backup"
```

### 5. 正则表达式匹配替换

```bash
python -m batch_rename /path/to/files --mode regex --pattern "IMG_(\d+)" --replace "Photo_\1"
```

### 6. 预览模式（不实际执行）

```bash
python -m batch_rename /path/to/files --mode sequence --name "file" --preview
```

### 7. 撤销上一次操作

```bash
python -m batch_rename /path/to/files --undo
```

### 8. 强制执行模式（自动化脚本）

```bash
# 跳过交互式确认，直接执行重命名
python -m batch_rename /path/to/files --mode sequence --name "file" --force
```

**注意**：
- 默认情况下，非预览模式会要求用户交互式确认后才执行重命名
- 使用 `--force` 参数可以跳过确认，适合自动化脚本和批处理场景
- 建议先使用 `--preview` 预览结果，确认无误后再使用 `--force`

## 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| directory | 文件所在目录 | 是 |
| --mode | 重命名模式 (sequence/timestamp/replace/prefix/suffix/regex) | 否(与--undo互斥) |
| --name | 序列模式的基础名称 | 序列模式 |
| --start | 起始序号(默认:1) | 否 |
| --padding | 序号填充位数(默认:3) | 否 |
| --format | 日期格式(默认:%Y%m%d_%H%M%S) | 否 |
| --find | 查找的字符串 | 替换模式 |
| --replace | 替换的字符串 | 替换模式 |
| --prefix | 添加的前缀 | 前缀模式 |
| --suffix | 添加的后缀 | 后缀模式 |
| --pattern | 正则表达式匹配模式 | 正则模式 |
| --preview | 仅预览，不执行 | 否 |
| --force | 强制执行，跳过交互式确认(用于自动化脚本) | 否 |
| --undo | 撤销上次批量重命名 | 否 |

## 运行测试

```bash
pytest
```

## 生成Allure报告

```bash
pytest
allure serve allure_results
```

## 测试覆盖率

运行测试后将自动显示覆盖率报告，目标覆盖率不低于80%。

## 系统设计

详细的系统设计文档请参考 `docs/system_design.md`
