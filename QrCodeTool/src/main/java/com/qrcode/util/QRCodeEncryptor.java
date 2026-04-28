package com.qrcode.util;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.PBEParameterSpec;
import java.nio.charset.StandardCharsets;
import java.security.spec.KeySpec;
import java.util.Base64;

public class QRCodeEncryptor {

    private static final String ALGORITHM = "PBEWithMD5AndDES";
    private static final byte[] SALT = {
        (byte) 0x12, (byte) 0x34, (byte) 0x56, (byte) 0x78,
        (byte) 0x9A, (byte) 0xBC, (byte) 0xDE, (byte) 0xF0
    };
    private static final int ITERATION_COUNT = 1000;
    private static final String ENCRYPTED_PREFIX = "ENC:";

    public static String encrypt(String content, String password) throws Exception {
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("密码不能为空");
        }
        
        KeySpec keySpec = new PBEKeySpec(password.toCharArray(), SALT, ITERATION_COUNT);
        SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(ALGORITHM);
        SecretKey secretKey = keyFactory.generateSecret(keySpec);
        
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new PBEParameterSpec(SALT, ITERATION_COUNT));
        
        byte[] encrypted = cipher.doFinal(content.getBytes(StandardCharsets.UTF_8));
        return ENCRYPTED_PREFIX + Base64.getEncoder().encodeToString(encrypted);
    }

    public static String decrypt(String encryptedContent, String password) throws Exception {
        if (!isEncrypted(encryptedContent)) {
            return encryptedContent;
        }
        
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("密码不能为空");
        }
        
        String base64Content = encryptedContent.substring(ENCRYPTED_PREFIX.length());
        byte[] encrypted = Base64.getDecoder().decode(base64Content);
        
        KeySpec keySpec = new PBEKeySpec(password.toCharArray(), SALT, ITERATION_COUNT);
        SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(ALGORITHM);
        SecretKey secretKey = keyFactory.generateSecret(keySpec);
        
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.DECRYPT_MODE, secretKey, new PBEParameterSpec(SALT, ITERATION_COUNT));
        
        byte[] decrypted = cipher.doFinal(encrypted);
        return new String(decrypted, StandardCharsets.UTF_8);
    }

    public static boolean isEncrypted(String content) {
        return content != null && content.startsWith(ENCRYPTED_PREFIX);
    }

    public static boolean verifyPassword(String encryptedContent, String password) {
        try {
            decrypt(encryptedContent, password);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
