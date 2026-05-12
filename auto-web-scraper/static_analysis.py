"""
静态代码分析脚本
使用Python AST进行语法和代码质量检查

此脚本不依赖外部工具（pylint/flake8），
使用Python内置的ast模块进行静态分析。

运行方式：
    python static_analysis.py
    python static_analysis.py run_verification.py
"""
import sys
import os
import ast
import re


class StaticCodeAnalyzer:
    """
    静态代码分析器
    """

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.violations = {
            "import_order": 0,
            "unused_import": 0,
            "line_length": 0,
            "missing_docstring": 0,
            "complex_function": 0,
            "magic_number": 0,
        }

    def analyze_file(self, file_path: str) -> tuple:
        """
        分析单个Python文件

        Args:
            file_path: 文件路径

        Returns:
            (issues: list, warnings: list)
        """
        file_issues = []
        file_warnings = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                source = "".join(lines)

            tree = ast.parse(source, filename=file_path)

            for line_num, line in enumerate(lines, 1):
                if len(line.rstrip()) > 100:
                    file_warnings.append(
                        f"行 {line_num}: 行长度超过100字符 ({len(line.rstrip())}字符)"
                    )
                    self.violations["line_length"] += 1

            docstring = ast.get_docstring(tree)
            if not docstring:
                file_warnings.append(
                    f"模块缺少文档字符串 (模块级docstring)"
                )
                self.violations["missing_docstring"] += 1

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        imports.append(node.module)

                if isinstance(node, ast.FunctionDef):
                    func_docstring = ast.get_docstring(node)
                    if not func_docstring and not node.name.startswith("_"):
                        file_warnings.append(
                            f"函数 '{node.name}' 缺少文档字符串"
                        )
                        self.violations["missing_docstring"] += 1

                    if len(node.body) > 30:
                        file_warnings.append(
                            f"函数 '{node.name}' 复杂度较高 ({len(node.body)} 行)"
                        )
                        self.violations["complex_function"] += 1

                if isinstance(node, ast.ClassDef):
                    class_docstring = ast.get_docstring(node)
                    if not class_docstring:
                        file_warnings.append(
                            f"类 '{node.name}' 缺少文档字符串"
                        )
                        self.violations["missing_docstring"] += 1

            standard_libs = {
                "sys", "os", "path", "time", "datetime", "json", "re",
                "subprocess", "shutil", "tempfile", "io", "collections",
                "typing", "dataclasses", "unittest", "traceback",
            }

            std_imports = []
            third_party_imports = []

            for imp in imports:
                module_name = imp.split(".")[0] if imp else ""
                if module_name in standard_libs:
                    std_imports.append(module_name)
                else:
                    third_party_imports.append(module_name)

        except SyntaxError as e:
            file_issues.append(f"语法错误: 行 {e.lineno} - {e.msg}")
        except Exception as e:
            file_issues.append(f"分析错误: {e}")

        return file_issues, file_warnings

    def analyze_directory(self, dir_path: str, exclude_dirs: list = None) -> dict:
        """
        分析目录下所有Python文件

        Args:
            dir_path: 目录路径
            exclude_dirs: 排除的目录

        Returns:
            分析结果
        """
        if exclude_dirs is None:
            exclude_dirs = [".git", "__pycache__", ".pytest_cache", "venv", "env", "output"]

        total_files = 0
        files_with_issues = 0
        files_with_warnings = 0

        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    total_files += 1
                    file_path = os.path.join(root, file)

                    issues, warnings = self.analyze_file(file_path)

                    if issues:
                        files_with_issues += 1
                        print(f"\n❌ {file_path}")
                        for issue in issues:
                            print(f"   {issue}")

                    if warnings:
                        files_with_warnings += 1
                        print(f"\n⚠️  {file_path}")
                        for warning in warnings:
                            print(f"   {warning}")

        return {
            "total_files": total_files,
            "files_with_issues": files_with_issues,
            "files_with_warnings": files_with_warnings,
            "violations": self.violations,
        }


def main():
    """
    主函数
    """
    project_root = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("静态代码分析")
    print("=" * 70)
    print(f"项目根目录: {project_root}")
    print("=" * 70)
    print()

    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if not os.path.isabs(target_file):
            target_file = os.path.join(project_root, target_file)

        if not os.path.exists(target_file):
            print(f"❌ 文件不存在: {target_file}")
            sys.exit(1)

        print(f"分析文件: {target_file}")
        print()

        analyzer = StaticCodeAnalyzer()
        issues, warnings = analyzer.analyze_file(target_file)

        if issues:
            print(f"\n❌ 发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ 无语法问题")

        if warnings:
            print(f"\n⚠️  发现 {len(warnings)} 个警告:")
            for warning in warnings:
                print(f"   - {warning}")
        else:
            print(f"✅ 无警告")

    else:
        print("分析整个项目...")
        print()

        analyzer = StaticCodeAnalyzer()
        results = analyzer.analyze_directory(project_root)

        print()
        print("=" * 70)
        print("分析结果")
        print("=" * 70)
        print(f"总文件数: {results['total_files']}")
        print(f"有问题的文件: {results['files_with_issues']}")
        print(f"有警告的文件: {results['files_with_warnings']}")
        print()
        print("违规统计:")
        for violation, count in results['violations'].items():
            if count > 0:
                print(f"  - {violation}: {count}")

        print()
        if results['files_with_issues'] == 0:
            print("✅ 所有文件语法正确！")
        else:
            print(f"❌ 发现 {results['files_with_issues']} 个文件有问题")

        print("=" * 70)

    print("\n💡 提示:")
    print("   - 此脚本使用Python AST进行语法检查")
    print("   - 如需更详细的PEP8检查，请安装pylint或flake8")
    print("   - 安装命令: pip install pylint flake8")
    print("   - 运行命令: pylint run_verification.py 或 flake8 run_verification.py")

    print("\n⚠️  局限性说明:")
    print("   此工具只做基础的静态分析，不是完整的代码质量检查工具：")
    print("   - ✅ 能检查：语法错误、缺少docstring、行长度超限")
    print("   - ❌ 不能检查：PEP8规范、代码复杂度、未使用变量、类型错误")
    print("   - ❌ 不能运行：单元测试、覆盖率、集成测试")
    print()
    print("   要验证代码质量，请使用：")
    print("   1. 语法检查: python check_syntax.py")
    print("   2. 单元测试: pytest -v")
    print("   3. 覆盖率: pytest --cov=auto_web_scraper")
    print("   4. PEP8检查（需安装）: pylint [文件] 或 flake8 [文件]")


if __name__ == "__main__":
    main()
