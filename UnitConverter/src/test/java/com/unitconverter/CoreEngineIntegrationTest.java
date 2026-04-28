package com.unitconverter;

import com.unitconverter.calculator.CalculatorEngine;
import com.unitconverter.converter.ConversionEngine;
import com.unitconverter.manager.BatchConversionManager;
import com.unitconverter.manager.CustomUnitManager;
import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitSystem;
import com.unitconverter.model.UnitType;
import com.unitconverter.registry.UnitRegistry;
import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.*;

public class CoreEngineIntegrationTest {

    private UnitRegistry unitRegistry;
    private CalculatorEngine calculatorEngine;
    private BatchConversionManager batchManager;
    private CustomUnitManager customManager;

    @Before
    public void setUp() {
        unitRegistry = UnitRegistry.getInstance();
        calculatorEngine = CalculatorEngine.getInstance();
        batchManager = BatchConversionManager.getInstance();
        customManager = CustomUnitManager.getInstance();
        
        batchManager.clearHistory();
        for (UnitDefinition unit : customManager.getCustomUnits()) {
            unitRegistry.removeUnit(unit.getId());
        }
    }

    @Test
    public void testUnitRegistryInitialization() {
        assertNotNull(unitRegistry);
        
        List<UnitDefinition> lengthUnits = unitRegistry.getUnitsByType(UnitType.LENGTH);
        assertFalse(lengthUnits.isEmpty());
        assertTrue(lengthUnits.size() >= 10);
        
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        assertNotNull(meter);
        assertEquals("米", meter.getName());
        assertEquals("m", meter.getSymbol());
        assertTrue(meter.isBaseUnit());
    }

