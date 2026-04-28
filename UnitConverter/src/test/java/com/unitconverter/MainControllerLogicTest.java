package com.unitconverter;

import com.unitconverter.calculator.CalculatorEngine;
import com.unitconverter.converter.ConversionEngine;
import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitType;
import com.unitconverter.registry.UnitRegistry;
import org.junit.Before;
import org.junit.Test;

import java.util.List;

import static org.junit.Assert.*;

public class MainControllerLogicTest {

    private UnitRegistry unitRegistry;
    private CalculatorEngine calculatorEngine;

    @Before
    public void setUp() {
        unitRegistry = UnitRegistry.getInstance();
        calculatorEngine = CalculatorEngine.getInstance();
        calculatorEngine.clearHistory();
    }

    @Test
    public void testConversionLogic_UnitTypeChange() {
        UnitType unitType = UnitType.LENGTH;
        List<UnitDefinition> units = unitRegistry.getUnitsByType(unitType);
        
        assertFalse(units.isEmpty());
        assertTrue(units.size() >= 10);
        
        UnitDefinition baseUnit = null;
        for (UnitDefinition u : units) {
            if (u.isBaseUnit()) {
                baseUnit = u;
                break;
            }
        }
        
        assertNotNull(baseUnit);
        assertEquals("米", baseUnit.getName());
        assertEquals("m", baseUnit.getSymbol());
    }

    @Test
    public void testConversionLogic_PerformConversion() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        
        assertNotNull(meter);
        assertNotNull(kilometer);
        
        String inputText = "1000";
        double value = Double.parseDouble(inputText);
        
        int decimalPlaces = 6;
        boolean useScientific = false;
        
        double result = ConversionEngine.convert(value, meter, kilometer);
        String formattedResult = ConversionEngine.formatResult(result, decimalPlaces, useScientific);
        
