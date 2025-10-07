"""
Mistral AI Tool - Intelligent reasoning assistant
Uses Mistral as a tool for understanding, explaining, and suggesting reasoning steps
NOT as the main decision maker
"""

import os
from typing import Dict, List, Optional, Any
import requests
import json


class MistralAPIError(Exception):
    """Raised when Mistral API calls fail"""
    pass


class MistralTool:
    """
    Mistral AI as a reasoning tool
    
    Mistral helps with:
    - Understanding problem statements
    - Suggesting reasoning approaches
    - Explaining patterns
    - Natural language interpretation
    
    But symbolic/computational tools make final decisions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY", "DvJWwEBKjoxbC0ZjR7jfiyTP2XwhDLny")
        self.base_url = "https://api.mistral.ai/v1"
        self.model = "mistral-tiny"  # Fast and efficient for reasoning tasks
        
        if not self.api_key:
            raise MistralAPIError("Mistral API key not provided")
    
    def _call_api(self, messages: List[Dict[str, str]], 
                  max_tokens: int = 500, 
                  temperature: float = 0.0) -> str:
        """Make API call to Mistral"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature  # Zero temperature for deterministic reasoning
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise MistralAPIError(f"API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise MistralAPIError(f"Request failed: {str(e)}")
    
    def understand_problem(self, problem: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Use Mistral to understand the problem structure
        
        Returns:
            Dict with: key_info, constraints, what_to_find
        """
        
        prompt = f"""Analyze this logic problem and extract key information. Be concise and factual.

Problem: {problem}
{f'Topic: {topic}' if topic else ''}

Provide:
1. Key information (numbers, entities, relationships)
2. Constraints (rules, limitations)
3. What needs to be found/proven

Format your response as:
KEY_INFO: [list the important facts]
CONSTRAINTS: [list the constraints]
GOAL: [what needs to be determined]"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=300, temperature=0.0)
            
            # Parse response
            understanding = {
                "key_info": [],
                "constraints": [],
                "goal": ""
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith("KEY_INFO:"):
                    current_section = "key_info"
                    content = line.replace("KEY_INFO:", "").strip()
                    if content:
                        understanding["key_info"].append(content)
                elif line.startswith("CONSTRAINTS:"):
                    current_section = "constraints"
                    content = line.replace("CONSTRAINTS:", "").strip()
                    if content:
                        understanding["constraints"].append(content)
                elif line.startswith("GOAL:"):
                    current_section = "goal"
                    understanding["goal"] = line.replace("GOAL:", "").strip()
                elif line and current_section:
                    if current_section in ["key_info", "constraints"]:
                        understanding[current_section].append(line.lstrip("- •*"))
                    elif current_section == "goal":
                        understanding["goal"] += " " + line
            
            return understanding
            
        except Exception as e:
            # If Mistral fails, return empty understanding
            return {
                "key_info": ["Could not parse with Mistral"],
                "constraints": [],
                "goal": "Solve the problem"
            }
    
    def suggest_approach(self, problem: str, problem_type: str) -> str:
        """
        Suggest a reasoning approach for the problem
        
        Returns:
            String describing suggested approach
        """
        
        prompt = f"""Given this {problem_type} problem, suggest a brief reasoning approach (2-3 steps max).

Problem: {problem}

Provide a concise, step-by-step approach. Focus on WHAT to do, not HOW.
Be specific and actionable."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=200, temperature=0.0)
            return response.strip()
        except:
            return "Analyze the problem systematically step by step"
    
    def explain_pattern(self, sequence: List[float]) -> str:
        """
        Help explain a pattern in a sequence
        
        Returns:
            String explaining the pattern
        """
        
        prompt = f"""Analyze this number sequence and explain the pattern concisely:

Sequence: {sequence}

Provide:
1. The pattern type (arithmetic, geometric, other)
2. The rule in one sentence
3. What the next number should be

Be brief and precise."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=150, temperature=0.0)
            return response.strip()
        except:
            return "Unable to explain pattern"
    
    def interpret_answer_options(self, problem: str, options: List[str]) -> Dict[str, str]:
        """
        Help interpret which answer options are most relevant using chain-of-thought
        
        Returns:
            Dict with detailed analysis and recommended option
        """
        
        prompt = f"""Analyze this problem step-by-step to determine the correct answer.

Problem: {problem}

Options:
{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(options))}

Think through this systematically:

Step 1: What is being asked? (Identify the question)
Step 2: What information is given? (Extract key facts)
Step 3: What reasoning applies? (Method/formula/logic)
Step 4: Work through the solution
Step 5: Which option matches?

Provide your reasoning and conclude with: "Therefore, the answer is [option]" """

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=500, temperature=0.0)
            
            # Extract recommended option from response
            recommended = None
            response_lower = response.lower()
            
            # Look for explicit answer statement
            if "therefore" in response_lower or "answer is" in response_lower:
                for i, opt in enumerate(options, 1):
                    if opt.lower()[:30] in response_lower or f"option {i}" in response_lower:
                        recommended = opt
                        break
            
            return {
                "analysis": response.strip(),
                "recommended": recommended,
                "reasoning_steps": response.split("Step") if "Step" in response else []
            }
        except:
            return {"analysis": "Unable to analyze options", "recommended": None}
    
    def verify_reasoning(self, problem: str, reasoning: str, answer: str) -> Dict[str, Any]:
        """
        Use Mistral to check if reasoning makes sense
        
        Returns:
            Dict with: is_logical, issues, confidence
        """
        
        prompt = f"""Check if this reasoning is logical for the given problem.

Problem: {problem}

Reasoning: {reasoning}

Proposed Answer: {answer}

Respond with:
LOGICAL: [yes/no]
ISSUES: [any logical problems, or "none"]
CONFIDENCE: [low/medium/high]

Be concise."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=150, temperature=0.0)
            
            verification = {
                "is_logical": True,
                "issues": [],
                "confidence": "medium"
            }
            
            response_lower = response.lower()
            
            if "logical: no" in response_lower or "not logical" in response_lower:
                verification["is_logical"] = False
            
            # Extract issues
            if "issues:" in response_lower:
                issues_text = response.split("ISSUES:")[-1].split("CONFIDENCE:")[0]
                if "none" not in issues_text.lower():
                    verification["issues"] = [issues_text.strip()]
            
            # Extract confidence
            if "confidence:" in response_lower:
                conf_text = response.split("CONFIDENCE:")[-1].strip().lower()
                if "high" in conf_text:
                    verification["confidence"] = "high"
                elif "low" in conf_text:
                    verification["confidence"] = "low"
            
            return verification
            
        except:
            return {
                "is_logical": True,
                "issues": [],
                "confidence": "medium"
            }
    
    def enhance_thought(self, action: str, context: str) -> str:
        """
        Generate a reasoning thought for a step
        
        Returns:
            String with reasoning explanation
        """
        
        prompt = f"""Given this reasoning action and context, provide ONE clear sentence explaining the thought process.

Action: {action}
Context: {context}

Provide a single, concise sentence of reasoning."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=100, temperature=0.0)
            return response.strip()
        except:
            return f"Executing: {action}"
    
    def suggest_tool(self, problem: str, step_description: str) -> Optional[str]:
        """
        Suggest which computational tool to use for a step
        
        Returns:
            Tool name suggestion or None
        """
        
        prompt = f"""Given this problem and reasoning step, which computational tool is most appropriate?

Problem: {problem}
Step: {step_description}

Available tools:
- calculator: arithmetic, basic math
- symbolic_solver: equations, algebra, LCM, GCD
- pattern_analyzer: sequences, patterns
- code_executor: computational problems
- logic_reasoner: logical deduction

Respond with ONLY the tool name or "none"."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, max_tokens=30, temperature=0.0)
            tool = response.strip().lower()
            
            valid_tools = ["calculator", "symbolic_solver", "pattern_analyzer", 
                          "code_executor", "logic_reasoner"]
            
            for valid_tool in valid_tools:
                if valid_tool in tool:
                    return valid_tool
            
            return None
        except:
            return None


# Convenience function
def create_mistral_tool(api_key: Optional[str] = None) -> MistralTool:
    """Create a Mistral tool instance"""
    return MistralTool(api_key=api_key)
