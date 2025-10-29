# Agent Work Coordination - Merge Strategy

**Date**: 2025-10-29  
**Purpose**: Prevent merge conflicts between parallel agent work

## Agent Assignments Overview

| Agent | Focus | Branch | ETA |
|-------|-------|--------|-----|
| **Agent 1 (DevOps)** | CI/CD, deployment automation | `feature/devops-automation` | TBD |
| **Agent 2 (Features)** | Phase 3 features + code audits | `feature/phase-3-features` | TBD |
| **Agent 3 (AI/ML)** | Phase 4 RAG + architecture audits | `feature/phase-4-rag` | TBD |
| **Agent 4 (Docs)** | Documentation site + guides | `feature/docs-site` | In Progress |

---

## File Conflict Matrix

### 🔴 HIGH CONFLICT RISK - Requires Coordination

#### `README.md`
**All agents will modify this file.**

**Proposed sections**:
```markdown
# AGI Signpost Tracker

[Existing intro - DON'T MODIFY]

## Badges [Agent 1 - DevOps]
[![CI](https://github.com/...)...

## Documentation [Agent 4 - Docs]
- 📖 [Full Documentation](https://docs.agi-tracker.vercel.app)
- 📚 [User Guides](https://docs.agi-tracker.vercel.app/docs/guides)

## Features [Agent 2 + Agent 3]
### Phase 3 Features [Agent 2]
- Signpost deep-dive pages
- Custom preset builder
...

### Phase 4 Features [Agent 3]
- RAG chatbot
- Scenario explorer
...

[Rest of README - existing content]
```

**Resolution**: Each agent modifies ONLY their designated section. Agent 4 (me) creates section markers now.

#### `services/etl/app/main.py`
**Agents 2 and 3 will both add endpoints.**

**Resolution**:
1. **Agent 2 merges first** (Phase 3 endpoints)
2. **Agent 3 rebases** on Agent 2's branch before merging
3. Both agents: Add endpoints in alphabetical order within section
4. Use clear comments to delineate sections:
   ```python
   # ===== Phase 3 Endpoints (Agent 2) =====
   @app.get("/v1/signposts/by-code/{code}/full")
   ...
   
   # ===== Phase 4 Endpoints (Agent 3) =====
   @app.post("/v1/chat")
   ...
   ```

#### `CONTRIBUTING.md`
**Agents 1 and 4 will modify.**

**Resolution**:
- **Agent 1**: Add "Development Setup" section with pre-commit hooks, CI/CD
- **Agent 4**: Add "Pull Request Examples" section
- Coordinate on structure:
  ```markdown
  # Contributing Guide
  
  ## Development Setup [Agent 1]
  - Pre-commit hooks
  - CI/CD pipeline
  
  ## Code Standards [Agent 4]
  - TypeScript/Python standards
  - Testing requirements
  
  ## Pull Request Process [Agent 4]
  - 3+ example PR walkthroughs
  
  ## CI/CD Workflow [Agent 1]
  - How pipelines work
  - Deployment process
  ```

---

### 🟡 MEDIUM CONFLICT RISK - Duplicate Work

#### User Guides in `docs/guides/`

**Problem**: Agents 2 and 3 will create guides that Agent 4 already created.

| Guide | Agent 2 Creates | Agent 3 Creates | Agent 4 Created (Docusaurus) |
|-------|----------------|----------------|------------------------------|
| signpost-deep-dives.md | ✓ | | ✓ (in docs-site/) |
| custom-presets.md | ✓ | | ✓ (in docs-site/) |
| chatbot-usage.md | | ✓ | ✓ (as rag-chatbot.md in docs-site/) |
| scenario-explorer.md | | ✓ | ✓ (in docs-site/) |

**Resolution**:
1. **Agent 4's guides are comprehensive** (already done, in Docusaurus site)
2. **Agents 2 & 3**: Skip creating duplicate guides in docs/guides/
3. **Instead**: Update Agent 4's Docusaurus guides with:
   - **Agent 2**: Technical implementation details for Phase 3 features
   - **Agent 3**: Technical implementation details for Phase 4 features
4. **Location**: All guides live in `docs-site/docs/guides/` (not root `docs/guides/`)

