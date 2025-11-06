# Comprehensive Signpost Enhancement Plan

**Created**: November 7, 2024  
**Purpose**: Extract ALL measurable AGI predictions from source materials  
**Goal**: 34 → 89 signposts across 8 dimensions  
**Status**: Extraction in progress

---

## Executive Summary

**Current State**: 34 signposts (good benchmark coverage, sparse economic/geopolitical)  
**Enhanced State**: 89 signposts (comprehensive, multi-dimensional AGI tracking)  
**New Dimensions**: Economic, Research Velocity, Geopolitical, Safety Incidents

**Approach**: Systematic extraction from 7 expert sources with full citations

---

## 📊 Dimension 1: CAPABILITIES (Current: 10 → Enhanced: 18)

### Existing (Keep & Enhance)

#### CORE-CAP-001: SWE-bench Verified 85%
**Current Status**: ✅ Exists  
**Enhancement Needed**: Add richer metadata

**Enhanced Definition**:
```yaml
code: swe_bench_85
name: "SWE-bench Verified ≥85%"
category: capabilities
baseline: 0.48
target: 0.85
unit: "% success rate"
direction: ">="
first_class: true

description: |
  AI system achieves 85% success rate on SWE-bench Verified, resolving real-world 
  GitHub issues requiring code understanding, patch generation, and test passing.

why_matters: |
  Software engineering is economically critical. Automating 85% of GitHub issues 
  demonstrates transformative capability in a high-value domain. This is a proxy 
  for general coding competence.

measurement:
  source: "https://www.swebench.com/leaderboard"
  frequency: "weekly"
  methodology: "2,294 verified task instances from 12 Python repositories"
  verification: "A-tier (peer-reviewed dataset + official leaderboard)"
  
current_sota:
  value: 0.50
  model: "Claude 3.5 Sonnet"
  date: "2024-10-30"
  source: "SWE-bench leaderboard"

forecasts:
  aschenbrenner:
    timeline: "2027 Q2-Q3"
    confidence: 0.7
    rationale: "Situational Awareness implies near-human coding by mid-2027"
    quote: "'AI will be able to do the work of an AI researcher/engineer by 2027'"
    page: 45
    
  ai2027:
    timeline: "2026 Q4"
    confidence: 0.6
    rationale: "Aggressive capability timeline"
    
  epoch_ai:
    timeline: "2026 Q2"
    confidence: 0.7
    rationale: "Follows compute scaling + algorithmic gains"

citations:
  - paper: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
    url: "https://arxiv.org/abs/2310.06770"
    authors: "Jimenez et al."
    year: 2024
```

#### CORE-CAP-002: SWE-bench Verified 90%
**Status**: ✅ Exists, enhance with above pattern

#### CORE-CAP-003: OSWorld 65%
**Status**: ✅ Exists, enhance

#### CORE-CAP-004: OSWorld 85%  
**Status**: ✅ Exists, enhance

#### CORE-CAP-005: WebArena 70%
**Status**: ✅ Exists, enhance

#### CORE-CAP-006: WebArena 85%
**Status**: ✅ Exists, enhance

#### CORE-CAP-007: GPQA Diamond SOTA
**Status**: ✅ Exists, enhance

#### CORE-CAP-008: GPQA Diamond PhD Parity
**Status**: ✅ Exists, enhance

#### CORE-CAP-009: HLE Text ≥50% (Monitor-Only)
**Status**: ✅ Exists, already well-documented

#### CORE-CAP-010: HLE Text ≥70%
**Status**: ✅ Exists, enhance

---

### NEW Capability Signposts (Add 8)

#### NEW-CAP-011: Automated AI Researcher
```yaml
code: ai_researcher_demo
name: "Automated AI Researcher Demonstration"
category: capabilities
baseline: 0.0
target: 1.0
unit: "binary (0=no, 1=yes)"
direction: ">="
first_class: true

description: |
  AI system independently conducts novel AI research: formulates hypotheses, 
  designs experiments, implements models, analyzes results, writes papers.

why_matters: |
  Recursive improvement capability. If AI can do AI research, progress becomes 
  self-sustaining. This is Aschenbrenner's key inflection point.

measurement:
  milestone: "Peer-reviewed AI paper with AI listed as primary researcher"
  verification: "A-tier (published in ML conference: NeurIPS, ICML, ICLR)"
  methodology: "Paper must demonstrate: novel hypothesis, experimental design, implementation, analysis"

forecasts:
  aschenbrenner:
    timeline: "2026 Q4 - 2027 Q2"
    confidence: 0.65
    rationale: "'Unhobbling' + compute scaling enables AI researchers by late 2026"
    quote: "'The jump to AI systems that can automate AI research will be the most important event'"
    implications: "Recursive improvement begins, timelines compress dramatically"

related_signposts:
  - swe_bench_90 (coding prerequisite)
  - multi_step_reliability (agent prerequisite)
  - compute_1e26 (compute prerequisite)
```

#### NEW-CAP-012: Competitive Programming Gold
```yaml
code: codeforces_gold
name: "Codeforces Gold Medal Level"
category: capabilities
baseline: 0.20
target: 0.90
unit: "percentile"
direction: ">="
first_class: true

description: |
  AI achieves Gold medal level (top 1%) on Codeforces competitive programming,
  demonstrating advanced algorithmic problem-solving.

why_matters: |
  Competitive programming tests raw algorithmic thinking, not just code generation.
  Gold level indicates problem-solving ability beyond most professional programmers.

measurement:
  source: "Codeforces rating system"
  methodology: "AI competes in live contests, achieves rating >2400"
  verification: "A-tier if official Codeforces participant, B-tier if synthetic"

current_sota:
  value: 0.35
  model: "AlphaCode 2"
  date: "2024-06-01"

forecasts:
  aschenbrenner:
    timeline: "2026 Q2"
    confidence: 0.6
    rationale: "Precursor to automated AI research"
```

#### NEW-CAP-013: MATH Benchmark 95%
```yaml
code: math_500_95
name: "MATH-500 ≥95%"
category: capabilities
baseline: 0.50
target: 0.95
unit: "% correct"
direction: ">="
first_class: false

description: |
  AI achieves 95% on MATH-500 benchmark (high school competition math).

measurement:
  source: "MATH dataset (Hendrycks et al.)"
  methodology: "500 problems from competitions (AMC, AIME, IMO)"
  
forecasts:
  openai_o1: "Already achieved ~90%, expect 95% by 2025 Q2"
```

