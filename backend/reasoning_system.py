"""
Main Agentic AI Reasoning System
Orchestrates all agents to solve complex logic problems
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time

from agents.planner import PlannerAgent, ReasoningPlan
from agents.reasoner import ReasonerAgent, ReasoningChain
from agents.verifier import VerifierAgent, VerificationResult


@dataclass
class SolutionResult:
    """Complete solution with reasoning trace"""
    problem: str
    answer: str
    reasoning_chain: ReasoningChain
    verification: VerificationResult
    confidence: float
    execution_time: float
    
    def to_dict(self) -> Dict:
        return {
            'problem': self.problem,
            'answer': self.answer,
            'confidence': self.confidence,
            'execution_time': self.execution_time,
            'reasoning_steps': [step.to_dict() for step in self.reasoning_chain.steps],
            'verification': self.verification.to_dict()
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        summary = "\n" + "=" * 70 + "\n"
        summary += "SOLUTION SUMMARY\n"
        summary += "=" * 70 + "\n\n"
        summary += f"Problem: {self.problem[:100]}...\n\n"
        summary += f"Answer: {self.answer}\n"
        summary += f"Confidence: {self.confidence:.1%}\n"
        summary += f"Execution Time: {self.execution_time:.2f}s\n\n"
        summary += self.reasoning_chain.get_summary()
        summary += "\n" + self.verification.get_verification_report() if hasattr(self.verification, 'get_verification_report') else ""
        return summary


class AgenticReasoningSystem:
    """
    Main system that orchestrates all reasoning agents
    """
    
    def __init__(self, llm_client=None, verbose: bool = True):
        self.planner = PlannerAgent()
        self.reasoner = ReasonerAgent(llm_client)
        self.verifier = VerifierAgent()
        self.verbose = verbose
        
        self.solution_cache: Dict[str, SolutionResult] = {}
    
    def solve(self, problem: str, topic: Optional[str] = None, 
             options: Optional[List[str]] = None) -> SolutionResult:
        """
        Solve a problem using the agentic reasoning system
        
        Args:
            problem: The problem statement
            topic: Optional topic/category hint
            options: Optional list of answer choices
            
        Returns:
            SolutionResult with answer and reasoning trace
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"🧠 SOLVING PROBLEM")
            print(f"{'='*70}")
            print(f"Topic: {topic or 'Unknown'}")
            print(f"Problem: {problem[:100]}...")
            print(f"{'='*70}\n")
        
        # Step 1: Plan
        if self.verbose:
            print("📋 Step 1: Planning...")
        
        plan = self.planner.create_plan(problem, topic)
        
        if self.verbose:
            print(f"   Problem Type: {plan.problem_type.value}")
            print(f"   Strategy: {plan.strategy.value}")
            print(f"   Sub-problems: {len(plan.sub_problems)}")
            print(f"   Tools: {', '.join(plan.required_tools)}")
        
        # Step 2: Execute reasoning
        if self.verbose:
            print("\n🤔 Step 2: Reasoning...")
        
        reasoning_chain = self.reasoner.execute_plan(problem, plan, options)
        
        if self.verbose:
            print(f"   Executed {len(reasoning_chain.steps)} reasoning steps")
            print(f"   Preliminary Answer: {reasoning_chain.final_answer}")
        
        # Step 3: Verify
        if self.verbose:
            print("\n✓ Step 3: Verification...")
        
        verification = self.verifier.verify_chain(reasoning_chain)
        
        if self.verbose:
            print(f"   Valid: {verification.is_valid}")
            print(f"   Verification Confidence: {verification.confidence:.1%}")
            if verification.issues:
                print(f"   Issues: {len(verification.issues)}")
        
        # Step 4: Calculate final confidence
        final_confidence = self.verifier.calculate_confidence_score(
            reasoning_chain, verification
        )
        
        # Step 5: Refine answer if needed
        final_answer = self._refine_answer(
            reasoning_chain.final_answer, 
            options, 
            verification
        )
        
        execution_time = time.time() - start_time
        
        if self.verbose:
            print(f"\n✅ SOLUTION COMPLETE")
            print(f"   Final Answer: {final_answer}")
            print(f"   Confidence: {final_confidence:.1%}")
            print(f"   Time: {execution_time:.2f}s")
            print(f"{'='*70}\n")
        
        result = SolutionResult(
            problem=problem,
            answer=final_answer,
            reasoning_chain=reasoning_chain,
            verification=verification,
            confidence=final_confidence,
            execution_time=execution_time
        )
        
        # Cache result
        self.solution_cache[problem] = result
        
        return result
    
    def _refine_answer(self, preliminary_answer: str, 
                      options: Optional[List[str]],
                      verification: VerificationResult) -> str:
        """Refine the answer based on verification results"""
        
        # Try to match preliminary answer with options (regardless of verification)
        if options:
            # Try exact match first
            for opt in options:
                if preliminary_answer.lower().strip() == opt.lower().strip():
                    return opt
            
            # Try partial match (answer contained in option)
            for opt in options:
                if preliminary_answer.lower() in opt.lower():
                    return opt
            
            # Try partial match (option contained in answer)
            for opt in options:
                if opt.lower() in preliminary_answer.lower():
                    return opt
            
            # If preliminary answer looks valid (not a status string), use it even if not in options
            status_strings = ['processed', 'calculated', 'verified', 'Another answer']
            if preliminary_answer not in status_strings:
                # Try to find closest match
                for opt in options:
                    # Match by any overlapping words
                    opt_words = set(opt.lower().split())
                    answer_words = set(preliminary_answer.lower().split())
                    if opt_words & answer_words:  # If there's any overlap
                        return opt
            
            # Only use "Another answer" if preliminary answer is clearly invalid
            if preliminary_answer in status_strings or not preliminary_answer or preliminary_answer == "Unable to determine answer":
                if "Another answer" in options:
                    return "Another answer"
        
        return preliminary_answer
    
    def solve_batch(self, problems: List[Dict[str, Any]], 
                   max_workers: int = 1) -> List[SolutionResult]:
        """
        Solve multiple problems
        
        Args:
            problems: List of problem dicts with 'problem', 'topic', 'options'
            max_workers: Number of parallel workers (future enhancement)
            
        Returns:
            List of SolutionResults
        """
        results = []
        
        for i, prob_data in enumerate(problems, 1):
            if self.verbose:
                print(f"\n{'='*70}")
                print(f"Problem {i}/{len(problems)}")
                print(f"{'='*70}")
            
            result = self.solve(
                problem=prob_data.get('problem', ''),
                topic=prob_data.get('topic'),
                options=prob_data.get('options')
            )
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about solved problems"""
        if not self.solution_cache:
            return {}
        
        results = list(self.solution_cache.values())
        
        return {
            'total_problems': len(results),
            'average_confidence': sum(r.confidence for r in results) / len(results),
            'average_execution_time': sum(r.execution_time for r in results) / len(results),
            'high_confidence_count': sum(1 for r in results if r.confidence > 0.8),
            'medium_confidence_count': sum(1 for r in results if 0.6 <= r.confidence <= 0.8),
            'low_confidence_count': sum(1 for r in results if r.confidence < 0.6),
        }
    
    def export_reasoning_traces(self, filepath: str):
        """Export all reasoning traces to a file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for problem, result in self.solution_cache.items():
                f.write(result.get_summary())
                f.write("\n\n" + "="*70 + "\n\n")
        
        print(f"✅ Exported reasoning traces to: {filepath}")


def create_reasoning_system(verbose: bool = True) -> AgenticReasoningSystem:
    """Factory function to create a reasoning system"""
    return AgenticReasoningSystem(verbose=verbose)


if __name__ == "__main__":
    # Quick test
    system = create_reasoning_system(verbose=True)
    
    test_problem = "You are in a race and you overtake the second person. What position are you in now?"
    test_options = ["First", "Second", "Third", "Fourth", "Another answer"]
    
    result = system.solve(test_problem, topic="Classic riddles", options=test_options)
    
    print(result.get_summary())
