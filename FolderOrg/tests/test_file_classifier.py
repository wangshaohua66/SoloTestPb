"""
文件类型识别模块单元测试
"""

import pytest
from folder_organizer.file_classifier import FileClassifier


class TestFileClassifier:
    """
    文件分类器测试类
    """

    def test_init(self, test_categories):
        """
        测试初始化
        """
        classifier = FileClassifier(test_categories)
        assert classifier.categories == test_categories

    def test_get_file_extension(self, test_categories):
        """
        测试获取文件扩展名
        """
        classifier = FileClassifier(test_categories)
        
        assert classifier.get_file_extension("/path/to/file.pdf") == ".pdf"
        assert classifier.get_file_extension("/path/to/IMAGE.JPG") == ".jpg"
        assert classifier.get_file_extension("/path/to/no_extension") == ""
        assert classifier.get_file_extension("file.with.multiple.dots.txt") == ".txt"

    def test_classify_file_documents(self, test_categories):
        """
        测试分类文档类型文件
        """
        classifier = FileClassifier(test_categories)
        
        category, target_dir = classifier.classify_file("/path/to/report.pdf")
        assert category == "documents"
        assert target_dir == "Documents"
        
        category, target_dir = classifier.classify_file("/path/to/notes.txt")
        assert category == "documents"
        assert target_dir == "Documents"

    def test_classify_file_images(self, test_categories):
        """
        测试分类图片类型文件
        """
        classifier = FileClassifier(test_categories)
        
        category, target_dir = classifier.classify_file("/path/to/photo.jpg")
        assert category == "images"
        assert target_dir == "Images"
        
        category, target_dir = classifier.classify_file("/path/to/PICTURE.PNG")
        assert category == "images"
        assert target_dir == "Images"

    def test_classify_file_others(self, test_categories):
        """
        测试分类未知类型文件
        """
        classifier = FileClassifier(test_categories)
        
        category, target_dir = classifier.classify_file("/path/to/unknown.xyz")
        assert category == "others"
        assert target_dir == "Others"
        
        category, target_dir = classifier.classify_file("/path/to/no_extension")
        assert category == "others"
        assert target_dir == "Others"

    def test_get_category_target_dir(self, test_categories):
        """
        测试获取分类目标目录
        """
        classifier = FileClassifier(test_categories)
        
        assert classifier.get_category_target_dir("documents") == "Documents"
        assert classifier.get_category_target_dir("images") == "Images"
        assert classifier.get_category_target_dir("non_existent") is None

    def test_list_categories(self, test_categories):
        """
        测试列出所有分类
        """
        classifier = FileClassifier(test_categories)
        categories = classifier.list_categories()
        
        assert "documents" in categories
        assert "images" in categories
        assert "videos" in categories
        assert "audio" in categories
        assert "others" in categories

    def test_get_category_extensions(self, test_categories):
        """
        测试获取分类扩展名
        """
        classifier = FileClassifier(test_categories)
        
        assert ".pdf" in classifier.get_category_extensions("documents")
        assert ".jpg" in classifier.get_category_extensions("images")
        assert classifier.get_category_extensions("non_existent") == []

    def test_is_extension_in_category(self, test_categories):
        """
        测试检查扩展名是否属于分类
        """
        classifier = FileClassifier(test_categories)
        
        assert classifier.is_extension_in_category(".pdf", "documents") is True
        assert classifier.is_extension_in_category(".PDF", "documents") is True
        assert classifier.is_extension_in_category(".jpg", "images") is True
        assert classifier.is_extension_in_category(".xyz", "documents") is False

    def test_update_categories(self, test_categories):
        """
        测试更新分类配置
        """
        classifier = FileClassifier(test_categories)
        
        new_categories = {
            "new_cat": {
                "extensions": [".new"],
                "target_dir": "NewDir"
            }
        }
        classifier.update_categories(new_categories)
        
        assert classifier.categories == new_categories
        category, target_dir = classifier.classify_file("/path/to/file.new")
        assert category == "new_cat"
        assert target_dir == "NewDir"

    def test_case_insensitive_extensions(self, test_categories):
        """
        测试扩展名大小写不敏感
        """
        classifier = FileClassifier(test_categories)
        
        category1, _ = classifier.classify_file("/path/to/FILE.PDF")
        category2, _ = classifier.classify_file("/path/to/file.pdf")
        category3, _ = classifier.classify_file("/path/to/file.Pdf")
        
        assert category1 == "documents"
        assert category2 == "documents"
        assert category3 == "documents"