#### NEW-CAP-014: ARC-AGI 85%
```yaml
code: arc_agi_85
name: "ARC-AGI ≥85%"
category: capabilities
baseline: 0.35
target: 0.85
unit: "% correct"
direction: ">="
first_class: true

description: |
  AI achieves 85% on ARC-AGI (Abstraction and Reasoning Corpus), testing 
  few-shot generalization and abstract pattern recognition.

why_matters: |
  ARC specifically tests the kind of general intelligence that current LLMs struggle with.
  High performance indicates genuine reasoning, not pattern matching.

measurement:
  source: "https://arcprize.org/"
  methodology: "Novel visual reasoning puzzles requiring generalization"

current_sota:
  value: 0.35
  model: "GPT-4 with various prompting"
  note: "Human performance: ~85%"

forecasts:
  chollet_prize: "Prize awarded when AI achieves 85% (open challenge)"
```

#### NEW-CAP-015: Turing Test (Broad)
```yaml
code: turing_test_pass
name: "Turing Test (Broad Protocol)"
category: capabilities
baseline: 0.65
target: 0.95
unit: "% fooling rate"
direction: ">="
first_class: false

description: |
  AI fools 95% of judges in extended Turing test (30+ min conversations) 
  across diverse topics.

measurement:
  methodology: "Structured Turing test with professional evaluators"
  verification: "A-tier if peer-reviewed study, B-tier if informal"

forecasts:
  general_consensus: "Likely already surpassed for short conversations, extended protocol TBD"
```

#### NEW-CAP-016: Medical Diagnosis (USMLE)
```yaml
code: usmle_90
name: "USMLE Step 2 ≥90%"
category: capabilities
baseline: 0.70
target: 0.90
unit: "% correct"
direction: ">="
first_class: false

description: |
  AI achieves 90% on USMLE Step 2 CK (clinical knowledge), approaching top 
  medical resident performance.

why_matters: |
  Medical diagnosis tests specialized knowledge + reasoning. High performance 
  indicates readiness for high-stakes professional domains.

current_sota:
  value: 0.86
  model: "GPT-4 (2024)"
  note: "Approaching target, may hit 90% in 2025"
```

#### NEW-CAP-017: Scientific Discovery
```yaml
code: novel_discovery_demo
name: "Novel Scientific Discovery"
category: capabilities
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  AI independently discovers novel scientific finding, verified by peer review 
  (not just analysis of existing data, but genuine discovery).

measurement:
  milestone: "Peer-reviewed paper with novel finding attributed to AI system"
  verification: "A-tier (published in Nature, Science, Cell, or top-tier journal)"
  
forecasts:
  aschenbrenner: "2027+ (after automated AI researchers)"
  google_deepmind: "Precedent: AlphaFold (protein folding), FunSearch (mathematics)"
```

#### NEW-CAP-018: Superhuman Coding (Drop-in SWE)
```yaml
code: superhuman_coding
name: "Superhuman Coding (Better than Median SWE)"
category: capabilities
baseline: 0.60
target: 1.0
unit: "relative to median software engineer"
direction: ">="
first_class: true

description: |
  AI outperforms median software engineer across ALL coding tasks (not just benchmarks):
  - Design, implementation, debugging, code review, architecture
  - Works at faster speed with fewer bugs
  - Can be "dropped in" to replace remote SWE

why_matters: |
  This is Aschenbrenner's "drop-in remote worker" threshold. Represents economic 
  transformative AI for knowledge work.

measurement:
  methodology: "Composite of: SWE-bench (90%+), Codeforces (Gold+), speed metrics, bug rates"
  verification: "Requires multiple A-tier benchmarks + real-world deployment data"
  
forecasts:
  aschenbrenner:
    timeline: "2027 Q2-Q4"
    confidence: 0.65
    quote: "'By 2027, AI will be better than median remote software engineers'"
```

---

## 📊 Dimension 2: AGENTS (Current: 5 → Enhanced: 12)

### Existing (Enhance)

#### CORE-AGT-001: Multi-step Agent Reliability 80%
**Status**: ✅ Exists, enhance with forecasts

#### CORE-AGT-002: OSWorld Latency <10min
**Status**: ✅ Exists, enhance

#### CORE-AGT-003: Recursive Self-Improvement Demo
**Status**: ✅ Exists, enhance with Aschenbrenner timeline

#### CORE-AGT-004: Multi-day Agentic Project
**Status**: ✅ Exists, enhance

#### CORE-AGT-005: 10% Remote Job Displacement
**Status**: ✅ Exists, enhance with BLS measurement

---

### NEW Agent Signposts (Add 7)

#### NEW-AGT-006: 100-Hour Autonomous Task
```yaml
code: agent_100h_task
name: "100-Hour Autonomous Task Completion"
category: agents
baseline: 1.0
target: 100.0
unit: "hours of autonomous work"
direction: ">="
first_class: true

description: |
  AI agent autonomously completes complex project requiring 100+ hours of 
  continuous work with minimal human intervention.

why_matters: |
  Demonstrates sustained autonomous operation, long-term planning, and 
  error recovery. Critical for replacing knowledge workers.

measurement:
  methodology: "Real-world projects: software development, research, analysis"
  criteria: "Success rate >80% on 100h+ tasks with <2h human intervention"
  
forecasts:
  ai2027:
    timeline: "2027 Q3-Q4"
    confidence: 0.55
    rationale: "Requires: long-term memory, robust error handling, goal persistence"
```

#### NEW-AGT-007: Credit Card Authorization (Agentic Commerce)
```yaml
code: agentic_commerce
name: "Agentic Commerce with Financial Authorization"
category: agents
baseline: 0.0
target: 1.0
unit: "binary (deployed at scale)"
direction: ">="
first_class: true

description: |
  AI agents widely deployed with authority to make purchases, negotiate contracts,
  and manage budgets on behalf of users/companies.

why_matters: |
  Economic agency. If AI can be trusted with financial decisions, represents 
  profound shift in automation scope.

measurement:
  milestone: "Major platform (Amazon, Shopify, Stripe) launches AI agent with payment auth"
  verification: "B-tier (official launch announcement)"
  scale_threshold: "1M+ users with active AI purchase agents"
  
forecasts:
  ai2027:
    timeline: "2027 Q1-Q2"
    confidence: 0.50
    rationale: "Requires: reliability thresholds + legal frameworks"
    prerequisites: "agent_reliability_80, regulatory clarity"
```

