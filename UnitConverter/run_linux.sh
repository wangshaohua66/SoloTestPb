#!/bin/bash

# 单位换算器启动脚本 (Linux)
# 此脚本确保使用包含 JavaFX 的 Java 8 运行应用

set -e

echo "========================================"
echo "  单位换算器 - Unit Converter"
echo "========================================"
echo ""

# 查找可用的 Java 8 并包含 JavaFX
JAVA_CMD=""

# 检查 JAVA_HOME
if [ -n "$JAVA_HOME" ]; then
    if [ -f "$JAVA_HOME/jre/lib/ext/jfxrt.jar" ] || [ -f "$JAVA_HOME/lib/ext/jfxrt.jar" ]; then
        echo "使用 JAVA_HOME 中的 Java 8 (包含 JavaFX)"
        JAVA_CMD="$JAVA_HOME/bin/java"
    fi
fi

# 如果没有找到，检查默认 java
if [ -z "$JAVA_CMD" ]; then
    JAVA_VERSION=$(java -version 2>&1 | head -1 | grep -E "1\.8|8\." || true)
    if [ -n "$JAVA_VERSION" ]; then
        # 检查是否包含 JavaFX
        JAVA_HOME=$(java -XshowSettings:properties -version 2>&1 | grep "java.home" | awk -F " = " '{print $2}')
        if [ -f "$JAVA_HOME/jre/lib/ext/jfxrt.jar" ] || [ -f "$JAVA_HOME/lib/ext/jfxrt.jar" ]; then
            echo "使用默认 Java 8 (包含 JavaFX)"
            JAVA_CMD="java"
        fi
    fi
fi

# 如果没有找到，提示用户
if [ -z "$JAVA_CMD" ]; then
    echo "警告: 未找到包含 JavaFX 的 Java 8"
    echo ""
    echo "建议安装包含 JavaFX 的 JDK:"
    echo "  - Oracle JDK 8"
    echo "  - ZuluFX 8"
    echo "  - BellSoft Liberica JDK 8 Full JDK"
    echo ""
    echo "尝试使用默认 java，但可能无法启动 GUI"
    echo ""
    JAVA_CMD="java"
fi

echo "使用 Java: $JAVA_CMD"
echo ""

# 查找 jar 文件
JAR_FILE=""
if [ -f "target/UnitConverter-1.0.0.jar" ]; then
    JAR_FILE="target/UnitConverter-1.0.0.jar"
elif [ -f "UnitConverter-1.0.0.jar" ]; then
    JAR_FILE="UnitConverter-1.0.0.jar"
fi

if [ -z "$JAR_FILE" ]; then
    echo "错误: 未找到 UnitConverter-1.0.0.jar"
    echo "请先运行: mvn clean package -Plinux"
    exit 1
fi

echo "启动应用: $JAR_FILE"
echo "========================================"
echo ""

# 启动应用
"$JAVA_CMD" -jar "$JAR_FILE"
