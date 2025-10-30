# Scenario Explorer Guide

**Note**: This feature is planned for Phase 6. This guide describes the future functionality.

## Overview

The Scenario Explorer lets you model "what-if" scenarios by adjusting signpost progress, category weights, and hypothetical events to forecast how they would affect the overall AGI proximity score.

**Example scenarios**:
- "What if GPT-6 hits 95% on SWE-bench next month?"
- "What if a major security incident forces 6-month pause?"
- "What if training compute doubles every 6 months (vs 9 months)?"

Access at: http://localhost:3000/scenarios (when implemented)

## Use Cases

### Research: Sensitivity Analysis

**Goal**: Test how robust conclusions are to assumptions

**Example**:
1. Baseline: Current progress → 45% overall
2. Scenario A: +20% Capabilities → 52% overall
3. Scenario B: -10% Security → 41% overall
4. Conclusion: 11pp variance suggests moderate sensitivity

### Policymaking: Risk Modeling

**Goal**: Model worst-case scenarios for resource allocation

**Example**:
1. Baseline: Security 5%, Capabilities 68%
2. Scenario: Major security incident (-50% Security)
3. Result: Safety margin -68pp (critical risk)
4. Policy: Justify emergency security funding

### Forecasting: Timeline Projections

**Goal**: Predict when signposts will be achieved

**Example**:
1. Current SWE-bench progress: 52% toward 70% target
2. Velocity: +8pp/month (last 3 months)
3. Scenario: Maintain velocity → hit 70% in Feb 2026
4. Scenario: Accelerate to +12pp/month → hit 70% in Dec 2025

## Creating Scenarios

### Basic Scenario

1. Navigate to **Scenarios** → **New Scenario**
2. Name it: "GPT-6 Optimistic"
3. Adjust sliders:
   ```
   SWE-bench ≥70%: 52% → 95% (+43pp)
   OSWorld ≥30%:   12% → 40% (+28pp)
   ```
4. Click **Compute Impact**
5. See results:
   ```
   Capabilities: 68% → 85% (+17pp)
   Overall:      45% → 61% (+16pp)
   ```

### Advanced Scenario

Add hypothetical events:

1. Create scenario: "Scaling Pause"
2. Add event:
   ```
   Title: "6-Month AI Training Pause (Hypothetical)"
   Impact:
     - Inputs: -20% (no new training runs)
     - Security: +15% (time to catch up)
   Date: 2025-11-01
   ```
3. Compute:
   ```
   Before: Overall 45%
   After:  Overall 38% (bottleneck in Inputs)
   ```

## Scenario Types

### Optimistic Scenarios

Model best-case progress:

**Assumptions**:
- Scaling laws hold
- No regulatory slowdowns
- Algorithmic breakthroughs

**Example**:
```
"AGI by 2027" (AI2027 optimistic track)
- Capabilities: +50%
- Agents: +60%
- Inputs: +40%
- Security: +20%
→ Overall: 82%
```

### Pessimistic Scenarios

Model worst-case outcomes:

**Assumptions**:
- Scaling laws break
- Major security incidents
- Regulatory crackdowns

**Example**:
```
"Regulatory Freeze"
- Capabilities: -10% (paused research)
- Agents: -30% (deployment bans)
- Inputs: -50% (compute restrictions)
- Security: +10% (forced investment)
→ Overall: 28%
```

### Neutral Scenarios

Model status quo:

**Assumptions**:
- Current velocity continues
- No major surprises
- Linear extrapolation

**Example**:
```
"Business as Usual"
- All categories: +5%/quarter
→ Overall: 45% → 65% in 12 months
```

## Comparing Scenarios

### Side-by-Side View

Enable **Compare Mode**:

```
┌──────────────┬──────────┬───────────┬────────────┐
│ Metric       │ Baseline │ Optimistic│ Pessimistic│
├──────────────┼──────────┼───────────┼────────────┤
│ Overall      │ 45%      │ 82%       │ 28%        │
│ Capabilities │ 68%      │ 95%       │ 60%        │
│ Agents       │ 12%      │ 70%       │ 5%         │
│ Inputs       │ 78%      │ 95%       │ 40%        │
│ Security     │ 5%       │ 25%       │ 15%        │
└──────────────┴──────────┴───────────┴────────────┘

Range: 28% to 82% (54pp variance)
```

**Interpretation**: Wide range → high uncertainty

### Probability Weighting

Assign probabilities to scenarios:

