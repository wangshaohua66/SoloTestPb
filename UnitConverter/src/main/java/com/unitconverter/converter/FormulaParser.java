package com.unitconverter.converter;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Stack;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FormulaParser {

    private static final Pattern VARIABLE_PATTERN = Pattern.compile("\\b([a-zA-Z])\\b");
    
    private static final Map<String, Double> CONSTANTS = new HashMap<>();
    static {
        CONSTANTS.put("e", Math.E);
        CONSTANTS.put("pi", Math.PI);
    }

    public static double evaluate(String formula, double x) throws IllegalArgumentException, ArithmeticException {
        if (formula == null || formula.trim().isEmpty()) {
            throw new IllegalArgumentException("公式不能为空");
        }

        try {
            String processedFormula = formula.trim();
            processedFormula = insertImplicitMultiplication(processedFormula);
            processedFormula = replaceVariables(processedFormula, x);
            return evaluateExpression(processedFormula);
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (ArithmeticException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalArgumentException("公式计算错误: " + e.getMessage(), e);
        }
    }

    private static String insertImplicitMultiplication(String formula) {
        StringBuilder result = new StringBuilder();
        int len = formula.length();
        
        for (int i = 0; i < len; i++) {
            char current = formula.charAt(i);
            result.append(current);
            
            if (i == len - 1) {
                continue;
            }
            
            char next = formula.charAt(i + 1);
            
            if (isDigitOrCloseParen(current) && (next == '(' || isLetter(next))) {
                result.append('*');
            }
            else if (current == ')' && (Character.isDigit(next) || next == '(' || isLetter(next))) {
                result.append('*');
            }
        }
        
        return result.toString();
    }

    private static boolean isDigitOrCloseParen(char c) {
        return Character.isDigit(c) || c == ')' || c == '.';
    }

    private static boolean isLetter(char c) {
        return Character.isLetter(c);
    }

    private static String replaceVariables(String formula, double x) {
        String result = formula;
        java.util.Set<String> replaced = new java.util.HashSet<>();
        
        Matcher matcher = VARIABLE_PATTERN.matcher(result);
        while (matcher.find()) {
            String varName = matcher.group(1).toLowerCase();
            if (replaced.contains(varName)) {
                continue;
            }
            
            if (CONSTANTS.containsKey(varName)) {
                continue;
            }
            
            double value;
            if (varName.equals("x")) {
                value = x;
            } else if (varName.equals("y")) {
                value = 0.0;
            } else if (varName.equals("a")) {
                value = 4.0;
            } else if (varName.equals("b")) {
                value = 0.0;
            } else {
                value = 0.0;
            }
            
            String valueStr = formatValue(value);
            result = result.replaceAll("\\b" + Pattern.quote(varName) + "\\b", Matcher.quoteReplacement(valueStr));
            replaced.add(varName);
            matcher = VARIABLE_PATTERN.matcher(result);
        }
        
        return result;
    }

    private static String formatValue(double value) {
        if (value < 0) {
            return "(" + value + ")";
        }
        return String.valueOf(value);
    }

    private static double evaluateExpression(String expression) {
        List<Token> tokens = tokenize(expression);
        return evaluateTokens(tokens);
    }

    private static List<Token> tokenize(String expression) {
        List<Token> tokens = new ArrayList<>();
        int i = 0;
        int len = expression.length();

        while (i < len) {
            char c = expression.charAt(i);

            if (Character.isWhitespace(c)) {
                i++;
                continue;
            }

            if (Character.isLetter(c)) {
                int start = i;
                while (i < len && Character.isLetter(expression.charAt(i))) {
                    i++;
                }
                String word = expression.substring(start, i);
                
                if (CONSTANTS.containsKey(word.toLowerCase())) {
                    tokens.add(new Token(TokenType.NUMBER, String.valueOf(CONSTANTS.get(word.toLowerCase()))));
                } else {
                    TokenType type = getFunctionType(word);
                    if (type != null) {
                        tokens.add(new Token(type, word));
                    } else {
                        throw new IllegalArgumentException("未知标识符: " + word);
                    }
                }
                continue;
            }

            if (Character.isDigit(c) || c == '.') {
                int start = i;
                boolean hasDecimal = false;
                while (i < len && (Character.isDigit(expression.charAt(i)) || 
                       (expression.charAt(i) == '.' && !hasDecimal))) {
                    if (expression.charAt(i) == '.') {
                        hasDecimal = true;
                    }
                    i++;
                }
                String numStr = expression.substring(start, i);
                tokens.add(new Token(TokenType.NUMBER, numStr));
                continue;
            }

            if (c == '+' || c == '-' || c == '*' || c == '/' || c == '^' || c == '%') {
                if (c == '-' && (i == 0 || isUnaryMinusContext(tokens, expression, i))) {
                    tokens.add(new Token(TokenType.UNARY_MINUS, "-"));
                } else {
                    tokens.add(new Token(TokenType.OPERATOR, String.valueOf(c)));
                }
                i++;
                continue;
            }

            if (c == '(') {
                tokens.add(new Token(TokenType.LEFT_PAREN, "("));
                i++;
                continue;
            }

            if (c == ')') {
                tokens.add(new Token(TokenType.RIGHT_PAREN, ")"));
                i++;
                continue;
            }

            throw new IllegalArgumentException("未知字符: " + c);
        }

        return tokens;
    }

    private static boolean isUnaryMinusContext(List<Token> tokens, String expression, int pos) {
        if (tokens.isEmpty()) {
            return true;
        }
        
        Token lastToken = tokens.get(tokens.size() - 1);
        
        if (lastToken.type == TokenType.LEFT_PAREN) {
            return true;
        }
        
        if (lastToken.type == TokenType.OPERATOR) {
            return true;
        }
        
        if (lastToken.type == TokenType.UNARY_MINUS) {
            return true;
        }
        
        return false;
    }

    private static TokenType getFunctionType(String word) {
        String lower = word.toLowerCase();
        switch (lower) {
            case "sqrt": return TokenType.FUNC_SQRT;
            case "cbrt": return TokenType.FUNC_CBRT;
            case "log": return TokenType.FUNC_LOG;
            case "ln": return TokenType.FUNC_LN;
            case "sin": return TokenType.FUNC_SIN;
            case "cos": return TokenType.FUNC_COS;
            case "tan": return TokenType.FUNC_TAN;
            case "abs": return TokenType.FUNC_ABS;
            case "exp": return TokenType.FUNC_EXP;
            case "floor": return TokenType.FUNC_FLOOR;
            case "ceil": return TokenType.FUNC_CEIL;
            case "round": return TokenType.FUNC_ROUND;
            default: return null;
        }
    }

    private static double evaluateTokens(List<Token> tokens) {
        Stack<Double> values = new Stack<>();
        Stack<TokenType> operators = new Stack<>();

        for (int i = 0; i < tokens.size(); i++) {
            Token token = tokens.get(i);

            switch (token.type) {
                case NUMBER:
                    values.push(Double.parseDouble(token.value));
                    break;

                case UNARY_MINUS:
                    operators.push(TokenType.UNARY_MINUS);
                    break;

                case OPERATOR:
                    TokenType currentOp = getOperatorType(token.value.charAt(0));
                    while (!operators.isEmpty() && operators.peek() != TokenType.LEFT_PAREN &&
                           hasHigherPrecedence(operators.peek(), currentOp)) {
                        applyOperator(values, operators);
                    }
                    operators.push(currentOp);
                    break;

                case LEFT_PAREN:
                    operators.push(TokenType.LEFT_PAREN);
                    break;

                case RIGHT_PAREN:
                    while (!operators.isEmpty() && operators.peek() != TokenType.LEFT_PAREN) {
                        applyOperator(values, operators);
                    }
                    if (operators.isEmpty()) {
                        throw new IllegalArgumentException("括号不匹配");
                    }
                    operators.pop();

                    if (!operators.isEmpty() && isFunctionType(operators.peek())) {
                        applyFunction(values, operators.pop());
                    }
                    break;

                case FUNC_SQRT:
                case FUNC_CBRT:
                case FUNC_LOG:
                case FUNC_LN:
                case FUNC_SIN:
                case FUNC_COS:
                case FUNC_TAN:
                case FUNC_ABS:
                case FUNC_EXP:
                case FUNC_FLOOR:
                case FUNC_CEIL:
                case FUNC_ROUND:
                    operators.push(token.type);
                    break;
            }
        }

        while (!operators.isEmpty()) {
            if (operators.peek() == TokenType.LEFT_PAREN) {
                throw new IllegalArgumentException("括号不匹配");
            }
            applyOperator(values, operators);
        }

        if (values.size() != 1) {
            throw new IllegalArgumentException("表达式格式错误");
        }

        return values.pop();
    }

    private static void applyOperator(Stack<Double> values, Stack<TokenType> operators) {
        if (operators.isEmpty()) {
            return;
        }

        TokenType op = operators.pop();

        if (op == TokenType.UNARY_MINUS) {
            if (values.isEmpty()) {
                throw new IllegalArgumentException("一元减号缺少操作数");
            }
            double val = values.pop();
            values.push(-val);
            return;
        }

        if (values.size() < 2) {
            throw new IllegalArgumentException("操作符缺少操作数");
        }

        double b = values.pop();
        double a = values.pop();

        switch (op) {
            case OP_ADD: values.push(a + b); break;
            case OP_SUB: values.push(a - b); break;
            case OP_MUL: values.push(a * b); break;
            case OP_DIV:
                if (b == 0) {
                    throw new IllegalArgumentException("除数不能为零");
                }
                values.push(a / b); break;
            case OP_MOD:
                if (b == 0) {
                    throw new IllegalArgumentException("模数不能为零");
                }
                values.push(a % b); break;
            case OP_POW: values.push(Math.pow(a, b)); break;
            default:
                throw new IllegalArgumentException("未知操作符");
        }
    }

    private static void applyFunction(Stack<Double> values, TokenType func) {
        if (values.isEmpty()) {
            throw new IllegalArgumentException("函数缺少参数");
        }

        double val = values.pop();

        switch (func) {
            case FUNC_SQRT:
                if (val < 0) {
                    throw new ArithmeticException("负数不能开平方");
                }
                values.push(Math.sqrt(val));
                break;
            case FUNC_CBRT:
                values.push(Math.cbrt(val));
                break;
            case FUNC_LOG:
                if (val <= 0) {
                    throw new ArithmeticException("对数的参数必须大于零");
                }
                values.push(Math.log10(val));
                break;
            case FUNC_LN:
                if (val <= 0) {
                    throw new ArithmeticException("对数的参数必须大于零");
                }
                values.push(Math.log(val));
                break;
            case FUNC_SIN:
                values.push(Math.sin(Math.toRadians(val)));
                break;
            case FUNC_COS:
                values.push(Math.cos(Math.toRadians(val)));
                break;
            case FUNC_TAN:
                values.push(Math.tan(Math.toRadians(val)));
                break;
            case FUNC_ABS:
                values.push(Math.abs(val));
                break;
            case FUNC_EXP:
                values.push(Math.exp(val));
                break;
            case FUNC_FLOOR:
                values.push(Math.floor(val));
                break;
            case FUNC_CEIL:
                values.push(Math.ceil(val));
                break;
            case FUNC_ROUND:
                values.push((double) Math.round(val));
                break;
            default:
                throw new IllegalArgumentException("未知函数");
        }
    }

    private static TokenType getOperatorType(char c) {
        switch (c) {
            case '+': return TokenType.OP_ADD;
            case '-': return TokenType.OP_SUB;
            case '*': return TokenType.OP_MUL;
            case '/': return TokenType.OP_DIV;
            case '%': return TokenType.OP_MOD;
            case '^': return TokenType.OP_POW;
            default: throw new IllegalArgumentException("未知操作符: " + c);
        }
    }

    private static boolean isFunctionType(TokenType type) {
        return type == TokenType.FUNC_SQRT || type == TokenType.FUNC_CBRT ||
               type == TokenType.FUNC_LOG || type == TokenType.FUNC_LN ||
               type == TokenType.FUNC_SIN || type == TokenType.FUNC_COS ||
               type == TokenType.FUNC_TAN || type == TokenType.FUNC_ABS ||
               type == TokenType.FUNC_EXP || type == TokenType.FUNC_FLOOR ||
               type == TokenType.FUNC_CEIL || type == TokenType.FUNC_ROUND;
    }

    private static boolean hasHigherPrecedence(TokenType op1, TokenType op2) {
        int prec1 = getPrecedence(op1);
        int prec2 = getPrecedence(op2);
        if (prec1 == prec2 && op1 == TokenType.OP_POW) {
            return false;
        }
        return prec1 >= prec2;
    }

    private static int getPrecedence(TokenType op) {
        switch (op) {
            case OP_ADD:
            case OP_SUB:
                return 1;
            case OP_MUL:
            case OP_DIV:
            case OP_MOD:
                return 2;
            case OP_POW:
                return 3;
            case UNARY_MINUS:
                return 4;
            default:
                return 0;
        }
    }

    private enum TokenType {
        NUMBER,
        UNARY_MINUS,
        OPERATOR,
        OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD, OP_POW,
        LEFT_PAREN,
        RIGHT_PAREN,
        FUNC_SQRT, FUNC_CBRT, FUNC_LOG, FUNC_LN,
        FUNC_SIN, FUNC_COS, FUNC_TAN,
        FUNC_ABS, FUNC_EXP, FUNC_FLOOR, FUNC_CEIL, FUNC_ROUND
    }

    private static class Token {
        final TokenType type;
        final String value;

        Token(TokenType type, String value) {
            this.type = type;
            this.value = value;
        }
    }

    public static boolean isValidFormula(String formula) {
        if (formula == null || formula.trim().isEmpty()) {
            return false;
        }
        try {
            evaluate(formula, 1.0);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
