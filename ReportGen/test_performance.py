"""
性能测试脚本：测试10万行数据生成报表的时间。
"""

import sys
import time
import os
import tempfile
import pandas as pd
import numpy as np

from reportgen.core import ReportGenerator


def generate_large_dataframe(n_rows=100000):
    """
    生成10万行测试数据。
    """
    np.random.seed(42)

    data = {
        "id": range(1, n_rows + 1),
        "name": [f"用户{i}" for i in range(1, n_rows + 1)],
        "age": np.random.randint(18, 60, n_rows),
        "salary": np.random.randint(3000, 20000, n_rows),
        "department": np.random.choice(
            ["技术部", "市场部", "销售部", "财务部", "人力资源部"], n_rows
        ),
        "score": np.random.uniform(0, 100, n_rows).round(2),
    }

    return pd.DataFrame(data)


def test_performance():
    """
    测试性能：处理10万行数据不超过30秒。

    Returns:
        bool: 测试是否通过
    """
    print("=" * 60)
    print("自动化报表生成工具 - 性能测试")
    print("=" * 60)

    print("\n[1/3] 正在生成10万行测试数据...")
    df = generate_large_dataframe(100000)
    print(f"      数据生成完成，共 {len(df)} 行，{len(df.columns)} 列")

    generator = ReportGenerator()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "large_report.xlsx")

        print("\n[2/3] 开始性能测试（生成Excel报表）...")
        start_time = time.time()

        result = generator.generate_report_from_dataframe(
            df,
            "excel",
            output_path,
        )

        end_time = time.time()
        duration = end_time - start_time

        print("\n[3/3] 测试结果统计：")
        print(f"      - 数据行数：{len(df)}")
        print(f"      - 列数：{len(df.columns)}")
        print(f"      - 输出文件：{output_path}")
        print(f"      - 文件是否存在：{'是' if os.path.exists(output_path) else '否'}")
        file_size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"      - 文件大小：{file_size_mb:.2f} MB")
        print(f"      - 处理耗时：{duration:.2f} 秒")
        print(f"      - 耗时要求：≤ 30 秒")

        print("\n" + "=" * 60)

        assert os.path.exists(output_path), "生成的报表文件不存在"
        assert duration < 30, (
            f"性能测试失败：处理10万行数据耗时 {duration:.2f} 秒，"
            f"超过30秒限制"
        )

        print(f"✓ 性能测试通过！耗时 {duration:.2f} 秒 < 30 秒")
        print("=" * 60)

        return True


if __name__ == "__main__":
    try:
        success = test_performance()
        print("\n测试完成，退出码：0")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ 测试失败：{e}")
        print("\n测试完成，退出码：1")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试发生异常：{e}")
        import traceback
        traceback.print_exc()
        print("\n测试完成，退出码：2")
        sys.exit(2)
