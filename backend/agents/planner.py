"""
Planner Agent - Problem Decomposition Module
Analyzes problems and creates reasoning strategies
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ProblemType(Enum):
    SPATIAL_REASONING = "spatial_reasoning"
    MATHEMATICAL = "mathematical"
    LOGICAL = "logical"
    SEQUENCE = "sequence"
    OPTIMIZATION = "optimization"
    LATERAL_THINKING = "lateral_thinking"
    CLASSIC_RIDDLE = "classic_riddle"


class ReasoningStrategy(Enum):
    DIRECT_CALCULATION = "direct_calculation"
    STEP_BY_STEP_LOGIC = "step_by_step_logic"
    PATTERN_RECOGNITION = "pattern_recognition"
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    SPATIAL_VISUALIZATION = "spatial_visualization"
    CREATIVE_THINKING = "creative_thinking"


@dataclass
class ReasoningPlan:
    """A structured plan for solving a problem"""
    problem_type: ProblemType
    strategy: ReasoningStrategy
    sub_problems: List[str]
    required_tools: List[str]
    constraints: List[str]
    expected_answer_format: str
    confidence_threshold: float = 0.7


class PlannerAgent:
    """
    Analyzes problems and creates structured reasoning plans
    """
    
    def __init__(self, use_mistral: bool = True):
        self.use_mistral = use_mistral
        self.mistral_tool = None
        
        if use_mistral:
            try:
                from tools.mistral_tool import MistralTool
                self.mistral_tool = MistralTool()
            except:
                pass
        
        self.problem_keywords = {
            ProblemType.SPATIAL_REASONING: [
                "cube", "3d", "surface", "volume", "faces", "edges", 
                "corner", "diagonal", "geometry", "shape", "rotate", "painted"
            ],
            ProblemType.MATHEMATICAL: [
                "calculate", "equation", "sum", "multiply", "divide",
                "percentage", "ratio", "average", "total", "machines"
            ],
            ProblemType.LOGICAL: [
                "if", "then", "true", "false", "statement", "consistent",
                "contradiction", "must be", "cannot be", "machine", "button"
            ],
            ProblemType.SEQUENCE: [
                "sequence", "pattern", "next number", "series", "follows",
                "continue", "missing", "dots"
            ],
            ProblemType.OPTIMIZATION: [
                "minimize", "maximize", "optimal", "best", "schedule",
                "efficiency", "shortest", "longest", "most", "least",
                "planning", "days", "hours", "tasks"
            ],
            ProblemType.LATERAL_THINKING: [
                "how can", "possible", "unexpected", "strange", 
                "shoots", "underwater", "hangs", "dies", "survived"
            ],
            ProblemType.CLASSIC_RIDDLE: [
                "riddle", "what am i", "puzzle", "classic", "race", 
                "overtake", "position", "gold coins", "will", "divide"
            ]
        }
    
    def classify_problem(self, problem: str, topic: Optional[str] = None) -> ProblemType:
        """Classify the problem type based on keywords and context"""
        problem_lower = problem.lower()
        
        # Use topic hint if provided
        if topic:
            topic_lower = topic.lower().replace(" ", "_")
            for ptype in ProblemType:
                if ptype.value in topic_lower or topic_lower in ptype.value:
                    return ptype
        
        # Score each problem type based on keyword matches
        scores = {}
        for ptype, keywords in self.problem_keywords.items():
            score = sum(1 for keyword in keywords if keyword in problem_lower)
            scores[ptype] = score
        
        # Return the highest scoring type, or default to LOGICAL
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return ProblemType.LOGICAL
    
    def select_strategy(self, problem_type: ProblemType, problem: str) -> ReasoningStrategy:
        """Select the appropriate reasoning strategy"""
        strategy_map = {
            ProblemType.SPATIAL_REASONING: ReasoningStrategy.SPATIAL_VISUALIZATION,
            ProblemType.MATHEMATICAL: ReasoningStrategy.DIRECT_CALCULATION,
            ProblemType.LOGICAL: ReasoningStrategy.STEP_BY_STEP_LOGIC,
            ProblemType.SEQUENCE: ReasoningStrategy.PATTERN_RECOGNITION,
            ProblemType.OPTIMIZATION: ReasoningStrategy.CONSTRAINT_SATISFACTION,
            ProblemType.LATERAL_THINKING: ReasoningStrategy.CREATIVE_THINKING,
            ProblemType.CLASSIC_RIDDLE: ReasoningStrategy.CREATIVE_THINKING
        }
        
        return strategy_map.get(problem_type, ReasoningStrategy.STEP_BY_STEP_LOGIC)
    
    def decompose_problem(self, problem: str, problem_type: ProblemType) -> List[str]:
        """Break down the problem into sub-problems"""
        sub_problems = []
        
        if problem_type == ProblemType.SPATIAL_REASONING:
            sub_problems = [
                "Identify the geometric shape/structure",
                "Determine relevant dimensions",
                "Apply spatial formulas or logic",
                "Calculate the answer"
            ]
        elif problem_type == ProblemType.MATHEMATICAL:
            sub_problems = [
                "Extract numerical values and relationships",
                "Set up equations or formulas",
                "Perform calculations",
                "Verify answer against constraints"
            ]
        elif problem_type == ProblemType.SEQUENCE:
            sub_problems = [
                "Identify the given sequence",
                "Analyze differences or ratios",
                "Determine the pattern rule",
                "Apply rule to find next term"
            ]
        elif problem_type == ProblemType.OPTIMIZATION:
            sub_problems = [
                "Identify constraints and objectives",
                "List all possible approaches",
                "Evaluate each option",
                "Select optimal solution"
            ]
        elif problem_type == ProblemType.LOGICAL:
            sub_problems = [
                "Identify given facts and conditions",
                "Determine what needs to be proven",
                "Apply logical rules step by step",
                "Reach conclusion"
            ]
        else:  # LATERAL_THINKING, CLASSIC_RIDDLE
            sub_problems = [
                "Identify literal interpretation",
                "Consider alternative meanings",
                "Apply creative thinking",
                "Find unconventional solution"
            ]
        
        return sub_problems
    
    def identify_tools(self, problem_type: ProblemType, problem: str) -> List[str]:
        """Identify which tools are needed"""
        tools = []
        
        # Always need basic reasoning
        tools.append("reasoning_engine")
        
        if problem_type in [ProblemType.MATHEMATICAL, ProblemType.SPATIAL_REASONING]:
            tools.append("calculator")
            tools.append("symbolic_solver")
        
        if problem_type == ProblemType.SEQUENCE:
            tools.append("pattern_analyzer")
            tools.append("calculator")
        
        if problem_type == ProblemType.OPTIMIZATION:
            tools.append("constraint_solver")
            tools.append("calculator")
        
        if "code" in problem.lower() or "program" in problem.lower():
            tools.append("code_executor")
        
        # Always add verifier
        tools.append("verifier")
        
        return tools
    
    def extract_constraints(self, problem: str) -> List[str]:
        """Extract constraints from the problem"""
        constraints = []
        
        # Look for common constraint patterns
        constraint_indicators = [
            "must", "cannot", "only", "exactly", "at least", "at most",
            "without", "given that", "assuming", "if", "provided that"
        ]
        
        sentences = problem.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in constraint_indicators):
                constraints.append(sentence.strip())
        
        return constraints
    
    def create_plan(self, problem: str, topic: Optional[str] = None) -> ReasoningPlan:
        """Create a complete reasoning plan for the problem"""
        
        # Use Mistral to understand problem structure (if available)
        problem_understanding = None
        if self.use_mistral and self.mistral_tool:
            try:
                problem_understanding = self.mistral_tool.understand_problem(problem, topic)
            except:
                pass
        
        # Step 1: Classify problem type
        problem_type = self.classify_problem(problem, topic)
        
        # Step 2: Select reasoning strategy
        strategy = self.select_strategy(problem_type, problem)
        
        # Step 3: Decompose into sub-problems
        sub_problems = self.decompose_problem(problem, problem_type)
        
        # Step 4: Identify required tools
        tools = self.identify_tools(problem_type, problem)
        
        # Step 5: Extract constraints
        constraints = self.extract_constraints(problem)
        
        # Step 6: Determine expected answer format
        answer_format = self._determine_answer_format(problem)
        
        plan = ReasoningPlan(
            problem_type=problem_type,
            strategy=strategy,
            sub_problems=sub_problems,
            required_tools=tools,
            constraints=constraints,
            expected_answer_format=answer_format,
            confidence_threshold=0.7
        )
        
        return plan
    
    def _determine_answer_format(self, problem: str) -> str:
        """Determine the expected format of the answer"""
        problem_lower = problem.lower()
        
        if "how many" in problem_lower:
            return "integer"
        elif "what is the" in problem_lower:
            if "percentage" in problem_lower or "%" in problem:
                return "percentage"
            elif "ratio" in problem_lower:
                return "ratio"
            else:
                return "value"
        elif "which" in problem_lower or "what" in problem_lower:
            return "categorical"
        elif "true or false" in problem_lower:
            return "boolean"
        else:
            return "text"
    
    def get_plan_summary(self, plan: ReasoningPlan) -> str:
        """Generate a human-readable summary of the plan"""
        summary = f"""
REASONING PLAN:
--------------
Problem Type: {plan.problem_type.value}
Strategy: {plan.strategy.value}

Sub-Problems:
{chr(10).join(f"  {i+1}. {sp}" for i, sp in enumerate(plan.sub_problems))}

Required Tools:
{chr(10).join(f"  - {tool}" for tool in plan.required_tools)}

Constraints:
{chr(10).join(f"  - {c}" for c in plan.constraints) if plan.constraints else "  None identified"}

Expected Answer Format: {plan.expected_answer_format}
Confidence Threshold: {plan.confidence_threshold * 100}%
"""
        return summary
