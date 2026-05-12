package com.unitconverter.model;

public enum UnitSystem {
    METRIC("公制", "metric"),
    IMPERIAL("英制", "imperial"),
    US_CUSTOMARY("美制", "us_customary"),
    SI("国际单位制", "si"),
    MIXED("混合", "mixed"),
    CUSTOM("自定义", "custom");

    private final String displayName;
    private final String key;

    UnitSystem(String displayName, String key) {
        this.displayName = displayName;
        this.key = key;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getKey() {
        return key;
    }

    public static UnitSystem fromKey(String key) {
        for (UnitSystem system : values()) {
            if (system.getKey().equalsIgnoreCase(key)) {
                return system;
            }
        }
        return CUSTOM;
    }
}