    @Test
    public void testAllUnitTypesAvailable() {
        assertNotNull(unitRegistry.getUnitsByType(UnitType.LENGTH));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.WEIGHT));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.TEMPERATURE));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.AREA));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.VOLUME));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.SPEED));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.TIME));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.DATA_STORAGE));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.PRESSURE));
        assertNotNull(unitRegistry.getUnitsByType(UnitType.POWER));
    }

    @Test
    public void testConversionEngine_Length() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        UnitDefinition centimeter = unitRegistry.getUnit("length_centimeter");
        UnitDefinition foot = unitRegistry.getUnit("length_foot");
        
        assertNotNull(meter);
        assertNotNull(kilometer);
        assertNotNull(centimeter);
        assertNotNull(foot);
        
        double result = ConversionEngine.convert(1.0, kilometer, meter);
        assertEquals(1000.0, result, 0.0001);
        
        result = ConversionEngine.convert(100.0, meter, centimeter);
        assertEquals(10000.0, result, 0.0001);
        
        result = ConversionEngine.convert(1.0, meter, foot);
        assertEquals(3.28084, result, 0.0001);
    }

    @Test
    public void testConversionEngine_Temperature() {
        UnitDefinition celsius = unitRegistry.getUnit("temp_celsius");
        UnitDefinition fahrenheit = unitRegistry.getUnit("temp_fahrenheit");
        UnitDefinition kelvin = unitRegistry.getUnit("temp_kelvin");
        
        assertNotNull(celsius);
        assertNotNull(fahrenheit);
        assertNotNull(kelvin);
        
        double result = ConversionEngine.convert(0.0, celsius, fahrenheit);
        assertEquals(32.0, result, 0.0001);
        
        result = ConversionEngine.convert(100.0, celsius, fahrenheit);
        assertEquals(212.0, result, 0.0001);
        
        result = ConversionEngine.convert(32.0, fahrenheit, celsius);
        assertEquals(0.0, result, 0.0001);
        
        result = ConversionEngine.convert(0.0, celsius, kelvin);
        assertEquals(273.15, result, 0.0001);
    }

    @Test
    public void testConversionEngine_Weight() {
        UnitDefinition kilogram = unitRegistry.getUnit("weight_kilogram");
        UnitDefinition gram = unitRegistry.getUnit("weight_gram");
        UnitDefinition pound = unitRegistry.getUnit("weight_pound");
        
        assertNotNull(kilogram);
        assertNotNull(gram);
        assertNotNull(pound);
        
        double result = ConversionEngine.convert(1.0, kilogram, gram);
        assertEquals(1000.0, result, 0.0001);
        
        result = ConversionEngine.convert(1.0, kilogram, pound);
        assertEquals(2.20462, result, 0.001);
    }

    @Test
    public void testConversionEngine_DataStorage() {
        UnitDefinition byteUnit = unitRegistry.getUnit("data_byte");
        UnitDefinition kilobyte = unitRegistry.getUnit("data_kilobyte");
        UnitDefinition megabyte = unitRegistry.getUnit("data_megabyte");
        UnitDefinition gigabyte = unitRegistry.getUnit("data_gigabyte");
        
        assertNotNull(byteUnit);
        assertNotNull(kilobyte);
        assertNotNull(megabyte);
        assertNotNull(gigabyte);
        
        double result = ConversionEngine.convert(1.0, gigabyte, megabyte);
        assertEquals(1024.0, result, 0.0001);
        
        result = ConversionEngine.convert(1.0, megabyte, kilobyte);
        assertEquals(1024.0, result, 0.0001);
        
        result = ConversionEngine.convert(1.0, kilobyte, byteUnit);
        assertEquals(1024.0, result, 0.0001);
    }

    @Test
    public void testBatchConversion() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        UnitDefinition centimeter = unitRegistry.getUnit("length_centimeter");
        
        List<Double> values = new ArrayList<>();
        values.add(1000.0);
        values.add(2000.0);
        values.add(500.0);
        
        List<UnitDefinition> toUnits = new ArrayList<>();
        toUnits.add(kilometer);
        toUnits.add(centimeter);
        
        assertEquals(0, batchManager.getConversionHistory().size());
        
        List<com.unitconverter.model.ConversionHistory> results = batchManager.batchConvert(values, meter, toUnits);
        
        assertEquals(3, results.size());
        assertEquals(3, batchManager.getConversionHistory().size());
    }

    @Test
    public void testCustomUnitCreation() {
        assertEquals(0, customManager.getCustomUnits().size());
        
        String name = "光年测试";
        String symbol = "ly-test";
        UnitType unitType = UnitType.LENGTH;
        UnitSystem unitSystem = UnitSystem.CUSTOM;
        double conversionFactor = 9.461e15;
        String baseUnitId = "length_meter";
        
        UnitDefinition unit = customManager.createCustomUnit(
            name, symbol, unitType, unitSystem, conversionFactor, baseUnitId
        );
        
        assertNotNull(unit);
        assertTrue(unit.isCustom());
        assertEquals(1, customManager.getCustomUnits().size());
        
        UnitDefinition retrieved = unitRegistry.getUnit(unit.getId());
        assertNotNull(retrieved);
        assertEquals(name, retrieved.getName());
        assertEquals(symbol, retrieved.getSymbol());
        
        customManager.deleteCustomUnit(unit.getId());
        assertEquals(0, customManager.getCustomUnits().size());
    }

    @Test
    public void testCustomUnitWithFormula() {
        String name = "华氏度自定义";
        String symbol = "F-custom";
        UnitType unitType = UnitType.TEMPERATURE;
        UnitSystem unitSystem = UnitSystem.CUSTOM;
        String toBaseFormula = "(x - 32) * 5 / 9";
        String fromBaseFormula = "x * 9 / 5 + 32";
        String baseUnitId = "temp_celsius";
        
        int initialCount = customManager.getCustomUnits().size();
        
        UnitDefinition unit = customManager.createCustomUnitWithFormula(
            name, symbol, unitType, unitSystem, toBaseFormula, fromBaseFormula, baseUnitId
        );
        
        assertNotNull(unit);
        assertTrue(unit.usesFormulaConversion());
        assertNotNull(unit.getToBaseFormula());
        assertNotNull(unit.getFromBaseFormula());
        
        assertEquals(initialCount + 1, customManager.getCustomUnits().size());
        
        customManager.deleteCustomUnit(unit.getId());
    }

    @Test
    public void testCalculatorEngine_BasicOperations() {
        calculatorEngine.clearHistory();
        
        double result = calculatorEngine.calculate("2+3");
        assertEquals(5.0, result, 0.0001);
        
        result = calculatorEngine.calculate("10-4");
        assertEquals(6.0, result, 0.0001);
        
        result = calculatorEngine.calculate("5*6");
        assertEquals(30.0, result, 0.0001);
        
        result = calculatorEngine.calculate("20/4");
        assertEquals(5.0, result, 0.0001);
    }

    @Test
    public void testCalculatorEngine_ComplexExpressions() {
        double result = calculatorEngine.calculate("(2+3)*4");
        assertEquals(20.0, result, 0.0001);
        
        result = calculatorEngine.calculate("2+3*4");
        assertEquals(14.0, result, 0.0001);
        
        result = calculatorEngine.calculate("10/2+3");
        assertEquals(8.0, result, 0.0001);
    }

    @Test
    public void testCalculatorEngine_History() {
        calculatorEngine.clearHistory();
        
        assertEquals(0, calculatorEngine.getCalculationHistory().size());
        
        calculatorEngine.calculate("2+2");
        assertEquals(1, calculatorEngine.getCalculationHistory().size());
        
        calculatorEngine.calculate("3*3");
        assertEquals(2, calculatorEngine.getCalculationHistory().size());
    }

    @Test
    public void testResultFormatting() {
        String formatted = ConversionEngine.formatResult(123.456, 2, false);
        assertEquals("123.46", formatted);
        
        formatted = ConversionEngine.formatResult(100.0, 0, false);
        assertEquals("100", formatted);
        
        formatted = ConversionEngine.formatResult(1.234567, 4, false);
        assertEquals("1.2346", formatted);
    }

    @Test
    public void testUnitDefinition_Equality() {
        UnitDefinition meter1 = unitRegistry.getUnit("length_meter");
        UnitDefinition meter2 = unitRegistry.getUnit("length_meter");
        
        assertNotNull(meter1);
        assertNotNull(meter2);
        assertEquals(meter1.getId(), meter2.getId());
        assertEquals(meter1.getName(), meter2.getName());
        assertEquals(meter1.getSymbol(), meter2.getSymbol());
    }

    @Test
    public void testAllUnitSystems() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition foot = unitRegistry.getUnit("length_foot");
        
        assertEquals(UnitSystem.METRIC, meter.getUnitSystem());
        assertEquals(UnitSystem.IMPERIAL, foot.getUnitSystem());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testInvalidFormula_ThrowsException() {
        customManager.createCustomUnitWithFormula(
            "测试", "t", UnitType.TEMPERATURE, UnitSystem.CUSTOM,
            "invalid formula", "x*2", "temp_celsius"
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void testNullName_ThrowsException() {
        customManager.createCustomUnit(
            null, "t", UnitType.LENGTH, UnitSystem.CUSTOM, 1.0, "length_meter"
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void testDeleteNonCustomUnit_ThrowsException() {
        customManager.deleteCustomUnit("length_meter");
    }

    @Test
    public void testConversionChain() {
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition centimeter = unitRegistry.getUnit("length_centimeter");
        
        double result = ConversionEngine.convertWithChain(1.0, kilometer, meter, centimeter);
        assertEquals(100000.0, result, 0.0001);
    }

    @Test
    public void testValidateFormula() {
        assertTrue(customManager.validateFormula("x*2"));
        assertTrue(customManager.validateFormula("(x-32)*5/9"));
        assertTrue(customManager.validateFormula("sqrt(x)+log(100)"));
        
        assertFalse(customManager.validateFormula(""));
        assertFalse(customManager.validateFormula(null));
    }

    @Test
    public void testTestFormula() {
        double result = customManager.testFormula("x*2", 5.0);
        assertEquals(10.0, result, 0.0001);
        
        result = customManager.testFormula("(x-32)*5/9", 32.0);
        assertEquals(0.0, result, 0.0001);
        
        result = customManager.testFormula("x*9/5+32", 0.0);
        assertEquals(32.0, result, 0.0001);
    }
}