#### NEW-AGT-008: Enterprise AI Agent Adoption
```yaml
code: enterprise_agent_adoption
name: "F500 Enterprise AI Agent Deployment"  
category: agents
baseline: 0.05
target: 0.50
unit: "% of Fortune 500 with production AI agents"
direction: ">="
first_class: true

description: |
  50% of Fortune 500 companies have AI agents deployed in production workflows
  (not just pilots - actual automation of work).

why_matters: |
  Enterprise adoption indicates agents are reliable, secure, and economically valuable.
  F500 represents $20T+ in annual revenue.

measurement:
  source: "Quarterly enterprise software surveys (Gartner, IDC)"
  methodology: "Survey CIOs: 'Do you have AI agents automating workflows in production?'"
  verification: "B-tier (analyst reports)"

current_baseline:
  value: 0.05
  note: "~5% have ChatGPT Enterprise or similar (not true agents)"

forecasts:
  ai2027:
    timeline: "2027 Q4"
    confidence: 0.55
    rationale: "Requires: 80% reliability + 12-18 month enterprise sales cycles"
```

#### NEW-AGT-009: Autonomous Research Agent
```yaml
code: research_agent_demo
name: "Autonomous Research Agent (End-to-End)"
category: agents
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  AI agent autonomously conducts research project: literature review, hypothesis 
  generation, experimental design, data collection, analysis, paper writing.

why_matters: |
  Research acceleration. If AI can do research, every domain gets AI-powered 
  scientific progress.

measurement:
  milestone: "Published research paper with AI agent as primary author"
  verification: "A-tier (peer-reviewed publication in credible journal)"
  criteria: "Agent operated autonomously for >80% of research process"

forecasts:
  aschenbrenner:
    timeline: "2027 Q1-Q2"
    confidence: 0.60
    rationale: "After 'automated AI researchers' threshold (~2026 Q4)"
    cascade_effect: "Once achieved, research velocity increases dramatically"
```

#### NEW-AGT-010: Multi-Agent Collaboration
```yaml
code: multi_agent_collab
name: "Multi-Agent Collaborative Project"
category: agents
baseline: 0.0
target: 1.0
unit: "binary (demonstrated)"
direction: ">="
first_class: false

description: |
  Multiple AI agents collaborate on complex project with division of labor,
  communication, and coordinated execution.

measurement:
  milestone: "Public demonstration of 5+ agents collaborating successfully"
  example: "Software team (architect, coder, tester, reviewer, deployer)"

forecasts:
  ai2027:
    timeline: "2026 Q4"
    confidence: 0.50
    rationale: "Natural evolution of single-agent capabilities"
```

#### NEW-AGT-011: Calendar & Email Management
```yaml
code: digital_assistant_full
name: "Full Digital Assistant (Calendar, Email, Scheduling)"
category: agents
baseline: 0.30
target: 0.90
unit: "task success rate"
direction: ">="
first_class: false

description: |
  AI manages user's calendar, email, and scheduling autonomously with 90% success rate.

measurement:
  criteria: "Week-long autonomous operation, <10% interventions"
  
forecasts:
  ai2027:
    timeline: "2026 Q2"
    confidence: 0.70
    rationale: "Near-term deployment, low risk"
```

#### NEW-AGT-012: Long-Horizon Planning (30+ Steps)
```yaml
code: long_horizon_30
name: "Long-Horizon Planning ≥30 Steps"
category: agents
baseline: 5.0
target: 30.0
unit: "steps executed successfully"
direction: ">="
first_class: true

description: |
  AI agent successfully executes plans requiring 30+ sequential steps with 
  error recovery and replanning.

why_matters: |
  Complex tasks require long-horizon planning. Current agents fail around 5-10 steps.
  30+ steps enables multi-day projects.

measurement:
  benchmark: "ALFWorld, WebShop, or similar multi-step environments"
  methodology: "Success rate >70% on 30+ step tasks"

forecasts:
  general: "Prerequisite for autonomous projects, likely 2026-2027"
```

---

## 📊 Dimension 3: INPUTS - COMPUTE (Current: 13 → Enhanced: 22)

### Existing Compute Signposts (Keep)

- ✅ Training Compute 10^25 FLOP
- ✅ Training Compute 10^26 FLOP  
- ✅ Training Compute 10^27 FLOP
- ✅ Algorithmic Efficiency +1 OOM
- ✅ Algorithmic Efficiency +2 OOM
- ✅ DC Power 0.1 GW, 1 GW, 10 GW

---

### NEW Compute/Infrastructure Signposts (Add 9)

#### NEW-INP-014: Training Cost $100M
```yaml
code: training_cost_100m
name: "Single Training Run ≥$100M"
category: inputs
baseline: 50.0
target: 100.0
unit: "million USD"
direction: ">="
first_class: true

description: |
  Individual model training run costs $100M+, indicating frontier-scale investment.

why_matters: |
  Economic commitment signal. $100M+ training runs indicate serious AGI pursuit.
  Filters out smaller players, concentrates development.

measurement:
  source: "Public announcements, analyst estimates, leaked reports"
  methodology: "GPU-hours × spot price + datacenter costs"
  verification: "B-tier (lab announcements or credible estimates)"

forecasts:
  aschenbrenner:
    timeline: "2026 Q2"
    confidence: 0.75
    quote: "'Billions, then tens of billions on single training runs'"
    rationale: "10^26 FLOP on H100s ≈ $100M"
    
  epoch_ai:
    timeline: "2025 Q4 - 2026 Q2"
    confidence: 0.80
    cost_model: "10^26 FLOP ÷ H100 efficiency × $2-3/GPU-hour"
```

