package com.passwordmanager.util;

import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;

public class PasswordGenerator {
    public static final String UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    public static final String LOWERCASE = "abcdefghijklmnopqrstuvwxyz";
    public static final String NUMBERS = "0123456789";
    public static final String SYMBOLS = "!@#$%^&*()_+-=[]{}|;':,.<>?";
    public static final String AMBIGUOUS_CHARS = "0O1lI";

    private final SecureRandom random = new SecureRandom();
    private int length = 16;
    private boolean includeUppercase = true;
    private boolean includeLowercase = true;
    private boolean includeNumbers = true;
    private boolean includeSymbols = true;
    private boolean excludeAmbiguous = false;

    public PasswordGenerator() {
    }

    public PasswordGenerator(int length) {
        this.length = length;
    }

    public String generate() {
        if (!includeUppercase && !includeLowercase && !includeNumbers && !includeSymbols) {
            includeLowercase = true;
        }

        String characterPool = buildCharacterPool();
        if (characterPool.isEmpty()) {
            return "";
        }

        StringBuilder password = new StringBuilder();
        List<String> requiredChars = new ArrayList<>();

        if (includeUppercase) {
            String upperPool = excludeAmbiguous ? removeAmbiguous(UPPERCASE) : UPPERCASE;
            requiredChars.add(String.valueOf(upperPool.charAt(random.nextInt(upperPool.length()))));
        }
        if (includeLowercase) {
            String lowerPool = excludeAmbiguous ? removeAmbiguous(LOWERCASE) : LOWERCASE;
            requiredChars.add(String.valueOf(lowerPool.charAt(random.nextInt(lowerPool.length()))));
        }
        if (includeNumbers) {
            String numPool = excludeAmbiguous ? removeAmbiguous(NUMBERS) : NUMBERS;
            requiredChars.add(String.valueOf(numPool.charAt(random.nextInt(numPool.length()))));
        }
        if (includeSymbols) {
            requiredChars.add(String.valueOf(SYMBOLS.charAt(random.nextInt(SYMBOLS.length()))));
        }

        for (int i = 0; i < length; i++) {
            int index = random.nextInt(characterPool.length());
            password.append(characterPool.charAt(index));
        }

        for (String requiredChar : requiredChars) {
            int pos = random.nextInt(password.length());
            password.setCharAt(pos, requiredChar.charAt(0));
        }

        if (length > 1) {
            for (int i = 0; i < length; i++) {
                int j = random.nextInt(length);
                char temp = password.charAt(i);
                password.setCharAt(i, password.charAt(j));
                password.setCharAt(j, temp);
            }
        }

        return password.toString();
    }

    public List<String> generateBatch(int count) {
        List<String> passwords = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            passwords.add(generate());
        }
        return passwords;
    }

    private String buildCharacterPool() {
        StringBuilder pool = new StringBuilder();

        if (includeUppercase) {
            pool.append(excludeAmbiguous ? removeAmbiguous(UPPERCASE) : UPPERCASE);
        }
        if (includeLowercase) {
            pool.append(excludeAmbiguous ? removeAmbiguous(LOWERCASE) : LOWERCASE);
        }
        if (includeNumbers) {
            pool.append(excludeAmbiguous ? removeAmbiguous(NUMBERS) : NUMBERS);
        }
        if (includeSymbols) {
            pool.append(SYMBOLS);
        }

        return pool.toString();
    }

    private String removeAmbiguous(String input) {
        StringBuilder result = new StringBuilder();
        for (char c : input.toCharArray()) {
            if (AMBIGUOUS_CHARS.indexOf(c) == -1) {
                result.append(c);
            }
        }
        return result.toString();
    }

    public int getLength() {
        return length;
    }

    public void setLength(int length) {
        this.length = Math.max(4, Math.min(128, length));
    }

    public boolean isIncludeUppercase() {
        return includeUppercase;
    }

    public void setIncludeUppercase(boolean includeUppercase) {
        this.includeUppercase = includeUppercase;
    }

    public boolean isIncludeLowercase() {
        return includeLowercase;
    }

    public void setIncludeLowercase(boolean includeLowercase) {
        this.includeLowercase = includeLowercase;
    }

    public boolean isIncludeNumbers() {
        return includeNumbers;
    }

    public void setIncludeNumbers(boolean includeNumbers) {
        this.includeNumbers = includeNumbers;
    }

    public boolean isIncludeSymbols() {
        return includeSymbols;
    }

    public void setIncludeSymbols(boolean includeSymbols) {
        this.includeSymbols = includeSymbols;
    }

    public boolean isExcludeAmbiguous() {
        return excludeAmbiguous;
    }

    public void setExcludeAmbiguous(boolean excludeAmbiguous) {
        this.excludeAmbiguous = excludeAmbiguous;
    }
}
