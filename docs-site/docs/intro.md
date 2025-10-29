# Welcome to AGI Signpost Tracker

## What is the AGI Signpost Tracker?

The **AGI Signpost Tracker** is an evidence-first dashboard that tracks proximity to Artificial General Intelligence (AGI) through measurable, verifiable signposts across four key domains:

- **Capabilities**: Benchmark performance (SWE-bench, OSWorld, WebArena, GPQA)
- **Agents**: Real-world deployment and economic impact
- **Inputs**: Training compute, algorithmic efficiency, datacenter capacity
- **Security**: Model weight security, deployment controls, governance maturity

## Why This Project Exists

Unlike prediction markets or expert surveys, we anchor exclusively on **verifiable evidence**:

✅ **A-tier (Primary)**: Peer-reviewed papers, official leaderboards, reproducible evals  
✅ **B-tier (Official Lab)**: Lab announcements, model cards (provisional until A-tier corroboration)  
⚠️ **C-tier (Reputable Press)**: Reuters, AP, Bloomberg (displayed as "If true" analysis)  
⛔ **D-tier (Social)**: Twitter, Reddit (opt-in only, never moves gauges)

Our **harmonic mean aggregation** prevents cherry-picking—progress requires advancement across *all* domains.

## Key Features

- 📊 **Real-time Dashboard**: Composite AGI proximity gauge with category breakdowns
- 📈 **Evidence Timeline**: Track significant events with AI-generated impact analysis
- 🔍 **Signpost Deep-Dives**: Detailed explanations of each milestone and why it matters
- 🎯 **Expert Predictions**: Compare actual progress vs forecasts from AI2027, Aschenbrenner, Metaculus
- 🔐 **Transparency**: All data CC BY 4.0, open methodology, source credibility tracking
- ⚡ **Public API**: Read-only endpoints for researchers and developers

## Getting Started

Choose your path:

<div className="button-grid">
  <a className="button button--primary button--lg" href="/docs/getting-started/installation">
    🚀 Quick Start (10 min)
  </a>
  <a className="button button--secondary button--lg" href="/docs/guides/events-feed">
    📖 User Guides
  </a>
  <a className="button button--secondary button--lg" href="/docs/api/overview">
    🔌 API Reference
  </a>
</div>

## Live Dashboard

Visit the live dashboard at **[agi-tracker.vercel.app](https://agi-tracker.vercel.app)**

## Core Principles

### Evidence-First
Only peer-reviewed papers (A-tier) and official lab announcements (B-tier) move gauges. C/D tier shown for context but never affect scores.

### Reproducible
All scoring logic is versioned, tested, and documented. Harmonic mean aggregation ensures no single category dominates.

### Neutral
No assumptions about timelines or outcomes. Track observable metrics without advocacy.

### Transparent
Open methodology, public API (CC BY 4.0), changelog for all updates.

## Who Is This For?

- **Researchers**: Track AI capabilities progress with verifiable evidence
- **Policymakers**: Make informed decisions based on measurable metrics
- **Developers**: Build on our public API for custom analyses
- **General Public**: Stay informed about AGI proximity with transparent methodology

## Architecture Overview

```
┌─────────────────┐
│   Next.js Web   │  ← User Interface
└────────┬────────┘
         │
    ┌────▼─────┐
    │ FastAPI  │  ← Public API
    └────┬─────┘
         │
┌────────▼────────┐
│   PostgreSQL    │  ← Data Storage
│   + pgvector    │
└─────────────────┘
         ▲
         │
┌────────┴────────┐
│  Celery + Redis │  ← ETL Pipeline
└─────────────────┘
```

## License

- **Code**: MIT License
- **Public JSON Feed**: CC BY 4.0
- **Data**: Sources retain their original licenses

## Support

- 📖 **Documentation**: You're reading it!
- 💬 **GitHub Discussions**: Ask questions and share feedback
- 🐛 **Issues**: Report bugs on GitHub
- 📧 **Email**: contact@agi-tracker.dev

---

Ready to dive in? Head to the [Installation Guide](/docs/getting-started/installation) to get started!
