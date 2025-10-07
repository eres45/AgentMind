# Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd agentic-reasoning-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Process Test CSV

**Windows**:
```bash
run_test.bat
```

**Linux/Mac**:
```bash
chmod +x run_test.sh
./run_test.sh
```

**Manual**:
```bash
python process_test.py --input ../test.csv --output predictions.csv
```

### 3. Run Demo

```bash
# Interactive demo with examples
python demo.py --mode demo

# Quick solve single problem
python demo.py --mode quick
```

## Command Line Options

### process_test.py

```bash
python process_test.py [OPTIONS]

Options:
  -i, --input PATH    Input test CSV file [default: ../test.csv]
  -o, --output PATH   Output predictions CSV [default: predictions.csv]
  -q, --quiet         Suppress verbose output
```

### demo.py

```bash
python demo.py [OPTIONS]

Options:
  -m, --mode MODE     Run mode: demo or quick [default: demo]
```

## Python API

### Basic Usage

```python
from reasoning_system import create_reasoning_system

# Create system
system = create_reasoning_system(verbose=True)

# Solve a problem
result = system.solve(
    problem="You overtake second place in a race. What position are you in?",
    topic="Classic riddles",
    options=["First", "Second", "Third", "Fourth", "Another answer"]
)

# Access results
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Time: {result.execution_time:.2f}s")

# Get reasoning trace
print(result.reasoning_chain.get_summary())
```

### Batch Processing

```python
from reasoning_system import create_reasoning_system

system = create_reasoning_system(verbose=False)

problems = [
    {
        'problem': 'What is 2+2?',
        'topic': 'Mathematical',
        'options': ['3', '4', '5', '6', 'Another answer']
    },
    {
        'problem': 'What comes next: 1, 2, 4, 8, __?',
        'topic': 'Sequence solving',
        'options': ['12', '16', '20', '32', 'Another answer']
    }
]

results = system.solve_batch(problems)

for result in results:
    print(f"{result.problem[:50]}... → {result.answer}")
```

### Accessing Individual Agents

```python
from agents.planner import PlannerAgent
from agents.reasoner import ReasonerAgent
from agents.verifier import VerifierAgent

# Use planner independently
planner = PlannerAgent()
plan = planner.create_plan(
    "Find the next number: 2, 4, 6, 8, __",
    topic="Sequence solving"
)

print(f"Problem Type: {plan.problem_type}")
print(f"Strategy: {plan.strategy}")
print(f"Sub-problems: {len(plan.sub_problems)}")
```

### Using Tools Directly

```python
from tools.tool_engine import ToolEngine

engine = ToolEngine()

# Calculator
result = engine.calculator.evaluate("2 + 3 * 4")
print(f"Result: {result}")  # 14

# Pattern Analyzer
sequence = [2, 4, 6, 8, 10]
next_val = engine.pattern_analyzer.predict_next(sequence)
print(f"Next: {next_val}")  # 12

# Symbolic Solver
solutions = engine.symbolic_solver.solve_equation("x**2 - 5*x + 6")
print(f"Solutions: {solutions}")  # [2.0, 3.0]

# LCM calculation
lcm = engine.symbolic_solver.find_lcm(12, 18, 24)
print(f"LCM: {lcm}")  # 72
```

## Output Files

### predictions.csv

Format: `topic,problem_statement,solution,correct_option`

```csv
topic,problem_statement,solution,correct_option
Spatial reasoning,"A cube has...",REASONING PLAN:...,answer_option_2
Sequence solving,"Find next: 2,4,6...",Step 1: Identify...,answer_option_3
```

### predictions_reasoning_traces.txt

Detailed reasoning chain for each problem:
- Complete thought process
- All reasoning steps
- Tool usage
- Verification results

### predictions_summary.txt

Statistical summary:
- Total problems solved
- Processing time
- Confidence distribution
- Problem breakdown by topic

## Understanding Results

### Confidence Levels

- **High (>80%)**: Strong confidence in answer
- **Medium (60-80%)**: Reasonable confidence, may need review
- **Low (<60%)**: Uncertain, answer may be incorrect

### Reasoning Chain

Each step shows:
- **Action**: What was done
- **Thought**: Reasoning process
- **Tool**: Tool used (if any)
- **Output**: Tool result
- **Result**: Step conclusion
- **Verified**: ✓ or ✗
- **Confidence**: Step confidence score

### Verification Report

- **Valid**: Whether reasoning chain is logically sound
- **Issues**: Problems found in reasoning
- **Suggestions**: Ways to improve reasoning

## Common Issues

### Issue: Module not found

**Solution**:
```bash
# Ensure you're in the correct directory
cd agentic-reasoning-system

# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: test.csv not found

**Solution**:
- Ensure test.csv is in parent directory (`../test.csv`)
- Or specify path: `python process_test.py --input /path/to/test.csv`

### Issue: Low confidence scores

**Possible causes**:
- Ambiguous problem statement
- Insufficient information
- Complex multi-step reasoning
- Tool execution errors

**Actions**:
- Review reasoning trace
- Check for verification issues
- Manually verify the answer

### Issue: Slow processing

**Solutions**:
- Run in quiet mode: `--quiet`
- Reduce problem set for testing
- Check for network issues (if using LLM APIs)

## Advanced Usage

### Custom Problem Types

Add new problem types by extending the planner:

```python
from agents.planner import PlannerAgent, ProblemType
from enum import Enum

# Extend ProblemType
class CustomProblemType(Enum):
    MY_CUSTOM_TYPE = "my_custom_type"

# Add detection logic
planner = PlannerAgent()
planner.problem_keywords[CustomProblemType.MY_CUSTOM_TYPE] = [
    "keyword1", "keyword2"
]
```

### Custom Tools

Add new reasoning tools:

```python
from tools.tool_engine import ToolEngine

class MyCustomTool:
    def process(self, data):
        # Your custom logic
        return result

engine = ToolEngine()
engine.tool_registry['my_tool'] = MyCustomTool()
```

### Exporting Traces

```python
system = create_reasoning_system()

# Solve problems
# ...

# Export all reasoning traces
system.export_reasoning_traces('all_traces.txt')

# Get statistics
stats = system.get_statistics()
print(f"Average confidence: {stats['average_confidence']:.1%}")
```

## Best Practices

1. **Always review low-confidence answers** - These may need manual correction

2. **Use appropriate problem topics** - Helps the system choose the right strategy

3. **Provide answer options when available** - Improves answer matching

4. **Check reasoning traces for errors** - Understand where reasoning went wrong

5. **Cache results for repeated problems** - The system automatically caches solutions

6. **Monitor execution time** - Complex problems may take longer

## Performance Tips

- Use `verbose=False` for batch processing
- Process in batches for large datasets
- Monitor memory usage for very large test files
- Use quiet mode (`--quiet`) to reduce console output

## Getting Help

- Review `ARCHITECTURE.md` for system details
- Check `README.md` for project overview
- Examine example code in `demo.py`
- Look at reasoning traces to understand decisions