```
Optimistic:   20% probability → Expected value: 0.20 * 82 = 16.4
Neutral:      60% probability → Expected value: 0.60 * 45 = 27.0
Pessimistic:  20% probability → Expected value: 0.20 * 28 = 5.6

Weighted average: 16.4 + 27.0 + 5.6 = 49.0%
```

**Use**: More nuanced than single point estimate

## Timeline Projections

### Velocity-Based Forecasting

Extrapolate current trends:

**Example**: SWE-bench ≥70%
- Current: 52.3%
- Target: 70.0%
- Gap: 17.7pp
- Velocity: +8pp/month (3-month average)
- Forecast: 17.7 / 8 = 2.2 months → Jan 2026

**Confidence intervals**:
- Optimistic (+12pp/month): 1.5 months → Dec 2025
- Pessimistic (+4pp/month): 4.4 months → Mar 2026

### Event-Driven Forecasting

Model impact of expected events:

**Scenario**: "GPT-5.5 in Q1 2026"
- Assumed impact: +15pp SWE-bench, +10pp GPQA
- Capabilities: 68% → 78%
- Overall: 45% → 53%

**Comparison**:
- Without GPT-5.5: 45% → 48% (linear trend)
- With GPT-5.5: 45% → 53% (jump)
- Delta: +5pp accelerated progress

## Exporting Scenarios

### Export as JSON

```bash
curl "http://localhost:8000/v1/scenarios/123" > scenario.json
```

Output:
```json
{
  "name": "GPT-6 Optimistic",
  "created_at": "2025-10-29",
  "adjustments": {
    "swebench_70": {"from": 0.52, "to": 0.95},
    "osworld_30": {"from": 0.12, "to": 0.40}
  },
  "results": {
    "capabilities": 0.85,
    "overall": 0.61
  }
}
```

### Export as Report

Generate PDF with:
- Scenario assumptions
- Adjustments made
- Results comparison table
- Timeline projection chart

### Share via Permalink

```
https://agi-tracker.vercel.app/scenarios?id=abc123
```

Anyone can view (read-only unless they clone).

## Advanced Features

### Monte Carlo Simulation

Run 10,000 simulations with random variations:

**Input**:
- SWE-bench: 52% ± 10% (uncertainty range)
- Training compute: +2 OOMs ± 0.5 OOMs

**Output**:
- Distribution of overall scores
- Percentiles: 10th (38%), 50th (45%), 90th (52%)
- Mean: 45.3%
- Std dev: 6.2pp

**Use**: Quantify uncertainty

### Sensitivity Heatmap

See which signposts matter most:

```
            │ Overall Impact
────────────┼────────────────────
SWE-bench   │ ███████████ 11pp
OSWorld     │ ██████ 6pp
WebArena    │ ████ 4pp
GPQA        │ ████ 4pp
Training $  │ ████████ 8pp
Security L1 │ ██ 2pp
```

**Interpretation**: Focus research on high-impact signposts.

### Scenario Chains

Model sequences of events:

```
Jan 2026: GPT-6 released (+20% Capabilities)
  ↓
Mar 2026: Security incident (-30% Security)
  ↓
Jun 2026: 6-month pause (-50% Inputs)
  ↓
Dec 2026: Regulations stabilize (+20% Security)

Net result: Overall 45% → 35% (-10pp)
```

## Troubleshooting

### "Invalid scenario: Total > 100%"

**Cause**: Signpost progress can't exceed 100%

**Fix**: Adjust so no signpost exceeds 100%

### Scenarios Not Saving

**Cause**: Not logged in (requires admin account)

**Fix**: Login with admin API key or save locally (JSON export)

### Results Don't Change

**Cause**: Harmonic mean bottleneck (one category at 0%)

**Explanation**: If Inputs or Security is 0%, overall stays "N/A" regardless of other changes.

**Fix**: Ensure both Inputs and Security are above 0% in scenario

## Best Practices

✅ **Do**:
- Document assumptions clearly
- Test multiple scenarios (optimistic/neutral/pessimistic)
- Use probability weighting for expected values
- Export scenarios for reproducibility
- Cite baseline data sources

❌ **Don't**:
- Cherry-pick favorable scenarios
- Ignore confidence intervals
- Assume linear extrapolation
- Forget to update scenarios (refresh monthly)
- Present single scenario as certainty

## Next Steps

- [Custom Presets](/docs/guides/custom-presets) - Adjust category weights
- [RAG Chatbot](/docs/guides/rag-chatbot) - Ask natural language questions
- [API Usage](/docs/guides/api-usage) - Programmatic scenario modeling

---

**Status**: Planned for Phase 6 (not yet implemented)

**Follow development**: [GitHub Roadmap](https://github.com/hankthevc/AGITracker/projects)

