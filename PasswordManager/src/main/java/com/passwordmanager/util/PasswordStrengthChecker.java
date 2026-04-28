package com.passwordmanager.util;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Pattern;

public class PasswordStrengthChecker {
    public enum Strength {
        VERY_WEAK("非常弱", 1),
        WEAK("弱", 2),
        FAIR("一般", 3),
        STRONG("强", 4),
        VERY_STRONG("非常强", 5);

        private final String displayName;
        private final int level;

        Strength(String displayName, int level) {
            this.displayName = displayName;
            this.level = level;
        }

        public String getDisplayName() {
            return displayName;
        }

        public int getLevel() {
            return level;
        }
    }

    private static final Pattern HAS_UPPERCASE = Pattern.compile("[A-Z]");
    private static final Pattern HAS_LOWERCASE = Pattern.compile("[a-z]");
    private static final Pattern HAS_NUMBER = Pattern.compile("[0-9]");
    private static final Pattern HAS_SYMBOL = Pattern.compile("[^A-Za-z0-9]");
    private static final Pattern REPEATED_CHARS = Pattern.compile("(.)\\1{2,}");
    private static final Pattern SEQUENTIAL = Pattern.compile("(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)");
    private static final Pattern KEYBOARD_PATTERN = Pattern.compile("(qwe|wer|ert|rty|tyu|yui|uio|iop|asd|sdf|dfg|fgh|ghj|hjk|jkl|zxc|xcv|cvb|vbn|bnm)");

    private static final Set<String> COMMON_PASSWORDS = new HashSet<>(Arrays.asList(
            "password", "123456", "123456789", "qwerty", "abc123",
            "monkey", "1234567", "letmein", "trustno1", "dragon",
            "password1", "iloveyou", "sunshine", "princess", "admin",
            "welcome", "shadow", "ashley", "football", "jesus",
            "ninja", "mustang", "password123", "hello", "charlie",
            "samsung", "hannah", "amanda", "thomas", "jordan",
            "tigger", "robert", "michael", "jennifer", "joshua",
            "basketball", "andrew", "justin", "daniel", "william"
    ));

    public static Strength checkStrength(String password) {
        if (password == null || password.isEmpty()) {
            return Strength.VERY_WEAK;
        }

        int score = 0;
        int length = password.length();

        if (COMMON_PASSWORDS.contains(password.toLowerCase())) {
            return Strength.VERY_WEAK;
        }

        if (length < 6) {
            return Strength.VERY_WEAK;
        }

        if (length >= 8) score += 1;
        if (length >= 12) score += 1;
        if (length >= 16) score += 1;

        if (HAS_UPPERCASE.matcher(password).find()) score += 1;
        if (HAS_LOWERCASE.matcher(password).find()) score += 1;
        if (HAS_NUMBER.matcher(password).find()) score += 1;
        if (HAS_SYMBOL.matcher(password).find()) score += 1;

        int varietyCount = 0;
        if (HAS_UPPERCASE.matcher(password).find()) varietyCount++;
        if (HAS_LOWERCASE.matcher(password).find()) varietyCount++;
        if (HAS_NUMBER.matcher(password).find()) varietyCount++;
        if (HAS_SYMBOL.matcher(password).find()) varietyCount++;
        if (varietyCount >= 3) score += 1;
        if (varietyCount == 4) score += 1;

        if (REPEATED_CHARS.matcher(password).find()) score -= 1;
        if (SEQUENTIAL.matcher(password.toLowerCase()).find()) score -= 1;
        if (KEYBOARD_PATTERN.matcher(password.toLowerCase()).find()) score -= 1;

        if (score <= 2) {
            return Strength.VERY_WEAK;
        } else if (score <= 4) {
            return Strength.WEAK;
        } else if (score <= 6) {
            return Strength.FAIR;
        } else if (score <= 8) {
            return Strength.STRONG;
        } else {
            return Strength.VERY_STRONG;
        }
    }

    public static int getScore(String password) {
        Strength strength = checkStrength(password);
        return strength.getLevel();
    }

    public static String getStrengthDisplay(String password) {
        Strength strength = checkStrength(password);
        return strength.getDisplayName();
    }

    public static boolean isWeak(String password) {
        Strength strength = checkStrength(password);
        return strength == Strength.VERY_WEAK || strength == Strength.WEAK;
    }

    public static boolean isStrong(String password) {
        Strength strength = checkStrength(password);
        return strength == Strength.STRONG || strength == Strength.VERY_STRONG;
    }

    public static boolean containsRepeatedChars(String password) {
        return REPEATED_CHARS.matcher(password).find();
    }

    public static boolean containsSequentialChars(String password) {
        return SEQUENTIAL.matcher(password.toLowerCase()).find();
    }

    public static boolean isCommonPassword(String password) {
        return password != null && COMMON_PASSWORDS.contains(password.toLowerCase());
    }

    public static int getEntropy(String password) {
        if (password == null || password.isEmpty()) {
            return 0;
        }

        int poolSize = 0;
        if (HAS_UPPERCASE.matcher(password).find()) poolSize += 26;
        if (HAS_LOWERCASE.matcher(password).find()) poolSize += 26;
        if (HAS_NUMBER.matcher(password).find()) poolSize += 10;
        if (HAS_SYMBOL.matcher(password).find()) poolSize += 32;

        if (poolSize == 0) poolSize = 26;

        double entropy = password.length() * (Math.log(poolSize) / Math.log(2));
        return (int) Math.round(entropy);
    }
}
