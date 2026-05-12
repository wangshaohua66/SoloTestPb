package com.notetaking.service;

import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class EncryptionServiceTest {

    private EncryptionService encryptionService;

    @Before
    public void setUp() {
        encryptionService = new EncryptionService();
    }

    @Test
    public void testEncryptAndDecrypt() {
        String originalText = "这是一段需要加密的测试文本。Hello World!";
        String password = "testPassword123";

        String encrypted = encryptionService.encrypt(originalText, password);
        assertNotNull(encrypted);
        assertNotEquals(originalText, encrypted);

        String decrypted = encryptionService.decrypt(encrypted, password);
        assertEquals(originalText, decrypted);
    }

    @Test
    public void testDecryptWithWrongPassword() {
        String originalText = "测试文本";
        String correctPassword = "correct";
        String wrongPassword = "wrong";

        String encrypted = encryptionService.encrypt(originalText, correctPassword);
        assertNotNull(encrypted);

        assertThrows(RuntimeException.class, () -> {
            encryptionService.decrypt(encrypted, wrongPassword);
        });
    }

    @Test
    public void testHashPassword() {
        String password = "mySecurePassword123";
        String hash1 = encryptionService.hashPassword(password);
        String hash2 = encryptionService.hashPassword(password);

        assertNotNull(hash1);
        assertNotNull(hash2);
        assertEquals(hash1, hash2);
        assertNotEquals(password, hash1);
    }

    @Test
    public void testVerifyPassword() {
        String password = "testPassword";
        String hash = encryptionService.hashPassword(password);

        assertTrue(encryptionService.verifyPassword(password, hash));
        assertFalse(encryptionService.verifyPassword("wrongPassword", hash));
    }

    @Test
    public void testCanDecrypt() {
        String originalText = "测试内容";
        String password = "password";

        String encrypted = encryptionService.encrypt(originalText, password);

        assertTrue(encryptionService.canDecrypt(encrypted, password));
        assertFalse(encryptionService.canDecrypt(encrypted, "wrong"));
    }

    @Test
    public void testMultipleEncryptions() {
        String text1 = "文本1";
        String text2 = "文本2";
        String password = "password";

        String encrypted1 = encryptionService.encrypt(text1, password);
        String encrypted2 = encryptionService.encrypt(text2, password);

        assertNotEquals(encrypted1, encrypted2);

        assertEquals(text1, encryptionService.decrypt(encrypted1, password));
        assertEquals(text2, encryptionService.decrypt(encrypted2, password));
    }

    @Test
    public void testLongTextEncryption() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1000; i++) {
            sb.append("这是一段较长的测试文本。");
        }
        String longText = sb.toString();
        String password = "password";

        String encrypted = encryptionService.encrypt(longText, password);
        assertNotNull(encrypted);

        String decrypted = encryptionService.decrypt(encrypted, password);
        assertEquals(longText, decrypted);
    }

    @Test
    public void testSpecialCharactersEncryption() {
        String specialText = "!@#$%^&*()_+{}[]|\\\\:;\"'<>,.?/~`";
        String password = "password";

        String encrypted = encryptionService.encrypt(specialText, password);
        assertNotNull(encrypted);

        String decrypted = encryptionService.decrypt(encrypted, password);
        assertEquals(specialText, decrypted);
    }

    @Test
    public void testEmptyPassword() {
        String text = "测试文本";
        String emptyPassword = "";

        String encrypted = encryptionService.encrypt(text, emptyPassword);
        assertNotNull(encrypted);

        String decrypted = encryptionService.decrypt(encrypted, emptyPassword);
        assertEquals(text, decrypted);
    }
}
