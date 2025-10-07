"""
Problem Parser - Extracts structured information from problem statements
Improves accuracy by better understanding problem structure
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedProblem:
    """Structured representation of a problem"""
    problem_type: str
    key_numbers: List[float]
    dimensions: Optional[Tuple[int, ...]] = None
    constraints: List[str] = None
    question_type: str = ""
    entities: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.entities is None:
            self.entities = []


class ProblemParser:
    """Intelligently parses problem statements"""
    
    def __init__(self):
        self.patterns = self._init_patterns()
    
    def _init_patterns(self):
        return {
            'cube_dimensions': r'(\d+)x(\d+)x(\d+)\s*cube',
            'grid_dimensions': r'(\d+)\s*x\s*(\d+)(?:\s*x\s*(\d+))?',
            'painted_faces': r'exactly\s+(\w+)\s+(?:painted\s+)?(?:face|side)',
            'time_units': r'(\d+)\s*(hour|minute|day|second|week)',
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'ratio': r'(\d+):(\d+)',
            'sequence_pattern': r'sequence.*?:\s*([\d\s,]+)',
            'optimization': r'(?:maximum|minimum|optimal|best|worst)',
            'logic_trap_keywords': r'(?:overtake|position|race|surprise|paradox)',
        }
    
    def parse(self, problem: str) -> ParsedProblem:
        """Parse problem into structured format"""
        problem_lower = problem.lower()
        
        # Detect cube dimensions (e.g., "4x4x4 cube" or "10x10x10 cube")
        cube_match = re.search(self.patterns['cube_dimensions'], problem_lower)
        if cube_match:
            dims = tuple(int(d) for d in cube_match.groups())
            return ParsedProblem(
                problem_type='spatial_cube',
                key_numbers=[dims[0]],  # Use first dimension as cube size
                dimensions=dims,
                question_type='painted_cube' if 'paint' in problem_lower else 'cube_geometry'
            )
        
        # Detect grid/matrix dimensions
        grid_match = re.search(self.patterns['grid_dimensions'], problem)
        if grid_match and ('grid' in problem_lower or 'matrix' in problem_lower or 'table' in problem_lower):
            dims = tuple(int(d) for d in grid_match.groups() if d)
            return ParsedProblem(
                problem_type='spatial_grid',
                key_numbers=list(dims),
                dimensions=dims
            )
        
        # Detect sequences
        seq_match = re.search(self.patterns['sequence_pattern'], problem)
        if seq_match or 'sequence' in problem_lower:
            numbers = re.findall(r'-?\d+\.?\d*', problem)
            numbers = [float(n) for n in numbers]
            return ParsedProblem(
                problem_type='sequence',
                key_numbers=numbers,
                question_type='find_next' if '?' in problem else 'find_pattern'
            )
        
        # Detect optimization problems
        if re.search(self.patterns['optimization'], problem_lower):
            return ParsedProblem(
                problem_type='optimization',
                key_numbers=self._extract_all_numbers(problem),
                constraints=self._extract_constraints(problem)
            )
        
        # Detect logic traps
        if re.search(self.patterns['logic_trap_keywords'], problem_lower):
            return ParsedProblem(
                problem_type='logic_trap',
                key_numbers=self._extract_all_numbers(problem),
                question_type='counter_intuitive'
            )
        
        # Detect time/rate problems
        time_matches = re.findall(self.patterns['time_units'], problem_lower)
        if time_matches:
            return ParsedProblem(
                problem_type='time_calculation',
                key_numbers=[float(t[0]) for t in time_matches],
                constraints=[t[1] for t in time_matches]
            )
        
        # Default: extract all numbers
        return ParsedProblem(
            problem_type='general',
            key_numbers=self._extract_all_numbers(problem)
        )
    
    def _extract_all_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) for n in numbers if n]
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraint phrases"""
        constraints = []
        
        # Time constraints
        if 'at least' in text.lower():
            match = re.search(r'at least (\d+)', text.lower())
            if match:
                constraints.append(f"minimum:{match.group(1)}")
        
        if 'at most' in text.lower():
            match = re.search(r'at most (\d+)', text.lower())
            if match:
                constraints.append(f"maximum:{match.group(1)}")
        
        # Percentage constraints
        pct_matches = re.findall(r'(\d+)%', text)
        for pct in pct_matches:
            constraints.append(f"percentage:{pct}")
        
        # Equality constraints
        if 'equal' in text.lower() or 'same' in text.lower():
            constraints.append("equality:true")
        
        return constraints
    
    def detect_pattern_type(self, text: str) -> Optional[str]:
        """Detect special pattern types (months, days, etc.)"""
        text_upper = text.upper()
        
        # Month initials: JFMAMJJASON_D or JFMAMJJASOND
        months = "JFMAMJJASOND"
        if months in text_upper or "JFMAMJJASON" in text_upper:
            return "months"
        
        # Days of week: MTWTFSS or variations
        if "MTWTFSS" in text_upper or "SMTWTFS" in text_upper:
            return "days_of_week"
        
        # Check for month names in sequence
        month_names = ["january", "february", "march", "april", "may", "june",
                      "july", "august", "september", "october", "november", "december"]
        text_lower = text.lower()
        month_count = sum(1 for month in month_names if month in text_lower)
        if month_count >= 3:
            return "month_names"
        
        return None
    
    def find_missing_in_sequence(self, text: str) -> Optional[str]:
        """Find missing letter/element in common sequences"""
        pattern_type = self.detect_pattern_type(text)
        
        if pattern_type == "months":
            # Extract the sequence  
            match = re.search(r"['\"](.*?)['\"]", text)
            if match:
                sequence = match.group(1).upper()
                months = "JFMAMJJASOND"
                
                # Handle underscore - it represents the blank to fill
                if '_' in sequence:
                    # Check which month letter appears fewer times in sequence than in months
                    # JFMAMJJASON_D has all letters except one occurrence is missing
                    seq_without_underscore = sequence.replace('_', '')
                    for month_char in months:
                        count_in_months = months.count(month_char)
                        count_in_seq = seq_without_underscore.count(month_char)
                        if count_in_seq < count_in_months:
                            return month_char
                    
                    # Fallback: return the character at underscore position
                    pos = sequence.index('_')
                    if pos < len(months):
                        return months[pos]
                
                # Find first mismatch
                for i, char in enumerate(months):
                    if i < len(sequence):
                        if sequence[i] != char and sequence[i] != '_':
                            return char
                    else:
                        # Beyond sequence length
                        return char
        
        elif pattern_type == "days_of_week":
            days = "SMTWTFS"  # Sunday to Saturday
            match = re.search(r"['\"](.*?)['\"]", text)
            if match:
                sequence = match.group(1).upper()
                if '_' in sequence:
                    pos = sequence.index('_')
                    return days[pos]
        
        return None
    
    def detect_counter_intuitive_logic(self, text: str) -> Optional[Dict]:
        """Detect counter-intuitive logic problems and provide reasoning hints"""
        text_lower = text.lower()
        
        # Overtake second place
        if "overtake" in text_lower and "second" in text_lower and "position" in text_lower:
            return {
                "type": "counter_intuitive",
                "hint": "When you overtake the person in second place, you take their position (2nd), not 1st",
                "reasoning": "You are now ahead of them but behind the person in 1st"
            }
        
        # Surprise test paradox
        if "surprise" in text_lower and "test" in text_lower:
            return {
                "type": "paradox",
                "hint": "The surprise test paradox resolves when the test actually happens",
                "reasoning": "Any day can be a surprise if the reasoning is circular"
            }
        
        # Survivors (you don't bury survivors)
        if "bury" in text_lower and "survivor" in text_lower:
            return {
                "type": "trick_question",
                "hint": "You don't bury survivors - they're alive",
                "reasoning": "The question contains a logical impossibility"
            }
        
        return None
    
    def extract_cube_size(self, problem: str) -> Optional[int]:
        """Extract cube size from problem, handling formats like '4x4x4' or '10x10x10'"""
        # First try the explicit pattern
        match = re.search(r'(\d+)x(\d+)x(\d+)\s*cube', problem.lower())
        if match:
            sizes = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
            if len(set(sizes)) == 1:  # All same size
                return sizes[0]
        
        # Try "NxNxN" format anywhere
        match = re.search(r'(\d+)x\1x\1', problem)
        if match:
            return int(match.group(1))
        
        # Look for "27 smaller cubes" (3x3x3), "64 smaller cubes" (4x4x4), etc.
        if '27' in problem and 'smaller' in problem.lower():
            return 3
        if '64' in problem and 'smaller' in problem.lower():
            return 4
        if '125' in problem and 'smaller' in problem.lower():
            return 5
        if '1000' in problem and 'smaller' in problem.lower() or '1x1x1' in problem and '10x10x10' in problem:
            return 10
        
        return None
    
    def extract_painted_faces_query(self, problem: str) -> Optional[int]:
        """Extract how many faces should be painted (0, 1, 2, or 3)"""
        problem_lower = problem.lower()
        
        # Explicit numbers
        if 'exactly two' in problem_lower or '2 painted' in problem_lower or '2 red' in problem_lower:
            return 2
        if 'exactly one' in problem_lower or '1 painted' in problem_lower or '1 red' in problem_lower:
            return 1
        if 'exactly three' in problem_lower or '3 painted' in problem_lower or '3 red' in problem_lower or 'corner' in problem_lower:
            return 3
        if 'zero' in problem_lower or '0 painted' in problem_lower or 'no paint' in problem_lower or 'internal' in problem_lower:
            return 0
        
        # Word forms
        if 'two' in problem_lower and ('face' in problem_lower or 'side' in problem_lower):
            return 2
        if 'one' in problem_lower and ('face' in problem_lower or 'side' in problem_lower):
            return 1
        if 'three' in problem_lower and ('face' in problem_lower or 'side' in problem_lower):
            return 3
        
        return None


# Convenience function
def parse_problem(problem: str) -> ParsedProblem:
    """Quick function to parse a problem"""
    parser = ProblemParser()
    return parser.parse(problem)
