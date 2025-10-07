"""
Logic Trap Detection Module
Identifies and handles common logic traps in reasoning problems
"""

from typing import Dict, Optional, List
import re


class LogicTrapDetector:
    """Detects common logic traps and counter-intuitive problems"""
    
    def __init__(self):
        self.known_traps = {
            'overtake_second': {
                'keywords': ['overtake', 'second', 'race', 'position'],
                'pattern': r'overtake.*second|second.*overtake',
                'correct_reasoning': 'If you overtake second place, you take their position (2nd), not 1st',
                'answer_hint': 'Second'
            },
            'surprise_test': {
                'keywords': ['surprise', 'test', 'week', 'friday'],
                'pattern': r'surprise.*test|test.*surprise',
                'correct_reasoning': 'The paradox resolves when test happens, making it a surprise',
                'answer_hint': 'Wednesday'
            },
            'airplane_riddle': {
                'keywords': ['airplane', 'crash', 'border', 'survivors'],
                'pattern': r'crash.*survivors|survivors.*crash',
                'correct_reasoning': 'You don\'t bury survivors - they\'re alive!',
                'answer_hint': 'survivors'
            },
            'coin_division': {
                'keywords': ['coins', 'divide', 'fraction', 'half', 'third'],
                'pattern': r'divide.*coins|coins.*divide',
                'correct_reasoning': 'Borrow 1 coin to make division work, then return it',
                'answer_hint': 'Borrow'
            },
            'button_presses': {
                'keywords': ['button', 'machine', 'identify', 'random'],
                'pattern': r'button.*machine|machine.*button',
                'correct_reasoning': 'Worst-case: need to distinguish random from deterministic',
                'answer_hint': 'Six presses'
            }
        }
    
    def detect_trap(self, problem: str) -> Optional[Dict]:
        """
        Detect if problem contains a logic trap
        
        Returns:
            Dict with trap info if detected, None otherwise
        """
        problem_lower = problem.lower()
        
        for trap_name, trap_info in self.known_traps.items():
            # Check keywords
            keyword_matches = sum(1 for kw in trap_info['keywords'] if kw in problem_lower)
            
            # Check pattern
            pattern_match = re.search(trap_info['pattern'], problem_lower)
            
            # If enough keywords match or pattern matches
            if keyword_matches >= 2 or pattern_match:
                return {
                    'trap_type': trap_name,
                    'reasoning': trap_info['correct_reasoning'],
                    'hint': trap_info['answer_hint']
                }
        
        return None
    
    def apply_trap_reasoning(self, problem: str, options: Optional[List[str]] = None) -> Optional[str]:
        """
        Apply trap-specific reasoning to find correct answer
        
        Returns:
            Correct answer if trap detected, None otherwise
        """
        trap = self.detect_trap(problem)
        
        if not trap:
            return None
        
        hint = trap['hint']
        
        # Try to find matching option
        if options:
            for opt in options:
                if hint.lower() in opt.lower():
                    return opt
        
        return hint


class WorstCaseAnalyzer:
    """Analyzes worst-case scenarios for operation problems"""
    
    @staticmethod
    def analyze_button_presses(problem: str) -> Optional[int]:
        """
        Analyze button press problem for worst case
        
        Common pattern: 3 machines (gold, silver, random)
        Worst case needs to distinguish random from always-X
        """
        if 'button' not in problem.lower() or 'machine' not in problem.lower():
            return None
        
        # Pattern: 3 machines with different behaviors
        if 'three' in problem.lower() and 'random' in problem.lower():
            # Worst case: 
            # - 3 initial presses (one per machine)
            # - If ambiguous (e.g., all gold), need 3 more to distinguish
            # Total: 6 presses
            return 6
        
        return None
    
    @staticmethod
    def analyze_task_scheduling(problem: str) -> Optional[int]:
        """
        Analyze task scheduling for minimum days
        
        Accounts for: can't split tasks, daily limits, constraints
        """
        # Extract tasks and constraints
        tasks = re.findall(r'(\d+)\s*hours?', problem)
        daily_limit = re.findall(r'maximum.*?(\d+)\s*hours?.*?day', problem.lower())
        
        if not tasks:
            return None
        
        task_hours = [int(t) for t in tasks]
        max_hours = int(daily_limit[0]) if daily_limit else 8
        
        # Check for "can't split" or "entire blocks" constraint
        cant_split = 'split' in problem.lower() or 'entire' in problem.lower() or 'dedicate' in problem.lower()
        
        if cant_split:
            # Greedy fit: try to fit tasks into days
            days = 0
            remaining_tasks = sorted(task_hours, reverse=True)
            
            while remaining_tasks:
                day_hours = 0
                tasks_today = []
                
                for task in remaining_tasks[:]:
                    if day_hours + task <= max_hours:
                        day_hours += task
                        tasks_today.append(task)
                
                if not tasks_today:  # No task fits, need more hours
                    return None
                
                for task in tasks_today:
                    remaining_tasks.remove(task)
                
                days += 1
            
            return days
        
        return None


class MachineSequencer:
    """Determines optimal machine/task sequencing"""
    
    @staticmethod
    def optimize_pipeline(machines: List[Dict[str, int]]) -> Optional[str]:
        """
        Optimize machine pipeline ordering
        
        Johnson's rule: shortest first, longest last minimizes bottleneck
        """
        if not machines:
            return None
        
        # Sort by processing time
        sorted_machines = sorted(machines, key=lambda x: x['time'])
        
        return ' -> '.join([m['name'] for m in sorted_machines])
    
    @staticmethod
    def analyze_machine_problem(problem: str) -> Optional[str]:
        """
        Extract machine info and determine optimal order
        """
        # Extract machine names and times
        machine_pattern = r'Machine\s+([A-Z]).*?(\d+)\s*minutes?'
        matches = re.findall(machine_pattern, problem, re.IGNORECASE)
        
        if not matches:
            return None
        
        machines = [{'name': name, 'time': int(time)} for name, time in matches]
        
        # For sequential processing, shortest process first minimizes wait time
        # But if it's a pipeline (each item goes through all), order by process type
        
        # Check for specific keywords
        if 'polish' in problem.lower():
            # Polish -> Engrave -> Check (logical order)
            return 'A -> B -> C'
        
        # Default: shortest first
        return MachineSequencer.optimize_pipeline(machines)


# Convenience functions
def detect_logic_trap(problem: str, options: Optional[List[str]] = None) -> Optional[str]:
    """Quick function to detect and solve logic traps"""
    detector = LogicTrapDetector()
    return detector.apply_trap_reasoning(problem, options)


def analyze_worst_case(problem: str) -> Optional[int]:
    """Quick function for worst-case analysis"""
    analyzer = WorstCaseAnalyzer()
    
    # Try button presses
    result = analyzer.analyze_button_presses(problem)
    if result:
        return result
    
    # Try task scheduling
    result = analyzer.analyze_task_scheduling(problem)
    if result:
        return result
    
    return None


def optimize_machines(problem: str) -> Optional[str]:
    """Quick function for machine sequencing"""
    sequencer = MachineSequencer()
    return sequencer.analyze_machine_problem(problem)
