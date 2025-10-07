"""
Verifier & Validation System
Checks correctness of reasoning steps and validates final answers
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

from agents.reasoner import ReasoningChain, ReasoningStep
from agents.planner import ReasoningPlan


@dataclass
class VerificationResult:
    """Result of verification"""
    is_valid: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'is_valid': self.is_valid,
            'confidence': self.confidence,
            'issues': self.issues,
            'suggestions': self.suggestions
        }


class VerifierAgent:
    """
    Validates reasoning steps and final answers
    """
    
    def __init__(self):
        self.verification_rules = self._load_verification_rules()
    
    def _load_verification_rules(self) -> Dict:
        """Load verification rules for different problem types"""
        return {
            'spatial_reasoning': {
                'checks': [
                    'dimensions_positive',
                    'calculations_correct',
                    'units_consistent'
                ]
            },
            'mathematical': {
                'checks': [
                    'arithmetic_correct',
                    'constraints_satisfied',
                    'answer_reasonable'
                ]
            },
            'sequence': {
                'checks': [
                    'pattern_consistent',
                    'next_term_valid'
                ]
            },
            'logical': {
                'checks': [
                    'no_contradictions',
                    'premises_used',
                    'conclusion_follows'
                ]
            }
        }
    
    def verify_step(self, step: ReasoningStep, problem: str, 
                   plan: ReasoningPlan) -> VerificationResult:
        """Verify a single reasoning step"""
        
        issues = []
        suggestions = []
        confidence = 0.8  # Default confidence
        
        # Check if step has a result
        if not step.result and not step.tool_output:
            issues.append("Step produced no result")
            confidence = 0.3
        
        # Check if tool was used when expected
        if 'calculate' in step.action.lower() and not step.tool_used:
            suggestions.append("Consider using calculator tool for calculations")
            confidence -= 0.1
        
        # Verify tool output makes sense
        if step.tool_output:
            try:
                # Check for NaN or infinity
                if isinstance(step.tool_output, float):
                    import math
                    if math.isnan(step.tool_output) or math.isinf(step.tool_output):
                        issues.append("Tool output is NaN or infinite")
                        confidence = 0.2
            except:
                pass
        
        # Check thought process
        if not step.thought or len(step.thought) < 10:
            suggestions.append("Add more detailed reasoning")
            confidence -= 0.1
        
        is_valid = len(issues) == 0 and confidence > 0.5
        
        return VerificationResult(
            is_valid=is_valid,
            confidence=max(0.0, min(1.0, confidence)),
            issues=issues,
            suggestions=suggestions
        )
    
    def verify_chain(self, chain: ReasoningChain) -> VerificationResult:
        """Verify the complete reasoning chain"""
        
        all_issues = []
        all_suggestions = []
        step_confidences = []
        
        # Verify each step
        for step in chain.steps:
            result = self.verify_step(step, chain.problem, chain.plan)
            all_issues.extend(result.issues)
            all_suggestions.extend(result.suggestions)
            step_confidences.append(result.confidence)
            
            # Mark step as verified
            step.verified = result.is_valid
            step.confidence = result.confidence
        
        # Check chain completeness
        if len(chain.steps) < len(chain.plan.sub_problems):
            all_issues.append("Not all sub-problems were addressed")
        
        # Check for logical flow
        if len(chain.steps) > 1:
            for i in range(len(chain.steps) - 1):
                if not self._steps_connected(chain.steps[i], chain.steps[i+1]):
                    all_suggestions.append(f"Steps {i+1} and {i+2} may not be well connected")
        
        # Check final answer
        if not chain.final_answer or chain.final_answer == "Unable to determine answer":
            all_issues.append("No valid final answer determined")
            step_confidences.append(0.0)
        
        # Calculate overall confidence
        overall_confidence = (
            sum(step_confidences) / len(step_confidences) 
            if step_confidences else 0.5
        )
        
        # Reduce confidence if there are issues
        if all_issues:
            overall_confidence *= 0.7
        
        is_valid = len(all_issues) == 0 and overall_confidence > 0.6
        
        return VerificationResult(
            is_valid=is_valid,
            confidence=overall_confidence,
            issues=all_issues,
            suggestions=all_suggestions
        )
    
    def _steps_connected(self, step1: ReasoningStep, step2: ReasoningStep) -> bool:
        """Check if two consecutive steps are logically connected"""
        # Simple heuristic: check if step2 references step1's result
        if step1.result and step2.thought:
            return step1.result in step2.thought.lower()
        return True  # Assume connected if can't verify
    
    def validate_against_constraints(self, answer: str, constraints: List[str]) -> Tuple[bool, List[str]]:
        """Validate answer against problem constraints"""
        
        violations = []
        
        for constraint in constraints:
            # Parse constraint
            if not self._check_constraint(answer, constraint):
                violations.append(f"Violates constraint: {constraint}")
        
        return len(violations) == 0, violations
    
    def _check_constraint(self, answer: str, constraint: str) -> bool:
        """Check if answer satisfies a specific constraint"""
        
        # Simple constraint checking
        constraint_lower = constraint.lower()
        answer_lower = answer.lower()
        
        # Check for negative constraints
        if 'cannot' in constraint_lower or 'must not' in constraint_lower:
            # Extract what cannot be
            parts = re.split(r'cannot|must not', constraint_lower)
            if len(parts) > 1:
                forbidden = parts[1].strip()
                if forbidden in answer_lower:
                    return False
        
        # Check for positive constraints
        if 'must' in constraint_lower:
            parts = re.split(r'must', constraint_lower)
            if len(parts) > 1:
                required = parts[1].strip()
                if required not in answer_lower:
                    return False
        
        return True
    
    def calculate_confidence_score(self, chain: ReasoningChain, 
                                   verification: VerificationResult) -> float:
        """Calculate overall confidence score"""
        
        factors = []
        
        # Factor 1: Verification confidence
        factors.append(verification.confidence)
        
        # Factor 2: Plan completion
        plan_completion = len(chain.steps) / len(chain.plan.sub_problems) if chain.plan.sub_problems else 1.0
        factors.append(min(1.0, plan_completion))
        
        # Factor 3: Tool usage
        steps_with_tools = sum(1 for s in chain.steps if s.tool_used)
        expected_tools = len([t for t in chain.plan.required_tools if t != 'reasoning_engine'])
        tool_usage = steps_with_tools / expected_tools if expected_tools > 0 else 0.8
        factors.append(min(1.0, tool_usage))
        
        # Factor 4: No critical issues
        critical_issues = sum(1 for issue in verification.issues if 'error' in issue.lower())
        if critical_issues > 0:
            factors.append(0.3)
        else:
            factors.append(1.0)
        
        # Weighted average
        weights = [0.4, 0.2, 0.2, 0.2]
        confidence = sum(f * w for f, w in zip(factors, weights))
        
        return max(0.0, min(1.0, confidence))
    
    def get_verification_report(self, verification: VerificationResult) -> str:
        """Generate human-readable verification report"""
        
        report = "VERIFICATION REPORT\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Valid: {'✓' if verification.is_valid else '✗'}\n"
        report += f"Confidence: {verification.confidence:.0%}\n\n"
        
        if verification.issues:
            report += "Issues Found:\n"
            for issue in verification.issues:
                report += f"  ❌ {issue}\n"
            report += "\n"
        
        if verification.suggestions:
            report += "Suggestions:\n"
            for suggestion in verification.suggestions:
                report += f"  💡 {suggestion}\n"
            report += "\n"
        
        if not verification.issues and not verification.suggestions:
            report += "✓ All checks passed!\n"
        
        return report
