"""
单元测试 - 测试重命名策略
"""

import pytest
import allure
import datetime
from batch_rename.core import (
    SequenceRenameStrategy,
    TimestampRenameStrategy,
    ReplaceRenameStrategy,
    PrefixRenameStrategy,
    SuffixRenameStrategy,
    RegexRenameStrategy,
)


@allure.feature("重命名策略")
class TestSequenceRenameStrategy:
    """
    测试序列重命名策略
    """

    @allure.story("基础序列重命名")
    @allure.title("测试默认参数的序列重命名")
    def test_default_sequence(self):
        strategy = SequenceRenameStrategy(name="file")
        
        result = strategy.generate_new_name("document.txt", 0)
        assert result == "file_001.txt"
        
        result = strategy.generate_new_name("document.txt", 1)
        assert result == "file_002.txt"

    @allure.story("自定义起始序号")
    @allure.title("测试自定义起始序号")
    def test_custom_start(self):
        strategy = SequenceRenameStrategy(name="photo", start=100, padding=3)
        
        result = strategy.generate_new_name("image.jpg", 0)
        assert result == "photo_100.jpg"
        
        result = strategy.generate_new_name("image.jpg", 5)
        assert result == "photo_105.jpg"

    @allure.story("自定义填充位数")
    @allure.title("测试不同填充位数")
    def test_custom_padding(self):
        strategy_2 = SequenceRenameStrategy(name="file", padding=2)
        assert strategy_2.generate_new_name("a.txt", 0) == "file_01.txt"
        assert strategy_2.generate_new_name("a.txt", 9) == "file_10.txt"
        assert strategy_2.generate_new_name("a.txt", 99) == "file_100.txt"

        strategy_5 = SequenceRenameStrategy(name="file", padding=5)
        assert strategy_5.generate_new_name("a.txt", 0) == "file_00001.txt"

    @allure.story("处理不同扩展名")
    @allure.title("测试处理不同文件扩展名")
    def test_different_extensions(self):
        strategy = SequenceRenameStrategy(name="doc")
        
        assert strategy.generate_new_name("report.pdf", 0) == "doc_001.pdf"
        assert strategy.generate_new_name("data.csv", 1) == "doc_002.csv"
        assert strategy.generate_new_name("image.png", 2) == "doc_003.png"

    @allure.story("处理无扩展名文件")
    @allure.title("测试处理无扩展名的文件")
    def test_no_extension(self):
        strategy = SequenceRenameStrategy(name="file")
        assert strategy.generate_new_name("readme", 0) == "file_001"


@allure.feature("重命名策略")
class TestTimestampRenameStrategy:
    """
    测试时间戳重命名策略
    """

    @allure.story("固定时间戳")
    @allure.title("测试使用固定时间戳")
    def test_fixed_timestamp(self):
        fixed_time = datetime.datetime(2024, 1, 15, 10, 30, 45)
        strategy = TimestampRenameStrategy(timestamp=fixed_time)
        
        assert strategy.generate_new_name("file.txt", 0) == "20240115_103045_1.txt"
        assert strategy.generate_new_name("file.txt", 1) == "20240115_103045_2.txt"
        assert strategy.generate_new_name("file.txt", 2) == "20240115_103045_3.txt"

    @allure.story("自定义日期格式")
    @allure.title("测试自定义日期格式")
    def test_custom_format(self):
        fixed_time = datetime.datetime(2024, 1, 15, 10, 30, 45)
        strategy = TimestampRenameStrategy(timestamp=fixed_time, format_str="%Y-%m-%d")
        
        assert strategy.generate_new_name("file.txt", 0) == "2024-01-15_1.txt"

    @allure.story("简化日期格式")
    @allure.title("测试仅使用日期格式")
    def test_date_only_format(self):
        fixed_time = datetime.datetime(2024, 12, 31, 23, 59, 59)
        strategy = TimestampRenameStrategy(timestamp=fixed_time, format_str="%Y%m%d")
        
        assert strategy.generate_new_name("photo.jpg", 0) == "20241231_1.jpg"


@allure.feature("重命名策略")
class TestReplaceRenameStrategy:
    """
    测试查找替换重命名策略
    """

    @allure.story("基础替换")
    @allure.title("测试简单的字符串替换")
    def test_basic_replace(self):
        strategy = ReplaceRenameStrategy(find="old", replace="new")
        
        assert strategy.generate_new_name("old_file.txt", 0) == "new_file.txt"
        assert strategy.generate_new_name("file_old.txt", 0) == "file_new.txt"
        assert strategy.generate_new_name("old_old.txt", 0) == "new_new.txt"

    @allure.story("替换为空字符串")
    @allure.title("测试删除特定字符串")
    def test_replace_with_empty(self):
        strategy = ReplaceRenameStrategy(find="_backup", replace="")
        
        assert strategy.generate_new_name("document_backup.txt", 0) == "document.txt"
        assert strategy.generate_new_name("photo_backup.jpg", 0) == "photo.jpg"

    @allure.story("无匹配替换")
    @allure.title("测试没有匹配的情况")
    def test_no_match(self):
        strategy = ReplaceRenameStrategy(find="xyz", replace="abc")
        
        assert strategy.generate_new_name("file.txt", 0) == "file.txt"

    @allure.story("特殊字符替换")
    @allure.title("测试替换空格和特殊字符")
    def test_special_characters(self):
        strategy = ReplaceRenameStrategy(find=" ", replace="_")
        
        assert strategy.generate_new_name("my file name.txt", 0) == "my_file_name.txt"


