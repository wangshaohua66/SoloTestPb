"""
pytest 配置和 fixtures
"""
import pytest
import tempfile
import os


@pytest.fixture
def temp_output_dir():
    """
    创建临时输出目录 fixture
    """
    dir_path = tempfile.mkdtemp()
    yield dir_path
    import shutil
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


@pytest.fixture
def sample_html():
    """
    示例HTML fixture
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1 class="title">Hello World</h1>
        <div class="content">
            <p class="desc">Test description</p>
            <a href="https://example.com/page1" class="link">Link 1</a>
            <a href="https://example.com/page2" class="link">Link 2</a>
        </div>
        <ul class="items">
            <li data-id="1">Item 1</li>
            <li data-id="2">Item 2</li>
        </ul>
    </body>
    </html>
    """
