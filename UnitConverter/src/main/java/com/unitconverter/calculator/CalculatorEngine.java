package com.unitconverter.calculator;

import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

public class CalculatorEngine {
    private static CalculatorEngine instance;
    private final List<CalculationHistory> calculationHistory;

    private CalculatorEngine() {
        calculationHistory = new ArrayList<>();
    }

    public static synchronized CalculatorEngine getInstance() {
        if (instance == null) {
            instance = new CalculatorEngine();
        }
        return instance;
    }

    public double calculate(String expression) throws IllegalArgumentException {
        if (expression == null || expression.trim().isEmpty()) {
            throw new IllegalArgumentException("表达式不能为空");
        }

        try {
            double result = evaluateExpression(expression);
            calculationHistory.add(0, new CalculationHistory(expression, result));
            return result;
        } catch (ArithmeticException e) {
            throw new IllegalArgumentException("计算错误: " + e.getMessage(), e);
        } catch (Exception e) {
            throw new IllegalArgumentException("表达式错误: " + e.getMessage(), e);
        }
    }

    private double evaluateExpression(String expression) {
        String processed = preprocess(expression);
        return evaluatePostfix(infixToPostfix(processed));
    }

    private String preprocess(String expression) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < expression.length(); i++) {
            char c = expression.charAt(i);
            if (Character.isWhitespace(c)) {
                continue;
            }
            result.append(c);
        }
        return insertImplicitMultiplication(result.toString());
    }

    private String insertImplicitMultiplication(String expression) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < expression.length(); i++) {
            char current = expression.charAt(i);
            result.append(current);

            if (i < expression.length() - 1) {
                char next = expression.charAt(i + 1);

                if ((Character.isDigit(current) || current == ')') &&
                    (next == '(' || Character.isLetter(next))) {
                    result.append('*');
                }

                if (current == ')' && Character.isDigit(next)) {
                    result.append('*');
                }
            }
        }
        return result.toString();
    }

    private List<String> infixToPostfix(String infix) {
        List<String> postfix = new ArrayList<>();
        Stack<Character> operators = new Stack<>();
        StringBuilder currentToken = new StringBuilder();

        for (int i = 0; i < infix.length(); i++) {
            char c = infix.charAt(i);

            if (Character.isDigit(c) || c == '.' || (c == '-' && isNegativeSign(infix, i))) {
                currentToken.append(c);
            } else if (Character.isLetter(c)) {
                currentToken.append(c);
            } else {
                if (currentToken.length() > 0) {
                    postfix.add(currentToken.toString());
                    currentToken.setLength(0);
                }

                if (c == '(') {
                    operators.push(c);
                } else if (c == ')') {
                    while (!operators.isEmpty() && operators.peek() != '(') {
                        postfix.add(String.valueOf(operators.pop()));
                    }
                    if (!operators.isEmpty()) {
                        operators.pop();
                    }
                } else if (isOperator(c)) {
                    while (!operators.isEmpty() && operators.peek() != '(' &&
                           hasHigherPrecedence(operators.peek(), c)) {
                        postfix.add(String.valueOf(operators.pop()));
                    }
                    operators.push(c);
                }
            }
        }

        if (currentToken.length() > 0) {
            postfix.add(currentToken.toString());
        }

        while (!operators.isEmpty()) {
            postfix.add(String.valueOf(operators.pop()));
        }

        return postfix;
    }

    private boolean isNegativeSign(String infix, int index) {
        if (index == 0) {
            return true;
        }
        char prev = infix.charAt(index - 1);
        return prev == '(' || prev == '+' || prev == '-' || prev == '*' || prev == '/' || prev == '^';
    }

    private boolean isOperator(char c) {
        return c == '+' || c == '-' || c == '*' || c == '/' || c == '^' || c == '%';
    }

    private boolean hasHigherPrecedence(char op1, char op2) {
        int prec1 = getPrecedence(op1);
        int prec2 = getPrecedence(op2);
        if (prec1 == prec2) {
            return op1 != '^';
        }
        return prec1 > prec2;
    }

    private int getPrecedence(char op) {
        switch (op) {
            case '+':
            case '-':
                return 1;
            case '*':
            case '/':
            case '%':
                return 2;
            case '^':
                return 3;
            default:
                return 0;
        }
    }

    private double evaluatePostfix(List<String> postfix) {
        Stack<Double> stack = new Stack<>();

        for (String token : postfix) {
            if (isNumber(token)) {
                stack.push(Double.parseDouble(token));
            } else if (isFunction(token)) {
                double value = stack.pop();
                stack.push(applyFunction(token, value));
            } else if (token.length() == 1 && isOperator(token.charAt(0))) {
                double b = stack.pop();
                double a = stack.isEmpty() ? 0 : stack.pop();
                stack.push(applyOperation(token.charAt(0), a, b));
            }
        }

        return stack.pop();
    }

    private boolean isNumber(String token) {
        try {
            Double.parseDouble(token);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    private boolean isFunction(String token) {
        String lower = token.toLowerCase();
        return lower.equals("sin") || lower.equals("cos") || lower.equals("tan") ||
               lower.equals("asin") || lower.equals("acos") || lower.equals("atan") ||
               lower.equals("log") || lower.equals("ln") || lower.equals("log10") ||
               lower.equals("sqrt") || lower.equals("cbrt") || lower.equals("abs") ||
               lower.equals("exp") || lower.equals("fact") || lower.equals("floor") ||
               lower.equals("ceil") || lower.equals("round");
    }

    private double applyFunction(String function, double value) {
        String lower = function.toLowerCase();
        switch (lower) {
            case "sin":
                return Math.sin(Math.toRadians(value));
            case "cos":
                return Math.cos(Math.toRadians(value));
            case "tan":
                return Math.tan(Math.toRadians(value));
            case "asin":
                return Math.toDegrees(Math.asin(value));
            case "acos":
                return Math.toDegrees(Math.acos(value));
            case "atan":
                return Math.toDegrees(Math.atan(value));
            case "log":
            case "ln":
                return Math.log(value);
            case "log10":
                return Math.log10(value);
            case "sqrt":
                if (value < 0) throw new ArithmeticException("负数不能开平方");
                return Math.sqrt(value);
            case "cbrt":
                return Math.cbrt(value);
            case "abs":
                return Math.abs(value);
            case "exp":
                return Math.exp(value);
            case "fact":
                if (value < 0 || value != Math.floor(value)) {
                    throw new ArithmeticException("阶乘仅支持非负整数");
                }
                return factorial((long) value);
            case "floor":
                return Math.floor(value);
            case "ceil":
                return Math.ceil(value);
            case "round":
                return Math.round(value);
            default:
                throw new IllegalArgumentException("未知函数: " + function);
        }
    }

    private double factorial(long n) {
        if (n == 0 || n == 1) return 1;
        double result = 1;
        for (long i = 2; i <= n; i++) {
            result *= i;
            if (Double.isInfinite(result)) {
                throw new ArithmeticException("阶乘结果太大");
            }
        }
        return result;
    }

    private double applyOperation(char op, double a, double b) {
        switch (op) {
            case '+':
                return a + b;
            case '-':
                return a - b;
            case '*':
                return a * b;
            case '/':
                if (b == 0) throw new ArithmeticException("除数不能为零");
                return a / b;
            case '^':
                return Math.pow(a, b);
            case '%':
                if (b == 0) throw new ArithmeticException("模数不能为零");
                return a % b;
            default:
                throw new IllegalArgumentException("未知操作符: " + op);
        }
    }

    public List<CalculationHistory> getCalculationHistory() {
        return new ArrayList<>(calculationHistory);
    }

    public List<CalculationHistory> getCalculationHistory(int limit) {
        if (limit <= 0 || calculationHistory.isEmpty()) {
            return new ArrayList<>();
        }
        int end = Math.min(limit, calculationHistory.size());
        return new ArrayList<>(calculationHistory.subList(0, end));
    }

    public void clearHistory() {
        calculationHistory.clear();
    }

    public static class CalculationHistory {
        private final String expression;
        private final double result;
        private final long timestamp;

        public CalculationHistory(String expression, double result) {
            this.expression = expression;
            this.result = result;
            this.timestamp = System.currentTimeMillis();
        }

        public String getExpression() {
            return expression;
        }

        public double getResult() {
            return result;
        }

        public long getTimestamp() {
            return timestamp;
        }

        @Override
        public String toString() {
            return expression + " = " + result;
        }
    }
}
