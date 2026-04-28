package com.unitconverter.manager;

import com.unitconverter.converter.FormulaParser;
import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitSystem;
import com.unitconverter.model.UnitType;
import com.unitconverter.registry.UnitRegistry;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class CustomUnitManager {
    private static CustomUnitManager instance;
    private final UnitRegistry registry;

    private CustomUnitManager() {
        registry = UnitRegistry.getInstance();
    }

    public static synchronized CustomUnitManager getInstance() {
        if (instance == null) {
            instance = new CustomUnitManager();
        }
        return instance;
    }

    public UnitDefinition createCustomUnit(String name, String symbol, UnitType unitType,
                                           UnitSystem unitSystem, double conversionFactor,
                                           String baseUnitId) throws IllegalArgumentException {
        validateUnitParameters(name, symbol, unitType);

        UnitDefinition unit = new UnitDefinition();
        unit.setId(generateCustomUnitId(unitType));
        unit.setName(name);
        unit.setSymbol(symbol);
        unit.setUnitType(unitType);
        unit.setUnitSystem(unitSystem);
        unit.setConversionFactor(conversionFactor);
        unit.setBaseUnitId(baseUnitId);
        unit.setCustom(true);
        unit.setBaseUnit(false);

        registry.addUnit(unit);
        return unit;
    }

    public UnitDefinition createCustomUnitWithFormula(String name, String symbol, UnitType unitType,
                                                       UnitSystem unitSystem, String toBaseFormula,
                                                       String fromBaseFormula, String baseUnitId)
            throws IllegalArgumentException {
        validateUnitParameters(name, symbol, unitType);

        if (toBaseFormula == null || toBaseFormula.trim().isEmpty()) {
            throw new IllegalArgumentException("转换公式不能为空");
        }

        if (fromBaseFormula == null || fromBaseFormula.trim().isEmpty()) {
            throw new IllegalArgumentException("逆转换公式不能为空");
        }

        if (!FormulaParser.isValidFormula(toBaseFormula)) {
            throw new IllegalArgumentException("转换公式无效");
        }

        if (!FormulaParser.isValidFormula(fromBaseFormula)) {
            throw new IllegalArgumentException("逆转换公式无效");
        }

        UnitDefinition unit = new UnitDefinition();
        unit.setId(generateCustomUnitId(unitType));
        unit.setName(name);
        unit.setSymbol(symbol);
        unit.setUnitType(unitType);
        unit.setUnitSystem(unitSystem);
        unit.setToBaseFormula(toBaseFormula);
        unit.setFromBaseFormula(fromBaseFormula);
        unit.setBaseUnitId(baseUnitId);
        unit.setCustom(true);
        unit.setBaseUnit(false);

        registry.addUnit(unit);
        return unit;
    }

    private void validateUnitParameters(String name, String symbol, UnitType unitType) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("单位名称不能为空");
        }

        if (symbol == null || symbol.trim().isEmpty()) {
            throw new IllegalArgumentException("单位符号不能为空");
        }

        if (unitType == null) {
            throw new IllegalArgumentException("单位类型不能为空");
        }
    }

    private String generateCustomUnitId(UnitType unitType) {
        return "custom_" + unitType.getKey() + "_" + UUID.randomUUID().toString().substring(0, 8);
    }

    public void updateCustomUnit(String unitId, String name, String symbol,
                                  double conversionFactor) throws IllegalArgumentException {
        UnitDefinition unit = registry.getUnit(unitId);
        if (unit == null) {
            throw new IllegalArgumentException("单位不存在: " + unitId);
        }

        if (!unit.isCustom()) {
            throw new IllegalArgumentException("只能修改自定义单位");
        }

        if (name != null && !name.trim().isEmpty()) {
            unit.setName(name);
        }
        if (symbol != null && !symbol.trim().isEmpty()) {
            unit.setSymbol(symbol);
        }
        unit.setConversionFactor(conversionFactor);

        registry.removeUnit(unitId);
        registry.addUnit(unit);
    }

    public void deleteCustomUnit(String unitId) throws IllegalArgumentException {
        UnitDefinition unit = registry.getUnit(unitId);
        if (unit == null) {
            throw new IllegalArgumentException("单位不存在: " + unitId);
        }

        if (!unit.isCustom()) {
            throw new IllegalArgumentException("只能删除自定义单位");
        }

        registry.removeUnit(unitId);
    }

    public List<UnitDefinition> getCustomUnits() {
        return registry.getCustomUnits();
    }

    public List<UnitDefinition> getCustomUnitsByType(UnitType type) {
        List<UnitDefinition> result = new ArrayList<>();
        for (UnitDefinition unit : registry.getCustomUnits()) {
            if (unit.getUnitType() == type) {
                result.add(unit);
            }
        }
        return result;
    }

    public UnitDefinition getUnit(String unitId) {
        return registry.getUnit(unitId);
    }

    public boolean isCustomUnit(String unitId) {
        UnitDefinition unit = registry.getUnit(unitId);
        return unit != null && unit.isCustom();
    }

    public boolean validateFormula(String formula) {
        return FormulaParser.isValidFormula(formula);
    }

    public double testFormula(String formula, double testValue) {
        return FormulaParser.evaluate(formula, testValue);
    }

    public UnitDefinition createUnitGroup(String groupName, List<UnitDefinition> units) {
        UnitDefinition groupUnit = new UnitDefinition();
        groupUnit.setId("group_" + UUID.randomUUID().toString().substring(0, 8));
        groupUnit.setName(groupName);
        groupUnit.setSymbol("GROUP");
        groupUnit.setUnitType(UnitType.CUSTOM);
        groupUnit.setUnitSystem(UnitSystem.CUSTOM);
        groupUnit.setCustom(true);
        groupUnit.setDescription("单位分组: " + groupName);

        registry.addUnit(groupUnit);
        return groupUnit;
    }
}
