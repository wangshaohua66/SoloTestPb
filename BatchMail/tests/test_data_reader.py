"""
数据读取模块单元测试
"""

import os

import allure
import pandas as pd
import pytest

from batch_mail.data_reader import DataReader, Recipient


@allure.feature("数据读取")
@allure.story("收件人数据类")
class TestRecipient:
    """
    Recipient测试类
    """

    @allure.title("测试Recipient初始化")
    def test_recipient_init(self):
        """
        测试Recipient正常初始化
        """
        recipient = Recipient(
            email="test@example.com",
            name="张三",
            variables={"company": "科技公司"},
            attachments=["file.pdf"],
        )

        assert recipient.email == "test@example.com"
        assert recipient.name == "张三"
        assert recipient.variables == {"company": "科技公司"}
        assert recipient.attachments == ["file.pdf"]

    @allure.title("测试Recipient默认值")
    def test_recipient_defaults(self):
        """
        测试Recipient默认值
        """
        recipient = Recipient(email="test@example.com")

        assert recipient.name is None
        assert recipient.variables == {}
        assert recipient.attachments == []

    @allure.title("测试无效邮箱抛出异常")
    def test_recipient_invalid_email(self):
        """
        测试无效邮箱时抛出ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            Recipient(email="invalid-email")
        assert "无效的邮箱地址" in str(exc_info.value)

    @allure.title("测试空邮箱抛出异常")
    def test_recipient_empty_email(self):
        """
        测试空邮箱时抛出ValueError
        """
        with pytest.raises(ValueError):
            Recipient(email="")


@allure.feature("数据读取")
@allure.story("CSV读取")
class TestDataReaderCSV:
    """
    DataReader CSV读取测试类
    """

    @allure.title("测试读取CSV文件")
    def test_read_csv(self, sample_csv_path: str):
        """
        测试读取CSV文件
        """
        reader = DataReader(sample_csv_path)
        recipients = reader.read()

        assert len(recipients) == 3
        assert recipients[0].email == "test1@example.com"
        assert recipients[0].name == "张三"
        assert recipients[0].variables["company"] == "科技公司"

    @allure.title("测试读取CSV时正确解析变量")
    def test_read_csv_variables(self, temp_dir: str):
        """
        测试CSV中额外列被解析为variables
        """
        csv_path = os.path.join(temp_dir, "test.csv")
        df = pd.DataFrame({
            "email": ["user1@example.com"],
            "name": ["用户A"],
            "order_id": ["ORD001"],
            "amount": [99.99],
        })
        df.to_csv(csv_path, index=False)

        reader = DataReader(csv_path)
        recipients = reader.read()

        assert recipients[0].variables["order_id"] == "ORD001"
        assert recipients[0].variables["amount"] == 99.99

    @allure.title("测试CSV附件列解析")
    def test_read_csv_attachments(self, temp_dir: str):
        """
        测试CSV中附件列解析
        """
        csv_path = os.path.join(temp_dir, "test_att.csv")
        df = pd.DataFrame({
            "email": ["user@example.com"],
            "Attachment": ["file1.pdf;file2.xlsx"],
        })
        df.to_csv(csv_path, index=False)

        reader = DataReader(csv_path)
        recipients = reader.read()

        assert "file1.pdf" in recipients[0].attachments
        assert "file2.xlsx" in recipients[0].attachments

    @allure.title("测试缺少email列抛出异常")
    def test_read_csv_missing_email_column(self, temp_dir: str):
        """
        测试缺少必要列时抛出异常
        """
        csv_path = os.path.join(temp_dir, "invalid.csv")
        df = pd.DataFrame({
            "name": ["张三"],
        })
        df.to_csv(csv_path, index=False)

        reader = DataReader(csv_path)
        with pytest.raises(ValueError) as exc_info:
            reader.read()
        assert "缺少必要的列" in str(exc_info.value)


@allure.feature("数据读取")
@allure.story("Excel读取")
class TestDataReaderExcel:
    """
    DataReader Excel读取测试类
    """

    @allure.title("测试读取Excel文件")
    def test_read_excel(self, sample_excel_path: str):
        """
        测试读取Excel文件
        """
        reader = DataReader(sample_excel_path)
        recipients = reader.read()

        assert len(recipients) == 2
        assert recipients[0].email == "test1@example.com"
        assert recipients[0].name == "张三"
        assert recipients[0].variables["discount"] == "10%"

    @allure.title("测试读取Excel时正确解析变量")
    def test_read_excel_variables(self, temp_dir: str):
        """
        测试Excel中额外列被解析为variables
        """
        xlsx_path = os.path.join(temp_dir, "test.xlsx")
        df = pd.DataFrame({
            "email": ["user1@example.com"],
            "name": ["用户A"],
            "product": ["服务A"],
            "price": [100],
        })
        df.to_excel(xlsx_path, index=False)

        reader = DataReader(xlsx_path)
        recipients = reader.read()

        assert recipients[0].variables["product"] == "服务A"
        assert recipients[0].variables["price"] == 100


@allure.feature("数据读取")
@allure.story("文件验证")
class TestDataReaderValidation:
    """
    DataReader验证测试类
    """

    @allure.title("测试文件不存在抛出异常")
    def test_file_not_found(self, temp_dir: str):
        """
        测试文件不存在时抛出FileNotFoundError
        """
        non_existent = os.path.join(temp_dir, "nonexistent.csv")
        with pytest.raises(FileNotFoundError):
            DataReader(non_existent)

    @allure.title("测试不支持的文件格式抛出异常")
    def test_unsupported_format(self, temp_dir: str):
        """
        测试不支持的文件格式时抛出ValueError
        """
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write("test")

        with pytest.raises(ValueError) as exc_info:
            DataReader(txt_path)
        assert "不支持的文件格式" in str(exc_info.value)

    @allure.title("测试文件名不区分大小写")
    def test_case_insensitive_extension(self, temp_dir: str):
        """
        测试扩展名不区分大小写
        """
        csv_path = os.path.join(temp_dir, "test.CSV")
        df = pd.DataFrame({
            "email": ["test@example.com"],
        })
        df.to_csv(csv_path, index=False)

        reader = DataReader(csv_path)
        assert reader.file_ext == ".csv"

    @allure.title("测试email列存在但值为NaN抛出异常")
    def test_email_column_nan_value(self, temp_dir: str):
        """
        测试email列存在但值为NaN时抛出ValueError
        """
        csv_path = os.path.join(temp_dir, "nan_email.csv")
        df = pd.DataFrame({
            "email": [None, pd.NA, "valid@example.com"],
            "name": ["用户A", "用户B", "用户C"],
        })
        df.to_csv(csv_path, index=False)

        reader = DataReader(csv_path)
        with pytest.raises(ValueError) as exc_info:
            reader.read()
        assert "缺少必要的邮箱字段" in str(exc_info.value)

    @allure.title("测试Recipient对空字符串邮箱抛出异常")
    def test_recipient_empty_email_validation(self):
        """
        测试Recipient类对空字符串邮箱的验证
        """
        with pytest.raises(ValueError) as exc_info:
            Recipient(email="")
        assert "无效的邮箱地址" in str(exc_info.value)

    @allure.title("测试Excel中email列存在但值为NaN抛出异常")
    def test_excel_email_column_nan_value(self, temp_dir: str):
        """
        测试Excel中email列存在但值为NaN时抛出ValueError
        """
        xlsx_path = os.path.join(temp_dir, "nan_email.xlsx")
        df = pd.DataFrame({
            "email": [pd.NA, "valid@example.com"],
            "name": ["用户A", "用户B"],
        })
        df.to_excel(xlsx_path, index=False)

        reader = DataReader(xlsx_path)
        with pytest.raises(ValueError) as exc_info:
            reader.read()
        assert "缺少必要的邮箱字段" in str(exc_info.value)

    @allure.title("测试混合大小写email列名")
    def test_case_insensitive_email_column(self, temp_dir: str):
        """
        测试email列名不区分大小写
        """
        csv_path = os.path.join(temp_dir, "mixed_case.csv")
        df = pd.DataFrame({
            "EMAIL": ["test@example.com"],
            "NAME": ["用户A"],
        })
        df.to_csv(csv_path, index=False)

        reader = DataReader(csv_path)
        recipients = reader.read()

        assert len(recipients) == 1
        assert recipients[0].email == "test@example.com"
        assert recipients[0].name == "用户A"