@allure.feature("重命名策略")
class TestPrefixRenameStrategy:
    """
    测试前缀重命名策略
    """

    @allure.story("添加前缀")
    @allure.title("测试添加简单前缀")
    def test_add_prefix(self):
        strategy = PrefixRenameStrategy(prefix="2024_")
        
        assert strategy.generate_new_name("file.txt", 0) == "2024_file.txt"
        assert strategy.generate_new_name("photo.jpg", 0) == "2024_photo.jpg"

    @allure.story("多字符前缀")
    @allure.title("测试添加复杂前缀")
    def test_complex_prefix(self):
        strategy = PrefixRenameStrategy(prefix="backup_v1_")
        
        assert strategy.generate_new_name("data.csv", 0) == "backup_v1_data.csv"

    @allure.story("空前缀")
    @allure.title("测试使用空前缀")
    def test_empty_prefix(self):
        strategy = PrefixRenameStrategy(prefix="")
        
        assert strategy.generate_new_name("file.txt", 0) == "file.txt"


@allure.feature("重命名策略")
class TestSuffixRenameStrategy:
    """
    测试后缀重命名策略
    """

    @allure.story("添加后缀")
    @allure.title("测试添加简单后缀")
    def test_add_suffix(self):
        strategy = SuffixRenameStrategy(suffix_str="_edited")
        
        assert strategy.generate_new_name("photo.jpg", 0) == "photo_edited.jpg"
        assert strategy.generate_new_name("document.pdf", 0) == "document_edited.pdf"

    @allure.story("后缀不影响扩展名")
    @allure.title("测试后缀在扩展名之前")
    def test_suffix_before_extension(self):
        strategy = SuffixRenameStrategy(suffix_str="_v2")
        
        result = strategy.generate_new_name("report.version.1.0.docx", 0)
        assert result == "report.version.1.0_v2.docx"

    @allure.story("空后缀")
    @allure.title("测试使用空后缀")
    def test_empty_suffix(self):
        strategy = SuffixRenameStrategy(suffix_str="")
        
        assert strategy.generate_new_name("file.txt", 0) == "file.txt"


@allure.feature("重命名策略")
class TestRegexRenameStrategy:
    """
    测试正则表达式重命名策略
    """

    @allure.story("简单正则替换")
    @allure.title("测试基础正则匹配")
    def test_simple_regex(self):
        strategy = RegexRenameStrategy(pattern="IMG_", replace="Photo_")
        
        assert strategy.generate_new_name("IMG_001.jpg", 0) == "Photo_001.jpg"
        assert strategy.generate_new_name("IMG_1234.png", 0) == "Photo_1234.png"

    @allure.story("反向引用")
    @allure.title("测试使用反向引用")
    def test_backreference(self):
        strategy = RegexRenameStrategy(
            pattern=r"IMG_(\d{4})_(\d{2})_(\d{2})",
            replace=r"Photo_\1-\2-\3"
        )
        
        assert strategy.generate_new_name("IMG_2024_01_15.jpg", 0) == "Photo_2024-01-15.jpg"

    @allure.story("提取数字")
    @allure.title("测试提取并重排数字")
    def test_extract_numbers(self):
        strategy = RegexRenameStrategy(
            pattern=r"file(\d+)",
            replace=r"doc_\1"
        )
        
        assert strategy.generate_new_name("file1.txt", 0) == "doc_1.txt"
        assert strategy.generate_new_name("file123.txt", 0) == "doc_123.txt"

    @allure.story("无匹配正则")
    @allure.title("测试正则无匹配的情况")
    def test_no_match(self):
        strategy = RegexRenameStrategy(pattern=r"\d+", replace="X")
        
        assert strategy.generate_new_name("file.txt", 0) == "file.txt"

    @allure.story("替换所有匹配")
    @allure.title("测试替换所有匹配项")
    def test_replace_all(self):
        strategy = RegexRenameStrategy(pattern="_", replace="-")
        
        assert strategy.generate_new_name("my_file_name.txt", 0) == "my-file-name.txt"

    @allure.story("复杂正则模式")
    @allure.title("测试复杂的正则表达式")
    def test_complex_pattern(self):
        strategy = RegexRenameStrategy(
            pattern=r"^(DSC|IMG)_(\d{3})",
            replace=r"Camera_\2"
        )
        
        assert strategy.generate_new_name("DSC_001.jpg", 0) == "Camera_001.jpg"
        assert strategy.generate_new_name("IMG_999.jpg", 0) == "Camera_999.jpg"
