"""
Tool Selection & Execution Engine
Provides various tools for reasoning: calculators, symbolic solvers, code execution, etc.
"""

import ast
import operator
import re
from typing import Any, Dict, List, Optional, Union
from sympy import symbols, solve, simplify, sympify, lcm, gcd, factorial
from sympy.parsing.sympy_parser import parse_expr
import math


class ToolExecutionError(Exception):
    """Raised when tool execution fails"""
    pass


class Calculator:
    """Basic calculator for arithmetic operations"""
    
    @staticmethod
    def evaluate(expression: str) -> float:
        """Safely evaluate mathematical expressions"""
        try:
            # Remove spaces
            expression = expression.replace(" ", "")
            
            # Replace common math functions
            expression = expression.replace("^", "**")
            
            # Safe evaluation using ast
            allowed_names = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow,
                'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
                'tan': math.tan, 'log': math.log, 'exp': math.exp,
                'pi': math.pi, 'e': math.e
            }
            
            # Try sympy first for better math support
            try:
                result = sympify(expression)
                return float(result.evalf())
            except:
                # Fallback to ast eval
                code = compile(expression, "<string>", "eval")
                return eval(code, {"__builtins__": {}}, allowed_names)
                
        except Exception as e:
            raise ToolExecutionError(f"Calculator error: {str(e)}")
    
    @staticmethod
    def solve_arithmetic(operation: str, *args) -> float:
        """Perform specific arithmetic operations"""
        ops = {
            'add': operator.add,
            'subtract': operator.sub,
            'multiply': operator.mul,
            'divide': operator.truediv,
            'power': operator.pow,
            'modulo': operator.mod
        }
        
        if operation not in ops:
            raise ToolExecutionError(f"Unknown operation: {operation}")
        
        result = args[0]
        for arg in args[1:]:
            result = ops[operation](result, arg)
        
        return result


class SymbolicSolver:
    """Symbolic mathematics solver using SymPy"""
    
    @staticmethod
    def solve_equation(equation: str, variable: str = 'x') -> List[Any]:
        """Solve algebraic equations"""
        try:
            var = symbols(variable)
            eq = parse_expr(equation)
            solutions = solve(eq, var)
            return [float(sol.evalf()) if sol.is_real else sol for sol in solutions]
        except Exception as e:
            raise ToolExecutionError(f"Symbolic solver error: {str(e)}")
    
    @staticmethod
    def simplify(expression: str) -> str:
        """Simplify mathematical expressions"""
        try:
            expr = parse_expr(expression)
            return str(simplify(expr))
        except Exception as e:
            raise ToolExecutionError(f"Simplification error: {str(e)}")
    
    @staticmethod
    def find_lcm(*numbers) -> int:
        """Find least common multiple"""
        try:
            result = numbers[0]
            for num in numbers[1:]:
                result = lcm(result, num)
            return int(result)
        except Exception as e:
            raise ToolExecutionError(f"LCM error: {str(e)}")
    
    @staticmethod
    def find_gcd(*numbers) -> int:
        """Find greatest common divisor"""
        try:
            result = numbers[0]
            for num in numbers[1:]:
                result = gcd(result, num)
            return int(result)
        except Exception as e:
            raise ToolExecutionError(f"GCD error: {str(e)}")
    
    @staticmethod
    def factorial(n: int) -> int:
        """Calculate factorial"""
        try:
            return int(factorial(n))
        except Exception as e:
            raise ToolExecutionError(f"Factorial error: {str(e)}")


class PatternAnalyzer:
    """Analyzes sequences and patterns"""
    
    @staticmethod
    def find_arithmetic_pattern(sequence: List[float]) -> Optional[float]:
        """Find common difference in arithmetic sequence"""
        if len(sequence) < 2:
            return None
        
        differences = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
        
        # Check if all differences are the same
        if len(set(differences)) == 1:
            return differences[0]
        
        return None
    
    @staticmethod
    def find_geometric_pattern(sequence: List[float]) -> Optional[float]:
        """Find common ratio in geometric sequence"""
        if len(sequence) < 2 or any(x == 0 for x in sequence[:-1]):
            return None
        
        ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence)-1)]
        
        # Check if all ratios are the same (within tolerance)
        if all(abs(r - ratios[0]) < 1e-6 for r in ratios):
            return ratios[0]
        
        return None
    
    @staticmethod
    def find_polynomial_pattern(sequence: List[float]) -> Optional[str]:
        """Try to find polynomial pattern by analyzing differences"""
        if len(sequence) < 3:
            return None
        
        # Try first differences
        diff1 = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
        if PatternAnalyzer.find_arithmetic_pattern(diff1):
            return "quadratic"
        
        # Try second differences
        if len(diff1) >= 2:
            diff2 = [diff1[i+1] - diff1[i] for i in range(len(diff1)-1)]
            if PatternAnalyzer.find_arithmetic_pattern(diff2):
                return "quadratic"
        
        return None
    
    @staticmethod
    def predict_next(sequence: List[float]) -> Optional[float]:
        """Predict the next number in a sequence"""
        # Try arithmetic
        diff = PatternAnalyzer.find_arithmetic_pattern(sequence)
        if diff is not None:
            return sequence[-1] + diff
        
        # Try geometric
        ratio = PatternAnalyzer.find_geometric_pattern(sequence)
        if ratio is not None:
            return sequence[-1] * ratio
        
        # Try quadratic (constant second difference)
        if len(sequence) >= 3:
            diff1 = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
            diff2 = [diff1[i+1] - diff1[i] for i in range(len(diff1)-1)]
            
            if len(set(diff2)) == 1:
                # Quadratic pattern
                next_diff1 = diff1[-1] + diff2[0]
                return sequence[-1] + next_diff1
        
        return None


