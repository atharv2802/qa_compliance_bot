"""
FastAPI application for QA Coach.

Provides REST endpoints for suggestions and event logging.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.coach import suggest, SuggestionResponse
from app.providers.provider_manager import get_provider_manager
from app.evals.judge import evaluate_suggestion, JudgeResponse

# Load environment variables
load_dotenv()

# Database connection
DB_PATH = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")
db_conn = None


def init_db():
    """Initialize DuckDB database and create tables."""
    global db_conn
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    db_conn = duckdb.connect(DB_PATH)
    
    # Create coach_events table
    db_conn.execute("""
        CREATE TABLE IF NOT EXISTS coach_events (
            id VARCHAR PRIMARY KEY,
            ts TIMESTAMP,
            event VARCHAR,
            session_id VARCHAR,
            agent_draft TEXT,
            suggestion_used TEXT,
            policy_refs VARCHAR,
            latency_ms INTEGER,
            ab_test_bucket VARCHAR
        )
    """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    init_db()
    yield
    # Shutdown
    if db_conn:
        db_conn.close()


# Create FastAPI app
app = FastAPI(
    title="QA Coach API",
    description="Conversational QA Coach for Compliance",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class SuggestRequest(BaseModel):
    """Request model for /coach/suggest endpoint."""
    session_id: str = Field(..., description="Session identifier")
    agent_draft: str = Field(..., description="Agent's draft message")
    context: str = Field(default="", description="Conversation context")
    policy_hits: List[str] = Field(default_factory=list, description="Known policy violations")
    brand_tone: str = Field(
        default="professional, clear, empathetic",
        description="Desired brand tone"
    )
    required_disclosures: List[str] = Field(
        default_factory=list,
        description="Required disclosure phrases"
    )


class SuggestResponseModel(BaseModel):
    """Response model for /coach/suggest endpoint."""
    suggestion: str = Field(..., description="Primary compliant suggestion")
    alternates: List[str] = Field(..., description="Alternate suggestions")
    rationale: str = Field(..., description="Explanation of the rewrite")
    policy_refs: List[str] = Field(..., description="Referenced policy IDs")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    evidence_spans: List[List[int]] = Field(..., description="Violation positions in draft")


class CoachEventRequest(BaseModel):
    """Request model for /events/coach endpoint."""
    event: str = Field(..., description="Event type: offered|accepted|edited|rejected|timeout")
    session_id: str = Field(..., description="Session identifier")
    agent_draft: str = Field(..., description="Original agent draft")
    suggestion_used: Optional[str] = Field(None, description="Suggestion that was used")
    policy_refs: List[str] = Field(default_factory=list, description="Policy references")
    latency_ms: int = Field(..., description="Latency in milliseconds")
    ab_test_bucket: str = Field(default="on", description="A/B test bucket: on|off")


class CoachEventResponse(BaseModel):
    """Response model for /events/coach endpoint."""
    ok: bool
    event_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


class EvaluateRequest(BaseModel):
    """Request model for /evals/judge endpoint."""
    agent_draft: str = Field(..., description="Original agent draft")
    suggestion: str = Field(..., description="Coach's suggested rewrite")
    policy_refs: List[str] = Field(default_factory=list, description="Policy references addressed")
    context: str = Field(default="", description="Conversation context")
    required_disclosures: List[str] = Field(default_factory=list, description="Required disclosures")


class EvaluateResponse(BaseModel):
    """Response model for /evals/judge endpoint."""
    overall_score: float = Field(..., description="Overall quality score (0-10)")
    compliance_score: float = Field(..., description="Compliance score (0-10)")
    clarity_score: float = Field(..., description="Clarity score (0-10)")
    tone_score: float = Field(..., description="Tone score (0-10)")
    completeness_score: float = Field(..., description="Completeness score (0-10)")
    feedback: str = Field(..., description="Evaluation feedback")
    strengths: List[str] = Field(..., description="Identified strengths")
    weaknesses: List[str] = Field(..., description="Identified weaknesses")
    pass_threshold: bool = Field(..., description="Whether suggestion passes threshold (≥7.0)")


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "QA Coach API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "coach": "/coach/suggest",
            "events": "/events/coach",
            "evaluate": "/evals/judge",
            "providers": "/providers/status"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/providers/status")
async def get_providers_status():
    """
    Get status of all configured LLM providers.
    
    Returns information about primary provider, fallbacks, and their availability.
    """
    try:
        manager = get_provider_manager()
        return manager.get_provider_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting provider status: {str(e)}")


@app.post("/coach/suggest", response_model=SuggestResponseModel)
async def coach_suggest(request: SuggestRequest):
    """
    Generate a compliant suggestion for an agent draft.
    
    This endpoint analyzes the agent's draft against compliance policies
    and returns a rewritten version that addresses any violations.
    """
    try:
        # Call coach suggest function
        response: SuggestionResponse = suggest(
            agent_draft=request.agent_draft,
            context=request.context,
            policy_hits=request.policy_hits if request.policy_hits else None,
            brand_tone=request.brand_tone,
            required_disclosures=request.required_disclosures if request.required_disclosures else None
        )
        
        # Convert to response model
        return SuggestResponseModel(
            suggestion=response.suggestion,
            alternates=response.alternates,
            rationale=response.rationale,
            policy_refs=response.policy_refs,
            confidence=response.confidence,
            evidence_spans=[list(span) for span in response.evidence_spans]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestion: {str(e)}")


@app.post("/events/coach", response_model=CoachEventResponse)
async def log_coach_event(event: CoachEventRequest):
    """
    Log a coaching event for analytics and A/B testing.
    
    Events track how suggestions are used:
    - offered: Suggestion was shown to agent
    - accepted: Agent used the suggestion as-is
    - edited: Agent modified the suggestion before using
    - rejected: Agent ignored the suggestion
    - timeout: Agent didn't respond in time
    """
    try:
        event_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Convert policy_refs list to JSON string
        import json
        policy_refs_json = json.dumps(event.policy_refs)
        
        # Insert into database
        db_conn.execute("""
            INSERT INTO coach_events (
                id, ts, event, session_id, agent_draft,
                suggestion_used, policy_refs, latency_ms, ab_test_bucket
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            event_id,
            timestamp,
            event.event,
            event.session_id,
            event.agent_draft,
            event.suggestion_used,
            policy_refs_json,
            event.latency_ms,
            event.ab_test_bucket
        ])
        
        return CoachEventResponse(ok=True, event_id=event_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging event: {str(e)}")


@app.get("/events/stats")
async def get_event_stats():
    """
    Get basic statistics about logged events.
    
    Returns event counts by type and recent activity.
    """
    try:
        # Count by event type
        event_counts = db_conn.execute("""
            SELECT event, COUNT(*) as count
            FROM coach_events
            GROUP BY event
            ORDER BY count DESC
        """).fetchall()
        
        # Total events
        total = db_conn.execute("SELECT COUNT(*) FROM coach_events").fetchone()[0]
        
        # Recent events
        recent = db_conn.execute("""
            SELECT event, session_id, ts
            FROM coach_events
            ORDER BY ts DESC
            LIMIT 10
        """).fetchall()
        
        return {
            "total_events": total,
            "event_counts": {row[0]: row[1] for row in event_counts},
            "recent_events": [
                {"event": row[0], "session_id": row[1], "timestamp": str(row[2])}
                for row in recent
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.get("/analytics/latency")
async def get_latency_stats():
    """
    Get latency statistics for coach suggestions.
    
    Returns average, min, max, and percentile latencies.
    """
    try:
        stats = db_conn.execute("""
            SELECT 
                AVG(latency_ms) as avg_latency,
                MIN(latency_ms) as min_latency,
                MAX(latency_ms) as max_latency,
                COUNT(*) as total_requests
            FROM coach_events 
            WHERE latency_ms > 0
        """).fetchone()
        
        # Get percentiles (p50, p90, p95, p99)
        percentiles = db_conn.execute("""
            SELECT 
                latency_ms,
                PERCENT_RANK() OVER (ORDER BY latency_ms) as percentile
            FROM coach_events
            WHERE latency_ms > 0
            ORDER BY latency_ms
        """).fetchall()
        
        p50 = p90 = p95 = p99 = None
        if percentiles:
            for lat, pct in percentiles:
                if p50 is None and pct >= 0.50:
                    p50 = lat
                if p90 is None and pct >= 0.90:
                    p90 = lat
                if p95 is None and pct >= 0.95:
                    p95 = lat
                if p99 is None and pct >= 0.99:
                    p99 = lat
        
        return {
            "avg_latency_ms": int(stats[0]) if stats[0] else 0,
            "min_latency_ms": int(stats[1]) if stats[1] else 0,
            "max_latency_ms": int(stats[2]) if stats[2] else 0,
            "total_requests": stats[3],
            "percentiles": {
                "p50": int(p50) if p50 else 0,
                "p90": int(p90) if p90 else 0,
                "p95": int(p95) if p95 else 0,
                "p99": int(p99) if p99 else 0
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latency stats: {str(e)}")


@app.get("/analytics/policies")
async def get_policy_violations():
    """
    Get policy violation statistics.
    
    Returns count of violations per policy across all events.
    """
    try:
        # Get all policy references
        policies_data = db_conn.execute("""
            SELECT policy_refs 
            FROM coach_events 
            WHERE policy_refs IS NOT NULL AND policy_refs != ''
        """).fetchall()
        
        policy_counts = {}
        for row in policies_data:
            try:
                # Parse JSON array of policy references
                import json
                policies = json.loads(row[0]) if row[0] else []
                for policy in policies:
                    if policy:  # Skip empty strings
                        policy_counts[policy] = policy_counts.get(policy, 0) + 1
            except (json.JSONDecodeError, TypeError):
                # If not JSON, try splitting by comma (fallback)
                policies = str(row[0]).split(',')
                for policy in policies:
                    policy = policy.strip()
                    if policy:
                        policy_counts[policy] = policy_counts.get(policy, 0) + 1
        
        # Sort by count descending
        sorted_policies = dict(sorted(policy_counts.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "policy_violations": sorted_policies,
            "total_policies": len(sorted_policies),
            "total_violations": sum(sorted_policies.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policy stats: {str(e)}")


@app.post("/evals/judge", response_model=EvaluateResponse)
async def evaluate_with_judge(request: EvaluateRequest):
    """
    Evaluate a suggestion using LLM-as-a-judge.
    
    Uses a separate judge model to assess the quality of a suggestion
    across multiple criteria: compliance, clarity, tone, and completeness.
    
    The judge model is configured independently (JUDGE_PROVIDER, JUDGE_MODEL)
    and should ideally be different/stronger than the primary model.
    """
    try:
        # Evaluate the suggestion
        result: JudgeResponse = evaluate_suggestion(
            agent_draft=request.agent_draft,
            suggestion=request.suggestion,
            policy_refs=request.policy_refs,
            context=request.context,
            required_disclosures=request.required_disclosures if request.required_disclosures else None
        )
        
        # Convert to response model
        return EvaluateResponse(
            overall_score=result.overall_score,
            compliance_score=result.compliance_score,
            clarity_score=result.clarity_score,
            tone_score=result.tone_score,
            completeness_score=result.completeness_score,
            feedback=result.feedback,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            pass_threshold=result.pass_threshold
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating suggestion: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