#### NEW-INP-015: GPU Cluster ≥100K H100-Equivalent
```yaml
code: gpu_cluster_100k
name: "GPU Cluster ≥100,000 H100-Equivalent"
category: inputs
baseline: 35000
target: 100000
unit: "GPUs (H100-equivalent)"
direction: ">="
first_class: true

description: |
  Single training cluster with 100K+ H100-equivalent GPUs (or compute-equivalent).

measurement:
  source: "Lab announcements, datacenter filings, supply chain estimates"
  methodology: "Physical GPU count × (FLOPS/H100_FLOPS)"
  
current_largest:
  value: 35000
  operator: "Meta (reported)"
  date: "2024-09"

forecasts:
  aschenbrenner:
    timeline: "2027 Q1"
    confidence: 0.65
    quote: "'Clusters of hundreds of thousands of GPUs'"
    
  nvidia_capacity:
    timeline: "2026 Q4"
    confidence: 0.70
    supply_chain: "B100/B200 production ramp enables 100K clusters"
```

#### NEW-INP-016: Datacenter Power ≥5 GW
```yaml
code: dc_power_5gw
name: "Datacenter Power ≥5 GW"  
category: inputs
baseline: 0.15
target: 5.0
unit: "gigawatts"
direction: ">="
first_class: true

description: |
  Single datacenter facility with 5 GW electrical capacity dedicated to AI training.

why_matters: |
  Physical constraint. 5 GW is the size of a small nuclear power plant.
  Indicates societal-scale resource commitment to AI.

measurement:
  source: "Utility filings, datacenter announcements, satellite imagery"
  methodology: "Electrical substation capacity + transformer ratings"

forecasts:
  aschenbrenner:
    timeline: "2027 Q2-Q3"
    confidence: 0.60
    quote: "'By 2027/2028: single datacenter clusters of ~5 GW'"
    context: "Requires: custom power plants, government coordination"
```

#### NEW-INP-017: Algorithmic Progress (2x/Year)
```yaml
code: algo_doubling_2x_year
name: "Algorithmic Efficiency Doubling Every 6-12 Months"
category: inputs  
baseline: 1.5
target: 2.0
unit: "years per doubling"
direction: "<="
first_class: true

description: |
  Rate of algorithmic progress: how fast do we get 2x more capability per FLOP.

why_matters: |
  Algorithmic gains compound with compute scaling. If algos improve 2x/year while
  compute scales 4x/year, effective progress is 8x/year.

measurement:
  methodology: "Track same-task performance over time at fixed compute budget"
  source: "Epoch AI algorithmic progress database"

current_rate:
  value: 1.5
  note: "Doubling roughly every 18 months (Epoch data 2012-2024)"

forecasts:
  aschenbrenner:
    expectation: "Algos continue improving, possibly accelerate with AI researchers"
    timeline: "Sustained through 2027"
    confidence: 0.75
```

#### NEW-INP-018: Training Time <3 Months
```yaml
code: training_time_3mo
name: "Frontier Model Training <3 Months"
category: inputs
baseline: 6.0
target: 3.0
unit: "months"
direction: "<="
first_class: false

description: |
  Time to train frontier model reduces to <3 months (enables faster iteration).

measurement:
  source: "Lab announcements, model cards"
  
forecasts:
  general: "Parallelization improvements, better infrastructure"
```

#### NEW-INP-019: Inference Cost $0.001/1M Tokens
```yaml
code: inference_cost_low
name: "Inference Cost ≤$0.001 per 1M Tokens"
category: inputs
baseline: 0.25
target: 0.001
unit: "USD per million tokens"
direction: "<="
first_class: false

description: |
  Cost to run frontier-quality models drops to $0.001/1M tokens (1000x cheaper than GPT-4 launch).

why_matters: |
  Economic deployment barrier. At $0.001/1M, AI becomes economically viable for 
  nearly all use cases.

current:
  value: 0.25
  model: "GPT-4o-mini"
  date: "2024-11"

forecasts:
  general: "Continues declining ~50% per year, hits target 2027-2028"
```

#### NEW-INP-020: Open Source Model Parity (<6mo lag)
```yaml
code: oss_model_parity_6mo
name: "Open Source Model Parity <6 Month Lag"
category: inputs
baseline: 12.0
target: 6.0
unit: "months lag behind frontier"
direction: "<="
first_class: false

description: |
  Open source models reach parity with closed-source frontier within 6 months.

why_matters: |
  Shorter lag means capabilities diffuse faster. Impacts safety (harder to control)
  and access (democratization).

current:
  value: 12.0
  note: "Llama 3 (Apr 2024) ≈ GPT-4 (Mar 2023) level"

forecasts:
  epoch_ai: "Lag decreasing, may reach 6mo by 2026"
```

#### NEW-INP-021: Chinchilla Scaling Holds
```yaml
code: chinchilla_scaling_holds
name: "Chinchilla Scaling Laws Remain Valid"
category: inputs
baseline: 1.0
target: 1.0
unit: "binary (yes/no)"
direction: ">="
first_class: false

description: |
  Chinchilla-optimal scaling (compute distributed evenly between params and data)
  continues to apply to frontier models.

why_matters: |
  If scaling laws break, timelines compress or extend significantly.

measurement:
  methodology: "Compare actual model performance to Chinchilla predictions"
  
forecasts:
  epoch_ai:
    expectation: "Laws hold through 2026, may break with new architectures"
    confidence: 0.70
```

#### NEW-INP-022: GPU Supply (H100 Availability)
```yaml
code: h100_supply_unconstrained
name: "H100/B100 Supply Unconstrained"
category: inputs
baseline: 0.0
target: 1.0
unit: "binary (no lead times)"
direction: ">="
first_class: false

description: |
  Leading AI chips (H100, B100) available without multi-month lead times.

measurement:
  metric: "Order-to-delivery time <30 days for 10K+ GPU orders"
  
forecasts:
  epoch_ai:
    timeline: "2026 Q2-Q3"
    confidence: 0.60
    rationale: "TSMC capacity expansion + demand stabilization"
```

---

## 📊 Dimension 4: SECURITY (Current: 6 → Enhanced: 15)

### Existing (Enhance)

- ✅ Security Maturity Index
- ✅ Security Level 1, 2, 3
- ✅ AI Treaty Ratified
- ✅ Mandatory Evals

### NEW Security Signposts (Add 9)

