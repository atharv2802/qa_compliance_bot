# LLM-as-a-Judge Evaluation Guide

## Overview

The QA Coach includes a sophisticated **LLM-as-a-Judge** evaluation system that uses a separate model to assess the quality of suggestions. This provides objective quality metrics and helps identify areas for improvement.

## Architecture

```
┌─────────────────┐
│  Agent Draft    │
│  (risky text)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Coach System   │  ← Primary LLM (e.g., Groq Llama 3.1)
│  (rewrite)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Suggestion     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Judge System   │  ← Separate LLM (e.g., GPT-4o-mini)
│  (evaluate)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Quality Scores │
│  + Feedback     │
└─────────────────┘
```

## Why Use a Separate Judge Model?

1. **Objectivity**: Independent evaluation reduces bias
2. **Quality Assurance**: Catches issues the primary model might miss
3. **Model Comparison**: Test different coach models against the same judge
4. **Continuous Improvement**: Track quality metrics over time
5. **Stronger Evaluation**: Use a more capable model (e.g., GPT-4) to judge a faster model (e.g., Groq)

## Configuration

### Environment Variables

```bash
# Judge Configuration
JUDGE_PROVIDER=openai              # Provider: openai, anthropic, or groq
JUDGE_MODEL=gpt-4o-mini           # Model to use for evaluation

# Primary Coach Configuration (for comparison)
LLM_PROVIDER=groq                  # Fast inference
LLM_MODEL=llama-3.1-8b-instant    # Lower cost
```

### Recommended Configurations

#### Production: GPT-4o-mini Judge + Groq Coach
```bash
JUDGE_PROVIDER=openai
JUDGE_MODEL=gpt-4o-mini
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
```
**Why**: Strong evaluation quality + ultra-fast coaching

#### Premium: Claude Judge + GPT-4o-mini Coach
```bash
JUDGE_PROVIDER=anthropic
JUDGE_MODEL=claude-3-haiku-20240307
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```
**Why**: High-quality evaluation + reliable coaching

#### Development: GPT-4o-mini for Both
```bash
JUDGE_PROVIDER=openai
JUDGE_MODEL=gpt-4o-mini
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```
**Why**: Consistent evaluation during development

## Evaluation Criteria

The judge evaluates suggestions across **5 dimensions** on a 0-10 scale:

### 1. Compliance Score (0-10)
- **What**: Does the suggestion address all policy violations?
- **Good**: All flagged policies are fixed, required disclosures included
- **Bad**: Policy violations remain, missing disclosures

### 2. Clarity Score (0-10)
- **What**: Is the suggestion clear and easy to understand?
- **Good**: Well-structured, concise, professional language
- **Bad**: Confusing, verbose, jargon-heavy

### 3. Tone Score (0-10)
- **What**: Does it maintain appropriate brand tone?
- **Good**: Professional, empathetic, helpful
- **Bad**: Robotic, aggressive, overly casual

### 4. Completeness Score (0-10)
- **What**: Does it preserve the original intent?
- **Good**: Addresses customer needs while fixing compliance
- **Bad**: Loses important information, changes meaning

### 5. Overall Score (0-10)
- **What**: Holistic quality assessment
- **Threshold**: ≥7.0 is considered "passing"

## Response Format

```json
{
  "overall_score": 8.5,
  "compliance_score": 9.0,
  "clarity_score": 8.0,
  "tone_score": 8.5,
  "completeness_score": 8.5,
  "feedback": "Excellent rewrite that addresses all compliance concerns",
  "strengths": [
    "Clearly addresses policy violations",
    "Maintains professional tone",
    "Includes required disclosures"
  ],
  "weaknesses": [
    "Could be slightly more concise"
  ],
  "pass_threshold": true
}
```

## Usage

### 1. REST API Endpoint

```bash
POST /evals/judge
Content-Type: application/json

{
  "agent_draft": "We guarantee 12% returns every year!",
  "suggestion": "Historical performance has varied, and past results don't guarantee future returns.",
  "policy_refs": ["ADV-6.2"],
  "context": "Customer asking about investment returns",
  "required_disclosures": []
}
```

