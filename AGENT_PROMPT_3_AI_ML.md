# Mission: Phase 4 RAG/AI Features + System Architecture Audit

You are an AI/ML engineer building Phase 4 intelligence features AND auditing the entire system architecture. Sprint 8-10 are done. Your job: ship RAG chatbot, vector search, AND surface all architectural issues.

## Context
- Project: AGI Signpost Tracker
- Recent work: 8,494 lines added in Sprints 8-10
- Database: PostgreSQL with pgvector extension (already installed)
- Project path: /Users/HenryAppel/AI Doomsday Tracker
- Read FIRST: README.md, ROADMAP.md, docs/AI_CONTEXT.md

## What's Already Done
- ✅ pgvector extension installed in database
- ✅ Multi-model consensus (GPT-4o-mini + Claude) from Sprint 7
- ✅ LLM budget tracking (Sprint 7)
- ✅ Event analysis with confidence scoring

## Phase 4 Features to Build

### 1. Vector Embeddings Foundation

**Goal**: Populate pgvector embeddings for all content

#### A. Create Embedding Service
File: services/etl/app/services/embedding_service.py

Features:
- Use OpenAI text-embedding-3-small (cheaper, faster)
- Batch processing (up to 2048 texts per request)
- Cost tracking (log spend)
- Caching in Redis (24h TTL)
- Retry logic with exponential backoff

#### B. Populate Embeddings
- Add embedding column to events table (vector(1536))
- Add embedding column to signposts table (vector(1536))
- Create Celery task: populate_embeddings()
- Embed: event title + summary + analysis
- Embed: signpost name + description + why_matters

#### C. Similarity Search Endpoints
- GET /v1/search/semantic?query=text&limit=10
- Uses pgvector's <-> operator (cosine distance)
- Returns similar events + signposts
- Hybrid search: Combine semantic + full-text

### 2. RAG Chatbot (/chat)

**Goal**: Conversational AI that answers questions with citations

#### A. LangChain Integration
Create: services/etl/app/services/rag_chatbot.py

**Features**:
- Conversational retrieval chain
- Vector store: pgvector
- LLM: GPT-4o-mini (cost-effective)
- Memory: Last 5 messages in session
- Streaming responses

**RAG Pipeline**:
1. User asks question
2. Embed question → Search similar events/signposts
3. Construct prompt with retrieved context
4. LLM generates answer
5. Extract citations from context
6. Return answer + sources

#### B. Chat API
- POST /v1/chat (streaming SSE)
- POST /v1/chat/history (session management)
- GET /v1/chat/suggestions (suggested questions)

Request:
```json
{
  "message": "What's the current progress on SWE-bench?",
  "session_id": "uuid",
  "stream": true
}
```

Response (streaming):
```
data: {"type": "token", "content": "Based"}
data: {"type": "token", "content": " on"}
data: {"type": "sources", "sources": [...]}
data: {"type": "done"}
```

#### C. Frontend Chat UI
Create: apps/web/app/chat/page.tsx

**Features**:
- Message list (user/assistant bubbles)
- Input box with send button
- Streaming responses (typewriter effect)
- Source citations as expandable cards
- Copy message button
- Clear chat button
- Suggested starter questions
- Loading indicator
- Error handling

**UX Details**:
- Auto-scroll to bottom
- Markdown rendering in responses
- Code syntax highlighting
- Keyboard shortcuts (Enter to send, Shift+Enter for newline)

#### D. Out-of-Scope Detection
- If question is not about AGI/AI progress → polite rejection
- Examples: "What's the weather?" → "I can only answer questions about AGI progress"
- Use simple keyword filtering OR prompt engineering

### 3. Scenario Explorer (/scenarios)

**Goal**: "What-if" simulator for hypothetical progress

Create: apps/web/app/scenarios/page.tsx

**Features**:
- Grid of all signposts with sliders
- Adjust hypothetical progress (0-100%)
- Real-time index calculation
- Show impact on overall AGI proximity
- Compare scenarios side-by-side
- Save scenarios to localStorage
- Export scenario as JSON
- Share via URL (encode in query params)

**Backend Support**:
- POST /v1/scenarios/calculate
- Request: { signpost_progress: {code: value}, preset: "equal" }
- Return: { overall_index, category_scores, safety_margin }

**Use Cases**:
- "What if GPT-5 scores 90% on SWE-bench?"
- "What if we hit 10^27 FLOP but security stays at 20%?"
- "When do we hit 50% overall proximity?"

### 4. Advanced Analytics

**Goal**: Deeper insights into AGI progress

Create: apps/web/app/analytics/page.tsx

