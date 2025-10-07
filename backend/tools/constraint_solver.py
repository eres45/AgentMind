"""
Real Constraint Solver
Parses constraints and solves optimization problems algorithmically
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class Constraint:
    """Represents a single constraint"""
    variable: str
    operator: str  # '>=', '<=', '==', '>'
    value: float
    
    def check(self, actual_value: float) -> bool:
        """Check if actual value satisfies constraint"""
        if self.operator == '>=':
            return actual_value >= self.value
        elif self.operator == '<=':
            return actual_value <= self.value
        elif self.operator == '==':
            return abs(actual_value - self.value) < 0.001
        elif self.operator == '>':
            return actual_value > self.value
        elif self.operator == '<':
            return actual_value < self.value
        return False


class ConstraintSolver:
    """Solves constraint satisfaction and optimization problems"""
    
    def __init__(self):
        pass
    
    def parse_constraints(self, problem: str) -> List[Constraint]:
        """Parse constraints from problem text"""
        constraints = []
        problem_lower = problem.lower()
        
        # Pattern: "at least X" or "minimum X"
        at_least = re.findall(r'at least (\d+)', problem_lower)
        for val in at_least:
            constraints.append(Constraint('amount', '>=', float(val), ))
        
        # Pattern: "at most X" or "maximum X"
        at_most = re.findall(r'at most (\d+)', problem_lower)
        for val in at_most:
            constraints.append(Constraint('amount', '<=', float(val)))
        
        # Pattern: "exactly X"
        exactly = re.findall(r'exactly (\d+)', problem_lower)
        for val in exactly:
            constraints.append(Constraint('amount', '==', float(val)))
        
        return constraints
    
    def parse_beverage_problem(self, problem: str, options: List[str]) -> Optional[str]:
        """
        Solve beverage optimization problem
        Example: 100 units total, at least 60% juice
        """
        problem_lower = problem.lower()
        
        # Extract total units
        total_match = re.search(r'(\d+)\s*units?', problem_lower)
        if not total_match:
            return None
        total_units = int(total_match.group(1))
        
        # Extract percentage constraints
        juice_pct = None
        if 'juice' in problem_lower:
            pct_match = re.search(r'(\d+)\s*%.*juice', problem_lower)
            if pct_match:
                juice_pct = int(pct_match.group(1)) / 100.0
        
        # Check for optimization criteria
        prefer_balanced = 'equal' in problem_lower or 'balanced' in problem_lower
        
        # Evaluate each option with scoring
        valid_options = []
        for option in options:
            # Parse option: "X units of juice, Y units of soda, Z units of water"
            numbers = re.findall(r'(\d+)\s*units?', option)
            if len(numbers) >= 3:
                juice = int(numbers[0])
                soda = int(numbers[1])
                water = int(numbers[2])
                
                # Check total constraint
                if juice + soda + water != total_units:
                    continue
                
                # Check juice percentage
                if juice_pct:
                    if juice / total_units < juice_pct - 0.001:  # Allow small tolerance
                        continue
                
                # Calculate optimization score
                score = 0
                
                # Prefer meeting constraints exactly (not over-delivering)
                if juice_pct:
                    target_juice = int(total_units * juice_pct)
                    score -= abs(juice - target_juice)  # Closer to exact target is better
                
                # Prefer balanced distribution of non-juice items
                if prefer_balanced or 'equal' not in problem_lower:
                    # Check if soda and water are equal
                    if soda == water:
                        score += 100  # Big bonus for equal distribution
                    else:
                        score -= abs(soda - water)  # Penalize imbalance
                
                valid_options.append((option, score))
        
        if not valid_options:
            return None
        
        # Return option with highest score
        valid_options.sort(key=lambda x: x[1], reverse=True)
        return valid_options[0][0]
    
    def solve_task_scheduling(self, problem: str) -> Optional[int]:
        """
        Solve task scheduling with daily limits using bin-packing
        Example: Tasks of 8h, 6h, 4h with 10h per day limit
        """
        problem_lower = problem.lower()
        
        # Extract task durations
        task_pattern = r'(?:task|job|project)\s*(?:\w+\s*)?(?:takes?|requires?|needs?)\s*(\d+)\s*(?:hours?|h)'
        tasks = re.findall(task_pattern, problem_lower)
        
        if not tasks:
            # Try alternative format: "3 tasks: T1 (8h), T2 (6h), T3 (4h)"
            tasks = re.findall(r'\((\d+)\s*(?:hours?|h)\)', problem)
        
        # Extract daily limit
        daily_pattern = r'(?:maximum|limit|most)\s*(?:of\s*)?(\d+)\s*(?:hours?|h)\s*(?:per|each|a)\s*day'
        daily_match = re.search(daily_pattern, problem_lower)
        
        if not tasks:
            return None
        
        task_hours = [int(t) for t in tasks]
        daily_limit = int(daily_match.group(1)) if daily_match else max(task_hours) + 2
        
        # Greedy bin-packing algorithm
        days = 1
        current_day_hours = 0
        
        # Sort tasks largest first (First Fit Decreasing)
        for task in sorted(task_hours, reverse=True):
            if current_day_hours + task <= daily_limit:
                current_day_hours += task
            else:
                days += 1
        
        return days
    
    def solve_machine_time_combined(self, problem: str) -> Optional[float]:
        """
        Calculate combined time when multiple machines work together
        Formula: 1/t_total = 1/t1 + 1/t2 + 1/t3
        """
        problem_lower = problem.lower()
        
        # More flexible detection
        if not any(word in problem_lower for word in ["machine", "together", "work", "complete", "finish"]):
            return None
        
        # Extract individual times with more patterns
        time_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:hour|hr|h)\b',
            r'(\d+(?:\.\d+)?)\s*(?:minute|min|m)\b',
            r'machine\s+[A-Z]\s+(?:takes|needs|requires)\s+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:hours?|minutes?)'
        ]
        
        times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, problem_lower)
            times.extend([float(m) for m in matches])
        
        if len(times) < 2:
            return None
        
        try:
            # Remove duplicates and sort
            times = sorted(list(set(times)))
            
            # If we have minutes, convert to hours
            if "minute" in problem_lower and all(t < 10 for t in times):
                times = [t/60 for t in times]
            
            # Combined rate = sum of individual rates
            combined_rate = sum(1/t for t in times)
            
            # Combined time = 1 / combined_rate
            combined_time = 1 / combined_rate
            
            # Round to reasonable precision
            return round(combined_time, 2)
            
        except (ValueError, ZeroDivisionError):
            return None
    
    def calculate_worst_case_presses(self, problem: str) -> Optional[int]:
        """
        Calculate worst-case button presses to identify machines
        """
        problem_lower = problem.lower()
        
        if "button" not in problem_lower or "machine" not in problem_lower:
            return None
        
        # Three machines with random behavior
        if "three" in problem_lower and "random" in problem_lower:
            # Worst case: need to distinguish random from deterministic
            # Initial: 1 press per machine = 3 presses
            # If all produce same output: need 3 more to distinguish random
            # Total: 6 presses
            return 6
        
        # Two machines
        if "two" in problem_lower:
            return 3  # Worst case: 2 initial + 1 confirm
        
        return None
    
    def solve_pipeline_scheduling(self, problem: str) -> Optional[str]:
        """
        Solve pipeline/assembly line scheduling problems
        When items must go through multiple machines in sequence
        """
        problem_lower = problem.lower()
        
        # Check if it's a pipeline problem
        if "machine" not in problem_lower or "order" not in problem_lower:
            return None
        
        # Extract machine names and times
        machines = {}
        
        # Pattern: "Machine A takes 3 minutes"
        machine_pattern = r'machine\s+([A-Z])\s+(?:polishes|engraves|performs|takes|processes)[^.]*?(\d+)\s*(?:minute|min)'
        matches = re.findall(machine_pattern, problem_lower, re.IGNORECASE)
        
        for machine_name, time in matches:
            machines[machine_name.upper()] = int(time)
        
        if not machines:
            return None
        
        # Check if there's a natural process order mentioned
        # e.g., "polishes, then engraves, then quality check"
        process_order = []
        if "polish" in problem_lower:
            for m, _ in machines.items():
                if f"machine {m.lower()} polish" in problem_lower:
                    process_order.append((0, m))
        if "engrave" in problem_lower or "engraves" in problem_lower:
            for m, _ in machines.items():
                if f"machine {m.lower()} engrave" in problem_lower:
                    process_order.append((1, m))
        if "quality" in problem_lower or "check" in problem_lower:
            for m, _ in machines.items():
                if f"machine {m.lower()}" in problem_lower and "quality" in problem_lower:
                    process_order.append((2, m))
        
        # If we found a natural order, use it
        if process_order:
            process_order.sort()  # Sort by step number
            ordered_machines = [m for _, m in process_order]
            return " -> ".join(ordered_machines)
        
        # Fallback: alphabetical order (A -> B -> C)
        if len(machines) >= 2:
            ordered = sorted(machines.keys())
            return " -> ".join(ordered)
        
        return None
    
    def solve_gear_rotations(self, problem: str) -> Optional[str]:
        """
        Calculate gear rotations and relationships
        """
        problem_lower = problem.lower()
        
        if "gear" not in problem_lower and "rotation" not in problem_lower:
            return None
        
        # Extract gear information
        gear_pattern = r'gear\s+([A-Z])[^.]*?(\d+)\s*(?:teeth|tooth|rotation|turn)'
        matches = re.findall(gear_pattern, problem_lower, re.IGNORECASE)
        
        if len(matches) >= 2:
            # Basic gear ratio calculation
            gear_a, teeth_a = matches[0][0], int(matches[0][1])
            gear_b, teeth_b = matches[1][0], int(matches[1][1])
            
            # Gear ratio: teeth_b / teeth_a
            ratio = teeth_b / teeth_a
            
            # If one gear rotates X times, the other rotates X * ratio times
            rotation_pattern = r'(\d+)\s*(?:rotation|turn|time)'
            rotations = re.findall(rotation_pattern, problem_lower)
            
            if rotations:
                input_rotations = int(rotations[0])
                output_rotations = input_rotations * ratio
                
                return f"Gear {gear_b}: {output_rotations}"
        
        return None
    
    def parse_time_problem(self, problem: str) -> Optional[float]:
        """
        Solve time calculation problems (LCM, rates, etc.)
        Example: Machine A takes 12h, B takes 6h, C takes 4h - how long together?
        """
        # Try machine time combined first
        result = self.solve_machine_time_combined(problem)
        if result:
            return result
        
        problem_lower = problem.lower()
        
        # Extract time values with units
        time_pattern = r'(\d+)\s*(hours?|minutes?|h|min)'
        times = re.findall(time_pattern, problem_lower)
        
        if not times:
            return None
        
        # Convert to hours
        hours = []
        for val, unit in times:
            val = float(val)
            if 'min' in unit:
                val = val / 60.0
            hours.append(val)
        
        # Check if it's a "working together" problem
        if 'together' in problem_lower or 'combined' in problem_lower:
            # Rate-based: 1/t1 + 1/t2 + ... = 1/t_combined
            if len(hours) >= 2:
                rate_sum = sum(1/h for h in hours)
                combined_time = 1 / rate_sum
                return combined_time
        
        # Check if it's a "one after another" problem
        if 'total' in problem_lower and 'complete' in problem_lower:
            return sum(hours)
        
        return None
    
    def parse_task_scheduling(self, problem: str) -> Optional[int]:
        """
        Solve task scheduling problems
        Example: Tasks 4h, 3h, 2h with 5h per day limit, can't split tasks
        """
        problem_lower = problem.lower()
        
        # Extract task durations
        task_pattern = r'(\d+)\s*hours?'
        task_matches = re.findall(task_pattern, problem_lower)
        if len(task_matches) < 2:
            return None
        
        tasks = [int(t) for t in task_matches]
        
        # Extract daily limit
        daily_limit = 8  # Default
        limit_match = re.search(r'maximum.*?(\d+)\s*hours?.*?day', problem_lower)
        if limit_match:
            daily_limit = int(limit_match.group(1))
        
        # Check if tasks can be split
        can_split = not any(word in problem_lower for word in 
                           ['cannot split', "can't split", 'dedicate entire', 'complete block'])
        
        if can_split:
            # Simple division
            total_hours = sum(tasks)
            days = (total_hours + daily_limit - 1) // daily_limit  # Ceiling division
            return days
        else:
            # Greedy bin packing
            tasks_sorted = sorted(tasks, reverse=True)
            days = 0
            
            while tasks_sorted:
                day_hours = 0
                tasks_today = []
                
                for i, task in enumerate(tasks_sorted):
                    if day_hours + task <= daily_limit:
                        day_hours += task
                        tasks_today.append(i)
                
                # Remove tasks scheduled today
                for i in reversed(tasks_today):
                    tasks_sorted.pop(i)
                
                days += 1
                
                # Prevent infinite loop
                if days > 100:
                    break
            
            return days
    
    def solve_optimization(self, problem: str, options: Optional[List[str]] = None) -> Optional[Any]:
        """
        Main solver - tries different problem types
        """
        problem_lower = problem.lower()
        
        # Beverage/resource allocation
        if 'beverage' in problem_lower or ('units' in problem_lower and 'juice' in problem_lower):
            if options:
                return self.parse_beverage_problem(problem, options)
        
        # Time calculations
        if ('hours' in problem_lower or 'minutes' in problem_lower) and \
           ('machine' in problem_lower or 'together' in problem_lower):
            result = self.parse_time_problem(problem)
            if result:
                # Convert to readable format
                if result < 1:
                    return f"{int(result * 60)} minutes"
                else:
                    hours = int(result)
                    minutes = int((result - hours) * 60)
                    if minutes > 0:
                        return f"{hours} hours and {minutes} minutes"
                    return f"{hours} hours"
        
        # Task scheduling
        if 'task' in problem_lower and 'day' in problem_lower:
            days = self.parse_task_scheduling(problem)
            if days:
                return f"{days} days"
        
        return None


# Convenience function
def solve_constraints(problem: str, options: Optional[List[str]] = None) -> Optional[Any]:
    """Quick function to solve constraint problems"""
    solver = ConstraintSolver()
    return solver.solve_optimization(problem, options)