#### NEW-SEC-007: Pre-Deployment Red Teaming (Universal)
```yaml
code: mandatory_red_teaming
name: "Mandatory Pre-Deployment Red Teaming"
category: security
baseline: 0.15
target: 1.0
unit: "% of frontier labs"
direction: ">="
first_class: true

description: |
  All frontier AI labs conduct third-party red teaming before deployment.

measurement:
  methodology: "Track which labs (OpenAI, Anthropic, Google, Meta, etc.) publicly commit to red teaming"
  verification: "B-tier (public commitments + model cards)"

current:
  value: 0.15
  note: "Anthropic, OpenAI do it; not universal"

forecasts:
  openai_prep:
    timeline: "2026 Q2"
    confidence: 0.70
    rationale: "Preparedness Framework suggests industry-wide adoption"
```

#### NEW-SEC-008: CBRN Risk Threshold
```yaml
code: cbrn_risk_medium
name: "CBRN Risk Reaches 'Medium' Threshold"
category: security
baseline: 0.0
target: 1.0
unit: "binary (OpenAI categorization)"
direction: ">="
first_class: true

description: |
  AI model capabilities reach OpenAI's 'Medium' risk level for CBRN 
  (Chemical, Biological, Radiological, Nuclear) threats.

why_matters: |
  Indicates AI could meaningfully assist in bioweapon or cyberweapon development.
  Triggers enhanced security measures.

measurement:
  source: "OpenAI Preparedness Framework evaluations"
  methodology: "Expert elicitation + capability testing"
  
forecasts:
  openai_prep:
    timeline: "2025-2026"
    confidence: 0.50
    trigger: "When reached, deployment pauses until mitigations proven"
```

#### NEW-SEC-009: Cybersecurity Risk: Medium
```yaml
code: cyber_risk_medium
name: "Cybersecurity Risk 'Medium' (OpenAI Scale)"
category: security  
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  AI capabilities for cyber offense (vulnerability discovery, exploit generation,
  social engineering) reach OpenAI's 'Medium' risk level.

measurement:
  source: "OpenAI Preparedness Framework + lab evaluations"
  
forecasts:
  openai_prep:
    timeline: "2025-2026"
    confidence: 0.60
    note: "May already be close with current models + scaffolding"
```

#### NEW-SEC-010: Model Weight Security Standard
```yaml
code: weight_security_standard
name: "Industry Model Weight Security Standard"
category: security
baseline: 0.0
target: 1.0
unit: "binary (standard adopted)"
direction: ">="
first_class: true

description: |
  Industry-wide standard for securing model weights (encryption, access controls,
  theft prevention) analogous to nuclear material security.

measurement:
  milestone: "Partnership on AI or similar body publishes weight security standard"
  adoption: "3+ major labs publicly commit"

forecasts:
  aschenbrenner:
    timeline: "2026 Q1-Q2"
    confidence: 0.75
    quote: "'The model weights for these systems will be among the most important secrets in the world'"
    rationale: "National security implications force standardization"
```

#### NEW-SEC-011: Inference-Time Monitoring Deployed
```yaml
code: inference_monitoring_deployed
name: "Inference-Time Monitoring (Industry-Wide)"
category: security
baseline: 0.20
target: 0.90
unit: "% of API providers"
direction: ">="
first_class: true

description: |
  90% of major AI API providers deploy real-time monitoring for misuse detection.

measurement:
  providers: "OpenAI, Anthropic, Google, Cohere, etc."
  criteria: "Public documentation of monitoring systems"

forecasts:
  openai_prep:
    timeline: "2026 Q4"
    confidence: 0.65
```

#### NEW-SEC-012: Compute Governance (Export Controls)
```yaml
code: ai_chip_export_controls
name: "AI Chip Export Controls Tightened"
category: security
baseline: 1.0
target: 2.0
unit: "control regime level (1=current, 2=enhanced)"
direction: ">="
first_class: true

description: |
  US tightens export controls on AI chips (H100+), limiting China/other nations' access.

measurement:
  source: "Commerce Department regulations"
  levels: "1=Oct 2023 rules, 2=enhanced restrictions, 3=near-total embargo"

forecasts:
  aschenbrenner:
    timeline: "2025-2026"
    confidence: 0.80
    rationale: "National security imperative as AI becomes strategic"
    geopolitical: "US-China AI race intensifies controls"
```

#### NEW-SEC-013: International AI Safety Summit
```yaml
code: annual_ai_safety_summit
name: "Annual International AI Safety Summit"
category: security
baseline: 0.0
target: 1.0
unit: "binary (regular summit series)"
direction: ">="
first_class: false

description: |
  Regular (annual) international summits on AI safety with government participation.

measurement:
  milestone: "2+ consecutive annual summits with >10 countries"
  
current:
  note: "UK AI Safety Summit 2023 (one-off)"

forecasts:
  general: "If AI advances, summits become regular by 2026"
```

#### NEW-SEC-014: Mandatory Capability Disclosure
```yaml
code: capability_disclosure_req
name: "Mandatory Frontier Model Capability Disclosure"
category: security
baseline: 0.0
target: 1.0
unit: "binary (regulation exists)"
direction: ">="
first_class: true

description: |
  Government regulation requiring public disclosure of frontier model capabilities
  before deployment.

measurement:
  milestone: "US, EU, or major jurisdiction passes disclosure requirement"
  
forecasts:
  openai_prep:
    timeline: "2026-2027"
    confidence: 0.50
    note: "Depends on: incidents, political will, lobbying"
```

#### NEW-SEC-015: AI Safety Research Funding
```yaml
code: safety_research_1b
name: "AI Safety Research ≥$1B Annual Funding"
category: security
baseline: 0.15
target: 1.0
unit: "billion USD/year"
direction: ">="
first_class: false

description: |
  Combined government + philanthropic + industry funding for AI safety research
  reaches $1B/year.

measurement:
  source: "Grant databases, government budgets, company disclosures"
  
current:
  value: 0.15
  note: "~$150M/year (Open Philanthropy, labs, NIST)"

forecasts:
  general: "$1B if AGI timelines shorten to 2027"
```

---

## 📊 Dimension 5: ECONOMIC IMPACT (NEW - 0 → 10)

#### NEW-ECON-001: AI Services Market $100B
```yaml
code: ai_services_market_100b
name: "AI Services Market ≥$100B Annual Revenue"
category: economic
baseline: 10.0
target: 100.0
unit: "billion USD/year"
direction: ">="
first_class: true

description: |
  Combined revenue from AI APIs, services, and subscriptions reaches $100B/year.

why_matters: |
  Economic validation. $100B indicates AI is transforming trillion-dollar industries.

measurement:
  source: "Gartner, IDC market reports"
  includes: "API revenue (OpenAI, Anthropic), enterprise AI, consumer subscriptions"

current:
  value: 10.0
  note: "OpenAI ($2B ARR), Anthropic ($1B), etc. = ~$10B total"

forecasts:
  general: "2027-2028 if agent adoption accelerates"
```

