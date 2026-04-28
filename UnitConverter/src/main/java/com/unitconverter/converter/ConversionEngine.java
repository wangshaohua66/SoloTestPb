package com.unitconverter.converter;

import com.unitconverter.model.UnitDefinition;

import java.math.BigDecimal;
import java.math.RoundingMode;

public class ConversionEngine {

    private static final int DEFAULT_SCALE = 10;

    public static double convert(double value, UnitDefinition fromUnit, UnitDefinition toUnit) 
            throws IllegalArgumentException {
        if (fromUnit == null || toUnit == null) {
            throw new IllegalArgumentException("单位不能为空");
        }

        if (fromUnit.getUnitType() != toUnit.getUnitType()) {
            throw new IllegalArgumentException("单位类型不匹配，无法转换");
        }

        if (fromUnit.getId().equals(toUnit.getId())) {
            return value;
        }

        double baseValue = convertToBase(value, fromUnit);
        double result = convertFromBase(baseValue, toUnit);

        return result;
    }

    public static double convertWithChain(double value, UnitDefinition... units) 
            throws IllegalArgumentException {
        if (units == null || units.length < 2) {
            throw new IllegalArgumentException("换算链至少需要两个单位");
        }

        double currentValue = value;
        for (int i = 0; i < units.length - 1; i++) {
            currentValue = convert(currentValue, units[i], units[i + 1]);
        }

        return currentValue;
    }

    private static double convertToBase(double value, UnitDefinition unit) {
        if (unit.isBaseUnit()) {
            return value;
        }

        if (unit.usesFormulaConversion()) {
            return FormulaParser.evaluate(unit.getToBaseFormula(), value);
        }

        return value * unit.getConversionFactor();
    }

    private static double convertFromBase(double baseValue, UnitDefinition unit) {
        if (unit.isBaseUnit()) {
            return baseValue;
        }

        if (unit.usesFormulaConversion()) {
            return FormulaParser.evaluate(unit.getFromBaseFormula(), baseValue);
        }

        return baseValue / unit.getConversionFactor();
    }

    public static String formatResult(double value, int decimalPlaces, boolean useScientificNotation) {
        if (Double.isInfinite(value) || Double.isNaN(value)) {
            return "无效值";
        }

        BigDecimal bd = new BigDecimal(value);
        
        if (useScientificNotation && (Math.abs(value) >= 1e6 || Math.abs(value) < 1e-6 && value != 0)) {
            return String.format("%." + decimalPlaces + "E", value);
        }

        try {
            bd = bd.setScale(decimalPlaces, RoundingMode.HALF_UP);
            return bd.stripTrailingZeros().toPlainString();
        } catch (ArithmeticException e) {
            return String.format("%." + decimalPlaces + "f", value);
        }
    }

    public static String formatResult(double value, int decimalPlaces) {
        return formatResult(value, decimalPlaces, false);
    }

    public static String formatResult(double value) {
        return formatResult(value, DEFAULT_SCALE, false);
    }

    public static double round(double value, int decimalPlaces) {
        if (decimalPlaces < 0) {
            throw new IllegalArgumentException("小数位数不能为负数");
        }

        BigDecimal bd = new BigDecimal(value);
        bd = bd.setScale(decimalPlaces, RoundingMode.HALF_UP);
        return bd.doubleValue();
    }
}