**Response:**
```json
{
  "overall_score": 8.5,
  "compliance_score": 9.0,
  "clarity_score": 8.5,
  "tone_score": 8.0,
  "completeness_score": 8.5,
  "feedback": "Strong compliance rewrite",
  "strengths": ["Clear policy fix", "Professional tone"],
  "weaknesses": ["Could mention specific disclaimers"],
  "pass_threshold": true
}
```

### 2. Python API

```python
from app.evals.judge import evaluate_suggestion

result = evaluate_suggestion(
    agent_draft="We guarantee 12% returns every year!",
    suggestion="Historical performance has varied...",
    policy_refs=["ADV-6.2"],
    context="Customer inquiry",
    required_disclosures=[]
)

print(f"Score: {result.overall_score}/10")
print(f"Pass: {result.pass_threshold}")
print(f"Feedback: {result.feedback}")
```

### 3. Batch Evaluation Script

Evaluate multiple suggestions at once:

```bash
# Use sample test cases
python scripts/run_evals.py

# Evaluate from database
python scripts/run_evals.py --db --limit 100

# Results saved to: ./data/eval_results_TIMESTAMP.json
```

**Output:**
```
Running evaluations on 50 test cases...
Judge: openai/gpt-4o-mini

[1/50] Evaluating... ✅ PASS (score: 8.5, 450ms)
[2/50] Evaluating... ✅ PASS (score: 9.0, 420ms)
[3/50] Evaluating... ❌ FAIL (score: 6.5, 480ms)
...

Evaluation Summary:
Total Cases:      50
Successful Evals: 50
Pass Rate:        88.0%

Average Scores (0-10 scale):
  Overall:        8.12
  Compliance:     8.45
  Clarity:        7.89
  Tone:           8.23
  Completeness:   8.01
```

## Integration Patterns

### 1. Real-Time Quality Check
Evaluate suggestions before showing them to agents:
```python
from app.coach import suggest
from app.evals.judge import evaluate_suggestion

# Generate suggestion
response = suggest(agent_draft, context)

# Evaluate quality
eval_result = evaluate_suggestion(
    agent_draft=agent_draft,
    suggestion=response.suggestion,
    policy_refs=response.policy_refs
)

# Only show if passes threshold
if eval_result.pass_threshold:
    return response
else:
    # Retry or flag for review
    return regenerate_suggestion()
```

### 2. A/B Testing Comparison
Compare different coach configurations:
```python
# Test Configuration A
os.environ["LLM_PROVIDER"] = "groq"
response_a = suggest(agent_draft, context)
eval_a = evaluate_suggestion(agent_draft, response_a.suggestion, [])

# Test Configuration B
os.environ["LLM_PROVIDER"] = "openai"
response_b = suggest(agent_draft, context)
eval_b = evaluate_suggestion(agent_draft, response_b.suggestion, [])

# Compare
print(f"Groq Score: {eval_a.overall_score}")
print(f"OpenAI Score: {eval_b.overall_score}")
```

### 3. Continuous Monitoring
Track quality metrics over time:
```python
# After each coaching session
eval_result = evaluate_suggestion(...)

# Log to DuckDB
db.execute("""
    INSERT INTO eval_logs (ts, score, pass, feedback)
    VALUES (?, ?, ?, ?)
""", [datetime.now(), eval_result.overall_score, 
      eval_result.pass_threshold, eval_result.feedback])

# Generate weekly reports
avg_score = db.execute("""
    SELECT AVG(score) 
    FROM eval_logs 
    WHERE ts >= NOW() - INTERVAL '7 days'
""").fetchone()[0]
```

## Interpreting Results

### Score Ranges

| Score | Interpretation | Action |
|-------|---------------|---------|
| 9-10  | Excellent | Production-ready, use as examples |
| 7-8.9 | Good | Minor tweaks, generally acceptable |
| 5-6.9 | Fair | Needs improvement, may use with caution |
| 0-4.9 | Poor | Requires significant rework |

### Common Issues

#### Low Compliance Score
**Symptoms**: Policy violations remain
**Fix**: 
- Update policy detection rules
- Improve coach prompt with policy examples
- Add required disclosure templates

#### Low Clarity Score
**Symptoms**: Confusing suggestions
**Fix**:
- Simplify coach prompt
- Add clarity guidelines to system prompt
- Use more structured output format

#### Low Tone Score
**Symptoms**: Robotic or inappropriate tone
**Fix**:
- Update brand tone specifications
- Add tone examples to coach prompt
- Test different temperature settings

