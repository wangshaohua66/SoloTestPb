package com.unitconverter.model;

import java.util.Arrays;
import java.util.List;

public enum UnitType {
    LENGTH("长度", "length"),
    WEIGHT("重量", "weight"),
    TEMPERATURE("温度", "temperature"),
    AREA("面积", "area"),
    VOLUME("体积", "volume"),
    SPEED("速度", "speed"),
    TIME("时间", "time"),
    DATA_STORAGE("数据存储", "data_storage"),
    PRESSURE("压力", "pressure"),
    POWER("功率", "power"),
    CUSTOM("自定义", "custom");

    private final String displayName;
    private final String key;

    UnitType(String displayName, String key) {
        this.displayName = displayName;
        this.key = key;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getKey() {
        return key;
    }

    public static List<UnitType> getBasicTypes() {
        return Arrays.asList(LENGTH, WEIGHT, TEMPERATURE, AREA, VOLUME);
    }

    public static List<UnitType> getAdvancedTypes() {
        return Arrays.asList(SPEED, TIME, DATA_STORAGE, PRESSURE, POWER);
    }

    public static UnitType fromKey(String key) {
        for (UnitType type : values()) {
            if (type.getKey().equalsIgnoreCase(key)) {
                return type;
            }
        }
        return CUSTOM;
    }
}
