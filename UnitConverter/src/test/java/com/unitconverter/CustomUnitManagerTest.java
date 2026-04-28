package com.unitconverter;

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

public class CustomUnitManagerTest {

    private CustomUnitManager customManager;
    private UnitRegistry unitRegistry;

    @Before
    public void setUp() {
        customManager = CustomUnitManager.getInstance();
        unitRegistry = UnitRegistry.getInstance();
        
        for (UnitDefinition unit : customManager.getCustomUnits()) {
            unitRegistry.removeUnit(unit.getId());
        }
    }

    @Test
    public void testSingletonInstance() {
        CustomUnitManager instance1 = CustomUnitManager.getInstance();
        CustomUnitManager instance2 = CustomUnitManager.getInstance();
        assertSame(instance1, instance2);
    }

    @Test
    public void testCreateCustomUnitWithFactor() {
        String name = "测试单位";
        String symbol = "tu";
        UnitType unitType = UnitType.LENGTH;
        UnitSystem unitSystem = UnitSystem.CUSTOM;
        double conversionFactor = 1000.0;
        String baseUnitId = "length_meter";

        UnitDefinition unit = customManager.createCustomUnit(
            name, symbol, unitType, unitSystem, conversionFactor, baseUnitId
        );

        assertNotNull(unit);
        assertNotNull(unit.getId());
        assertTrue(unit.getId().startsWith("custom_"));
        assertEquals(name, unit.getName());
        assertEquals(symbol, unit.getSymbol());
        assertEquals(unitType, unit.getUnitType());
        assertEquals(unitSystem, unit.getUnitSystem());
        assertEquals(conversionFactor, unit.getConversionFactor(), 0.0001);
        assertEquals(baseUnitId, unit.getBaseUnitId());
        assertTrue(unit.isCustom());
        assertFalse(unit.isBaseUnit());

        UnitDefinition retrieved = unitRegistry.getUnit(unit.getId());
        assertNotNull(retrieved);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCustomUnitWithNullName() {
        customManager.createCustomUnit(
            null, "tu", UnitType.LENGTH, UnitSystem.CUSTOM, 1000.0, "length_meter"
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCustomUnitWithEmptySymbol() {
        customManager.createCustomUnit(
            "测试单位", "", UnitType.LENGTH, UnitSystem.CUSTOM, 1000.0, "length_meter"
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCustomUnitWithNullType() {
        customManager.createCustomUnit(
            "测试单位", "tu", null, UnitSystem.CUSTOM, 1000.0, "length_meter"
        );
    }

    @Test
    public void testCreateCustomUnitWithFormula() {
        String name = "华氏度自定义";
        String symbol = "F-custom";
        UnitType unitType = UnitType.TEMPERATURE;
        UnitSystem unitSystem = UnitSystem.CUSTOM;
        String toBaseFormula = "(x - 32) * 5 / 9";
        String fromBaseFormula = "x * 9 / 5 + 32";
        String baseUnitId = "temp_celsius";

        UnitDefinition unit = customManager.createCustomUnitWithFormula(
            name, symbol, unitType, unitSystem, toBaseFormula, fromBaseFormula, baseUnitId
        );

        assertNotNull(unit);
        assertEquals(name, unit.getName());
        assertEquals(symbol, unit.getSymbol());
        assertEquals(unitType, unit.getUnitType());
        assertTrue(unit.isCustom());
        assertTrue(unit.usesFormulaConversion());
        assertEquals(toBaseFormula, unit.getToBaseFormula());
        assertEquals(fromBaseFormula, unit.getFromBaseFormula());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCustomUnitWithInvalidFormula() {
        customManager.createCustomUnitWithFormula(
            "测试", "t", UnitType.TEMPERATURE, UnitSystem.CUSTOM,
            "x + invalid", "x * 2", "temp_celsius"
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCustomUnitWithNullToBaseFormula() {
        customManager.createCustomUnitWithFormula(
            "测试", "t", UnitType.TEMPERATURE, UnitSystem.CUSTOM,
            null, "x * 2", "temp_celsius"
        );
    }

    @Test
    public void testGetCustomUnits() {
        List<UnitDefinition> initial = customManager.getCustomUnits();
        int initialCount = initial.size();

        customManager.createCustomUnit(
            "自定义单位1", "cu1", UnitType.LENGTH, UnitSystem.CUSTOM, 100.0, "length_meter"
        );
        customManager.createCustomUnit(
            "自定义单位2", "cu2", UnitType.WEIGHT, UnitSystem.CUSTOM, 0.5, "weight_kilogram"
        );

        List<UnitDefinition> customUnits = customManager.getCustomUnits();
        assertEquals(initialCount + 2, customUnits.size());
    }

    @Test
    public void testGetCustomUnitsByType() {
        customManager.createCustomUnit(
            "长度自定义1", "lc1", UnitType.LENGTH, UnitSystem.CUSTOM, 100.0, "length_meter"
        );
        customManager.createCustomUnit(
            "长度自定义2", "lc2", UnitType.LENGTH, UnitSystem.CUSTOM, 200.0, "length_meter"
        );
        customManager.createCustomUnit(
            "重量自定义", "wc", UnitType.WEIGHT, UnitSystem.CUSTOM, 0.5, "weight_kilogram"
        );

        List<UnitDefinition> lengthUnits = customManager.getCustomUnitsByType(UnitType.LENGTH);
        List<UnitDefinition> weightUnits = customManager.getCustomUnitsByType(UnitType.WEIGHT);

        assertEquals(2, lengthUnits.size());
        assertEquals(1, weightUnits.size());
    }

    @Test
    public void testDeleteCustomUnit() {
        UnitDefinition unit = customManager.createCustomUnit(
            "待删除单位", "td", UnitType.LENGTH, UnitSystem.CUSTOM, 100.0, "length_meter"
        );

        String unitId = unit.getId();
        assertNotNull(unitRegistry.getUnit(unitId));

        customManager.deleteCustomUnit(unitId);

        assertNull(unitRegistry.getUnit(unitId));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testDeleteNonExistentUnit() {
        customManager.deleteCustomUnit("non_existent_unit_id");
    }

    @Test(expected = IllegalArgumentException.class)
    public void testDeleteNonCustomUnit() {
        customManager.deleteCustomUnit("length_meter");
    }

    @Test
    public void testUpdateCustomUnit() {
        UnitDefinition unit = customManager.createCustomUnit(
            "原始名称", "os", UnitType.LENGTH, UnitSystem.CUSTOM, 100.0, "length_meter"
        );

        String unitId = unit.getId();
        customManager.updateCustomUnit(unitId, "新名称", "ns", 200.0);

        UnitDefinition updated = unitRegistry.getUnit(unitId);
        assertEquals("新名称", updated.getName());
        assertEquals("ns", updated.getSymbol());
        assertEquals(200.0, updated.getConversionFactor(), 0.0001);
    }

    @Test
    public void testValidateFormula() {
        assertTrue(customManager.validateFormula("x * 2"));
        assertTrue(customManager.validateFormula("(x - 32) * 5 / 9"));
        assertTrue(customManager.validateFormula("sqrt(x) + log(100)"));
        
        assertFalse(customManager.validateFormula(""));
        assertFalse(customManager.validateFormula(null));
    }

    @Test
    public void testTestFormula() {
        double result = customManager.testFormula("x * 2", 5.0);
        assertEquals(10.0, result, 0.0001);

        result = customManager.testFormula("(x - 32) * 5 / 9", 32.0);
        assertEquals(0.0, result, 0.0001);

        result = customManager.testFormula("x * 9 / 5 + 32", 0.0);
        assertEquals(32.0, result, 0.0001);
    }

    @Test
    public void testIsCustomUnit() {
        UnitDefinition customUnit = customManager.createCustomUnit(
            "自定义测试", "ct", UnitType.LENGTH, UnitSystem.CUSTOM, 100.0, "length_meter"
        );

        assertTrue(customManager.isCustomUnit(customUnit.getId()));
        assertFalse(customManager.isCustomUnit("length_meter"));
        assertFalse(customManager.isCustomUnit("non_existent"));
    }

    @Test
    public void testGetUnit() {
        UnitDefinition customUnit = customManager.createCustomUnit(
            "获取测试", "gt", UnitType.LENGTH, UnitSystem.CUSTOM, 100.0, "length_meter"
        );

        UnitDefinition retrieved = customManager.getUnit(customUnit.getId());
        assertNotNull(retrieved);
        assertEquals("获取测试", retrieved.getName());

        assertNull(customManager.getUnit("non_existent"));
    }

    @Test
    public void testCreateUnitGroup() {
        List<UnitDefinition> units = new ArrayList<>();
        units.add(unitRegistry.getUnit("length_meter"));
        units.add(unitRegistry.getUnit("length_kilometer"));

        UnitDefinition group = customManager.createUnitGroup("测试分组", units);

        assertNotNull(group);
        assertTrue(group.getId().startsWith("group_"));
        assertEquals("测试分组", group.getName());
        assertEquals("GROUP", group.getSymbol());
        assertEquals(UnitType.CUSTOM, group.getUnitType());
        assertEquals(UnitSystem.CUSTOM, group.getUnitSystem());
        assertTrue(group.isCustom());
    }

    @Test
    public void testWeightCustomUnit() {
        UnitDefinition customWeight = customManager.createCustomUnit(
            "自定义磅", "lb-custom", UnitType.WEIGHT, UnitSystem.IMPERIAL, 
            0.453592, "weight_kilogram"
        );

        assertNotNull(customWeight);
        assertEquals(0.453592, customWeight.getConversionFactor(), 0.000001);
        assertEquals(UnitSystem.IMPERIAL, customWeight.getUnitSystem());
    }
}
