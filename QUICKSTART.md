# ⚡ Quick Start Guide

Get up and running in 3 minutes!

## 🚀 Installation (1 minute)

```bash
# Navigate to project
cd agentic-reasoning-system

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Run Your First Problem (30 seconds)

```bash
python demo.py --mode quick
```

Enter a problem like:
```
Problem: You overtake second place in a race. What position are you in?
Topic: logic
Options: First, Second, Third
```

## 📊 Process Test CSV (1 minute)

```bash
# Windows
run_test.bat

# Linux/Mac
./run_test.sh
```

**Output**: `predictions.csv` with all answers!

## 🌐 Start API Server (30 seconds)

```bash
cd backend
python api.py
```

Visit: http://localhost:8000/docs

## 📝 Test Single Problem via Code

```python
from reasoning_system import create_reasoning_system

system = create_reasoning_system(verbose=True)

result = system.solve(
    problem="What is 2+2?",
    options=["3", "4", "5", "6"]
)

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence:.0%}")
```

## ✅ Verify It Works

Run the demo:
```bash
python demo.py --mode demo
```

You should see 5 example problems solved with reasoning traces!

## 🔑 Mistral API Key

Already configured in `.env.example`:
```
MISTRAL_API_KEY=DvJWwEBKjoxbC0ZjR7jfiyTP2XwhDLny
```

The system will use it automatically!

## 📂 Where Are My Results?

After running `process_test.py`:
- `predictions.csv` - Your answers
- `predictions_reasoning_traces.txt` - Full reasoning
- `predictions_summary.txt` - Statistics

## 🆘 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "test.csv not found"
Make sure test.csv is in parent directory (`../test.csv`)

### Mistral API issues
System works without Mistral! Symbolic tools still function.

## 🎓 Next Steps

1. ✅ Read `README.md` for overview
2. ✅ Check `USAGE.md` for detailed examples
3. ✅ Review `ARCHITECTURE.md` for technical details
4. ✅ See `MISTRAL_INTEGRATION.md` for AI insights

---

**You're ready! 🎉**
