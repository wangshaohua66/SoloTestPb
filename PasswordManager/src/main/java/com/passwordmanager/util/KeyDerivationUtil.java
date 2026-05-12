package com.passwordmanager.util;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.KeySpec;
import java.util.Base64;

public class KeyDerivationUtil {
    private static final String PBKDF2_ALGORITHM = "PBKDF2WithHmacSHA256";
    private static final int SALT_LENGTH = 32;
    private static final int ITERATION_COUNT = 100000;
    private static final int KEY_LENGTH = 256;

    public static byte[] generateSalt() {
        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[SALT_LENGTH];
        random.nextBytes(salt);
        return salt;
    }

    public static String generateSaltAsString() {
        return Base64.getEncoder().encodeToString(generateSalt());
    }

    public static byte[] deriveKey(char[] password, byte[] salt) throws NoSuchAlgorithmException, InvalidKeySpecException {
        KeySpec spec = new PBEKeySpec(password, salt, ITERATION_COUNT, KEY_LENGTH);
        SecretKeyFactory factory = SecretKeyFactory.getInstance(PBKDF2_ALGORITHM);
        return factory.generateSecret(spec).getEncoded();
    }

    public static byte[] deriveKey(char[] password, String saltBase64) throws NoSuchAlgorithmException, InvalidKeySpecException {
        byte[] salt = Base64.getDecoder().decode(saltBase64);
        return deriveKey(password, salt);
    }

    public static String deriveKeyAsString(char[] password, byte[] salt) throws NoSuchAlgorithmException, InvalidKeySpecException {
        byte[] key = deriveKey(password, salt);
        return Base64.getEncoder().encodeToString(key);
    }

    public static String deriveKeyAsString(char[] password, String saltBase64) throws NoSuchAlgorithmException, InvalidKeySpecException {
        byte[] key = deriveKey(password, saltBase64);
        return Base64.getEncoder().encodeToString(key);
    }

    public static boolean verifyPassword(char[] password, String saltBase64, String expectedHash) {
        try {
            String actualHash = deriveKeyAsString(password, saltBase64);
            return actualHash.equals(expectedHash);
        } catch (Exception e) {
            return false;
        }
    }

    public static void clearCharArray(char[] array) {
        if (array != null) {
            for (int i = 0; i < array.length; i++) {
                array[i] = '\0';
            }
        }
    }
}
