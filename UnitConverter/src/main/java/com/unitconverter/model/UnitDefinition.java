package com.unitconverter.model;

import java.io.Serializable;

public class UnitDefinition implements Serializable, Cloneable {
    private static final long serialVersionUID = 1L;

    private String id;
    private String name;
    private String symbol;
    private UnitType unitType;
    private UnitSystem unitSystem;
    private String toBaseFormula;
    private String fromBaseFormula;
    private double conversionFactor;
    private boolean isBaseUnit;
    private String baseUnitId;
    private String category;
    private String description;
    private boolean isCustom;
    private boolean isFavorite;

    public UnitDefinition() {
        this.isCustom = false;
        this.isFavorite = false;
        this.isBaseUnit = false;
    }

    public UnitDefinition(String id, String name, String symbol, UnitType unitType, 
                          UnitSystem unitSystem, double conversionFactor, boolean isBaseUnit) {
        this.id = id;
        this.name = name;
        this.symbol = symbol;
        this.unitType = unitType;
        this.unitSystem = unitSystem;
        this.conversionFactor = conversionFactor;
        this.isBaseUnit = isBaseUnit;
        this.isCustom = false;
        this.isFavorite = false;
    }

    public UnitDefinition(String id, String name, String symbol, UnitType unitType,
                          UnitSystem unitSystem, String toBaseFormula, String fromBaseFormula,
                          String baseUnitId) {
        this.id = id;
        this.name = name;
        this.symbol = symbol;
        this.unitType = unitType;
        this.unitSystem = unitSystem;
        this.toBaseFormula = toBaseFormula;
        this.fromBaseFormula = fromBaseFormula;
        this.baseUnitId = baseUnitId;
        this.isBaseUnit = false;
        this.isCustom = false;
        this.isFavorite = false;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSymbol() {
        return symbol;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public UnitType getUnitType() {
        return unitType;
    }

    public void setUnitType(UnitType unitType) {
        this.unitType = unitType;
    }

    public UnitSystem getUnitSystem() {
        return unitSystem;
    }

    public void setUnitSystem(UnitSystem unitSystem) {
        this.unitSystem = unitSystem;
    }

    public String getToBaseFormula() {
        return toBaseFormula;
    }

    public void setToBaseFormula(String toBaseFormula) {
        this.toBaseFormula = toBaseFormula;
    }

    public String getFromBaseFormula() {
        return fromBaseFormula;
    }

    public void setFromBaseFormula(String fromBaseFormula) {
        this.fromBaseFormula = fromBaseFormula;
    }

    public double getConversionFactor() {
        return conversionFactor;
    }

    public void setConversionFactor(double conversionFactor) {
        this.conversionFactor = conversionFactor;
    }

    public boolean isBaseUnit() {
        return isBaseUnit;
    }

    public void setBaseUnit(boolean baseUnit) {
        isBaseUnit = baseUnit;
    }

    public String getBaseUnitId() {
        return baseUnitId;
    }

    public void setBaseUnitId(String baseUnitId) {
        this.baseUnitId = baseUnitId;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public boolean isCustom() {
        return isCustom;
    }

    public void setCustom(boolean custom) {
        isCustom = custom;
    }

    public boolean isFavorite() {
        return isFavorite;
    }

    public void setFavorite(boolean favorite) {
        isFavorite = favorite;
    }

    public boolean usesFormulaConversion() {
        return toBaseFormula != null && !toBaseFormula.isEmpty();
    }

    public String getDisplayName() {
        return name + " (" + symbol + ")";
    }

    @Override
    public UnitDefinition clone() {
        try {
            return (UnitDefinition) super.clone();
        } catch (CloneNotSupportedException e) {
            UnitDefinition copy = new UnitDefinition();
            copy.id = this.id;
            copy.name = this.name;
            copy.symbol = this.symbol;
            copy.unitType = this.unitType;
            copy.unitSystem = this.unitSystem;
            copy.toBaseFormula = this.toBaseFormula;
            copy.fromBaseFormula = this.fromBaseFormula;
            copy.conversionFactor = this.conversionFactor;
            copy.isBaseUnit = this.isBaseUnit;
            copy.baseUnitId = this.baseUnitId;
            copy.category = this.category;
            copy.description = this.description;
            copy.isCustom = this.isCustom;
            copy.isFavorite = this.isFavorite;
            return copy;
        }
    }

    @Override
    public String toString() {
        return getDisplayName();
    }
}
