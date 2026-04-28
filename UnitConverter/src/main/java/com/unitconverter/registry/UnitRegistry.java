package com.unitconverter.registry;

import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitSystem;
import com.unitconverter.model.UnitType;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class UnitRegistry {
    private static UnitRegistry instance;
    private final Map<String, UnitDefinition> units;
    private final Map<UnitType, List<UnitDefinition>> unitsByType;

    private UnitRegistry() {
        units = new ConcurrentHashMap<>();
        unitsByType = new ConcurrentHashMap<>();
        initializePredefinedUnits();
    }

    public static synchronized UnitRegistry getInstance() {
        if (instance == null) {
            instance = new UnitRegistry();
        }
        return instance;
    }

    private void initializePredefinedUnits() {
        initializeLengthUnits();
        initializeWeightUnits();
        initializeTemperatureUnits();
        initializeAreaUnits();
        initializeVolumeUnits();
        initializeSpeedUnits();
        initializeTimeUnits();
        initializeDataStorageUnits();
        initializePressureUnits();
        initializePowerUnits();
    }

    private void initializeLengthUnits() {
        UnitDefinition meter = new UnitDefinition(
            "length_meter", "米", "m", UnitType.LENGTH, UnitSystem.METRIC, 1.0, true
        );
        addUnit(meter);

        addUnit(new UnitDefinition(
            "length_kilometer", "千米", "km", UnitType.LENGTH, UnitSystem.METRIC, 1000.0, false
        ));
        addUnit(new UnitDefinition(
            "length_centimeter", "厘米", "cm", UnitType.LENGTH, UnitSystem.METRIC, 0.01, false
        ));
        addUnit(new UnitDefinition(
            "length_millimeter", "毫米", "mm", UnitType.LENGTH, UnitSystem.METRIC, 0.001, false
        ));
        addUnit(new UnitDefinition(
            "length_micrometer", "微米", "μm", UnitType.LENGTH, UnitSystem.METRIC, 1e-6, false
        ));
        addUnit(new UnitDefinition(
            "length_nanometer", "纳米", "nm", UnitType.LENGTH, UnitSystem.METRIC, 1e-9, false
        ));

        addUnit(new UnitDefinition(
            "length_foot", "英尺", "ft", UnitType.LENGTH, UnitSystem.IMPERIAL, 0.3048, false
        ));
        addUnit(new UnitDefinition(
            "length_inch", "英寸", "in", UnitType.LENGTH, UnitSystem.IMPERIAL, 0.0254, false
        ));
        addUnit(new UnitDefinition(
            "length_yard", "码", "yd", UnitType.LENGTH, UnitSystem.IMPERIAL, 0.9144, false
        ));
        addUnit(new UnitDefinition(
            "length_mile", "英里", "mi", UnitType.LENGTH, UnitSystem.IMPERIAL, 1609.344, false
        ));
        addUnit(new UnitDefinition(
            "length_nautical_mile", "海里", "nmi", UnitType.LENGTH, UnitSystem.IMPERIAL, 1852.0, false
        ));

        addUnit(new UnitDefinition(
            "length_fathom", "英寻", "fathom", UnitType.LENGTH, UnitSystem.IMPERIAL, 1.8288, false
        ));
        addUnit(new UnitDefinition(
            "length_furlong", "弗隆", "furlong", UnitType.LENGTH, UnitSystem.IMPERIAL, 201.168, false
        ));
    }

    private void initializeWeightUnits() {
        UnitDefinition kilogram = new UnitDefinition(
            "weight_kilogram", "千克", "kg", UnitType.WEIGHT, UnitSystem.METRIC, 1.0, true
        );
        addUnit(kilogram);

        addUnit(new UnitDefinition(
            "weight_gram", "克", "g", UnitType.WEIGHT, UnitSystem.METRIC, 0.001, false
        ));
        addUnit(new UnitDefinition(
            "weight_milligram", "毫克", "mg", UnitType.WEIGHT, UnitSystem.METRIC, 1e-6, false
        ));
        addUnit(new UnitDefinition(
            "weight_microgram", "微克", "μg", UnitType.WEIGHT, UnitSystem.METRIC, 1e-9, false
        ));
        addUnit(new UnitDefinition(
            "weight_metric_ton", "公吨", "t", UnitType.WEIGHT, UnitSystem.METRIC, 1000.0, false
        ));

        addUnit(new UnitDefinition(
            "weight_pound", "磅", "lb", UnitType.WEIGHT, UnitSystem.IMPERIAL, 0.45359237, false
        ));
        addUnit(new UnitDefinition(
            "weight_ounce", "盎司", "oz", UnitType.WEIGHT, UnitSystem.IMPERIAL, 0.0283495, false
        ));
        addUnit(new UnitDefinition(
            "weight_stone", "英石", "stone", UnitType.WEIGHT, UnitSystem.IMPERIAL, 6.35029, false
        ));
        addUnit(new UnitDefinition(
            "weight_long_ton", "长吨", "long ton", UnitType.WEIGHT, UnitSystem.IMPERIAL, 1016.047, false
        ));
        addUnit(new UnitDefinition(
            "weight_short_ton", "短吨", "short ton", UnitType.WEIGHT, UnitSystem.US_CUSTOMARY, 907.185, false
        ));

        addUnit(new UnitDefinition(
            "weight_carat", "克拉", "carat", UnitType.WEIGHT, UnitSystem.MIXED, 0.0002, false
        ));
        addUnit(new UnitDefinition(
            "weight_grain", "格令", "gr", UnitType.WEIGHT, UnitSystem.IMPERIAL, 6.479891e-5, false
        ));
    }

    private void initializeTemperatureUnits() {
        UnitDefinition celsius = new UnitDefinition(
            "temp_celsius", "摄氏度", "°C", UnitType.TEMPERATURE, UnitSystem.METRIC, 1.0, true
        );
        celsius.setBaseUnit(true);
        addUnit(celsius);

        UnitDefinition fahrenheit = new UnitDefinition();
        fahrenheit.setId("temp_fahrenheit");
        fahrenheit.setName("华氏度");
        fahrenheit.setSymbol("°F");
        fahrenheit.setUnitType(UnitType.TEMPERATURE);
        fahrenheit.setUnitSystem(UnitSystem.US_CUSTOMARY);
        fahrenheit.setToBaseFormula("(x - 32) * 5 / 9");
        fahrenheit.setFromBaseFormula("x * 9 / 5 + 32");
        fahrenheit.setBaseUnitId("temp_celsius");
        addUnit(fahrenheit);

        UnitDefinition kelvin = new UnitDefinition();
        kelvin.setId("temp_kelvin");
        kelvin.setName("开尔文");
        kelvin.setSymbol("K");
        kelvin.setUnitType(UnitType.TEMPERATURE);
        kelvin.setUnitSystem(UnitSystem.SI);
        kelvin.setToBaseFormula("x - 273.15");
        kelvin.setFromBaseFormula("x + 273.15");
        kelvin.setBaseUnitId("temp_celsius");
        addUnit(kelvin);

        UnitDefinition rankine = new UnitDefinition();
        rankine.setId("temp_rankine");
        rankine.setName("兰金度");
        rankine.setSymbol("°R");
        rankine.setUnitType(UnitType.TEMPERATURE);
        rankine.setUnitSystem(UnitSystem.US_CUSTOMARY);
        rankine.setToBaseFormula("(x - 491.67) * 5 / 9");
        rankine.setFromBaseFormula("x * 9 / 5 + 491.67");
        rankine.setBaseUnitId("temp_celsius");
        addUnit(rankine);
    }

    private void initializeAreaUnits() {
        UnitDefinition squareMeter = new UnitDefinition(
            "area_square_meter", "平方米", "m²", UnitType.AREA, UnitSystem.METRIC, 1.0, true
        );
        addUnit(squareMeter);

        addUnit(new UnitDefinition(
            "area_square_kilometer", "平方千米", "km²", UnitType.AREA, UnitSystem.METRIC, 1000000.0, false
        ));
        addUnit(new UnitDefinition(
            "area_square_centimeter", "平方厘米", "cm²", UnitType.AREA, UnitSystem.METRIC, 0.0001, false
        ));
        addUnit(new UnitDefinition(
            "area_square_millimeter", "平方毫米", "mm²", UnitType.AREA, UnitSystem.METRIC, 0.000001, false
        ));

        addUnit(new UnitDefinition(
            "area_hectare", "公顷", "ha", UnitType.AREA, UnitSystem.METRIC, 10000.0, false
        ));
        addUnit(new UnitDefinition(
            "area_are", "公亩", "are", UnitType.AREA, UnitSystem.METRIC, 100.0, false
        ));

        addUnit(new UnitDefinition(
            "area_square_foot", "平方英尺", "ft²", UnitType.AREA, UnitSystem.IMPERIAL, 0.092903, false
        ));
        addUnit(new UnitDefinition(
            "area_square_inch", "平方英寸", "in²", UnitType.AREA, UnitSystem.IMPERIAL, 0.00064516, false
        ));
        addUnit(new UnitDefinition(
            "area_square_yard", "平方码", "yd²", UnitType.AREA, UnitSystem.IMPERIAL, 0.836127, false
        ));
        addUnit(new UnitDefinition(
            "area_square_mile", "平方英里", "mi²", UnitType.AREA, UnitSystem.IMPERIAL, 2589988.11, false
        ));
        addUnit(new UnitDefinition(
            "area_acre", "英亩", "acre", UnitType.AREA, UnitSystem.IMPERIAL, 4046.86, false
        ));
    }

    private void initializeVolumeUnits() {
        UnitDefinition cubicMeter = new UnitDefinition(
            "volume_cubic_meter", "立方米", "m³", UnitType.VOLUME, UnitSystem.METRIC, 1.0, true
        );
        addUnit(cubicMeter);

        addUnit(new UnitDefinition(
            "volume_liter", "升", "L", UnitType.VOLUME, UnitSystem.METRIC, 0.001, false
        ));
        addUnit(new UnitDefinition(
            "volume_milliliter", "毫升", "mL", UnitType.VOLUME, UnitSystem.METRIC, 0.000001, false
        ));
        addUnit(new UnitDefinition(
            "volume_centiliter", "厘升", "cL", UnitType.VOLUME, UnitSystem.METRIC, 0.00001, false
        ));
        addUnit(new UnitDefinition(
            "volume_deciliter", "分升", "dL", UnitType.VOLUME, UnitSystem.METRIC, 0.0001, false
        ));

        addUnit(new UnitDefinition(
            "volume_cubic_centimeter", "立方厘米", "cm³", UnitType.VOLUME, UnitSystem.METRIC, 0.000001, false
        ));
        addUnit(new UnitDefinition(
            "volume_cubic_millimeter", "立方毫米", "mm³", UnitType.VOLUME, UnitSystem.METRIC, 1e-9, false
        ));

        addUnit(new UnitDefinition(
            "volume_gallon_uk", "英制加仑", "gal (UK)", UnitType.VOLUME, UnitSystem.IMPERIAL, 0.00454609, false
        ));
        addUnit(new UnitDefinition(
            "volume_gallon_us", "美制加仑", "gal (US)", UnitType.VOLUME, UnitSystem.US_CUSTOMARY, 0.00378541, false
        ));
        addUnit(new UnitDefinition(
            "volume_quart_uk", "英制夸脱", "qt (UK)", UnitType.VOLUME, UnitSystem.IMPERIAL, 0.00113652, false
        ));
        addUnit(new UnitDefinition(
            "volume_quart_us", "美制夸脱", "qt (US)", UnitType.VOLUME, UnitSystem.US_CUSTOMARY, 0.000946353, false
        ));
        addUnit(new UnitDefinition(
            "volume_pint_uk", "英制品脱", "pt (UK)", UnitType.VOLUME, UnitSystem.IMPERIAL, 0.000568261, false
        ));
        addUnit(new UnitDefinition(
            "volume_pint_us", "美制品脱", "pt (US)", UnitType.VOLUME, UnitSystem.US_CUSTOMARY, 0.000473176, false
        ));
        addUnit(new UnitDefinition(
            "volume_fluid_ounce_uk", "英制液盎司", "fl oz (UK)", UnitType.VOLUME, UnitSystem.IMPERIAL, 2.84131e-5, false
        ));
        addUnit(new UnitDefinition(
            "volume_fluid_ounce_us", "美制液盎司", "fl oz (US)", UnitType.VOLUME, UnitSystem.US_CUSTOMARY, 2.95735e-5, false
        ));

        addUnit(new UnitDefinition(
            "volume_cubic_foot", "立方英尺", "ft³", UnitType.VOLUME, UnitSystem.IMPERIAL, 0.0283168, false
        ));
        addUnit(new UnitDefinition(
            "volume_cubic_inch", "立方英寸", "in³", UnitType.VOLUME, UnitSystem.IMPERIAL, 1.63871e-5, false
        ));
        addUnit(new UnitDefinition(
            "volume_cubic_yard", "立方码", "yd³", UnitType.VOLUME, UnitSystem.IMPERIAL, 0.764555, false
        ));
    }

    private void initializeSpeedUnits() {
        UnitDefinition meterPerSecond = new UnitDefinition(
            "speed_mps", "米/秒", "m/s", UnitType.SPEED, UnitSystem.METRIC, 1.0, true
        );
        addUnit(meterPerSecond);

        addUnit(new UnitDefinition(
            "speed_kph", "千米/小时", "km/h", UnitType.SPEED, UnitSystem.METRIC, 0.277778, false
        ));
        addUnit(new UnitDefinition(
            "speed_mph", "英里/小时", "mph", UnitType.SPEED, UnitSystem.IMPERIAL, 0.44704, false
        ));
        addUnit(new UnitDefinition(
            "speed_knot", "节", "kn", UnitType.SPEED, UnitSystem.IMPERIAL, 0.514444, false
        ));
        addUnit(new UnitDefinition(
            "speed_ftps", "英尺/秒", "ft/s", UnitType.SPEED, UnitSystem.IMPERIAL, 0.3048, false
        ));
        addUnit(new UnitDefinition(
            "speed_mach", "马赫", "Mach", UnitType.SPEED, UnitSystem.MIXED, 340.29, false
        ));
    }

    private void initializeTimeUnits() {
        UnitDefinition second = new UnitDefinition(
            "time_second", "秒", "s", UnitType.TIME, UnitSystem.SI, 1.0, true
        );
        addUnit(second);

        addUnit(new UnitDefinition(
            "time_millisecond", "毫秒", "ms", UnitType.TIME, UnitSystem.SI, 0.001, false
        ));
        addUnit(new UnitDefinition(
            "time_microsecond", "微秒", "μs", UnitType.TIME, UnitSystem.SI, 1e-6, false
        ));
        addUnit(new UnitDefinition(
            "time_nanosecond", "纳秒", "ns", UnitType.TIME, UnitSystem.SI, 1e-9, false
        ));

        addUnit(new UnitDefinition(
            "time_minute", "分钟", "min", UnitType.TIME, UnitSystem.MIXED, 60.0, false
        ));
        addUnit(new UnitDefinition(
            "time_hour", "小时", "h", UnitType.TIME, UnitSystem.MIXED, 3600.0, false
        ));
        addUnit(new UnitDefinition(
            "time_day", "天", "day", UnitType.TIME, UnitSystem.MIXED, 86400.0, false
        ));
        addUnit(new UnitDefinition(
            "time_week", "周", "week", UnitType.TIME, UnitSystem.MIXED, 604800.0, false
        ));
        addUnit(new UnitDefinition(
            "time_month", "月(30天)", "month", UnitType.TIME, UnitSystem.MIXED, 2592000.0, false
        ));
        addUnit(new UnitDefinition(
            "time_year", "年(365天)", "year", UnitType.TIME, UnitSystem.MIXED, 31536000.0, false
        ));
    }

    private void initializeDataStorageUnits() {
        UnitDefinition byteUnit = new UnitDefinition(
            "data_byte", "字节", "B", UnitType.DATA_STORAGE, UnitSystem.SI, 1.0, true
        );
        addUnit(byteUnit);

        addUnit(new UnitDefinition(
            "data_bit", "比特", "bit", UnitType.DATA_STORAGE, UnitSystem.SI, 0.125, false
        ));
        addUnit(new UnitDefinition(
            "data_kilobyte", "千字节", "KB", UnitType.DATA_STORAGE, UnitSystem.SI, 1024.0, false
        ));
        addUnit(new UnitDefinition(
            "data_megabyte", "兆字节", "MB", UnitType.DATA_STORAGE, UnitSystem.SI, 1048576.0, false
        ));
        addUnit(new UnitDefinition(
            "data_gigabyte", "吉字节", "GB", UnitType.DATA_STORAGE, UnitSystem.SI, 1073741824.0, false
        ));
        addUnit(new UnitDefinition(
            "data_terabyte", "太字节", "TB", UnitType.DATA_STORAGE, UnitSystem.SI, 1099511627776.0, false
        ));
        addUnit(new UnitDefinition(
            "data_petabyte", "拍字节", "PB", UnitType.DATA_STORAGE, UnitSystem.SI, 1125899906842624.0, false
        ));
        addUnit(new UnitDefinition(
            "data_exabyte", "艾字节", "EB", UnitType.DATA_STORAGE, UnitSystem.SI, 1152921504606846976.0, false
        ));

        addUnit(new UnitDefinition(
            "data_kibibyte", "千比字节", "KiB", UnitType.DATA_STORAGE, UnitSystem.SI, 1024.0, false
        ));
        addUnit(new UnitDefinition(
            "data_mebibyte", "兆比字节", "MiB", UnitType.DATA_STORAGE, UnitSystem.SI, 1048576.0, false
        ));
        addUnit(new UnitDefinition(
            "data_gibibyte", "吉比字节", "GiB", UnitType.DATA_STORAGE, UnitSystem.SI, 1073741824.0, false
        ));
    }

    private void initializePressureUnits() {
        UnitDefinition pascal = new UnitDefinition(
            "pressure_pascal", "帕斯卡", "Pa", UnitType.PRESSURE, UnitSystem.SI, 1.0, true
        );
        addUnit(pascal);

        addUnit(new UnitDefinition(
            "pressure_kilopascal", "千帕", "kPa", UnitType.PRESSURE, UnitSystem.SI, 1000.0, false
        ));
        addUnit(new UnitDefinition(
            "pressure_megapascal", "兆帕", "MPa", UnitType.PRESSURE, UnitSystem.SI, 1000000.0, false
        ));
        addUnit(new UnitDefinition(
            "pressure_bar", "巴", "bar", UnitType.PRESSURE, UnitSystem.METRIC, 100000.0, false
        ));
        addUnit(new UnitDefinition(
            "pressure_atmosphere", "标准大气压", "atm", UnitType.PRESSURE, UnitSystem.MIXED, 101325.0, false
        ));
        addUnit(new UnitDefinition(
            "pressure_psi", "磅/平方英寸", "psi", UnitType.PRESSURE, UnitSystem.IMPERIAL, 6894.76, false
        ));
        addUnit(new UnitDefinition(
            "pressure_mmhg", "毫米汞柱", "mmHg", UnitType.PRESSURE, UnitSystem.MIXED, 133.322, false
        ));
        addUnit(new UnitDefinition(
            "pressure_inhg", "英寸汞柱", "inHg", UnitType.PRESSURE, UnitSystem.IMPERIAL, 3386.39, false
        ));
        addUnit(new UnitDefinition(
            "pressure_torr", "托", "Torr", UnitType.PRESSURE, UnitSystem.MIXED, 133.322, false
        ));
    }

    private void initializePowerUnits() {
        UnitDefinition watt = new UnitDefinition(
            "power_watt", "瓦特", "W", UnitType.POWER, UnitSystem.SI, 1.0, true
        );
        addUnit(watt);

        addUnit(new UnitDefinition(
            "power_milliwatt", "毫瓦", "mW", UnitType.POWER, UnitSystem.SI, 0.001, false
        ));
        addUnit(new UnitDefinition(
            "power_kilowatt", "千瓦", "kW", UnitType.POWER, UnitSystem.SI, 1000.0, false
        ));
        addUnit(new UnitDefinition(
            "power_megawatt", "兆瓦", "MW", UnitType.POWER, UnitSystem.SI, 1000000.0, false
        ));
        addUnit(new UnitDefinition(
            "power_gigawatt", "吉瓦", "GW", UnitType.POWER, UnitSystem.SI, 1000000000.0, false
        ));

        addUnit(new UnitDefinition(
            "power_horsepower_metric", "公制马力", "PS", UnitType.POWER, UnitSystem.METRIC, 735.499, false
        ));
        addUnit(new UnitDefinition(
            "power_horsepower_imperial", "英制马力", "hp", UnitType.POWER, UnitSystem.IMPERIAL, 745.7, false
        ));
        addUnit(new UnitDefinition(
            "power_btu_per_hour", "英热单位/小时", "BTU/h", UnitType.POWER, UnitSystem.IMPERIAL, 0.293071, false
        ));
        addUnit(new UnitDefinition(
            "power_calorie_per_second", "卡路里/秒", "cal/s", UnitType.POWER, UnitSystem.METRIC, 4.1868, false
        ));
    }

    public void addUnit(UnitDefinition unit) {
        if (unit == null || unit.getId() == null || unit.getId().isEmpty()) {
            return;
        }

        units.put(unit.getId(), unit);

        unitsByType.computeIfAbsent(unit.getUnitType(), k -> new ArrayList<>()).add(unit);
    }

    public void removeUnit(String unitId) {
        UnitDefinition unit = units.get(unitId);
        if (unit != null) {
            units.remove(unitId);
            List<UnitDefinition> typeUnits = unitsByType.get(unit.getUnitType());
            if (typeUnits != null) {
                typeUnits.remove(unit);
            }
        }
    }

    public UnitDefinition getUnit(String unitId) {
        UnitDefinition unit = units.get(unitId);
        return unit != null ? unit.clone() : null;
    }

    public List<UnitDefinition> getUnitsByType(UnitType type) {
        List<UnitDefinition> typeUnits = unitsByType.get(type);
        if (typeUnits == null) {
            return Collections.emptyList();
        }

        List<UnitDefinition> result = new ArrayList<>();
        for (UnitDefinition unit : typeUnits) {
            result.add(unit.clone());
        }
        return result;
    }

    public List<UnitDefinition> getAllUnits() {
        List<UnitDefinition> result = new ArrayList<>();
        for (UnitDefinition unit : units.values()) {
            result.add(unit.clone());
        }
        return result;
    }

    public List<UnitDefinition> getCustomUnits() {
        List<UnitDefinition> result = new ArrayList<>();
        for (UnitDefinition unit : units.values()) {
            if (unit.isCustom()) {
                result.add(unit.clone());
            }
        }
        return result;
    }

    public List<UnitDefinition> getFavoriteUnits() {
        List<UnitDefinition> result = new ArrayList<>();
        for (UnitDefinition unit : units.values()) {
            if (unit.isFavorite()) {
                result.add(unit.clone());
            }
        }
        return result;
    }

    public void updateUnitFavorite(String unitId, boolean isFavorite) {
        UnitDefinition unit = units.get(unitId);
        if (unit != null) {
            unit.setFavorite(isFavorite);
        }
    }

    public boolean hasUnit(String unitId) {
        return units.containsKey(unitId);
    }

    public Set<UnitType> getAvailableTypes() {
        return unitsByType.keySet();
    }
}
