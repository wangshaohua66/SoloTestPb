#!/usr/bin/env python3
"""CiteMaster - Academic Citation Management & Literature Search System.

Entry point for the CiteMaster command-line application.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.main import run


if __name__ == "__main__":
    run()