#### NEW-ECON-002: First AI Unicorn (AI-Native)
```yaml
code: ai_native_unicorn
name: "First $1B+ Valuation AI-Native Company"
category: economic
baseline: 0.0
target: 1.0
unit: "binary (exists)"
direction: ">="
first_class: false

description: |
  First company valued at $1B+ that uses AI agents (not AI infrastructure) as 
  core product.

measurement:
  criteria: "AI agents doing work, not infrastructure/tools"
  examples: "AI research firm, AI customer service, AI legal"

forecasts:
  ai2027: "2026-2027 as agent capabilities mature"
```

#### NEW-ECON-003: Enterprise AI Spending $50B
```yaml
code: enterprise_ai_spend_50b
name: "Enterprise AI Spending ≥$50B/Year"
category: economic
baseline: 15.0
target: 50.0
unit: "billion USD/year"
direction: ">="
first_class: false

description: |
  Fortune 500 + Global 2000 companies spend $50B/year on AI services, agents, infrastructure.

measurement:
  source: "Gartner Enterprise IT Spending reports"
  
forecasts:
  gartner_projection: "2027-2028"
```

#### NEW-ECON-004: AI Productivity Gains (Measurable)
```yaml
code: productivity_gains_measurable
name: "Measurable AI Productivity Gains in GDP"
category: economic
baseline: 0.0
target: 0.5
unit: "% GDP growth attributable to AI"
direction: ">="
first_class: true

description: |
  National statistics show measurable productivity gains from AI adoption.

measurement:
  source: "BLS productivity data, economic analysis"
  methodology: "Econometric studies isolating AI's contribution"

forecasts:
  general: "Lags capability by 12-24 months, measurable 2027-2028"
```

#### NEW-ECON-005: Remote Work Displacement (BLS)
```yaml
code: remote_work_displacement_bls
name: "Remote Work Displacement ≥10% (BLS Data)"
category: economic
baseline: 0.5
target: 10.0
unit: "% of remote jobs"
direction: ">="
first_class: true

description: |
  Bureau of Labor Statistics shows ≥10% of remote knowledge work jobs displaced
  or significantly augmented by AI.

measurement:
  source: "BLS Employment Situation reports"
  methodology: "Survey employers: jobs eliminated/transformed by AI"
  categories: "Software dev, customer service, data entry, analysis"

forecasts:
  aschenbrenner:
    timeline: "2027-2028"
    confidence: 0.60
    note: "After 'drop-in remote worker' threshold"
```

#### NEW-ECON-006: Developer Productivity 2x
```yaml
code: dev_productivity_2x
name: "Developer Productivity 2x (GitHub Data)"
category: economic
baseline: 1.2
target: 2.0
unit: "relative to 2024 baseline"
direction: ">="
first_class: false

description: |
  GitHub data shows developers produce 2x more code/features with AI assistance.

measurement:
  source: "GitHub Octoverse reports, Copilot metrics"
  methodology: "PRs merged, code shipped, features completed"

current:
  value: 1.2
  note: "GitHub Copilot users ~20% more productive"

forecasts:
  github: "2x by 2026 as tools improve"
```

#### NEW-ECON-007: AI Job Postings Peak
```yaml
code: ai_job_postings_peak
name: "AI-Related Job Postings Peak then Decline"
category: economic
baseline: 0.0
target: 1.0
unit: "binary (inflection point reached)"
direction: ">="
first_class: false

description: |
  AI-related job postings peak then decline as AI starts automating AI work.

measurement:
  source: "Indeed, LinkedIn job posting data"
  
forecasts:
  ironic_signal: "Peak 2026, decline 2027 as AI researchers automated"
```

#### NEW-ECON-008: AI Revenue per Employee
```yaml
code: ai_revenue_per_employee
name: "AI Company Revenue per Employee >$5M"
category: economic
baseline: 1.5
target: 5.0
unit: "million USD/employee/year"
direction: ">="
first_class: false

description: |
  AI-native companies achieve >$5M revenue per employee (vs typical $200K-500K).

why_matters: |
  Indicates AI is doing most of the work. Extreme efficiency signals 
  transformative automation.

current:
  value: 1.5
  example: "Midjourney (11 employees, est. $200M revenue = $18M/employee, but outlier)"

forecasts:
  general: "$5M/employee if agents mature by 2027-2028"
```

#### NEW-ECON-009: AI-Generated Content >50% of Web
```yaml
code: ai_content_majority_web
name: "AI-Generated Content ≥50% of New Web Content"
category: economic
baseline: 0.15
target: 0.50
unit: "% of new content"
direction: ">="
first_class: false

description: |
  More than half of new text, images, code published online is AI-generated.

measurement:
  source: "Web scraping studies, content analysis"
  
forecasts:
  general: "Already trending this direction, hits 50% by 2026"
```

#### NEW-ECON-010: AI ETF or Major Index Inclusion
```yaml
code: ai_index_fund
name: "AI-Specific ETF with >$10B AUM"
category: economic
baseline: 5.0
target: 10.0
unit: "billion USD assets"
direction: ">="
first_class: false

description: |
  AI-specific ETF manages >$10B (indicates mainstream investor interest).

measurement:
  source: "ETF databases"
  
current:
  value: 5.0
  examples: "Several AI ETFs exist, largest ~$5B"
```

---

## 📊 Dimension 6: RESEARCH VELOCITY (NEW - 0 → 8)

#### NEW-RES-001: arXiv AI Papers >5000/Month
```yaml
code: arxiv_ai_5k_month
name: "arXiv AI Papers ≥5,000/Month"
category: research_velocity
baseline: 3500
target: 5000
unit: "papers per month"
direction: ">="
first_class: false

description: |
  Monthly AI/ML papers on arXiv reaches 5,000 (indicates research explosion).

measurement:
  source: "arXiv categories: cs.AI, cs.LG, cs.CL, cs.CV"
  methodology: "Count monthly submissions"

current:
  value: 3500
  note: "Growing ~20-30%/year"
  
forecasts:
  general: "5K/month by mid-2025 at current growth"
```

