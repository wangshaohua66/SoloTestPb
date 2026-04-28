#!/bin/bash

# 单位换算器启动脚本 (macOS)
# 此脚本确保使用包含 JavaFX 的 Java 8 运行应用

set -e

echo "========================================"
echo "  单位换算器 - Unit Converter"
echo "========================================"
echo ""

# 查找可用的 Java 8 并包含 JavaFX
JAVA_CMD=""

# 优先检查系统 Java 插件 (Oracle Java 8，包含 JavaFX)
SYSTEM_JAVA="/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java"
if [ -f "$SYSTEM_JAVA" ]; then
    JAVA_VERSION=$("$SYSTEM_JAVA" -version 2>&1 | head -1 | grep -E "1\.8|8\.")
    if [ -n "$JAVA_VERSION" ]; then
        echo "找到系统 Java 8 (包含 JavaFX)"
        JAVA_CMD="$SYSTEM_JAVA"
    fi
fi

# 如果没有找到，检查 JAVA_HOME
if [ -z "$JAVA_CMD" ] && [ -n "$JAVA_HOME" ]; then
    if [ -f "$JAVA_HOME/jre/lib/ext/jfxrt.jar" ] || [ -f "$JAVA_HOME/lib/ext/jfxrt.jar" ]; then
        echo "使用 JAVA_HOME 中的 Java 8 (包含 JavaFX)"
        JAVA_CMD="$JAVA_HOME/bin/java"
    fi
fi

# 如果没有找到，检查 /usr/libexec/java_home
if [ -z "$JAVA_CMD" ] && [ -x /usr/libexec/java_home ]; then
    JAVA8_HOME=$(/usr/libexec/java_home -v 1.8 2>/dev/null || true)
    if [ -n "$JAVA8_HOME" ]; then
        if [ -f "$JAVA8_HOME/jre/lib/ext/jfxrt.jar" ] || [ -f "$JAVA8_HOME/lib/ext/jfxrt.jar" ]; then
            echo "使用 /usr/libexec/java_home 找到的 Java 8"
            JAVA_CMD="$JAVA8_HOME/bin/java"
        fi
    fi
fi

# 最后的尝试：使用默认的 java
if [ -z "$JAVA_CMD" ]; then
    echo "警告: 未找到包含 JavaFX 的 Java 8"
    echo "尝试使用默认 java，但可能无法启动 GUI"
    echo ""
    echo "建议安装 Oracle JDK 8 或 ZuluFX 8 (包含 JavaFX)"
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
    echo "请先运行: mvn clean package -Pmacos"
    exit 1
fi

echo "启动应用: $JAR_FILE"
echo "========================================"
echo ""

# 启动应用
"$JAVA_CMD" -jar "$JAR_FILE"
