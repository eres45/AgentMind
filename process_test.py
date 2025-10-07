"""
Process test.csv and generate prediction CSV
Reads problems, solves them using the Agentic Reasoning System, and outputs predictions
"""

import csv
import sys
import os
from typing import List, Dict
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from reasoning_system import create_reasoning_system


def parse_csv_row(row: Dict) -> Dict:
    """Parse a CSV row into problem data"""
    problem_data = {
        'topic': row.get('topic', ''),
        'problem': row.get('problem_statement', ''),
        'options': [
            row.get('answer_option_1', ''),
            row.get('answer_option_2', ''),
            row.get('answer_option_3', ''),
            row.get('answer_option_4', ''),
            row.get('answer_option_5', 'Another answer')
        ]
    }
    
    # Remove empty options
    problem_data['options'] = [opt for opt in problem_data['options'] if opt]
    
    return problem_data


def find_matching_option(answer: str, options: List[str]) -> str:
    """Find which option matches the answer"""
    answer_lower = answer.lower().strip()
    
    # Try exact match first
    for i, opt in enumerate(options, 1):
        if answer_lower == opt.lower().strip():
            return f"answer_option_{i}"
    
    # Try partial match
    for i, opt in enumerate(options, 1):
        if answer_lower in opt.lower() or opt.lower() in answer_lower:
            return f"answer_option_{i}"
    
    # Check for "Another answer"
    if any("another" in opt.lower() for opt in options):
        return f"answer_option_5"
    
    # Default to option 1 if no match
    return "answer_option_1"


def process_test_file(input_file: str, output_file: str, verbose: bool = True):
    """
    Process test CSV and generate predictions
    
    Args:
        input_file: Path to test.csv
        output_file: Path to output prediction CSV
        verbose: Whether to print progress
    """
    
    print(f"\n{'='*70}")
    print(f"🚀 AGENTIC AI REASONING SYSTEM - TEST PROCESSOR")
    print(f"{'='*70}\n")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"{'='*70}\n")
    
    # Create reasoning system
    system = create_reasoning_system(verbose=verbose)
    
    # Read test file
    problems = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            problem_data = parse_csv_row(row)
            problem_data['original_row'] = row
            problems.append(problem_data)
    
    print(f"📚 Loaded {len(problems)} problems\n")
    
    # Solve all problems
    results = []
    start_time = datetime.now()
    
    for i, prob_data in enumerate(problems, 1):
        print(f"\n{'─'*70}")
        print(f"Problem {i}/{len(problems)}")
        print(f"{'─'*70}")
        print(f"Topic: {prob_data['topic']}")
        print(f"Problem: {prob_data['problem'][:80]}...")
        
        try:
            result = system.solve(
                problem=prob_data['problem'],
                topic=prob_data['topic'],
                options=prob_data['options']
            )
            
            # Find which option was selected
            correct_option = find_matching_option(result.answer, prob_data['options'])
            
            results.append({
                'topic': prob_data['topic'],
                'problem_statement': prob_data['problem'],
                'solution': result.reasoning_chain.get_summary(),
                'correct_option': correct_option,
                'answer': result.answer,
                'confidence': result.confidence
            })
            
            print(f"✅ Answer: {result.answer}")
            print(f"   Option: {correct_option}")
            print(f"   Confidence: {result.confidence:.1%}")
            
        except Exception as e:
            print(f"❌ Error solving problem: {str(e)}")
            results.append({
                'topic': prob_data['topic'],
                'problem_statement': prob_data['problem'],
                'solution': f"Error: {str(e)}",
                'correct_option': 'answer_option_1',
                'answer': 'Error',
                'confidence': 0.0
            })
    
    # Calculate statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*70}")
    print(f"📊 PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Total Problems: {len(problems)}")
    print(f"Time Taken: {duration:.1f}s")
    print(f"Average Time: {duration/len(problems):.2f}s per problem")
    
    stats = system.get_statistics()
    if stats:
        print(f"\nConfidence Distribution:")
        print(f"  High (>80%): {stats.get('high_confidence_count', 0)}")
        print(f"  Medium (60-80%): {stats.get('medium_confidence_count', 0)}")
        print(f"  Low (<60%): {stats.get('low_confidence_count', 0)}")
        print(f"  Average: {stats.get('average_confidence', 0):.1%}")
    
    # Write output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['topic', 'problem_statement', 'solution', 'correct_option']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'topic': result['topic'],
                'problem_statement': result['problem_statement'],
                'solution': result['solution'],
                'correct_option': result['correct_option']
            })
    
    print(f"\n✅ Predictions saved to: {output_file}")
    
    # Export detailed reasoning traces
    traces_file = output_file.replace('.csv', '_reasoning_traces.txt')
    system.export_reasoning_traces(traces_file)
    
    # Create summary report
    summary_file = output_file.replace('.csv', '_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("AGENTIC AI REASONING SYSTEM - SUMMARY REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Input File: {input_file}\n")
        f.write(f"Output File: {output_file}\n\n")
        f.write(f"Total Problems: {len(problems)}\n")
        f.write(f"Processing Time: {duration:.1f}s\n")
        f.write(f"Average Time: {duration/len(problems):.2f}s per problem\n\n")
        
        if stats:
            f.write("Confidence Distribution:\n")
            f.write(f"  High (>80%): {stats.get('high_confidence_count', 0)} ({stats.get('high_confidence_count', 0)/len(problems)*100:.1f}%)\n")
            f.write(f"  Medium (60-80%): {stats.get('medium_confidence_count', 0)} ({stats.get('medium_confidence_count', 0)/len(problems)*100:.1f}%)\n")
            f.write(f"  Low (<60%): {stats.get('low_confidence_count', 0)} ({stats.get('low_confidence_count', 0)/len(problems)*100:.1f}%)\n")
            f.write(f"  Average Confidence: {stats.get('average_confidence', 0):.1%}\n\n")
        
        f.write("\nProblem Breakdown by Topic:\n")
        topic_counts = {}
        for result in results:
            topic = result['topic']
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {topic}: {count}\n")
    
    print(f"✅ Summary report saved to: {summary_file}")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process test.csv and generate predictions')
    parser.add_argument('--input', '-i', default='../test.csv', 
                       help='Input test CSV file')
    parser.add_argument('--output', '-o', default='predictions.csv',
                       help='Output predictions CSV file')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress verbose output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        print(f"   Looking in: {os.path.abspath(args.input)}")
        sys.exit(1)
    
    # Process the test file
    process_test_file(args.input, args.output, verbose=not args.quiet)
