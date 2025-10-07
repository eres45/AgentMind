# System Architecture

## Overview

The Agentic AI Reasoning System is a multi-agent architecture designed to solve complex logic problems through systematic reasoning, verification, and self-correction.

## Core Components

### 1. Planner Agent (`agents/planner.py`)

**Responsibility**: Problem analysis and strategy formulation

**Key Functions**:
- `classify_problem()`: Identifies problem type (spatial, mathematical, logical, etc.)
- `select_strategy()`: Chooses appropriate reasoning approach
- `decompose_problem()`: Breaks complex problems into sub-tasks
- `identify_tools()`: Determines which reasoning tools are needed
- `extract_constraints()`: Identifies problem constraints

**Problem Types**:
- Spatial Reasoning
- Mathematical
- Logical
- Sequence Solving
- Optimization
- Lateral Thinking
- Classic Riddles

**Reasoning Strategies**:
- Direct Calculation
- Step-by-Step Logic
- Pattern Recognition
- Constraint Satisfaction
- Spatial Visualization
- Creative Thinking

### 2. Tool Engine (`tools/tool_engine.py`)

**Responsibility**: Provides computational tools for reasoning

**Available Tools**:

#### Calculator
- Basic arithmetic operations
- Safe mathematical expression evaluation
- Support for common math functions (sqrt, sin, cos, etc.)

#### Symbolic Solver
- Algebraic equation solving using SymPy
- Expression simplification
- LCM/GCD calculations
- Factorial computations

#### Pattern Analyzer
- Arithmetic sequence detection (common difference)
- Geometric sequence detection (common ratio)
- Polynomial pattern analysis
- Next term prediction

#### Code Executor
- Safe Python code execution
- Restricted namespace for security
- Timeout protection

#### Logic Reasoner
- Consistency checking
- Deductive reasoning
- Premise validation

### 3. Reasoner Agent (`agents/reasoner.py`)

**Responsibility**: Executes reasoning plan step-by-step

**Key Classes**:

#### ReasoningStep
Represents a single step in the reasoning chain:
- Action description
- Thought process
- Tool used and results
- Verification status
- Confidence score

#### ReasoningChain
Complete sequence of reasoning steps:
- Problem statement
- Reasoning plan
- All steps taken
- Final answer
- Overall confidence

**Execution Flow**:
1. Execute each sub-problem from the plan
2. Route to appropriate handler based on problem type
3. Use tools when needed
4. Document each step's thought process
5. Aggregate results into final answer

### 4. Verifier Agent (`agents/verifier.py`)

**Responsibility**: Validates reasoning and checks correctness

**Verification Checks**:

#### Step-Level Verification
- Result presence check
- Tool usage appropriateness
- Output validity (NaN, infinity checks)
- Thought process completeness

#### Chain-Level Verification
- Plan completeness
- Logical flow between steps
- Constraint satisfaction
- Final answer validity

#### Confidence Scoring
Factors considered:
- Verification pass rate (40%)
- Plan completion (20%)
- Tool usage (20%)
- Critical errors (20%)

### 5. Main Reasoning System (`reasoning_system.py`)

**Responsibility**: Orchestrates all agents

**Workflow**:

```
Input Problem
     ↓
1. PLAN (Planner Agent)
   - Classify problem type
   - Select strategy
   - Decompose into sub-problems
   - Identify required tools
     ↓
2. REASON (Reasoner Agent)
   - Execute each sub-problem
   - Use tools as needed
   - Build reasoning chain
   - Determine answer
     ↓
3. VERIFY (Verifier Agent)
   - Check each step
   - Validate chain logic
   - Calculate confidence
     ↓
4. REFINE
   - Match answer to options
   - Apply verification feedback
   - Finalize result
     ↓
Output: Answer + Reasoning Trace + Confidence
```

## Data Flow

```
Problem → PlannerAgent → ReasoningPlan
                              ↓
ReasoningPlan → ReasonerAgent → ReasoningChain
                                      ↓
ReasoningChain → VerifierAgent → VerificationResult
                                         ↓
                                  SolutionResult
```

## Key Design Principles

### 1. Separation of Concerns
Each agent has a single, well-defined responsibility

### 2. Transparency
Every reasoning step is documented and visible

### 3. Verifiability
All steps can be checked for correctness

### 4. Tool-Augmented Reasoning
Agents use specialized tools rather than relying solely on LLMs

### 5. Confidence Scoring
System provides honest assessment of solution quality

### 6. Extensibility
Easy to add new problem types, tools, or verification rules

## Error Handling

### Tool Execution Errors
- Caught and logged in reasoning step
- Alternative approaches attempted
- Confidence reduced appropriately

### Verification Failures
- Issues documented
- Suggestions provided
- Confidence adjusted

### Missing Tools
- Graceful degradation
- Use available tools
- Document limitations

## Performance Optimization

### Caching
- Solution results cached by problem
- Avoid re-solving identical problems

### Tool Selection
- Only load tools required by plan
- Minimize unnecessary computations

### Early Termination
- Stop if confidence threshold not met
- Request additional reasoning if needed

## Extensibility Points

### Adding New Problem Types
1. Add to `ProblemType` enum in `planner.py`
2. Add keywords to `problem_keywords` dict
3. Implement handler in `reasoner.py`
4. Add verification rules in `verifier.py`

### Adding New Tools
1. Create tool class in `tool_engine.py`
2. Register in `ToolEngine.__init__()`
3. Add to tool selection logic in planner

### Adding New Verification Rules
1. Add to `verification_rules` in `verifier.py`
2. Implement check method
3. Update confidence calculation

## Testing Strategy

### Unit Tests
- Individual tool functions
- Problem classification
- Pattern detection

### Integration Tests
- Complete reasoning chains
- Multi-step problems
- Tool coordination

### End-to-End Tests
- Full problem solving
- Verification accuracy
- Performance benchmarks

## Future Enhancements

1. **LLM Integration**: Use GPT-4 for enhanced reasoning
2. **Parallel Processing**: Solve multiple problems simultaneously
3. **Learning System**: Improve from past solutions
4. **Interactive Mode**: Allow human-in-the-loop verification
5. **Visualization**: Graph reasoning chains
6. **API Server**: REST API for external integration