#### Low Completeness Score
**Symptoms**: Loses original intent
**Fix**:
- Preserve more context from original
- Use longer max_tokens
- Add instruction to maintain core message

## Testing

Run the evaluation test suite:
```bash
pytest tests/test_judge.py -v
```

**Tests include:**
- Judge initialization with different providers
- Response parsing (JSON and markdown-wrapped)
- Score calculations and threshold logic
- Malformed response handling
- Prompt construction with all parameters

## Performance Considerations

### Latency
- **Judge calls add latency**: 300-600ms additional per evaluation
- **Solution**: Run evaluations asynchronously or in batch mode
- **Production**: Evaluate a sample (e.g., 10%) in real-time, rest in batch

### Cost
- **Judge calls have costs**: Similar to primary model costs
- **Optimization**: 
  - Use cheaper judge models (e.g., Haiku, GPT-4o-mini)
  - Sample evaluations (not every suggestion)
  - Batch process historical data

### Recommended Sampling Rates
- **Development**: 100% (evaluate everything)
- **Staging**: 50% (good coverage, lower cost)
- **Production**: 10-20% (spot checks, monitoring)

## Advanced Usage

### Custom Scoring Criteria
Modify `app/evals/judge.py` to add custom criteria:
```python
def _build_judge_prompt(self, ...):
    # Add custom criterion
    prompt += """
    6. **Customer Satisfaction (0-10):** 
       Will this response satisfy the customer?
    """
```

### Multi-Judge Ensemble
Use multiple judges for higher confidence:
```python
judges = [
    Judge(provider="openai", model="gpt-4o-mini"),
    Judge(provider="anthropic", model="claude-3-haiku-20240307"),
    Judge(provider="groq", model="llama-3.1-8b-instant")
]

scores = [judge.evaluate(...).overall_score for judge in judges]
consensus_score = sum(scores) / len(scores)
```

### Weighted Scoring
Weight criteria differently based on your needs:
```python
weights = {
    "compliance": 0.40,  # Most important
    "clarity": 0.20,
    "tone": 0.15,
    "completeness": 0.25
}

weighted_score = (
    result.compliance_score * weights["compliance"] +
    result.clarity_score * weights["clarity"] +
    result.tone_score * weights["tone"] +
    result.completeness_score * weights["completeness"]
)
```

## Troubleshooting

### Judge Returns Low Scores
1. **Check prompt quality**: Review coach prompts in `app/coach.py`
2. **Verify policies**: Ensure policies are correctly defined
3. **Test different judges**: Compare GPT-4o-mini vs Claude
4. **Inspect feedback**: Read judge's reasoning in `feedback` field

### Judge Returns Malformed JSON
1. **Check model capability**: Ensure model supports JSON mode
2. **Increase max_tokens**: Judge needs space for detailed response
3. **Review temperature**: Lower temperature (0.1-0.3) for consistency
4. **Fallback parser**: System extracts JSON from markdown if needed

### Inconsistent Scores
1. **Lower temperature**: Set judge temperature to 0.0-0.1
2. **More detailed prompts**: Add specific examples
3. **Use ensemble**: Average multiple judges
4. **Calibrate with human eval**: Compare to human ratings

## Best Practices

1. ✅ **Use a stronger model as judge** than your coach model
2. ✅ **Run batch evaluations regularly** to track quality trends
3. ✅ **Sample in production** (10-20%) to balance cost and monitoring
4. ✅ **Store evaluation results** for analysis and debugging
5. ✅ **Set up alerts** for sudden drops in pass rate
6. ✅ **Compare judges** to find the most reliable one
7. ✅ **Iterate on prompts** based on judge feedback
8. ✅ **Use human evaluation** to calibrate the judge

## Next Steps

- **Run evaluations**: `python scripts/run_evals.py`
- **View results**: Check `./data/eval_results_*.json`
- **Integrate into pipeline**: Add to CI/CD for regression testing
- **Set up monitoring**: Track scores over time in production
- **Tune prompts**: Use feedback to improve coach quality

---

**Related Docs:**
- Multi-Provider Guide: `MULTI_PROVIDER_GUIDE.md`
- Main README: `README.md`
- Judge Implementation: `app/evals/judge.py`
- Tests: `tests/test_judge.py`
