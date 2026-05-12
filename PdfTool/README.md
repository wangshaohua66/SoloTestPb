# PDF文档处理工具

一个用于自动化处理PDF文档的工具，支持合并、拆分、提取文本和图片等操作，帮助办公人员提高文档处理效率。

## 功能特性

- ✅ **PDF合并**：将多个PDF文件合并为一个文件
- ✅ **PDF拆分**：按页码范围拆分PDF文件
- ✅ **文本提取**：从PDF中提取文本内容，保存为TXT文件
- ✅ **图片提取**：从PDF中提取内嵌图片，保存为原始格式
- ✅ **页码添加**：给PDF添加页码，支持自定义位置和样式
- ✅ **页眉页脚**：给PDF添加自定义页眉页脚
- ✅ **加密解密**：支持PDF加密和解密，可设置密码和权限

## 技术栈

- **编程语言**：Python 3.8+
- **PDF处理**：PyPDF2、pdfplumber
- **图像提取**：pdf2image、Pillow
- **命令行**：Click
- **测试框架**：pytest + Allure
- **代码规范**：PEP8

## 安装说明

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆项目到本地
```bash
git clone <repository-url>
cd PdfTool
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

### 安装Poppler（PDF转图片功能必需）

**重要说明**：使用`--convert`选项将PDF页面转换为图片时，需要安装Poppler工具。如果只是提取PDF内嵌图片，则不需要安装Poppler。

**Windows安装：**
1. 访问 [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/) 下载最新版本
2. 解压到任意目录，例如 `C:\poppler`
3. 将解压后的 `bin` 目录添加到系统环境变量 PATH 中
4. 重启命令行窗口，执行 `pdfinfo -v` 验证安装

**Linux (Ubuntu/Debian)安装：**
```bash
sudo apt-get install poppler-utils
```

**macOS安装：**
```bash
brew install poppler
```

**验证安装：**
```bash
pdfinfo -v
```

## 使用方法

### 命令行使用

#### 1. PDF合并
```bash
python main.py merge --inputs file1.pdf file2.pdf file3.pdf --output merged.pdf
```

#### 2. PDF拆分
```bash
# 按页码范围拆分
python main.py split --input input.pdf --output output.pdf --start 1 --end 5
```

#### 3. 文本提取
```bash
# 提取所有文本并保存到文件
python main.py extract-text --input input.pdf --output output.txt

# 只提取指定页码范围的文本
python main.py extract-text --input input.pdf --start 1 --end 10
```

#### 4. 图片提取
```bash
# 提取PDF内嵌图片
python main.py extract-images --input input.pdf --output-dir ./images

# 将PDF页面转换为图片
python main.py extract-images --input input.pdf --output-dir ./images --convert --dpi 200
```

#### 5. 添加页码
```bash
python main.py add-page-numbers --input input.pdf --output output.pdf --position bottom_right --font-size 12
```

位置选项：
- `bottom_left`：左下角
- `bottom_center`：底部居中
- `bottom_right`：右下角（默认）
- `top_left`：左上角
- `top_center`：顶部居中
- `top_right`：右上角

#### 6. 添加页眉页脚
```bash
python main.py add-header-footer --input input.pdf --output output.pdf --header "页眉文本" --footer "页脚文本" --font-size 10
```

#### 7. PDF加密
```bash
python main.py encrypt --input input.pdf --output output.pdf --password "your_password"
```

#### 8. PDF解密
```bash
python main.py decrypt --input input.pdf --output output.pdf --password "your_password"
```

### Python API使用

也可以直接在Python代码中使用各个模块：

```python
from src.pdf_merger import PDFMerger
from src.pdf_splitter import PDFSplitter
from src.pdf_text_extractor import PDFTextExtractor

# 合并PDF
merger = PDFMerger()
merger.merge_pdfs(['file1.pdf', 'file2.pdf'], 'merged.pdf')

# 拆分PDF
splitter = PDFSplitter()
splitter.split_by_range('input.pdf', 'output.pdf', 1, 5)

# 提取文本
extractor = PDFTextExtractor()
text = extractor.extract_text('input.pdf', start_page=1, end_page=10)
print(text)
```

## 项目结构

```
PdfTool/
├── src/
│   ├── __init__.py
│   ├── pdf_merger.py        # PDF合并模块
│   ├── pdf_splitter.py       # PDF拆分模块
│   ├── pdf_text_extractor.py # 文本提取模块
│   ├── pdf_image_extractor.py # 图片提取模块
│   ├── pdf_header_footer.py  # 页眉页脚模块
│   ├── pdf_security.py       # 加密解密模块
│   └── cli.py               # 命令行接口
├── tests/                    # 单元测试目录
├── docs/                     # 文档目录
│   └── 系统设计文档.md
├── main.py                  # 程序入口
├── requirements.txt         # 依赖包列表
└── README.md               # 项目说明
```

## 测试说明

### 运行测试

```bash
# 运行所有测试（排除性能测试）
pytest -m "not performance"

# 运行所有测试（包括性能测试）
pytest

# 只运行性能测试
pytest -m performance

# 运行测试并生成Allure报告
pytest --alluredir=allure-results

# 查看Allure报告
allure serve allure-results
```

### 测试覆盖率

```bash
# 查看测试覆盖率
pytest --cov=src --cov-report=html

# 运行测试并查看覆盖率
pytest --cov=src --cov-report=term
```

项目要求测试覆盖率不低于80%。

## 性能指标

### 实际性能测试结果

**测试环境**：100页PDF文件

| 功能 | 平均处理时间 | 状态 |
|------|-----------|------|
| PDF合并 | 0.3秒 | ✅ 通过 |
| PDF拆分 | 0.2秒 | ✅ 通过 |
| 文本提取 | 0.2秒 | ✅ 通过 |
| 添加页码 | 0.2秒 | ✅ 通过 |
| 添加页眉页脚 | 0.2秒 | ✅ 通过 |
| PDF加密 | 0.2秒 | ✅ 通过 |

**性能要求**：所有功能处理100页PDF不超过30秒 ✅ 全部达标

### 内存优化

- 采用流式处理，避免一次性加载整个PDF文件到内存中
- 支持大文件处理，内存占用低

## 性能测试说明

性能测试使用pytest标记 `@pytest.mark.performance` 进行分类。测试内容包括：

1. **PDF合并性能**：合并多个100页PDF文件
2. **PDF拆分性能**：将100页PDF按范围拆分
3. **文本提取性能**：从100页PDF中提取文本
4. **页码添加性能**：给100页PDF添加页码
5. **页眉页脚添加性能**：给100页PDF添加页眉页脚
6. **PDF加密性能**：给100页PDF加密

所有性能测试均通过，处理时间远低于30秒的要求。

## 开发说明

### 代码规范

- 遵循PEP8代码规范
- 所有函数和类都有中文注释说明
- 使用类型注解提高代码可读性

### 添加新功能

1. 在`src/`目录下创建新的模块文件
2. 在模块中实现功能逻辑，添加异常处理和参数校验
3. 在`tests/`目录下创建对应的测试文件
4. 在`src/cli.py`中添加命令行接口
5. 更新文档

## 常见问题

### Q: 处理加密的PDF文件时出错？
A: 请先使用解密功能解密PDF文件，然后再进行其他操作。

### Q: 图片提取功能没有提取到图片？
A: 可能PDF中的图片不是内嵌的，可以尝试使用`--convert`选项将页面转换为图片。

### Q: 中文显示乱码？
A: 文本提取功能使用UTF-8编码保存，确保使用支持UTF-8的文本编辑器打开。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件

---

**版本**：v1.0.1
**更新日期**：2026年5月12日
