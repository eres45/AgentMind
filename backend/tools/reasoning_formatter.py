"""
Reasoning Trace Formatter
Provides human-readable, transparent reasoning traces for explainability
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FormattedTrace:
    """Structured reasoning trace with metadata"""
    step_number: int
    phase: str  # "Understanding", "Planning", "Execution", "Verification"
    action: str
    method: str  # Tool/algorithm used
    thought_process: str
    result: str
    confidence: float
    time_taken: float = 0.0


class ReasoningFormatter:
    """Formats reasoning chains into transparent, human-readable traces"""
    
    def __init__(self):
        self.phase_emojis = {
            "Understanding": "🔍",
            "Planning": "📋",
            "Execution": "⚙️",
            "Verification": "✓",
            "Final Answer": "🎯"
        }
    
    def format_step(self, step, step_type: str = "Execution") -> str:
        """
        Format a single reasoning step with rich context
        """
        emoji = self.phase_emojis.get(step_type, "•")
        
        # Build detailed explanation
        parts = []
        parts.append(f"{emoji} **Step {step.step_number}: {step.action}**\n")
        
        # Add thought process
        if step.thought:
            parts.append(f"   💭 Reasoning: {step.thought}\n")
        
        # Add tool/method used
        if step.tool_used:
            parts.append(f"   🔧 Method: {self._format_tool_name(step.tool_used)}\n")
        
        # Add tool input if relevant
        if step.tool_input and step.tool_used not in ['reasoning_engine', 'verifier']:
            parts.append(f"   📥 Input: {self._format_value(step.tool_input)}\n")
        
        # Add result
        if step.result and step.result not in ['processed', 'calculated', 'verified']:
            parts.append(f"   📤 Output: {self._format_value(step.result)}\n")
        
        # Add confidence if meaningful
        if step.confidence > 0 and step.confidence < 1:
            confidence_bar = self._confidence_bar(step.confidence)
            parts.append(f"   📊 Confidence: {confidence_bar} {step.confidence:.1%}\n")
        
        return "".join(parts)
    
    def format_chain(self, chain) -> str:
        """
        Format entire reasoning chain with structure
        """
        output = []
        output.append("=" * 70 + "\n")
        output.append("🧠 REASONING TRACE\n")
        output.append("=" * 70 + "\n\n")
        
        # Problem statement
        problem_preview = chain.problem[:100] + "..." if len(chain.problem) > 100 else chain.problem
        output.append(f"📝 Problem: {problem_preview}\n")
        output.append(f"🏷️  Type: {chain.plan.problem_type.value}\n")
        output.append(f"🎯 Strategy: {chain.plan.strategy.value}\n")
        output.append("\n")
        
        # Steps grouped by phase
        output.append("─" * 70 + "\n")
        output.append("REASONING STEPS\n")
        output.append("─" * 70 + "\n\n")
        
        for i, step in enumerate(chain.steps, 1):
            # Determine phase
            if i == 1:
                phase = "Understanding"
            elif i == len(chain.steps):
                phase = "Verification"
            else:
                phase = "Execution"
            
            output.append(self.format_step(step, phase))
            output.append("\n")
        
        # Final answer section
        output.append("=" * 70 + "\n")
        output.append(f"🎯 FINAL ANSWER: {chain.final_answer}\n")
        output.append(f"📊 Overall Confidence: {self._confidence_bar(chain.overall_confidence)} {chain.overall_confidence:.1%}\n")
        output.append("=" * 70 + "\n")
        
        return "".join(output)
    
    def format_comparison(self, preliminary: str, final: str, reason: str = None) -> str:
        """
        Format answer refinement explanation
        """
        output = []
        output.append("🔄 ANSWER REFINEMENT\n")
        output.append(f"   Initial: {preliminary}\n")
        output.append(f"   Final:   {final}\n")
        if reason:
            output.append(f"   Reason:  {reason}\n")
        return "".join(output)
    
    def format_tool_selection(self, problem_type: str, tools: List[str]) -> str:
        """
        Explain tool selection logic
        """
        output = []
        output.append("🔧 TOOL SELECTION\n")
        output.append(f"   Problem Type: {problem_type}\n")
        output.append(f"   Selected Tools: {', '.join(self._format_tool_name(t) for t in tools)}\n")
        output.append(f"   Rationale: Chosen based on problem characteristics\n")
        return "".join(output)
    
    def _format_tool_name(self, tool: str) -> str:
        """Format tool names to be human-readable"""
        name_map = {
            'calculator': 'Mathematical Calculator',
            'symbolic_solver': 'Symbolic Math Solver (SymPy)',
            'pattern_analyzer': 'Pattern Recognition Algorithm',
            'code_executor': 'Code Execution Engine',
            'logic_reasoner': 'Logical Deduction Engine',
            'mistral': 'Mistral AI Assistant',
            'constraint_solver': 'Constraint Satisfaction Solver',
            'geometry_calculator': 'Geometry Formula Calculator',
            'logic_trap_detector': 'Classic Logic Trap Database',
            'worst_case_analyzer': 'Worst-Case Scenario Analyzer',
            'machine_sequencer': 'Task Sequencing Optimizer',
            'verifier': 'Answer Verification System',
            'reasoning_engine': 'Multi-Step Reasoning Engine'
        }
        return name_map.get(tool, tool.replace('_', ' ').title())
    
    def _format_value(self, value: Any) -> str:
        """Format values for display"""
        if isinstance(value, (list, tuple)) and len(value) > 5:
            return f"[{', '.join(map(str, value[:5]))}...]"
        elif isinstance(value, float):
            return f"{value:.4f}"
        elif isinstance(value, str) and len(value) > 100:
            return value[:100] + "..."
        return str(value)
    
    def _confidence_bar(self, confidence: float) -> str:
        """Visual confidence bar"""
        filled = int(confidence * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}]"
    
    def export_to_dict(self, chain) -> Dict:
        """
        Export reasoning chain as structured JSON for analysis
        """
        return {
            'problem': chain.problem,
            'problem_type': chain.plan.problem_type.value,
            'strategy': chain.plan.strategy.value,
            'steps': [
                {
                    'step_number': step.step_number,
                    'action': step.action,
                    'thought': step.thought,
                    'tool_used': step.tool_used,
                    'result': step.result,
                    'confidence': step.confidence,
                    'verified': step.verified
                }
                for step in chain.steps
            ],
            'final_answer': chain.final_answer,
            'overall_confidence': chain.overall_confidence,
            'tools_used': list(set(step.tool_used for step in chain.steps if step.tool_used))
        }


# Convenience functions
def format_reasoning_trace(chain) -> str:
    """Quick function to format reasoning chain"""
    formatter = ReasoningFormatter()
    return formatter.format_chain(chain)

def export_reasoning_json(chain) -> Dict:
    """Quick function to export reasoning to JSON"""
    formatter = ReasoningFormatter()
    return formatter.export_to_dict(chain)
