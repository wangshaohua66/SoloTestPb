"""
包入口点
允许通过 python -m batch_mail 运行
"""

from .cli import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
