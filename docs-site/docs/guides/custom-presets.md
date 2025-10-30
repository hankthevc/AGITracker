# Custom Presets Guide

Weight AGI signpost categories differently to explore alternative perspectives on progress.

## Overview

**Presets** are weighting schemes that determine how much each category contributes to the overall AGI proximity score.

**Built-in presets**:
- **Equal**: 25% each category (neutral baseline)
- **Aschenbrenner**: Inputs-heavy (reflects compute-centric view)
- **AI-2027**: Agents-focused (emphasizes deployment capability)

**Custom presets**: Create your own weights to test different assumptions.

## Understanding Presets

### Why Presets Matter

The "overall AGI proximity" is inherently subjective. Different stakeholders prioritize different aspects:

| Stakeholder | Likely Preference |
|-------------|-------------------|
| **Compute-focused researcher** | High Inputs weight (Aschenbrenner style) |
| **Safety researcher** | High Security weight |
| **Product manager** | High Agents weight (real-world deployment) |
| **Benchmark researcher** | High Capabilities weight |

Presets let you model these perspectives without changing the underlying data.

### How Weighting Works

**Category score calculation**:
```python
category_score = weighted_mean(signpost_progresses, signpost_weights)
```

**Overall score calculation**:
```python
overall = 2 / (1/capabilities + 1/inputs)  # Harmonic mean
```

**Key insight**: Harmonic mean ensures both Capabilities and Inputs must advance together—bottleneck in either domain significantly reduces overall score.

## Built-In Presets

### Equal (Neutral Baseline)

```json
{
  "capabilities": 0.25,
  "agents": 0.25,
  "inputs": 0.25,
  "security": 0.25
}
```

**Philosophy**: No assumptions about relative importance

**Use when**: You want a neutral, unbiased view

**Example result**: Overall = 45%

### Aschenbrenner (Compute-Centric)

```json
{
  "capabilities": 0.20,
  "agents": 0.30,
  "inputs": 0.40,
  "security": 0.10
}
```

**Philosophy**: Training compute is the primary bottleneck (Situational Awareness thesis)

**Assumptions**:
- Scaling laws hold
- Algorithmic progress secondary to compute
- Security concerns overrated

**Use when**: You believe compute determines timelines

**Example result**: Overall = 52% (higher if Inputs ahead)

### AI-2027 (Agents-Focused)

```json
{
  "capabilities": 0.30,
  "agents": 0.35,
  "inputs": 0.25,
  "security": 0.10
}
```

**Philosophy**: Real-world deployment capability matters most (AI2027 scenarios)

**Assumptions**:
- Reliability and latency critical
- Benchmarks ≠ useful agents
- Economic value validates progress

**Use when**: You care about practical impact

**Example result**: Overall = 38% (if Agents lag)

## Creating Custom Presets

### Via Web UI

1. Navigate to **Settings** → **Presets**
2. Click **Create Custom Preset**
3. Enter weights for each category:
   ```
   Capabilities: [____] %
   Agents:       [____] %
   Inputs:       [____] %
   Security:     [____] %
   
   Total: 100% ✅
   ```
4. Name your preset (e.g., "Safety-First")
5. Click **Save**
6. Select from preset switcher

### Via API

**Create preset** (admin only):
```bash
curl -X POST "http://localhost:8000/v1/admin/presets" \
  -H "x-api-key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Safety-First",
    "weights": {
      "capabilities": 0.20,
      "agents": 0.20,
      "inputs": 0.20,
      "security": 0.40
    }
  }'
```

**Get index with custom preset**:
```bash
curl "http://localhost:8000/v1/index?preset=Safety-First"
```

### Validation Rules

Presets must satisfy:

1. **Sum to 1.0**: All weights add up to 100%
2. **Non-negative**: No negative weights
3. **Unique name**: No duplicate preset names
4. **Min weight**: Each category ≥ 5% (prevents zero-weight gaming)

**Example invalid preset**:
```json
{
  "capabilities": 0.95,  # Too dominant
  "agents": 0.0,         # Zero weight not allowed
  "inputs": 0.05,
  "security": 0.0        # Zero weight not allowed
}
```

## Example Custom Presets

### Safety-First

**Philosophy**: Security must keep pace with capabilities

```json
{
  "capabilities": 0.20,
  "agents": 0.20,
  "inputs": 0.20,
  "security": 0.40
}
```

**Use case**: Policy research, risk assessment

**Effect**: Lower overall score if Security lags

### Benchmark-Only

**Philosophy**: Only verified capabilities matter

```json
{
  "capabilities": 0.70,
  "agents": 0.10,
  "inputs": 0.10,
  "security": 0.10
}
```

**Use case**: ML research, comparing models

**Effect**: Higher overall score if benchmarks strong

### Deployment-Ready

**Philosophy**: Real-world reliability is everything

```json
{
  "capabilities": 0.15,
  "agents": 0.60,
  "inputs": 0.15,
  "security": 0.10
}
```

**Use case**: Product teams, enterprise adoption

**Effect**: Lower overall score if agents unreliable

## Comparing Presets

### Side-by-Side View

Enable **Compare Mode** to see multiple presets at once:

```
┌─────────────────────┬────────┬────────┬────────┐
│ Metric              │ Equal  │ Aschen │ AI2027 │
├─────────────────────┼────────┼────────┼────────┤
│ Overall Proximity   │ 45%    │ 52%    │ 38%    │
│ Capabilities        │ 68%    │ 68%    │ 68%    │
│ Agents              │ 12%    │ 12%    │ 12%    │
│ Inputs              │ 78%    │ 78%    │ 78%    │
│ Security            │ 5%     │ 5%     │ 5%     │
└─────────────────────┴────────┴────────┴────────┘

Variance: 14 percentage points
```