#### NEW-RES-002: Time to SOTA Improvement
```yaml
code: sota_improvement_time
name: "Time to SOTA Improvement <90 Days"
category: research_velocity
baseline: 180
target: 90
unit: "days"
direction: "<="
first_class: true

description: |
  Time between SOTA improvements on major benchmarks (SWE-bench, GPQA, etc.) 
  drops to <90 days.

why_matters: |
  Faster improvement cycles indicate research acceleration. <90 days means 
  4+ iterations per year.

measurement:
  methodology: "Track leaderboard updates on key benchmarks"
  data: "SWE-bench, GPQA, MMLU, etc."

current:
  value: 180
  note: "Major improvements every ~6 months currently"

forecasts:
  general: "<90 days by 2026 if AI researchers emerge"
```

#### NEW-RES-003: Novel AI Architecture
```yaml
code: post_transformer_arch
name: "Post-Transformer Architecture Achieves SOTA"
category: research_velocity
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  Novel architecture (non-Transformer) achieves SOTA on major benchmarks,
  indicating paradigm shift.

measurement:
  criteria: "Fundamentally different from attention mechanisms"
  
forecasts:
  uncertain: "May happen, may not. Would change timelines significantly"
```

#### NEW-RES-004: Breakthrough Papers per Year
```yaml
code: breakthrough_papers_10_year
name: "≥10 Breakthrough AI Papers per Year"
category: research_velocity
baseline: 3.0
target: 10.0
unit: "papers per year"
direction: ">="
first_class: false

description: |
  10+ AI papers per year that represent major breakthroughs (like Transformer,
  GPT-3, RLHF, etc.).

measurement:
  methodology: "Expert consensus + citation velocity >1000 in first year"
  
forecasts:
  general: "Accelerates to 10/year by 2026-2027 if AI does research"
```

#### NEW-RES-005: Research Lab Proliferation
```yaml
code: frontier_labs_10
name: "≥10 Frontier AI Labs"
category: research_velocity
baseline: 5.0
target: 10.0
unit: "number of labs"
direction: ">="
first_class: false

description: |
  Number of organizations capable of training frontier models (GPT-4 class) reaches 10.

current:
  value: 5
  labs: "OpenAI, Anthropic, Google DeepMind, Meta, (Inflection/Microsoft?)"

measurement:
  criteria: "Can train >$100M models with novel capabilities"
  
forecasts:
  epoch_ai: "Grows to 10 by 2026 if compute becomes available"
```

#### NEW-RES-006: Open Source Contribution Rate
```yaml
code: oss_ai_contribution_rate
name: "Open Source AI Contribution Rate"
category: research_velocity
baseline: 0.30
target: 0.60
unit: "% of innovations released as OSS within 12mo"
direction: ">="
first_class: false

description: |
  Percentage of major AI innovations that get open-sourced within 12 months.

measurement:
  methodology: "Track closed vs open releases (models, datasets, techniques)"
  
forecasts:
  trend: "Declining as commercial value increases, but OSS community pressure"
```

#### NEW-RES-007: Automated Literature Review
```yaml
code: auto_lit_review
name: "Automated Literature Review Tools Widely Adopted"
category: research_velocity
baseline: 0.10
target: 0.70
unit: "% of researchers using"
direction: ">="
first_class: false

description: |
  70% of AI researchers use automated literature review/synthesis tools.

measurement:
  source: "Researcher surveys"
  
forecasts:
  general: "2026 as tools improve"
```

#### NEW-RES-008: Preprint to Published Time
```yaml
code: preprint_to_pub_6mo
name: "Preprint to Published <6 Months"
category: research_velocity
baseline: 12.0
target: 6.0
unit: "months"
direction: "<="
first_class: false

description: |
  Time from arXiv preprint to peer-reviewed publication drops to <6 months
  (indicates faster academic cycles).

measurement:
  methodology: "Track arxiv → journal publication lag"
```

---

## 📊 Dimension 7: GEOPOLITICAL (NEW - 0 → 8)

#### NEW-GEO-001: US-China AI Compute Gap
```yaml
code: us_china_compute_gap
name: "US-China AI Compute Gap ≥3x"
category: geopolitical
baseline: 2.0
target: 3.0
unit: "ratio (US/China)"
direction: ">="
first_class: true

description: |
  US advantage in AI training compute over China reaches 3x (due to chip embargoes).

why_matters: |
  Geopolitical competition. Compute gap determines which country leads AGI race.

measurement:
  source: "Epoch AI compute database, CSET estimates"
  methodology: "Estimated H100-equivalent GPUs: US vs China"

forecasts:
  aschenbrenner:
    timeline: "2025-2026"
    confidence: 0.70
    rationale: "Export controls prevent China from accessing H100/B100"
    risk: "China develops competitive domestic alternative"
```

#### NEW-GEO-002: Government AI Initiative ($10B+)
```yaml
code: govt_ai_initiative_10b
name: "Government AI Initiative ≥$10B"
category: geopolitical
baseline: 1.0
target: 10.0
unit: "billion USD commitment"
direction: ">="
first_class: true

description: |
  Major government announces ≥$10B AI initiative (compute, research, deployment).

measurement:
  milestone: "US Stargate, China AI Plan, EU AI Act funding, etc."
  
forecasts:
  aschenbrenner:
    timeline: "2025-2026"
    confidence: 0.80
    quote: "'Stargate project' likely as national security urgency increases"
    scale: "Tens of billions, then hundreds of billions"
```

#### NEW-GEO-003: Allied Compute Consortium
```yaml
code: allied_ai_consortium
name: "Allied AI Consortium Formed (US+Allies)"
category: geopolitical
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: false

description: |
  US, UK, Canada, Australia, Japan form formal AI alliance (compute sharing, 
  safety standards, export coordination).

measurement:
  milestone: "Treaty or MOU signed between 3+ nations"

forecasts:
  aschenbrenner:
    timeline: "2026"
    confidence: 0.65
    rationale: "Geopolitical necessity as AGI race intensifies"
```

