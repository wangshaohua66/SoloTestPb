package com.unitconverter;

import com.unitconverter.converter.FormulaParser;
import org.junit.Test;

import static org.junit.Assert.*;

public class FormulaParserTest {

    @Test
    public void testBasicArithmetic() {
        double result = FormulaParser.evaluate("2 + 3", 0);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("10 - 4", 0);
        assertEquals(6.0, result, 0.0001);

        result = FormulaParser.evaluate("3 * 4", 0);
        assertEquals(12.0, result, 0.0001);

        result = FormulaParser.evaluate("20 / 4", 0);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("10 % 3", 0);
        assertEquals(1.0, result, 0.0001);

        result = FormulaParser.evaluate("2 ^ 3", 0);
        assertEquals(8.0, result, 0.0001);
    }

    @Test
    public void testOperatorPrecedence() {
        double result = FormulaParser.evaluate("2 + 3 * 4", 0);
        assertEquals(14.0, result, 0.0001);

        result = FormulaParser.evaluate("(2 + 3) * 4", 0);
        assertEquals(20.0, result, 0.0001);

        result = FormulaParser.evaluate("10 - 3 * 2 + 4", 0);
        assertEquals(8.0, result, 0.0001);
    }

    @Test
    public void testVariableSubstitution() {
        double result = FormulaParser.evaluate("x * 2", 5);
        assertEquals(10.0, result, 0.0001);

        result = FormulaParser.evaluate("x + 3", 7);
        assertEquals(10.0, result, 0.0001);

        result = FormulaParser.evaluate("(x - 32) * 5 / 9", 32);
        assertEquals(0.0, result, 0.0001);

        result = FormulaParser.evaluate("(x - 32) * 5 / 9", 212);
        assertEquals(100.0, result, 0.0001);
    }

    @Test
    public void testTemperatureFormulas() {
        double result = FormulaParser.evaluate("(x - 32) * 5 / 9", 32.0);
        assertEquals(0.0, result, 0.0001);

        result = FormulaParser.evaluate("(x - 32) * 5 / 9", 212.0);
        assertEquals(100.0, result, 0.0001);

        result = FormulaParser.evaluate("x * 9 / 5 + 32", 0.0);
        assertEquals(32.0, result, 0.0001);

        result = FormulaParser.evaluate("x * 9 / 5 + 32", 100.0);
        assertEquals(212.0, result, 0.0001);

        result = FormulaParser.evaluate("x - 273.15", 273.15);
        assertEquals(0.0, result, 0.0001);

        result = FormulaParser.evaluate("x + 273.15", 0.0);
        assertEquals(273.15, result, 0.0001);
    }

    @Test
    public void testSquareRootFunction() {
        double result = FormulaParser.evaluate("sqrt(16)", 0);
        assertEquals(4.0, result, 0.0001);

        result = FormulaParser.evaluate("sqrt(x)", 25);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("sqrt(x + 11)", 5);
        assertEquals(4.0, result, 0.0001);
    }

    @Test
    public void testLogarithmFunctions() {
        double result = FormulaParser.evaluate("log(100)", 0);
        assertEquals(2.0, result, 0.0001);

        result = FormulaParser.evaluate("ln(e)", 0);
        assertEquals(1.0, result, 0.0001);

        result = FormulaParser.evaluate("log(100 * x)", 10);
        assertEquals(3.0, result, 0.0001);
    }

    @Test
    public void testTrigonometricFunctions() {
        double result = FormulaParser.evaluate("sin(30)", 0);
        assertEquals(0.5, result, 0.0001);

        result = FormulaParser.evaluate("sin(x)", 90);
        assertEquals(1.0, result, 0.0001);

        result = FormulaParser.evaluate("cos(60)", 0);
        assertEquals(0.5, result, 0.0001);

        result = FormulaParser.evaluate("cos(x)", 0);
        assertEquals(1.0, result, 0.0001);

        result = FormulaParser.evaluate("tan(45)", 0);
        assertEquals(1.0, result, 0.0001);
    }

