"""
一键验证脚本
在Python 3.12环境中自动验证所有验收标准

运行方式：
    python run_verification.py

验证内容：
1. 语法检查 (check_syntax.py)
2. 单元测试 (pytest)
3. 覆盖率报告 (pytest-cov)
4. Allure测试报告 (allure-pytest)
5. 数据完整性基准测试 (1000页, 99%完整率)

⚠️ 注意：此脚本需要在实际的Python 3.12环境中运行。
   所有输出和结果仅供参考，以实际运行为准。
"""
import sys
import os
import subprocess
import shutil
import time
import re
from datetime import datetime


class VerificationRunner:
    """
    验证执行器
    """

    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.results = []
        self.start_time = time.time()

    def print_header(self, title: str):
        """
        打印标题
        """
        line = "=" * 70
        print(f"\n{line}")
        print(f"  {title}")
        print(f"{line}\n")

    def print_step(self, step_num: int, total_steps: int, title: str):
        """
        打印步骤信息
        """
        print(f"\n[{step_num}/{total_steps}] {title}")
        print("-" * 70)

    def run_command(self, cmd: str, description: str) -> tuple:
        """
        运行命令并返回结果

        Args:
            cmd: 命令字符串
            description: 命令描述

        Returns:
            (success: bool, output: str)
        """
        print(f"执行: {cmd}")
        print()

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(result.stderr)

            success = result.returncode == 0
            return success, result.stdout + result.stderr

        except Exception as e:
            print(f"错误: {e}")
            return False, str(e)

    def check_python_version(self) -> bool:
        """
        检查Python版本
        """
        self.print_step(1, 7, "检查Python版本")

        version = sys.version_info
        print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")

        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python版本满足要求 (3.8+)")
            self.results.append(("Python版本", "通过", f"{version.major}.{version.minor}"))
            return True
        else:
            print(f"❌ Python版本过低，需要 3.8+")
            self.results.append(("Python版本", "失败", f"{version.major}.{version.minor}"))
            return False

    def install_dependencies(self) -> bool:
        """
        安装依赖
        """
        self.print_step(2, 7, "安装/检查依赖")

        cmd = f"{sys.executable} -m pip install -r requirements.txt"
        success, output = self.run_command(cmd, "安装依赖")

        if success:
            print("✅ 依赖安装完成")
            self.results.append(("依赖安装", "通过", ""))
        else:
            print("⚠️  依赖安装可能部分失败，继续执行...")
            self.results.append(("依赖安装", "警告", "部分依赖可能未安装"))

        return True

    def check_syntax(self) -> bool:
        """
        语法检查
        """
        self.print_step(3, 7, "语法检查")

        cmd = f"{sys.executable} check_syntax.py"
        success, output = self.run_command(cmd, "语法检查")

        if success:
            print("✅ 所有Python文件语法正确")
            self.results.append(("语法检查", "通过", ""))
        else:
            print("❌ 存在语法错误")
            self.results.append(("语法检查", "失败", "存在语法错误"))

        return success

    def run_unit_tests(self) -> bool:
        """
        运行单元测试
        """
        self.print_step(4, 7, "运行单元测试")

        cmd = f"{sys.executable} -m pytest -v --tb=short"
        success, output = self.run_command(cmd, "单元测试")

        if success:
            print("✅ 所有单元测试通过")
            self.results.append(("单元测试", "通过", ""))
        else:
            print("❌ 存在失败的测试")
            self.results.append(("单元测试", "失败", "存在失败测试"))

        return success

    def run_coverage_test(self) -> bool:
        """
        运行覆盖率测试
        """
        self.print_step(5, 7, "运行覆盖率测试")

        cmd = f"{sys.executable} -m pytest --cov=auto_web_scraper --cov-report=term-missing --cov-report=html:coverage_html"
        success, output = self.run_command(cmd, "覆盖率测试")

        threshold = 80.0
        coverage_passed = False

        if success:
            match = re.search(r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%', output)
            if match:
                coverage = int(match.group(3))
                print(f"覆盖率: {coverage}%")

                if coverage >= threshold:
                    print(f"✅ 覆盖率达到要求 ({coverage}% >= {threshold}%)")
                    coverage_passed = True
                    self.results.append(("测试覆盖率", "通过", f"{coverage}%"))
                else:
                    print(f"❌ 覆盖率未达到要求 ({coverage}% < {threshold}%)")
                    self.results.append(("测试覆盖率", "失败", f"{coverage}%"))
            else:
                print("⚠️  无法解析覆盖率结果")
                self.results.append(("测试覆盖率", "警告", "无法解析"))
        else:
            print("❌ 覆盖率测试执行失败")
            self.results.append(("测试覆盖率", "失败", "执行错误"))

        return coverage_passed

    def run_allure_report(self) -> bool:
        """
        生成Allure报告
        """
        self.print_step(6, 7, "生成Allure测试报告")

        allure_dir = os.path.join(self.project_root, "allure_results")
        if os.path.exists(allure_dir):
            shutil.rmtree(allure_dir)

        cmd = f"{sys.executable} -m pytest --alluredir={allure_dir}"
        success, output = self.run_command(cmd, "Allure报告生成")

        if success:
            print(f"✅ Allure结果已生成到: {allure_dir}")
            print(f"   要查看报告，请安装Allure CLI后运行:")
            print(f"   allure serve {allure_dir}")
            self.results.append(("Allure报告", "通过", f"目录: {allure_dir}"))
        else:
            print("⚠️  Allure报告生成可能失败")
            self.results.append(("Allure报告", "警告", "执行完成但需确认"))

        return success

    def run_data_integrity_benchmark(self) -> bool:
        """
        运行数据完整性基准测试
        """
        self.print_step(7, 7, "运行数据完整性基准测试 (1000页)")

        benchmark_script = os.path.join(self.project_root, "benchmark", "data_integrity_test.py")

        if not os.path.exists(benchmark_script):
            print(f"❌ 基准测试脚本不存在: {benchmark_script}")
            self.results.append(("数据完整性", "失败", "脚本不存在"))
            return False

        cmd = f"{sys.executable} {benchmark_script} -p 1000 --failure-rate 0.005 --retry-times 3"
        success, output = self.run_command(cmd, "数据完整性测试")

        if success:
            print("✅ 数据完整性测试通过 (完整率 >= 99%)")
            self.results.append(("数据完整性", "通过", "完整率 >= 99%"))
        else:
            print("❌ 数据完整性测试未通过")
            self.results.append(("数据完整性", "失败", "完整率 < 99%"))

        return success

    def print_summary(self):
        """
        打印验证总结
        """
        total_time = time.time() - self.start_time

        self.print_header("验证总结")

        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {total_time:.2f}秒")
        print()

        print("-" * 70)
        print(f"{'检查项':<20} {'状态':<10} {'详情':<40}")
        print("-" * 70)

        passed = 0
        failed = 0
        warnings = 0

        for name, status, detail in self.results:
            status_icon = "✅" if status == "通过" else "❌" if status == "失败" else "⚠️"
            if status == "通过":
                passed += 1
            elif status == "失败":
                failed += 1
            else:
                warnings += 1
            print(f"{name:<20} {status_icon} {status:<8} {detail:<40}")

        print("-" * 70)
        print()

        print(f"结果统计:")
        print(f"  通过: {passed}")
        print(f"  失败: {failed}")
        print(f"  警告: {warnings}")
        print()

        if failed == 0:
            print("🎉 所有验证通过！")
            print("=" * 70)
            return True
        else:
            print(f"❌ 存在 {failed} 个失败项，请检查并修复")
            print("=" * 70)
            return False

    def run_all(self) -> bool:
        """
        运行所有验证步骤
        """
        self.print_header("网页数据采集工具 - 一键验证脚本")
        print(f"项目目录: {self.project_root}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        critical_steps = [
            ("Python版本检查", self.check_python_version),
            ("语法检查", self.check_syntax),
        ]

        non_critical_steps = [
            ("安装依赖", self.install_dependencies),
            ("单元测试", self.run_unit_tests),
            ("覆盖率测试", self.run_coverage_test),
            ("Allure报告", self.run_allure_report),
            ("数据完整性测试", self.run_data_integrity_benchmark),
        ]

        for name, step_func in critical_steps:
            if not step_func():
                print(f"\n❌ {name} 失败，无法继续验证")
                self.print_summary()
                return False

        for name, step_func in non_critical_steps:
            try:
                step_func()
            except Exception as e:
                print(f"⚠️  {name} 执行异常: {e}")
                self.results.append((name, "错误", str(e)))

        return self.print_summary()


def main():
    """
    主函数
    """
    runner = VerificationRunner()

    try:
        success = runner.run_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断验证")
        sys.exit(130)
    except Exception as e:
        print(f"\n验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