#### Architecture/Audit Docs

**Agent 2 creating**:
- docs/frontend-code-audit.md
- docs/backend-code-audit.md
- docs/database-schema-audit.md

**Agent 3 creating**:
- docs/architecture-review.md
- docs/security-architecture-review.md
- docs/llm-architecture-review.md
- docs/frontend-architecture-review.md
- docs/diagrams/

**Agent 1 creating**:
- docs/dependency-audit.md
- docs/ci-cd.md

**Resolution**: No conflict - different files. But **Agent 4 should**:
- Create `docs-site/docs/architecture/` section
- Move all audit docs there after agents complete them
- Integrate into Docusaurus navigation

---

### 🟢 LOW CONFLICT RISK - Separate Files

#### GitHub Actions Workflows
**Agent 1 creates**:
- .github/workflows/deploy.yml (new)
- .github/workflows/e2e-nightly.yml (new)
- .github/workflows/dependencies.yml (new)
- .github/workflows/ci.yml (may enhance existing)

**Resolution**: No conflict. Agent 1 owns all workflow files.

#### Frontend Pages
**Agent 2 creates**:
- apps/web/app/signposts/[code]/page.tsx (new)
- apps/web/app/presets/custom/page.tsx (new)

**Agent 3 creates**:
- apps/web/app/chat/page.tsx (new)
- apps/web/app/scenarios/page.tsx (new)
- apps/web/app/analytics/page.tsx (new)

**Resolution**: Different files, no conflict.

#### Backend Services
**Agent 3 creates**:
- services/etl/app/services/embedding_service.py (new)
- services/etl/app/services/rag_chatbot.py (new)

**Resolution**: New files, no conflict.

---

## Merge Order Strategy

**Recommended sequence**:

```
1. Agent 4 (Docs) - Foundation documentation
   └─→ Provides docs for other agents to reference
   
2. Agent 1 (DevOps) - CI/CD infrastructure
   └─→ Enables automated testing for Agents 2 & 3
   
3. Agent 2 (Phase 3) - Features + code audits
   └─→ Establishes new endpoints and patterns
   
4. Agent 3 (Phase 4) - RAG + architecture audits
   └─→ Builds on Phase 3 endpoints, adds AI features
```

**Rationale**:
- Docs first → others can reference while building
- DevOps second → testing infrastructure ready
- Phase 3 before Phase 4 → logical feature progression
- Agent 3 rebases on Agent 2's main.py changes

---

## Coordination Checklist

### Before Starting Work

- [ ] Read this coordination document
- [ ] Check which files you'll modify
- [ ] Note any HIGH CONFLICT files
- [ ] Coordinate with other agents on those files

### During Work

- [ ] Add clear section comments in shared files
- [ ] Update this document if you change scope
- [ ] Don't modify files outside your assignment
- [ ] Use descriptive commit messages with agent tag: `[Agent-1] Add CI/CD pipeline`

### Before Opening PR

- [ ] Check if any HIGH CONFLICT files were modified
- [ ] Verify you only modified your designated sections
- [ ] Test that your changes don't break existing features
- [ ] Update DOCUMENTATION_SPRINT_COMPLETE.md with your additions

### PR Review

- [ ] Tag other agents if your changes affect their work
- [ ] Wait for Agent 4 to merge first (if applicable)
- [ ] Rebase on main before merging
- [ ] Run full test suite after merge

---

## Communication Protocol

### When Conflicts Arise

1. **Comment in this file** with conflict details
2. **Tag affected agents** in GitHub issue
3. **Propose resolution** (who owns what section)
4. **Wait for agreement** before proceeding

### Conflict Resolution Template

```markdown
## Conflict: [File Name]

**Agents involved**: Agent X, Agent Y
**Issue**: Both need to modify [section]
**Proposed resolution**: 
- Agent X: Modify lines 1-50
- Agent Y: Modify lines 51-100
**Agreement**: [ ] Agent X agrees  [ ] Agent Y agrees
```

---

## Specific Coordination Notes

### README.md Updates

**Agent 1 (DevOps)** - Add AFTER line 3:
```markdown
[![CI](https://github.com/hankthevc/AGITracker/workflows/CI/badge.svg)](...)
[![Deploy](https://github.com/hankthevc/AGITracker/workflows/Deploy/badge.svg)](...)
```