**Visualizations**:
1. **Capability-Safety Heatmap**:
   - X-axis: Capabilities score
   - Y-axis: Security score
   - Current position vs historical
   - Danger zones highlighted

2. **Forecast Accuracy Leaderboard**:
   - Which forecasters are most accurate?
   - Brier scores for each source
   - Calibration curves

3. **Surprise Score Heatmap**:
   - Grid of signposts
   - Color by surprise score (how unexpected)
   - Darker = more surprising

4. **Velocity Dashboard**:
   - Progress per month by category
   - Trend lines
   - Acceleration/deceleration

**Backend**:
- GET /v1/analytics/capability-safety
- GET /v1/analytics/forecast-accuracy
- GET /v1/analytics/surprise-scores
- GET /v1/analytics/velocity

## Architecture Deep Dive

**CRITICAL**: Audit the entire system architecture

### 1. System Architecture Review

**Create**: docs/architecture-review.md

**Audit Areas**:

#### A. API Design
- Audit all 40+ endpoints in services/etl/app/main.py
- Inconsistent naming? (e.g., /events vs /event)
- Missing REST principles?
- Should use GraphQL instead?
- API versioning strategy?
- Response format consistency?

#### B. Database Architecture
- Review services/etl/app/models.py
- Normalization issues?
- Missing relationships?
- Inefficient joins?
- Should denormalize anything?
- Sharding strategy for scale?

#### C. Caching Strategy
- What's cached where?
- Redis usage patterns
- Cache invalidation logic
- Stale data risks?
- TTL appropriateness?

#### D. Error Handling
- Consistent error responses?
- Proper HTTP status codes?
- Error logging strategy?
- User-friendly error messages?

#### E. Scalability
- Bottlenecks at 10x traffic?
- Database connection pooling?
- Rate limiting effectiveness?
- CDN usage?
- Background job queue capacity?

### 2. Security Architecture

**Create**: docs/security-architecture-review.md

**Audit**:
- API key management (already built in Sprint 8)
- Request signing implementation
- PII handling
- SQL injection prevention
- XSS prevention
- CSRF protection
- Rate limiting bypasses
- Authentication flow
- Authorization model

### 3. LLM Architecture

**Create**: docs/llm-architecture-review.md

**Audit**:
- Prompt versioning (already exists)
- Cost tracking accuracy
- Budget enforcement
- Model selection strategy
- Fallback behavior
- Prompt injection risks
- Output validation
- Caching effectiveness

### 4. Frontend Architecture

**Create**: docs/frontend-architecture-review.md

**Audit**:
- State management (currently no global state - is this OK?)
- API call patterns (SWR usage)
- Component organization
- Shared components reuse
- Type safety (TypeScript strict mode)
- Bundle size optimization
- Code splitting strategy

### 5. Data Flow Architecture

**Create**: Architecture diagrams in docs/

**Create diagrams for**:
1. Request flow (user → frontend → API → database)
2. ETL pipeline (RSS → Celery → LLM → database)
3. Event mapping flow
4. Caching layers
5. Authentication flow

Use Mermaid diagrams or ASCII art.

## Success Criteria
- [ ] Vector embeddings for all events + signposts
- [ ] RAG chatbot functional with citations
- [ ] Scenario explorer working
- [ ] Advanced analytics dashboard
- [ ] Complete architecture review with findings
- [ ] 5+ architecture diagrams
- [ ] Top 10 architecture improvements prioritized

## Deliverables

**Phase 4 Features**:
1. services/etl/app/services/embedding_service.py
2. services/etl/app/services/rag_chatbot.py
3. Celery task: populate_embeddings()
4. apps/web/app/chat/page.tsx (RAG UI)
5. apps/web/app/scenarios/page.tsx (What-if simulator)
6. apps/web/app/analytics/page.tsx (Advanced charts)
7. 8+ new API endpoints

**Architecture Audits**:
8. docs/architecture-review.md
9. docs/security-architecture-review.md
10. docs/llm-architecture-review.md
11. docs/frontend-architecture-review.md
12. docs/diagrams/ (5+ Mermaid diagrams)
13. Create GitHub issues for top 10 critical findings

**Documentation**:
14. docs/guides/chatbot-usage.md
15. docs/guides/scenario-explorer.md
16. Update README with Phase 4 features

## Deep Dive Requirements
- Question everything - no sacred cows
- Provide specific recommendations, not just observations
- Include cost/benefit for architectural changes
- Consider 10x and 100x scale scenarios
- Think about failure modes
- Document trade-offs

## Resources
- LangChain: https://python.langchain.com/docs/get_started/introduction
- pgvector: https://github.com/pgvector/pgvector
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- SSE Streaming: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

Create a feature branch, build features, audit architecture, document everything, open PR. Good luck! 🤖