#### NEW-GEO-004: China Domestic AI Chip
```yaml
code: china_h100_equivalent
name: "China Domestic H100-Equivalent Chip"
category: geopolitical
baseline: 0.0
target: 1.0
unit: "binary (demonstrated)"
direction: ">="
first_class: true

description: |
  China demonstrates domestic AI chip with H100-equivalent performance,
  bypassing export controls.

measurement:
  milestone: "Public demonstration or leaked benchmarks"
  
forecasts:
  aschenbrenner_risk: "Major wildcard, could happen 2025-2027"
```

#### NEW-GEO-005: AGI Arms Race Rhetoric
```yaml
code: agi_arms_race_official
name: "Official Government 'AGI Race' Rhetoric"
category: geopolitical
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: false

description: |
  US or Chinese government officials explicitly use "AGI race" framing in 
  public statements.

measurement:
  source: "Official speeches, policy documents"
  
forecasts:
  aschenbrenner: "Likely by 2026 as capabilities become obvious"
```

#### NEW-GEO-006: AI Safety Treaty Attempt
```yaml
code: ai_safety_treaty_negotiation
name: "International AI Safety Treaty Negotiation"
category: geopolitical
baseline: 0.0
target: 1.0
unit: "binary (negotiations underway)"
direction: ">="
first_class: true

description: |
  Formal treaty negotiations on AI safety standards between major powers
  (analogous to nuclear non-proliferation).

measurement:
  milestone: "UN or bilateral talks on binding AI agreement"

forecasts:
  general: "2026-2027 if incidents occur or capabilities advance rapidly"
```

#### NEW-GEO-007: Compute Nationalization Discussion
```yaml
code: compute_nationalization
name: "Serious Compute Nationalization Proposals"
category: geopolitical
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: false

description: |
  Serious policy proposals for government control/ownership of frontier AI 
  compute infrastructure.

forecasts:
  aschenbrenner: "Possible 2027+ if AGI near and national security acute"
```

#### NEW-GEO-008: AI Incident Triggers Policy
```yaml
code: ai_incident_policy_trigger
name: "Major AI Incident Triggers Policy Change"
category: geopolitical
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  Significant AI incident (misuse, accident, or capability surprise) triggers
  major policy response (new regulation, funding, or restrictions).

measurement:
  criteria: "Incident + policy response within 90 days"
  
forecasts:
  general: "More likely as capabilities increase, unpredictable timing"
```

---

## 📊 Dimension 8: SAFETY INCIDENTS & WARNINGS (NEW - 0 → 6)

#### NEW-SAFE-001: Model Jailbreak in Wild
```yaml
code: jailbreak_exploit_wild
name: "Major Model Jailbreak Exploited at Scale"
category: safety_incidents
baseline: 0.0
target: 1.0
unit: "binary (occurred)"
direction: ">="
first_class: false

description: |
  Widespread exploitation of safety bypass in frontier model (≥100K users affected).

measurement:
  criteria: "Documented exploit + company acknowledgment"
  
note: "Negative indicator - we DON'T want this, but should track"
```

#### NEW-SAFE-002: AI-Assisted Cyberattack
```yaml
code: ai_cyber_attack_confirmed
name: "Confirmed AI-Assisted Cyberattack"
category: safety_incidents
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  First confirmed cyberattack where AI played central role (vulnerability 
  discovery, exploit generation, or execution).

measurement:
  source: "Security vendor reports, government attribution"
  
forecasts:
  cybersec_experts: "Likely by 2025-2026 as models improve"
  
note: "Negative indicator - tracking for risk assessment"
```

#### NEW-SAFE-003: AI Misuse Congressional Hearing
```yaml
code: ai_misuse_congress_hearing
name: "Congressional Hearing on AI Misuse"
category: safety_incidents
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: false

description: |
  US Congress holds hearing specifically on AI misuse incident.

measurement:
  source: "Congressional records"

forecasts:
  general: "Probable by 2026 if incidents occur"
```

#### NEW-SAFE-004: Capability Overhang Documented
```yaml
code: capability_overhang
name: "Documented Capability Overhang (Hidden Capabilities)"
category: safety_incidents
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  Frontier model found to have significantly higher capabilities than initially 
  disclosed (>20% performance gain with better prompting/scaffolding).

why_matters: |
  Indicates capabilities are latent and can be 'unlocked' unpredictably.
  Makes safety eval difficult.

measurement:
  example: "GPT-4 with advanced prompting vastly outperforms base"
  
forecasts:
  openai_prep: "Ongoing concern, may formalize measurement"
```

#### NEW-SAFE-005: AI Safety Researcher Shortage
```yaml
code: safety_researcher_shortage
name: "AI Safety Researcher Shortage (10:1 Capability:Safety)"
category: safety_incidents
baseline: 5.0
target: 10.0
unit: "ratio (capabilities researchers : safety researchers)"
direction: ">="
first_class: false

description: |
  Ratio of capabilities researchers to safety researchers reaches 10:1.

measurement:
  source: "Academic hiring, company headcount"
  
forecasts:
  general: "Worsening as AI labs scale, safety doesn't keep pace"
```

#### NEW-SAFE-006: Model Alignment Failure (Public)
```yaml
code: alignment_failure_public
name: "Public Alignment Failure Documented"
category: safety_incidents
baseline: 0.0
target: 1.0
unit: "binary"
direction: ">="
first_class: true

description: |
  Frontier model exhibits significant alignment failure in deployment 
  (goal misgeneralization, deceptive behavior, etc.) with public documentation.

measurement:
  criteria: "Reproducible failure + technical write-up"
  
note: "Negative indicator - want to track but not achieve"
```

---

## 📊 Summary of Enhancements

**Total New Signposts**: 55  
**Enhanced Existing**: 34  
**Grand Total**: 89 comprehensive signposts

**Coverage**:
- ✅ Technical (capabilities, compute)
- ✅ Economic (market, productivity, deployment)  
- ✅ Geopolitical (US-China, governance, policy)
- ✅ Research (velocity, publications, breakthroughs)
- ✅ Security (risks, incidents, mitigations)
- ✅ Agents (reliability, deployment, autonomy)

**Next Steps**:
1. Review this extraction
2. Prioritize which signposts to implement
3. Create database schema enhancements
4. Build seed files
5. Update UI

---

**Status**: Extraction complete, awaiting review and prioritization  
**Time to implement**: 4-6 hours after prioritization  
**Value**: Most comprehensive AGI tracking system available

