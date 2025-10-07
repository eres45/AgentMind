"""
Self-Correction Agent
Validates and corrects reasoning errors autonomously
"""

from typing import Optional, Dict, List, Tuple
import re


class SelfCorrector:
    """
    Validates reasoning and suggests corrections
    Adds robustness through autonomous error detection
    """
    
    def __init__(self):
        self.correction_rules = self._init_correction_rules()
    
    def _init_correction_rules(self) -> Dict:
        """Initialize common error patterns and corrections"""
        return {
            'status_string': {
                'pattern': r'^(processed|calculated|verified|identified|optimal_solution|conclusion_reached)$',
                'message': 'Status string detected instead of actual answer',
                'action': 'retry_with_fallback'
            },
            'empty_result': {
                'pattern': r'^$',
                'message': 'Empty result returned',
                'action': 'use_alternative_method'
            },
            'units_missing': {
                'check': lambda r: any(char.isdigit() for char in r) and not any(unit in r.lower() for unit in ['cm', 'm', 'km', 'hours', 'minutes', 'units', 'pieces']),
                'message': 'Numerical result missing units',
                'action': 'add_units_from_context'
            }
        }
    
    def validate_result(self, result: str, problem: str, options: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate if result makes sense
        Returns: (is_valid, correction_message)
        """
        if not result:
            return False, "Empty result"
        
        result_lower = result.lower().strip()
        
        # Check for status strings
        status_strings = ['processed', 'calculated', 'verified', 'identified', 
                         'optimal_solution', 'conclusion_reached', 'equation_ready',
                         'options_evaluated', 'pattern_identified']
        if result_lower in status_strings:
            return False, f"Status string '{result}' is not a valid answer"
        
        # Check if result matches any option (if options provided)
        if options:
            # Exact match
            for opt in options:
                if result.strip() == opt.strip():
                    return True, None
            
            # Partial match
            for opt in options:
                if result.lower() in opt.lower() or opt.lower() in result.lower():
                    return True, f"Consider using full option: '{opt}'"
        
        # Check for reasonable number ranges (if numerical)
        numbers = re.findall(r'-?\d+\.?\d*', result)
        if numbers:
            num = float(numbers[0])
            if abs(num) > 1000000:
                return False, f"Unreasonably large number: {num}"
            if 'percentage' in problem.lower() or '%' in problem:
                if num > 100:
                    return False, f"Percentage > 100%: {num}"
        
        return True, None
    
    def suggest_correction(self, result: str, problem: str, 
                          reasoning_steps: List, options: Optional[List[str]] = None) -> Optional[str]:
        """
        Suggest a corrected answer based on reasoning steps
        """
        # Look for tool outputs in reasoning steps
        for step in reversed(reasoning_steps):
            if hasattr(step, 'tool_output') and step.tool_output:
                # Skip if tool_output is also a status string
                if isinstance(step.tool_output, str):
                    if step.tool_output.lower() in ['processed', 'calculated', 'verified']:
                        continue
                
                # Check if tool output matches options
                if options:
                    tool_output_str = str(step.tool_output)
                    for opt in options:
                        if tool_output_str.lower() in opt.lower() or opt.lower() in tool_output_str.lower():
                            return opt
                
                # Use tool output if it looks valid
                return str(step.tool_output)
        
        # Look for meaningful results in steps
        for step in reversed(reasoning_steps):
            if hasattr(step, 'result') and step.result:
                result_lower = step.result.lower()
                if result_lower not in ['processed', 'calculated', 'verified', 'identified']:
                    if options:
                        for opt in options:
                            if step.result in opt or opt in step.result:
                                return opt
                    return step.result
        
        # If we have options but no match, return first option as fallback
        if options:
            return options[0]
        
        return None
    
    def calculate_confidence(self, result: str, problem: str, 
                           reasoning_steps: List, verification_result: Optional[Dict] = None) -> float:
        """
        Calculate confidence score based on multiple factors
        """
        confidence = 0.5  # Base confidence
        
        # Factor 1: Result validation (+0.2 if valid)
        is_valid, _ = self.validate_result(result, problem)
        if is_valid:
            confidence += 0.2
        else:
            confidence -= 0.1
        
        # Factor 2: Tool usage (+0.1 per reliable tool used)
        reliable_tools = ['calculator', 'symbolic_solver', 'geometry_calculator', 
                         'constraint_solver', 'pattern_analyzer']
        tools_used = set(step.tool_used for step in reasoning_steps if hasattr(step, 'tool_used') and step.tool_used)
        confidence += 0.1 * len(tools_used & set(reliable_tools))
        
        # Factor 3: Verification passed (+0.2)
        if verification_result and verification_result.get('is_valid'):
            confidence += 0.2
        
        # Factor 4: Step confidence average
        step_confidences = [step.confidence for step in reasoning_steps 
                          if hasattr(step, 'confidence') and step.confidence > 0]
        if step_confidences:
            avg_step_confidence = sum(step_confidences) / len(step_confidences)
            confidence = (confidence + avg_step_confidence) / 2  # Blend
        
        # Cap confidence between 0.1 and 0.95
        return max(0.1, min(0.95, confidence))
    
    def self_correct(self, preliminary_answer: str, problem: str, 
                    reasoning_steps: List, options: Optional[List[str]] = None) -> Tuple[str, str, float]:
        """
        Main self-correction method
        Returns: (corrected_answer, correction_reason, confidence)
        """
        # Validate preliminary answer
        is_valid, validation_msg = self.validate_result(preliminary_answer, problem, options)
        
        correction_reason = ""
        final_answer = preliminary_answer
        
        if not is_valid:
            # Attempt correction
            suggested = self.suggest_correction(preliminary_answer, problem, reasoning_steps, options)
            if suggested and suggested != preliminary_answer:
                final_answer = suggested
                correction_reason = f"Corrected: {validation_msg} → Using {suggested}"
            else:
                correction_reason = f"Warning: {validation_msg}"
        
        # Calculate confidence
        confidence = self.calculate_confidence(final_answer, problem, reasoning_steps)
        
        return final_answer, correction_reason, confidence
    
    def verify_against_constraints(self, answer: str, problem: str) -> Dict:
        """
        Check if answer satisfies problem constraints
        """
        result = {
            'satisfies_constraints': True,
            'violations': []
        }
        
        # Extract numerical constraints
        if 'at least' in problem.lower():
            matches = re.findall(r'at least (\d+)', problem.lower())
            answer_nums = re.findall(r'\d+', answer)
            if matches and answer_nums:
                constraint = int(matches[0])
                value = int(answer_nums[0])
                if value < constraint:
                    result['satisfies_constraints'] = False
                    result['violations'].append(f"Value {value} < required minimum {constraint}")
        
        if 'at most' in problem.lower():
            matches = re.findall(r'at most (\d+)', problem.lower())
            answer_nums = re.findall(r'\d+', answer)
            if matches and answer_nums:
                constraint = int(matches[0])
                value = int(answer_nums[0])
                if value > constraint:
                    result['satisfies_constraints'] = False
                    result['violations'].append(f"Value {value} > allowed maximum {constraint}")
        
        return result


# Convenience function
def self_correct_answer(preliminary: str, problem: str, steps: List, options: Optional[List[str]] = None) -> Tuple[str, str, float]:
    """Quick function for self-correction"""
    corrector = SelfCorrector()
    return corrector.self_correct(preliminary, problem, steps, options)
