# UnitConverter - 单位换算器

一个功能强大的本地单位换算器桌面应用，支持多种单位类型和自定义单位。

## 功能特性

### 基础换算
- **长度换算**：米、千米、厘米、毫米、微米、纳米、英尺、英寸、码、英里、海里等
- **重量换算**：千克、克、毫克、吨、磅、盎司、英石等
- **温度换算**：摄氏度、华氏度、开尔文、兰金度（支持公式换算）
- **面积换算**：平方米、平方千米、公顷、平方英尺、平方英寸、英亩等
- **体积换算**：立方米、升、毫升、立方英尺、立方英寸、加仑等

### 高级换算
- **速度换算**：米/秒、千米/小时、英里/小时、节等
- **时间换算**：秒、毫秒、微秒、分钟、小时、天、周、月、年等
- **数据存储换算**：字节、千字节、兆字节、吉字节、太字节等
- **压力换算**：帕斯卡、千帕、兆帕、标准大气压、巴、托、磅力/平方英寸等
- **功率换算**：瓦特、千瓦、兆瓦、马力等

### 自定义单位
- 添加自定义单位
- 设置换算公式（支持复杂公式）
- 单位分组管理
- 单位管理（删除、修改）

### 批量换算
- 批量输入数值（每行一个）
- 批量换算到多个目标单位
- 结果导出（CSV、JSON、文本格式）
- 换算历史记录

### 计算器
- 基础计算功能
- 科学计算（三角函数、对数、幂运算等）
- 换算结果计算
- 计算历史

### 常用换算
- 收藏常用单位
- 快捷换算
- 换算历史

## 技术栈

- **Java 8**
- **JavaFX** (桌面GUI框架)
- **Maven** (构建工具)
- **Gson** (JSON序列化)
- **JUnit 4** (单元测试)

## 环境要求

- JDK 8 (必须包含 JavaFX，如 Oracle JDK 8 或 ZuluFX 8)
- Maven 3.6+

### Java 8 与 JavaFX

本项目使用 Java 8 内置的 JavaFX。以下 JDK 发行版包含 JavaFX：

- Oracle JDK 8 (推荐)
- ZuluFX 8
- BellSoft Liberica JDK 8 Full JDK

**注意**：Amazon Corretto 8 无头版不包含 JavaFX，需要使用系统 Java 插件或安装完整 JDK。

## 构建和运行

### 构建项目

#### macOS
```bash
mvn clean package -Pmacos
```

#### Windows
```bash
mvn clean package -Pwindows
```

#### Linux
```bash
mvn clean package -Plinux
```

### 运行应用

```bash
java -jar target/UnitConverter-1.0.0.jar
```

### 运行测试

```bash
mvn test -Pmacos
```

## 项目结构

```
UnitConverter/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/com/unitconverter/
│   │   │   ├── Main.java                          # 应用入口
│   │   │   ├── calculator/
│   │   │   │   └── CalculatorEngine.java          # 计算器引擎
│   │   │   ├── converter/
│   │   │   │   ├── ConversionEngine.java          # 换算引擎
│   │   │   │   └── FormulaParser.java             # 公式解析器
│   │   │   ├── manager/
│   │   │   │   ├── BatchConversionManager.java    # 批量换算管理器
│   │   │   │   └── CustomUnitManager.java         # 自定义单位管理器
│   │   │   ├── model/
│   │   │   │   ├── ConversionHistory.java         # 换算历史模型
│   │   │   │   ├── ConversionResult.java          # 换算结果模型
│   │   │   │   ├── UnitDefinition.java            # 单位定义模型
│   │   │   │   ├── UnitSystem.java                # 单位系统枚举
│   │   │   │   └── UnitType.java                  # 单位类型枚举
│   │   │   ├── persistence/
│   │   │   │   └── DataManager.java               # 数据持久化管理器
│   │   │   ├── registry/
│   │   │   │   └── UnitRegistry.java              # 单位注册表
│   │   │   └── ui/
│   │   │       └── MainController.java              # GUI控制器
│   │   └── resources/
│   │       ├── css/
│   │       │   └── style.css                        # 样式表
│   │       ├── fxml/
│   │       │   └── main.fxml                        # FXML界面
│   │       └── images/
│   │           └── icon.png                        # 应用图标
│   └── test/
│       └── java/com/unitconverter/
│           ├── BatchConversionManagerTest.java      # 批量换算测试
│           ├── ConversionEngineTest.java           # 换算引擎测试
│           ├── CustomUnitManagerTest.java              # 自定义单位测试
│           └── FormulaParserTest.java                 # 公式解析测试
```

## 核心功能说明

### 公式解析器

支持复杂的数学公式，用于温度等非线性换算：

- **运算符**：+、-、*、/、%、^
- **函数**：sqrt、cbrt、log、ln、sin、cos、tan、abs、exp、floor、ceil、round
- **常量**：e、pi
- **变量**：x (输入值)、y、a、b (默认为0)
- **隐式乘法**：2(3+4)、(2+3)(4+5)、2x

示例：
- 华氏度转摄氏度：`(x - 32) * 5 / 9`
- 摄氏度转华氏度：`x * 9 / 5 + 32`
- 摄氏度转开尔文：`x + 273.15`

### 单位系统

- **公制 (METRIC)**：米、千克、摄氏度等
- **英制 (IMPERIAL)**：英尺、磅、华氏度等
- **美制 (US_CUSTOMARY)**：美制单位
- **自定义 (CUSTOM)**：用户自定义单位

### 精度控制

- 支持设置换算结果的小数位数（0-15位）
- 支持科学计数法显示
- 支持四舍五入

### 换算链

支持多步换算，如"米→英尺→英寸：

```java
double result = ConversionEngine.convertWithChain(1.0, meter, foot, inch);
```

## 数据持久化

应用数据保存到本地文件（JSON格式）：
- 自定义单位
- 收藏的单位
- 应用设置

## 测试覆盖

- **ConversionEngineTest**：14 个测试 - 核心换算功能
- **FormulaParserTest**：18 个测试 - 公式解析器
- **BatchConversionManagerTest**：14 个测试 - 批量换算
- **CustomUnitManagerTest**：20 个测试 - 自定义单位

总计：66 个单元测试

## 许可证

MIT License

## 作者

UnitConverter - 单位换算器