**Interpretation**: Wide variance suggests significant disagreement on what matters.

### Sensitivity Analysis

Test how small weight changes affect overall score:

```python
# Example: Vary Security weight from 10% to 40%
for security_weight in [0.10, 0.20, 0.30, 0.40]:
    other_weight = (1.0 - security_weight) / 3
    overall = compute_index(capabilities=other_weight, 
                           agents=other_weight,
                           inputs=other_weight,
                           security=security_weight)
    print(f"Security={security_weight:.0%} → Overall={overall:.1%}")

# Output:
# Security=10% → Overall=45.3%
# Security=20% → Overall=42.1%
# Security=30% → Overall=38.9%
# Security=40% → Overall=35.2%
```

**Insight**: 10pp increase in Security weight → ~3.5pp decrease in overall (given Security lags)

## Advanced Features

### Preset Scenarios

Combine presets with hypothetical events:

1. Select preset (e.g., "Aschenbrenner")
2. Add hypothetical event: "GPT-5 at 90% SWE-bench"
3. See projected overall score: 45% → 58%

**Use case**: "What if" analysis for forecasting

### Preset Tracking

Monitor how different presets evolve over time:

1. Enable **Preset Timeline**
2. See overlay of all presets on one chart
3. Identify convergence/divergence

**Example**: All presets agree on direction (good signal) vs wildly diverging (ambiguous progress)

### Export Preset Results

**CSV with all presets**:
```bash
curl "http://localhost:8000/v1/index?format=csv&compare=equal,aschenbrenner,ai2027"
```

Output:
```csv
date,preset,overall,capabilities,agents,inputs,security
2025-10-29,equal,0.45,0.68,0.12,0.78,0.05
2025-10-29,aschenbrenner,0.52,0.68,0.12,0.78,0.05
2025-10-29,ai2027,0.38,0.68,0.12,0.78,0.05
```

## Sharing Custom Presets

### Permalink

Share custom preset via URL:

```
https://agi-tracker.vercel.app/?preset=custom&weights=0.20,0.20,0.20,0.40
```

Anyone clicking this link sees your weighting scheme.

### Export as JSON

```bash
curl "http://localhost:8000/v1/presets/Safety-First" > preset.json
```

Share JSON for reproducibility:
```json
{
  "name": "Safety-First",
  "weights": {
    "capabilities": 0.20,
    "agents": 0.20,
    "inputs": 0.20,
    "security": 0.40
  },
  "created_at": "2025-10-29T12:00:00Z",
  "author": "Alice Researcher"
}
```

### Import Preset

```bash
curl -X POST "http://localhost:8000/v1/admin/presets/import" \
  -H "x-api-key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d @preset.json
```

## Use Cases

### Research: Testing Assumptions

**Goal**: See how different theories affect AGI timeline

**Steps**:
1. Create "Compute-Only" preset (Inputs=80%)
2. Create "Safety-Gated" preset (Security=50%)
3. Compare overall scores
4. Export both for paper
5. Discuss variance in results

### Policymaking: Risk Scenarios

**Goal**: Model worst-case (capabilities ahead, security behind)

**Steps**:
1. Create "Risk-Weighted" (Capabilities=50%, Security=40%)
2. Check overall score (likely low if security lags)
3. Use in policy briefs to justify funding

### Journalism: Explainer Articles

**Goal**: Show readers why experts disagree

**Steps**:
1. Use built-in presets (Equal, Aschenbrenner, AI2027)
2. Show side-by-side comparison
3. Explain assumptions behind each
4. Let readers choose their own weights

## Troubleshooting

### "Weights must sum to 1.0"

**Cause**: Weights don't add to 100%

**Fix**:
```json
# Bad: 0.25 + 0.25 + 0.25 + 0.30 = 1.05
# Good: 0.25 + 0.25 + 0.25 + 0.25 = 1.00
```

### Overall Score Doesn't Change

**Cause**: Harmonic mean only uses Capabilities and Inputs

**Explanation**: Agents and Security weights only affect category scores, not overall (by design).

**To change overall**: Adjust how signposts map to Capabilities/Inputs categories (requires code change).

### Preset Not Appearing

**Cause**: Not saved to database

**Fix**:
- Ensure API key is admin-level
- Check response status: `200 OK`
- Reload page or clear cache

## Best Practices

✅ **Do**:
- Document assumptions behind custom weights
- Compare multiple presets (show variance)
- Export presets for reproducibility
- Use permalinks for sharing
- Cite preset in papers

❌ **Don't**:
- Cherry-pick favorable preset without disclosure
- Use extreme weights (one category >70%)
- Assume one preset is "correct"
- Change weights mid-analysis (creates confusion)
- Ignore built-in presets (they represent expert views)

## Next Steps

- [Scenario Explorer](/docs/guides/scenario-explorer) - Combine presets with hypotheticals
- [Timeline](/docs/guides/timeline-visualization) - See preset evolution over time
- [API Usage](/docs/guides/api-usage) - Programmatic preset management
- [Methodology](/docs/methodology) - Deep-dive into scoring math

## Related Resources

- **Aschenbrenner's Situational Awareness**: [PDF](https://situational-awareness.ai/)
- **AI2027 Scenarios**: [Epoch AI](https://epochai.org/ai2027)
- **API Endpoint**: `GET /v1/index?preset=<name>` ([Docs](/docs/api/endpoints))

