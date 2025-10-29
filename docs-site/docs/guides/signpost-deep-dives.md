# Signpost Deep-Dives Guide

Understand each measurable milestone on the path to AGI, why it matters, and how close we are.

## Overview

**Signposts** are measurable milestones that operationalize AGI proximity. Each signpost has:

- **Clear target**: Specific threshold (e.g., "SWE-bench ≥70%")
- **Baseline**: Starting point for progress calculation
- **Current value**: Latest measurement from A/B tier evidence
- **Progress %**: (current - baseline) / (target - baseline)
- **Why this matters**: Educational explanation of significance
- **Linked events**: Real evidence moving this signpost

Access signposts at:
- **Web**: http://localhost:3000/signposts
- **API**: http://localhost:8000/v1/signposts

## Signpost Categories

### Capabilities (8 signposts)

Track performance on key benchmarks:

| Code | Name | Baseline | Target | Direction |
|------|------|----------|--------|-----------|
| `swebench_50` | SWE-bench ≥50% | 13.9% | 50% | ≥ |
| `swebench_70` | SWE-bench ≥70% | 13.9% | 70% | ≥ |
| `swebench_90` | SWE-bench ≥90% | 13.9% | 90% | ≥ |
| `osworld_30` | OSWorld ≥30% | 4.8% | 30% | ≥ |
| `webarena_50` | WebArena ≥50% | 14.4% | 50% | ≥ |
| `gpqa_70` | GPQA Diamond ≥70% | 50.1% | 70% | ≥ |
| `gpqa_85` | GPQA Diamond ≥85% | 50.1% | 85% | ≥ |
| `hle_text_70` | HLE Text ≥70% | 35.7% | 70% | ≥ |

**Why these benchmarks?**
- **SWE-bench**: Real-world software engineering (GitHub issues)
- **OSWorld**: Operating system-level computer use
- **WebArena**: Web navigation and interaction
- **GPQA**: PhD-level scientific reasoning
- **HLE**: Breadth of expert-level knowledge

### Agents (5 signposts)

Track real-world deployment:

| Code | Name | What It Measures |
|------|------|------------------|
| `agent_reliability_90` | Agent Reliability ≥90% | Multi-step task success rate |
| `agent_latency_2s` | Agent Latency ≤2s | Response time for 95th percentile |
| `agent_self_improve` | Self-Improvement Deployed | Agents that modify their own code |
| `agent_economic_1b` | Economic Value ≥$1B | Verified autonomous task value |
| `agent_deployment_scale` | Deployment Scale | Agents managing >1M tasks/day |

**Why agents matter?**
- Benchmarks ≠ real-world capability
- Reliability and latency crucial for adoption
- Economic impact validates usefulness
- Self-improvement = recursive progress

### Inputs (7 signposts)

Track training resources:

| Code | Name | Target | Current |
|------|------|--------|---------|
| `compute_6e25` | Training Run ≥6e25 FLOPs | 6e25 | ~5e25 (GPT-4) |
| `compute_1e26` | Training Run ≥1e26 FLOPs | 1e26 | TBD |
| `compute_1e27` | Training Run ≥1e27 FLOPs | 1e27 | TBD |
| `compute_1e28` | Training Run ≥1e28 FLOPs | 1e28 | TBD |
| `algorithmic_100x` | 100x Algo Efficiency | 100x GPT-4 | ~2x |
| `dc_power_5gw` | Datacenter Power ≥5GW | 5GW | ~1.5GW |
| `dc_power_20gw` | Datacenter Power ≥20GW | 20GW | ~1.5GW |

**Why inputs matter?**
- Compute scaling = empirical trendline
- OOMs predict capability jumps
- Datacenters = observable constraint
- Algorithmic efficiency = force multiplier

### Security (5 signposts)

Track safety maturity:

