package com.passwordmanager.model;

public enum PasswordCategory {
    SOCIAL("社交媒体"),
    EMAIL("邮箱"),
    FINANCE("金融"),
    SHOPPING("购物"),
    WORK("工作"),
    GAMING("游戏"),
    OTHER("其他");

    private String displayName;

    PasswordCategory(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }

    public static PasswordCategory fromDisplayName(String displayName) {
        for (PasswordCategory category : values()) {
            if (category.displayName.equals(displayName)) {
                return category;
            }
        }
        return OTHER;
    }
}
