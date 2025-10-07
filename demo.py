"""
Quick Demo of Agentic AI Reasoning System
Demonstrates solving various types of logic problems
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from reasoning_system import create_reasoning_system


def demo_examples():
    """Run demo with various example problems"""
    
    print("\n" + "="*70)
    print("🧠 AGENTIC AI REASONING SYSTEM - DEMO")
    print("="*70)
    print("\nDemonstrating multi-agent reasoning on different problem types\n")
    
    # Create reasoning system
    system = create_reasoning_system(verbose=True)
    
    # Example problems
    examples = [
        {
            'name': 'Classic Riddle',
            'problem': 'You are in a race and you overtake the second person. What position are you in now?',
            'topic': 'Classic riddles',
            'options': ['First', 'Second', 'Third', 'Fourth', 'Another answer']
        },
        {
            'name': 'Sequence Pattern',
            'problem': 'What is the next number in the sequence: 2, 6, 12, 20, __?',
            'topic': 'Sequence solving',
            'options': ['28', '30', '32', '34', 'Another answer']
        },
        {
            'name': 'Spatial Reasoning',
            'problem': 'A 10x10x10 cube is painted red on all sides. If broken into 1x1x1 cubes, how many small cubes will have red paint on exactly two sides?',
            'topic': 'Spatial reasoning',
            'options': ['88', '96', '104', '112', 'Another answer']
        },
        {
            'name': 'Logic Puzzle',
            'problem': 'Two fathers and two sons went fishing. Each caught one fish, so they brought home three fishes in total. How is that possible?',
            'topic': 'Classic riddles',
            'options': [
                'They threw back the smallest fish',
                'One fish got away',
                'There were only three men: a grandfather, his son, and his grandson',
                'One man caught two fish',
                'Another answer'
            ]
        },
        {
            'name': 'Mathematical Reasoning',
            'problem': 'A wealthy book collector dies and leaves 17 gold coins to his three sons. The eldest gets 1/2, the middle gets 1/3, and the youngest gets 1/9. How can they divide the coins without melting them?',
            'topic': 'Classic riddles',
            'options': [
                'Borrow 1 coin and divide; eldest gets 9, middle gets 6, and youngest gets 2, then return the borrowed coin',
                'The sons cannot divide the coins without melting or damaging them',
                'Each son gets an equal amount, 17 divided by 3, rounded down',
                'They auction the coins and divide the money according to the will\'s proportions',
                'Another answer'
            ]
        }
    ]
    
    results = []
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'#'*70}")
        print(f"# EXAMPLE {i}: {example['name']}")
        print(f"{'#'*70}\n")
        
        result = system.solve(
            problem=example['problem'],
            topic=example['topic'],
            options=example['options']
        )
        
        results.append({
            'name': example['name'],
            'result': result
        })
        
        print(f"\n{'─'*70}")
        print("RESULT:")
        print(f"{'─'*70}")
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Time: {result.execution_time:.2f}s")
        print(f"Reasoning Steps: {len(result.reasoning_chain.steps)}")
        
        if result.verification.issues:
            print(f"\n⚠️  Issues: {', '.join(result.verification.issues)}")
        
        input("\n⏎ Press Enter to continue to next example...")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 DEMO SUMMARY")
    print(f"{'='*70}\n")
    
    for item in results:
        print(f"✓ {item['name']}")
        print(f"  Answer: {item['result'].answer}")
        print(f"  Confidence: {item['result'].confidence:.1%}")
        print()
    
    stats = system.get_statistics()
    print(f"Average Confidence: {stats['average_confidence']:.1%}")
    print(f"Average Time: {stats['average_execution_time']:.2f}s")
    print(f"High Confidence (>80%): {stats['high_confidence_count']}/{stats['total_problems']}")
    
    print(f"\n{'='*70}\n")
    
    # Offer to show detailed trace
    show_trace = input("Would you like to see a detailed reasoning trace? (y/n): ")
    if show_trace.lower() == 'y':
        idx = int(input(f"Which example (1-{len(examples)})? ")) - 1
        if 0 <= idx < len(results):
            print(results[idx]['result'].get_summary())


def quick_solve():
    """Quick solve mode - solve a single problem"""
    
    print("\n" + "="*70)
    print("🚀 QUICK SOLVE MODE")
    print("="*70 + "\n")
    
    problem = input("Enter your problem: ")
    
    if not problem.strip():
        print("❌ No problem entered. Exiting.")
        return
    
    topic = input("Topic (optional, press Enter to skip): ")
    
    # Ask for options
    has_options = input("Do you have answer options? (y/n): ")
    options = None
    
    if has_options.lower() == 'y':
        print("Enter options (press Enter twice when done):")
        options = []
        while True:
            opt = input(f"  Option {len(options)+1}: ")
            if not opt.strip():
                break
            options.append(opt)
        
        if options:
            options.append("Another answer")
    
    # Solve
    system = create_reasoning_system(verbose=True)
    result = system.solve(problem, topic if topic else None, options)
    
    print(result.get_summary())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Agentic AI Reasoning System Demo')
    parser.add_argument('--mode', '-m', choices=['demo', 'quick'], default='demo',
                       help='Run mode: demo (examples) or quick (single problem)')
    
    args = parser.parse_args()
    
    if args.mode == 'demo':
        demo_examples()
    else:
        quick_solve()