| Code | Name | Maturity Level |
|------|------|----------------|
| `security_l1_weights` | L1: Model Weight Security | Basic access controls |
| `security_l2_deploy` | L2: Deployment Controls | Runtime monitoring, kill switches |
| `security_l3_incident` | L3: Incident Response | Coordinated disclosure, forensics |
| `security_mandatory_evals` | Mandatory Evals | Government-required safety testing |
| `security_governance` | Multi-Stakeholder Governance | International coordination |

**Why security matters?**
- Capabilities without safety = risk
- Governance lag = dangerous gap
- Mandatory evals = regulatory maturity
- Incident response = resilience

## Navigating a Signpost Page

### Header Section

```
SWE-bench ≥70%
Category: Capabilities | First-Class: Yes | Progress: 42%
```

- **Name**: Clear milestone description
- **Category**: Which domain this belongs to
- **First-Class**: Whether it receives 2x weight in scoring
- **Progress**: Current % toward target

### Progress Bar

Visual gauge showing:
- **Green bar**: Progress from baseline to current
- **Gray bar**: Remaining progress to target
- **Percentage**: Exact progress value

### Why This Matters

Educational explanation:

```markdown
**SWE-bench** tests models on real GitHub issues from popular open-source projects.
Achieving 70% means the model can autonomously resolve most routine software engineering
tasks with minimal human oversight.

**Significance**: Enables AI pair programmers to handle majority of coding work,
accelerating software development timelines and reducing median engineering costs.

**Precursors**: Requires strong code understanding, debugging skills, and ability
to interact with existing codebases.
```

### Current State

Latest measurement:

```
Current Value: 52.3%
Baseline: 13.9%
Target: 70.0%
Progress: 42.1% = (52.3 - 13.9) / (70.0 - 13.9)

Last Updated: 2025-10-15 (via GPT-5 announcement)
Evidence Tier: A-tier (OpenAI API + leaderboard)
```

### Expert Predictions

Comparison table:

| Source | Predicted Date | Actual Date | Status |
|--------|----------------|-------------|--------|
| AI2027 | 2025-12-31 | 2025-10-15 | ✅ 77 days ahead |
| Aschenbrenner | 2026-06-30 | 2025-10-15 | ✅ 258 days ahead |
| Metaculus | 2026-03-15 | 2025-10-15 | ✅ 151 days ahead |

**Interpretation**:
- All forecasts exceeded ahead of schedule
- Suggests faster progress than experts expected
- Potential acceleration in capabilities

### Linked Events

List of events that moved this signpost:

```
📄 GPT-5 Achieves 85% on SWE-bench Verified (2025-10-15) | A-tier | +32.4% progress
📄 Claude 3.5 Sonnet Reaches 60% on SWE-bench (2025-08-10) | B-tier | +12.1% progress
📰 Reports Suggest GPT-4.5 at 55% (2025-06-05) | C-tier | No impact (unverified)
```

Each entry shows:
- **Icon**: Source type (📄=paper, 📰=press, 💬=social)
- **Title**: Event description
- **Date**: When published
- **Tier**: Evidence quality
- **Impact**: Progress contribution

Click to view full event details.

### Related Signposts

Nearby or dependent milestones:

```
SWE-bench ≥50% (✅ Achieved 2024-11-20)
→ SWE-bench ≥70% (🔄 In Progress, 42%)
→ SWE-bench ≥90% (⏳ Not Started, 0%)

OSWorld ≥30% (🔄 In Progress, 18%) - Related: Computer use skills
WebArena ≥50% (⏳ Not Started, 5%) - Related: Web navigation
```

### Key Papers

Foundational research:

- **SWE-bench: Can Language Models Resolve Real-World GitHub Issues?**
  - Authors: Jimenez et al.
  - Published: 2024-10
  - Link: https://arxiv.org/abs/2310.06770

- **SWE-bench Verified: Human-Validated Subset**
  - Authors: OpenAI
  - Published: 2025-01
  - Link: https://swebench.com/verified

## Understanding Progress Calculation

### For Increasing Metrics (direction: "≥")

```python
progress = (current - baseline) / (target - baseline)
```

**Example**: SWE-bench ≥70%
- Current: 52.3%
- Baseline: 13.9%
- Target: 70.0%
- Progress: (52.3 - 13.9) / (70.0 - 13.9) = **68.5%**