    @Test
    public void testAbsFunction() {
        double result = FormulaParser.evaluate("abs(-5)", 0);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("abs(5)", 0);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("abs(x)", -10);
        assertEquals(10.0, result, 0.0001);
    }

    @Test
    public void testExpFunction() {
        double result = FormulaParser.evaluate("exp(0)", 0);
        assertEquals(1.0, result, 0.0001);

        result = FormulaParser.evaluate("exp(1)", 0);
        assertEquals(Math.E, result, 0.0001);

        result = FormulaParser.evaluate("exp(x)", 2);
        assertEquals(Math.exp(2), result, 0.0001);
    }

    @Test
    public void testNegativeNumbers() {
        double result = FormulaParser.evaluate("-5", 0);
        assertEquals(-5.0, result, 0.0001);

        result = FormulaParser.evaluate("-x", 5);
        assertEquals(-5.0, result, 0.0001);

        result = FormulaParser.evaluate("10 + -5", 0);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("x * 2", -3);
        assertEquals(-6.0, result, 0.0001);
    }

    @Test
    public void testImplicitMultiplication() {
        double result = FormulaParser.evaluate("2(3+4)", 0);
        assertEquals(14.0, result, 0.0001);

        result = FormulaParser.evaluate("(2+3)(4+5)", 0);
        assertEquals(45.0, result, 0.0001);

        result = FormulaParser.evaluate("2x", 5);
        assertEquals(10.0, result, 0.0001);
    }

    @Test
    public void testComplexFormulas() {
        double result = FormulaParser.evaluate("sqrt(x^2 + y^2)", 3);
        assertEquals(3.0, result, 0.0001);

        result = FormulaParser.evaluate("(x - a) * (x + b)", 5);
        assertEquals(5.0, result, 0.0001);

        result = FormulaParser.evaluate("1 / (1 + exp(-x))", 0);
        assertEquals(0.5, result, 0.0001);

        result = FormulaParser.evaluate("x * 9 / 5 + 32", 0);
        assertEquals(32.0, result, 0.0001);
    }

    @Test
    public void testIsValidFormula() {
        assertTrue(FormulaParser.isValidFormula("2 + 3"));
        assertTrue(FormulaParser.isValidFormula("x * 2"));
        assertTrue(FormulaParser.isValidFormula("(x - 32) * 5 / 9"));
        assertTrue(FormulaParser.isValidFormula("sqrt(x)"));
        assertTrue(FormulaParser.isValidFormula("sin(x)"));
        assertTrue(FormulaParser.isValidFormula("log(x) + ln(x)"));

        assertFalse(FormulaParser.isValidFormula(""));
        assertFalse(FormulaParser.isValidFormula(null));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testDivisionByZero() {
        FormulaParser.evaluate("5 / 0", 0);
    }

    @Test(expected = ArithmeticException.class)
    public void testSquareRootOfNegative() {
        FormulaParser.evaluate("sqrt(-1)", 0);
    }

    @Test(expected = ArithmeticException.class)
    public void testLogOfZero() {
        FormulaParser.evaluate("log(0)", 0);
    }

    @Test
    public void testNestedParentheses() {
        double result = FormulaParser.evaluate("((2 + 3) * (4 - 1)) / 5", 0);
        assertEquals(3.0, result, 0.0001);

        result = FormulaParser.evaluate("(x + (x * 2)) / 3", 5);
        assertEquals(5.0, result, 0.0001);
    }

    @Test
    public void testDecimalNumbers() {
        double result = FormulaParser.evaluate("2.5 * 4", 0);
        assertEquals(10.0, result, 0.0001);

        result = FormulaParser.evaluate("x * 1.5", 10);
        assertEquals(15.0, result, 0.0001);

        result = FormulaParser.evaluate("0.1 + 0.2", 0);
        assertEquals(0.3, result, 0.0001);
    }
}