**Agent 4 (Docs)** - Add AFTER "Vision & Approach" section (~line 8):
```markdown
## 📖 Documentation

Complete documentation available at **[docs.agi-tracker.vercel.app](https://docs.agi-tracker.vercel.app)**

Quick links:
- [Installation Guide](https://docs.agi-tracker.vercel.app/docs/getting-started/installation)
- [User Guides](https://docs.agi-tracker.vercel.app/docs/guides/events-feed)
- [API Reference](https://docs.agi-tracker.vercel.app/docs/api/quick-reference)
```

**Agent 2 (Features)** - Add new section BEFORE "Roadmap" section:
```markdown
## Phase 3 Features (NEW)

- **Signpost Deep-Dives**: Educational pages for each of 27 milestones
- **Custom Preset Builder**: Create your own category weights
- **Historical Charts**: Track index progress over time
- **Advanced Search**: Enhanced search with filters
- **Export Enhancements**: PDF, Excel, iCal formats
```

**Agent 3 (AI/ML)** - Add AFTER Agent 2's section:
```markdown
## Phase 4 Features (NEW)

- **RAG Chatbot**: Ask questions about AGI progress with citations
- **Scenario Explorer**: "What-if" simulator for hypothetical progress
- **Vector Search**: Semantic similarity search across all content
- **Advanced Analytics**: Capability-safety heatmaps, forecast accuracy
```

### main.py Endpoint Organization

**Current structure** (don't modify):
```python
# Lines 1-500: Imports, config, app setup
# Lines 501-1000: Public endpoints (v1/index, v1/events, etc.)
# Lines 1001-1500: Admin endpoints (v1/admin/*)
# Lines 1501-end: Health checks, utilities
```

**Agent 2 additions** (insert at line ~1000, before admin section):
```python
# ===== Phase 3 Endpoints (Signpost Deep-Dives, Custom Presets) =====
@app.get("/v1/signposts/by-code/{code}/full")
...
@app.get("/v1/index/custom")
...
@app.get("/v1/index/history")
...
```

**Agent 3 additions** (insert at line ~1100, after Agent 2):
```python
# ===== Phase 4 Endpoints (RAG, Vector Search, Scenarios) =====
@app.post("/v1/chat")
...
@app.get("/v1/search/semantic")
...
@app.post("/v1/scenarios/calculate")
...
```

---

## Documentation Location Strategy

### Current State

- **Root `/docs/`**: Legacy markdown files, AI_CONTEXT.md, archive/
- **`/docs-site/`**: Docusaurus site (Agent 4's work)

### Moving Forward

**Decision**: Migrate all documentation to Docusaurus

**Agent 1, 2, 3 deliverables**:
1. Initially create docs in `/docs/` as specified in prompts
2. **Agent 4 will migrate** to `/docs-site/docs/` after review
3. Root `/docs/` becomes deprecated (except AI_CONTEXT.md)

**Structure**:
```
docs-site/docs/
├── architecture/          [Agent 2 & 3 audits go here]
│   ├── overview.md
│   ├── frontend.md
│   ├── backend.md
│   ├── database.md
│   ├── code-audit.md      [Agent 2's audits]
│   └── system-review.md   [Agent 3's audits]
├── guides/                [User guides - Agent 4 already created]
│   └── [8 guides complete]
├── api/                   [API docs]
│   └── quick-reference.md [Agent 4 complete]
├── deployment/            [Agent 1's deployment docs]
│   ├── ci-cd.md
│   └── [other deployment guides]
└── contributing/
    └── [CONTRIBUTING.md content]
```

---

## Success Criteria

All agents complete work with:
- ✅ Zero merge conflicts
- ✅ All tests passing
- ✅ Documentation updated
- ✅ Changes reviewed by at least one other agent
- ✅ README properly updated with all sections

---

## Contact & Questions

If you have questions about coordination:
1. Update this document with your question
2. Tag other affected agents
3. Wait for response before proceeding

**Better to over-communicate than to create conflicts!**

---

**Last Updated**: 2025-10-29 by Agent 4 (Docs)  
**Status**: Active Coordination