### For Decreasing Metrics (direction: "≤")

```python
progress = (baseline - current) / (baseline - target)
```

**Example**: Agent Latency ≤2s
- Current: 5.2s
- Baseline: 8.0s
- Target: 2.0s
- Progress: (8.0 - 5.2) / (8.0 - 2.0) = **46.7%**

### Clamping

Progress is clamped to [0, 1]:

- **Negative values** → 0% (regressed below baseline)
- **Above 100%** → 100% (exceeded target)

## First-Class vs Monitor-Only

### First-Class Signposts

Receive **2x weight** in category scoring:

- Core benchmarks (SWE-bench, OSWorld, WebArena, GPQA)
- Critical compute milestones (6e25, 1e26, 1e27 FLOPs)
- Key security levels (L1, L2, L3)

**Why?** Most operationally relevant for AGI assessment.

### Monitor-Only Signposts

Displayed but **excluded from composite gauge**:

- HLE (known label quality issues in Bio/Chem)
- Experimental benchmarks
- Context-dependent metrics

**Why?** Useful for context, but not yet validated enough to affect main score.

## Using Signpost Data

### API Access

**Get all signposts**:
```bash
curl "http://localhost:8000/v1/signposts"
```

**Filter by category**:
```bash
curl "http://localhost:8000/v1/signposts?category=capabilities&first_class=true"
```

**Get specific signpost**:
```bash
curl "http://localhost:8000/v1/signposts/by-code/swebench_70"
```

**Get linked events**:
```bash
curl "http://localhost:8000/v1/signposts/by-code/swebench_70/events"
```

### Exporting Signpost Data

**CSV Export**:
```bash
curl "http://localhost:8000/v1/signposts" | \
  jq -r '.signposts[] | [.code, .name, .current_value, .progress] | @csv'
```

**JSON with Events**:
```bash
curl "http://localhost:8000/v1/signposts/by-code/swebench_70/events" > signpost-events.json
```

## Troubleshooting

### Progress Showing 0% or N/A

**Possible causes**:
1. No A/B tier evidence yet
2. Current value = baseline (no progress)
3. Signpost not mapped to any events

**Action**:
- Check "Linked Events" section
- If empty, no evidence has moved this signpost yet
- Filter events to see if C/D tier exists (unverified)

### Expert Predictions Missing

**Possible causes**:
1. Signpost added after forecast deadlines
2. Forecast source didn't cover this metric
3. Database not seeded with predictions

**Action**:
```bash
# Seed expert predictions
cd scripts
python seed_forecasts.py
```

### Current Value Outdated

**Possible causes**:
1. Recent event not yet approved
2. Scraper didn't run (leaderboard stale)
3. LLM mapping missed the link

**Action**:
- Check `/admin/review` for pending mappings
- Manually trigger re-scrape:
  ```bash
  curl -X POST http://localhost:8000/v1/admin/recompute \
    -H "x-api-key: your-admin-key"
  ```

## Best Practices

✅ **Do**:
- Read "Why this matters" before citing signpost
- Check evidence tier of linked events
- Compare multiple expert forecasts
- Export data for offline analysis

❌ **Don't**:
- Treat progress as certainty (it's directional)
- Ignore confidence bands (progress has variance)
- Assume linear extrapolation (can accelerate/decelerate)
- Cherry-pick favorable signposts (use composite gauge)

## Next Steps

- [Events Feed](/docs/guides/events-feed) - See what's moving signposts
- [Timeline](/docs/guides/timeline-visualization) - Track progress over time
- [Custom Presets](/docs/guides/custom-presets) - Weight signposts differently
- [API Usage](/docs/guides/api-usage) - Integrate signpost data

## Related Resources

- **Methodology**: [Scoring System](/docs/methodology) (on live site)
- **API Docs**: [Signposts Endpoint](/docs/api/endpoints#signposts)
- **Roadmap**: [Expert Predictions](/docs/roadmap) (project docs)

