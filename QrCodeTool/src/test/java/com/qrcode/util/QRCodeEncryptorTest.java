package com.qrcode.util;

import org.junit.Test;

import static org.junit.Assert.*;

public class QRCodeEncryptorTest {

    @Test
    public void testEncryptAndDecrypt() throws Exception {
        String originalContent = "这是需要加密的敏感内容";
        String password = "testPassword123";
        
        String encrypted = QRCodeEncryptor.encrypt(originalContent, password);
        
        assertNotNull("加密结果不应为null", encrypted);
        assertTrue("加密内容应以前缀开头", QRCodeEncryptor.isEncrypted(encrypted));
        assertNotEquals("加密内容不应与原文相同", originalContent, encrypted);
        
        String decrypted = QRCodeEncryptor.decrypt(encrypted, password);
        
        assertEquals("解密结果应与原文相同", originalContent, decrypted);
    }

    @Test
    public void testEncryptWithDifferentPasswords() throws Exception {
        String originalContent = "测试内容";
        String password1 = "password1";
        String password2 = "password2";
        
        String encrypted1 = QRCodeEncryptor.encrypt(originalContent, password1);
        String encrypted2 = QRCodeEncryptor.encrypt(originalContent, password2);
        
        assertNotNull("加密结果1不应为null", encrypted1);
        assertNotNull("加密结果2不应为null", encrypted2);
        assertNotEquals("不同密码加密结果应不同", encrypted1, encrypted2);
    }

    @Test
    public void testDecryptWithWrongPassword() {
        String originalContent = "敏感信息";
        String correctPassword = "correct123";
        String wrongPassword = "wrong456";
        
        try {
            String encrypted = QRCodeEncryptor.encrypt(originalContent, correctPassword);
            QRCodeEncryptor.decrypt(encrypted, wrongPassword);
            fail("使用错误密码解密应抛出异常");
        } catch (Exception e) {
            assertNotNull("异常不应为null", e);
        }
    }

    @Test
    public void testIsEncrypted() {
        String encryptedContent = "ENC:abcdef123456";
        String normalContent = "普通文本内容";
        
        assertTrue("加密内容应被识别", QRCodeEncryptor.isEncrypted(encryptedContent));
        assertFalse("普通内容不应被识别为加密", QRCodeEncryptor.isEncrypted(normalContent));
        assertFalse("null不应被识别为加密", QRCodeEncryptor.isEncrypted(null));
    }

    @Test
    public void testVerifyPassword() throws Exception {
        String originalContent = "验证密码测试";
        String correctPassword = "verifyPass";
        String wrongPassword = "wrongPass";
        
        String encrypted = QRCodeEncryptor.encrypt(originalContent, correctPassword);
        
        assertTrue("正确密码应返回true", QRCodeEncryptor.verifyPassword(encrypted, correctPassword));
        assertFalse("错误密码应返回false", QRCodeEncryptor.verifyPassword(encrypted, wrongPassword));
    }

    @Test
    public void testEncryptWithSpecialCharacters() throws Exception {
        String originalContent = "特殊字符: !@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`\n换行\n制表符\t中文";
        String password = "special@Pass";
        
        String encrypted = QRCodeEncryptor.encrypt(originalContent, password);
        String decrypted = QRCodeEncryptor.decrypt(encrypted, password);
        
        assertEquals("含特殊字符的内容加密解密应正确", originalContent, decrypted);
    }

    @Test
    public void testEncryptWithLongContent() throws Exception {
        StringBuilder longContent = new StringBuilder();
        for (int i = 0; i < 500; i++) {
            longContent.append("这是一段较长的测试内容。");
        }
        String password = "longContentPass";
        
        String encrypted = QRCodeEncryptor.encrypt(longContent.toString(), password);
        String decrypted = QRCodeEncryptor.decrypt(encrypted, password);
        
        assertEquals("长内容加密解密应正确", longContent.toString(), decrypted);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testEncryptWithEmptyPassword() throws Exception {
        String content = "测试内容";
        String emptyPassword = "";
        
        QRCodeEncryptor.encrypt(content, emptyPassword);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testEncryptWithNullPassword() throws Exception {
        String content = "测试内容";
        
        QRCodeEncryptor.encrypt(content, null);
    }

    @Test
    public void testDecryptNonEncryptedContent() throws Exception {
        String normalContent = "这不是加密内容";
        String password = "anyPassword";
        
        String result = QRCodeEncryptor.decrypt(normalContent, password);
        
        assertEquals("非加密内容应直接返回", normalContent, result);
    }

    @Test
    public void testEncryptDecryptChineseContent() throws Exception {
        String originalContent = "中文内容测试：我是中国人，我爱我的祖国。";
        String password = "chinese@Pass123";
        
        String encrypted = QRCodeEncryptor.encrypt(originalContent, password);
        String decrypted = QRCodeEncryptor.decrypt(encrypted, password);
        
        assertEquals("中文内容加密解密应正确", originalContent, decrypted);
    }

    @Test
    public void testEncryptDecryptEmptyContent() throws Exception {
        String emptyContent = "";
        String password = "testPass";
        
        String encrypted = QRCodeEncryptor.encrypt(emptyContent, password);
        String decrypted = QRCodeEncryptor.decrypt(encrypted, password);
        
        assertEquals("空内容加密解密应正确", emptyContent, decrypted);
    }
}
