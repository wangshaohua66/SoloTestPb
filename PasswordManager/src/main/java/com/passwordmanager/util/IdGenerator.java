package com.passwordmanager.util;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

public class IdGenerator {
    private static final SecureRandom random = new SecureRandom();
    private static final String HEX_CHARS = "0123456789ABCDEF";

    public static String generateUUID() {
        return UUID.randomUUID().toString();
    }

    public static String generateRandomId(int length) {
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            sb.append(HEX_CHARS.charAt(random.nextInt(HEX_CHARS.length())));
        }
        return sb.toString();
    }

    public static String generateTimestampId() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMddHHmmssSSS");
        String timestamp = LocalDateTime.now().format(formatter);
        String randomSuffix = generateRandomId(6);
        return timestamp + randomSuffix;
    }

    public static String generatePasswordEntryId() {
        return "PWD_" + generateTimestampId();
    }

    public static String generateHistoryId() {
        return "HIS_" + generateTimestampId();
    }
}