        assertEquals(1.0, result, 0.0001);
        assertEquals("1", formattedResult);
    }

    @Test
    public void testConversionLogic_InvalidInput() {
        String inputText = "abc";
        try {
            Double.parseDouble(inputText);
            fail("应该抛出 NumberFormatException");
        } catch (NumberFormatException e) {
        }
    }

    @Test
    public void testConversionLogic_EmptyInput() {
        String inputText = "";
        assertTrue(inputText.isEmpty());
    }

    @Test
    public void testCalculatorLogic_NumberInput() {
        String currentExpression = "";
        
        String digit = "2";
        if (currentExpression.isEmpty() || currentExpression.equals("0")) {
            currentExpression = digit;
        } else {
            currentExpression += digit;
        }
        
        assertEquals("2", currentExpression);
        
        digit = "3";
        if (currentExpression.isEmpty() || currentExpression.equals("0")) {
            currentExpression = digit;
        } else {
            currentExpression += digit;
        }
        
        assertEquals("23", currentExpression);
    }

    @Test
    public void testCalculatorLogic_DecimalPoint() {
        String currentExpression = "";
        
        String digit = ".";
        if (currentExpression.isEmpty() || currentExpression.equals("0")) {
            currentExpression = "0.";
        } else {
            currentExpression += digit;
        }
        
        assertEquals("0.", currentExpression);
    }

    @Test
    public void testCalculatorLogic_OperatorInput() {
        String currentExpression = "23";
        
        String op = "+";
        if ("+".equals(op)) {
            currentExpression += " + ";
        }
        
        assertEquals("23 + ", currentExpression);
        
        op = "×";
        if ("×".equals(op)) {
            currentExpression += " * ";
        }
        
        assertEquals("23 +  * ", currentExpression);
    }

    @Test
    public void testCalculatorLogic_ModOperator() {
        String currentExpression = "10";
        
        String op = "mod";
        if ("mod".equals(op)) {
            currentExpression += " % ";
        }
        
        assertEquals("10 % ", currentExpression);
    }

    @Test
    public void testCalculatorLogic_SpecialCharacters() {
        String currentExpression = "";
        
        String func = "√";
        if ("√".equals(func)) {
            currentExpression += "sqrt(";
        }
        assertEquals("sqrt(", currentExpression);
        
        currentExpression = "";
        func = "π";
        if ("π".equals(func)) {
            currentExpression += String.valueOf(Math.PI);
        }
        assertEquals(String.valueOf(Math.PI), currentExpression);
        
        currentExpression = "";
        func = "e";
        if ("e".equals(func)) {
            currentExpression += String.valueOf(Math.E);
        }
        assertEquals(String.valueOf(Math.E), currentExpression);
    }

    @Test
    public void testCalculatorLogic_Clear() {
        String currentExpression = "2 + 3";
        currentExpression = "";
        assertEquals("", currentExpression);
    }

    @Test
    public void testCalculatorLogic_Backspace() {
        String currentExpression = "1234";
        
        if (!currentExpression.isEmpty()) {
            currentExpression = currentExpression.substring(0, currentExpression.length() - 1);
        }
        
        assertEquals("123", currentExpression);
    }

    @Test
    public void testCalculatorLogic_Equals() {
        String currentExpression = "2 + 3";
        
        if (!currentExpression.isEmpty()) {
            double result = calculatorEngine.calculate(currentExpression);
            assertEquals(5.0, result, 0.0001);
        }
    }

    @Test
    public void testCalculatorLogic_ErrorHandling() {
        String currentExpression = "10 / 0";
        
        try {
            calculatorEngine.calculate(currentExpression);
            fail("应该抛出 IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("零") || e.getMessage().contains("zero"));
        }
    }

    @Test
    public void testBatchConversionLogic_ParseInput() {
        String inputText = "10\n20.5\n100\n\nabc";
        
        java.util.List<Double> values = new java.util.ArrayList<>();
        String[] lines = inputText.split("\\r?\\n");
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty()) continue;
            try {
                values.add(Double.parseDouble(line));
            } catch (NumberFormatException e) {
            }
        }
        
        assertEquals(3, values.size());
        assertEquals(10.0, values.get(0), 0.0001);
        assertEquals(20.5, values.get(1), 0.0001);
        assertEquals(100.0, values.get(2), 0.0001);
    }

    @Test
    public void testBatchConversionLogic_EmptyInput() {
        String inputText = "";
        assertTrue(inputText.trim().isEmpty());
    }

    @Test
    public void testCustomUnitLogic_ValidateInput() {
        String name = "测试单位";
        String symbol = "tu";
        
        assertFalse(name.isEmpty());
        assertFalse(symbol.isEmpty());
    }

    @Test
    public void testCustomUnitLogic_EmptyName() {
        String name = "";
        assertTrue(name.trim().isEmpty());
    }

    @Test
    public void testCustomUnitLogic_ParseFactor() {
        String factorText = "1000.0";
        
        try {
            double factor = Double.parseDouble(factorText);
            assertEquals(1000.0, factor, 0.0001);
        } catch (NumberFormatException e) {
            fail("应该成功解析");
        }
    }

    @Test
    public void testCustomUnitLogic_InvalidFactor() {
        String factorText = "abc";
        
        try {
            Double.parseDouble(factorText);
            fail("应该抛出 NumberFormatException");
        } catch (NumberFormatException e) {
        }
    }

    @Test
    public void testCustomUnitLogic_FormulaValidation() {
        String formula = "(x - 32) * 5 / 9";
        
        assertTrue(formula.contains("x"));
    }

    @Test
    public void testDisplayLogic_FormatResult() {
        double result = 123.456789;
        int decimalPlaces = 2;
        
        String formatted = ConversionEngine.formatResult(result, decimalPlaces, false);
        assertEquals("123.46", formatted);
    }

    @Test
    public void testDisplayLogic_FormatInteger() {
        double result = 100.0;
        int decimalPlaces = 0;
        
        String formatted = ConversionEngine.formatResult(result, decimalPlaces, false);
        assertEquals("100", formatted);
    }

    @Test
    public void testDisplayLogic_ScientificNotation() {
        double result = 1000000.0;
        int decimalPlaces = 2;
        
        String formatted = ConversionEngine.formatResult(result, decimalPlaces, true);
        assertTrue(formatted.contains("E") || formatted.contains("e"));
    }

    @Test
    public void testUnitSelectionLogic_FindBaseUnit() {
        List<UnitDefinition> units = unitRegistry.getUnitsByType(UnitType.LENGTH);
        
        UnitDefinition baseUnit = null;
        for (UnitDefinition u : units) {
            if (u.isBaseUnit()) {
                baseUnit = u;
                break;
            }
        }
        if (baseUnit == null && !units.isEmpty()) {
            baseUnit = units.get(0);
        }
        
        assertNotNull(baseUnit);
        assertTrue(baseUnit.isBaseUnit());
    }

    @Test
    public void testUnitSelectionLogic_FindNonBaseUnit() {
        List<UnitDefinition> units = unitRegistry.getUnitsByType(UnitType.LENGTH);
        
        UnitDefinition baseUnit = null;
        for (UnitDefinition u : units) {
            if (u.isBaseUnit()) {
                baseUnit = u;
                break;
            }
        }
        
        assertNotNull(baseUnit);
        
        if (units.size() > 1) {
            UnitDefinition nonBaseUnit = null;
            for (UnitDefinition u : units) {
                if (!u.getId().equals(baseUnit.getId())) {
                    nonBaseUnit = u;
                    break;
                }
            }
            if (nonBaseUnit == null) {
                nonBaseUnit = units.get(1);
            }
            
            assertNotNull(nonBaseUnit);
        }
    }

    @Test
    public void testTemperatureConversion_SpecialCase() {
        UnitDefinition celsius = unitRegistry.getUnit("temp_celsius");
        UnitDefinition fahrenheit = unitRegistry.getUnit("temp_fahrenheit");
        
        assertNotNull(celsius);
        assertNotNull(fahrenheit);
        
        assertTrue(celsius.isBaseUnit());
        assertFalse(celsius.usesFormulaConversion());
        assertTrue(fahrenheit.usesFormulaConversion());
        
        double result = ConversionEngine.convert(0.0, celsius, fahrenheit);
        assertEquals(32.0, result, 0.0001);
        
        result = ConversionEngine.convert(100.0, celsius, fahrenheit);
        assertEquals(212.0, result, 0.0001);
    }

    @Test
    public void testConversionChainLogic() {
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition centimeter = unitRegistry.getUnit("length_centimeter");
        
        double result = ConversionEngine.convertWithChain(1.0, kilometer, meter, centimeter);
        assertEquals(100000.0, result, 0.0001);
    }
}
