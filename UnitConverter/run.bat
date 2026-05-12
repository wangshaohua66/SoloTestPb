@echo off
REM 单位换算器启动脚本 (Windows)
REM 此脚本确保使用包含 JavaFX 的 Java 8 运行应用

echo ========================================
echo   单位换算器 - Unit Converter
echo ========================================
echo.

REM 检查 Java 版本
java -version 2>&1 | findstr "1.8" >nul
if %errorlevel% neq 0 (
    echo 错误: 需要 Java 8 或更高版本
    echo 请安装包含 JavaFX 的 Java 8 (Oracle JDK 8 或 ZuluFX 8)
    pause
    exit /b 1
)

REM 检查 jar 文件
if not exist "target\UnitConverter-1.0.0.jar" (
    if not exist "UnitConverter-1.0.0.jar" (
        echo 错误: 未找到 UnitConverter-1.0.0.jar
        echo 请先运行: mvn clean package
        pause
        exit /b 1
    ) else (
        set JAR_FILE=UnitConverter-1.0.0.jar
    )
) else (
    set JAR_FILE=target\UnitConverter-1.0.0.jar
)

echo 使用 Java 8 运行应用: %JAR_FILE%
echo ========================================
echo.

java -jar %JAR_FILE%

pause