class CodeExecutor:
    """Safe Python code execution for computational problems"""
    
    @staticmethod
    def execute(code: str, timeout: int = 5) -> Any:
        """Execute Python code safely with timeout"""
        try:
            # Create restricted globals
            safe_globals = {
                '__builtins__': {
                    'range': range, 'len': len, 'sum': sum,
                    'min': min, 'max': max, 'abs': abs,
                    'int': int, 'float': float, 'str': str,
                    'list': list, 'dict': dict, 'set': set,
                    'enumerate': enumerate, 'zip': zip,
                    'sorted': sorted, 'reversed': reversed,
                    'print': print
                },
                'math': math
            }
            
            local_vars = {}
            
            # Execute code
            exec(code, safe_globals, local_vars)
            
            # Return the result variable if it exists
            if 'result' in local_vars:
                return local_vars['result']
            
            return local_vars
            
        except Exception as e:
            raise ToolExecutionError(f"Code execution error: {str(e)}")


class LogicReasoner:
    """Logic reasoning engine for deductive reasoning"""
    
    @staticmethod
    def check_consistency(statements: List[Dict[str, Any]]) -> bool:
        """Check if a set of logical statements is consistent"""
        # Simple consistency checker
        facts = {}
        
        for stmt in statements:
            if 'variable' in stmt and 'value' in stmt:
                var = stmt['variable']
                val = stmt['value']
                
                if var in facts and facts[var] != val:
                    return False
                
                facts[var] = val
        
        return True
    
    @staticmethod
    def deduce(premises: List[str], rules: List[str]) -> List[str]:
        """Apply deductive reasoning"""
        # Simplified deductive reasoning
        conclusions = []
        
        # This would be more sophisticated in production
        # For now, return premises as baseline
        conclusions.extend(premises)
        
        return conclusions


class ToolEngine:
    """Main tool engine that manages all reasoning tools"""
    
    def __init__(self, use_mistral: bool = True):
        self.calculator = Calculator()
        self.symbolic_solver = SymbolicSolver()
        self.pattern_analyzer = PatternAnalyzer()
        self.code_executor = CodeExecutor()
        self.logic_reasoner = LogicReasoner()
        
        self.tool_registry = {
            'calculator': self.calculator,
            'symbolic_solver': self.symbolic_solver,
            'pattern_analyzer': self.pattern_analyzer,
            'code_executor': self.code_executor,
            'logic_reasoner': self.logic_reasoner
        }
        
        # Optional: Add Mistral as an intelligent assistant tool
        self.mistral_tool = None
        if use_mistral:
            try:
                from tools.mistral_tool import MistralTool
                self.mistral_tool = MistralTool()
                self.tool_registry['mistral'] = self.mistral_tool
            except Exception as e:
                print(f"Note: Mistral tool not available: {str(e)}")
                pass
    
    def get_tool(self, tool_name: str):
        """Get a specific tool by name"""
        if tool_name not in self.tool_registry:
            raise ToolExecutionError(f"Unknown tool: {tool_name}")
        return self.tool_registry[tool_name]
    
    def execute_tool(self, tool_name: str, method: str, *args, **kwargs) -> Any:
        """Execute a tool method"""
        try:
            tool = self.get_tool(tool_name)
            method_func = getattr(tool, method)
            return method_func(*args, **kwargs)
        except AttributeError:
            raise ToolExecutionError(f"Tool {tool_name} has no method {method}")
        except Exception as e:
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")
    
    def list_available_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tool_registry.keys())
