"""
FastAPI REST API for Agentic Reasoning System
Provides HTTP endpoints for problem solving
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn

from reasoning_system import create_reasoning_system, SolutionResult

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Reasoning System API",
    description="Multi-agent system for systematic logical reasoning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize reasoning system
reasoning_system = create_reasoning_system(verbose=False)


# Request/Response Models
class SolveRequest(BaseModel):
    problem: str = Field(..., description="The problem statement to solve")
    topic: Optional[str] = Field(None, description="Problem topic/category")
    options: Optional[List[str]] = Field(None, description="Answer options")


class ReasoningStepResponse(BaseModel):
    step_number: int
    action: str
    thought: str
    tool_used: Optional[str] = None
    tool_output: Optional[str] = None
    result: Optional[str] = None
    verified: bool
    confidence: float


class SolveResponse(BaseModel):
    problem: str
    answer: str
    confidence: float
    execution_time: float
    reasoning_steps: List[Dict[str, Any]]
    verification: Dict[str, Any]


class BatchSolveRequest(BaseModel):
    problems: List[SolveRequest]


class StatisticsResponse(BaseModel):
    total_problems: int
    average_confidence: float
    average_execution_time: float
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int


# API Endpoints
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Agentic AI Reasoning System API",
        "version": "1.0.0",
        "endpoints": {
            "solve": "/api/solve",
            "batch": "/api/solve/batch",
            "stats": "/api/statistics",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "operational",
        "agents": {
            "planner": "ready",
            "reasoner": "ready",
            "verifier": "ready"
        }
    }


@app.post("/api/solve", response_model=SolveResponse)
def solve_problem(request: SolveRequest):
    """
    Solve a single problem
    
    Example request:
    ```json
    {
        "problem": "You overtake second place. What position are you in?",
        "topic": "Logic",
        "options": ["First", "Second", "Third", "Fourth"]
    }
    ```
    """
    try:
        result = reasoning_system.solve(
            problem=request.problem,
            topic=request.topic,
            options=request.options
        )
        
        return SolveResponse(
            problem=result.problem,
            answer=result.answer,
            confidence=result.confidence,
            execution_time=result.execution_time,
            reasoning_steps=[step.to_dict() for step in result.reasoning_chain.steps],
            verification=result.verification.to_dict()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error solving problem: {str(e)}")


@app.post("/api/solve/batch")
def solve_batch(request: BatchSolveRequest):
    """
    Solve multiple problems in batch
    
    Returns list of solutions
    """
    try:
        problems = [
            {
                'problem': prob.problem,
                'topic': prob.topic,
                'options': prob.options
            }
            for prob in request.problems
        ]
        
        results = reasoning_system.solve_batch(problems)
        
        return {
            "total": len(results),
            "results": [
                {
                    "problem": r.problem[:100] + "..." if len(r.problem) > 100 else r.problem,
                    "answer": r.answer,
                    "confidence": r.confidence,
                    "execution_time": r.execution_time
                }
                for r in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch processing: {str(e)}")


@app.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics():
    """Get system statistics"""
    try:
        stats = reasoning_system.get_statistics()
        
        if not stats:
            return {
                "total_problems": 0,
                "average_confidence": 0.0,
                "average_execution_time": 0.0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0
            }
        
        return StatisticsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@app.get("/api/problem-types")
def get_problem_types():
    """Get list of supported problem types"""
    return {
        "problem_types": [
            "Spatial reasoning",
            "Mathematical",
            "Logical",
            "Sequence solving",
            "Optimization",
            "Lateral thinking",
            "Classic riddles"
        ],
        "strategies": [
            "Direct calculation",
            "Step-by-step logic",
            "Pattern recognition",
            "Constraint satisfaction",
            "Spatial visualization",
            "Creative thinking"
        ]
    }


@app.get("/api/tools")
def get_available_tools():
    """Get list of available reasoning tools"""
    return {
        "tools": [
            {
                "name": "calculator",
                "description": "Basic arithmetic and mathematical operations"
            },
            {
                "name": "symbolic_solver",
                "description": "Algebraic equation solving and symbolic mathematics"
            },
            {
                "name": "pattern_analyzer",
                "description": "Sequence and pattern recognition"
            },
            {
                "name": "code_executor",
                "description": "Safe Python code execution"
            },
            {
                "name": "logic_reasoner",
                "description": "Logical deduction and consistency checking"
            }
        ]
    }


@app.delete("/api/cache")
def clear_cache():
    """Clear solution cache"""
    reasoning_system.solution_cache.clear()
    return {"message": "Cache cleared successfully"}


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Starting Agentic AI Reasoning System API Server")
    print("="*70)
    print(f"\nServer will be available at: http://localhost:8000")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"OpenAPI Schema: http://localhost:8000/openapi.json")
    print("\n" + "="*70 + "\n")
    
    start_server()
