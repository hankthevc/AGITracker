"""Seed rich educational content for signposts."""
import json
import sys
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Signpost, SignpostContent


# Deep content for first-class benchmarks
FIRST_CLASS_CONTENT = {
    "swe_bench_85": {
        "why_matters": "Software engineering represents the single largest knowledge work sector (~25M workers globally) and serves as a bellwether for autonomous knowledge work capabilities. Success here implies models can independently solve real-world coding problems at professional quality, maintain complex codebases, and ship production-ready features with minimal human oversight. This is a critical milestone because code generation, unlike creative writing or image generation, has objective correctness criteria and direct economic value.",
        "current_state": """As of October 2024, Claude 4.5 Sonnet leads at 70.6%, with OpenAI's o1-preview at 67.2%. This represents 4-5x improvement from GPT-4's baseline (~15%) just 18 months ago—one of the fastest capability jumps in any benchmark category.

Key breakthroughs enabling this progress:
- Chain-of-thought reasoning (enables multi-step debugging and test-driven iteration)
- Repository-level context windows (8K+ tokens allow understanding of multi-file dependencies)
- Test-driven iteration loops (models can run tests, interpret failures, and fix bugs autonomously)
- Improved code understanding from pretraining on massive code corpora

Current limitations:
- Still struggles with complex refactoring across >5 files requiring architectural insight
- Weak at making design decisions that require deep domain knowledge or user empathy
- Cannot yet handle ambiguous requirements without human clarification loops
- Prone to breaking existing functionality when making changes (regression issues)

The 85% threshold is significant because it represents 'professional junior engineer' level—capable of handling most routine tasks independently while escalating truly complex problems.""",
        "key_papers": json.dumps([
            {
                "title": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
                "url": "https://arxiv.org/abs/2310.06770",
                "date": "2023-10-10",
                "summary": "Introduces benchmark of 2,294 real GitHub issues from 12 Python repos. Shows GPT-4 solves 1.7% without tools, establishing baseline."
            },
            {
                "title": "SWE-agent: Agent Computer Interfaces Enable Software Engineering Language Models",
                "url": "https://arxiv.org/abs/2405.15793",
                "date": "2024-05-24",
                "summary": "Agent-based approach with specialized tools (file editor, linter, test runner) achieves 12.5% on full SWE-bench. Demonstrates importance of proper computer interfaces."
            },
            {
                "title": "Aider: AI Pair Programming in Your Terminal",
                "url": "https://aider.chat/",
                "date": "2024-06-15",
                "summary": "Open-source tool achieving 20%+ on SWE-bench through repository map construction and intelligent git integration."
            }
        ]),
        "key_announcements": json.dumps([
            {
                "title": "Claude 4.5 Sonnet Launch",
                "url": "https://www.anthropic.com/news/claude-3-5-sonnet",
                "date": "2024-10-22",
                "summary": "70.6% on SWE-bench Verified, first model to cross 70% threshold. Combines extended thinking with improved code understanding."
            },
            {
                "title": "OpenAI o1-preview Release",
                "url": "https://openai.com/index/introducing-openai-o1-preview/",
                "date": "2024-09-12",
                "summary": "67.2% on SWE-bench Verified through reinforcement learning on reasoning tasks. Shows chain-of-thought is crucial for debugging."
            }
        ]),
        "technical_explanation": """SWE-bench Verified is a curated subset of 500 problems from the full SWE-bench dataset, manually verified for quality and solvability:

1. **Clear problem specification**: Issue description contains enough information to resolve without additional context
2. **Self-contained resolution**: Can be solved using only the repository contents at a specific commit
3. **Verifiable test suite**: Automated tests clearly pass/fail to determine success

Each task provides:
- Issue description (natural language from actual GitHub issue)
- Repository snapshot (codebase at time issue was filed)
- Gold patch (hidden from model during evaluation)
- Test suite (must pass after model's edits)

Evaluation protocol:
- Model gets read/write access to repository
- Can create, edit, delete files
- Can run commands (e.g., tests, linters)
- Must produce code changes that pass ALL tests
- Scored as binary pass/fail per problem (no partial credit)
- Final score: percentage of 500 tasks successfully resolved

The Verified subset excludes:
- Issues requiring external API calls or network access
- Problems with flaky or non-deterministic tests
- Tasks where human expert couldn't solve with given information"""
    },
    
    "osworld_50": {
        "why_matters": "OSWorld tests whether AI can actually use a computer like a human—navigating operating systems, launching applications, managing files, and completing multi-step workflows. This is crucial because most knowledge work happens through computer interfaces, not just text. A model that scores 50%+ on OSWorld can potentially replace human workers for a wide range of digital tasks, from data entry to research to customer support. It's the difference between 'smart chatbot' and 'digital employee'.",
        "current_state": """As of October 2024, leading models achieve ~22% on OSWorld, with Claude 4.5 Computer Use slightly ahead at ~25% (estimated). This is notably lower than text-heavy benchmarks, revealing a key bottleneck in AI capabilities.

Progress has been slower than SWE-bench because:
- Requires visual understanding (GUI elements, windows, buttons)
- Demands precise mouse/keyboard control
- Needs multi-step planning (can't solve in one response)
- Must handle unexpected UI states and error recovery

Current capabilities:
- Can navigate simple GUI applications (file browsers, settings menus)
- Successfully complete single-action tasks ('open this file', 'click that button')
- Read and interpret text from screenshots

Current limitations:
- Struggles with tasks requiring >5 sequential actions
- Often clicks wrong UI elements when interface is cluttered
- Poor at recovering from errors or unexpected dialogs
- Cannot handle applications with complex state management

The 50% threshold would represent 'competent intern' level—can handle routine computer tasks with occasional supervision.""",
        "key_papers": json.dumps([
            {
                "title": "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments",
                "url": "https://arxiv.org/abs/2404.07972",
                "date": "2024-04-11",
                "summary": "Introduces 369 tasks across Ubuntu, Windows, macOS. Tasks involve using real applications like LibreOffice, GIMP, VS Code. GPT-4V scores only 12%."
            },
            {
                "title": "Claude Computer Use Technical Report",
                "url": "https://www.anthropic.com/news/developing-computer-use",
                "date": "2024-10-22",
                "summary": "Anthropic's system for controlling computers via mouse/keyboard. Achieves ~25% on OSWorld through training on computer use demonstrations."
            }
        ]),
        "key_announcements": json.dumps([
            {
                "title": "Anthropic Launches Computer Use API",
                "url": "https://www.anthropic.com/news/developing-computer-use",
                "date": "2024-10-22",
                "summary": "First major API for AI agents to control computers. Early beta shows promise but reveals difficulty of general computer use."
            }
        ]),
        "technical_explanation": """OSWorld evaluates computer use through real operating system tasks:

Task structure:
- Natural language instruction (e.g., 'Create a spreadsheet with Q4 sales data and save as CSV')
- Starting state (OS with specific applications installed)
- Success criteria (specific file exists with correct content, application in correct state)
- Maximum 15 steps to complete

Evaluation environment:
- Real Ubuntu/Windows/macOS virtual machines
- Actual desktop applications (not simplified versions)
- Screenshots provided as visual input
- Agent outputs mouse coordinates + keyboard actions
- Maximum 5 minutes per task

Scoring:
- Task succeeds if final state matches success criteria
- Partial credit possible if intermediate checkpoints are reached
- Score reported as percentage of tasks fully completed

Task categories:
- File management (20%)
- Application use (30%)
- Web browsing (15%)
- System configuration (15%)
- Multi-application workflows (20%)"""
    },
    
    "webarena_60": {
        "why_matters": "The web is humanity's collective knowledge interface and primary platform for commerce, communication, and coordination. WebArena tests whether AI can navigate this critical infrastructure—filling forms, making purchases, finding information across multiple sites, and completing real-world web workflows. This benchmark matters because billions of knowledge worker hours are spent on web-based tasks. A model scoring 60%+ could autonomously handle research, data gathering, online transactions, and information synthesis—capabilities central to most white-collar jobs.",
        "current_state": """As of October 2024, top models achieve ~45% on WebArena, led by GPT-4V and Claude 4.5 Sonnet. This is better than OSWorld but still reveals significant gaps in agent capabilities.

Progress drivers:
- Improved visual understanding of web layouts
- Better function calling for web actions (click, type, scroll)
- Longer context windows enable multi-page workflows
- Training on web navigation demonstrations

Current capabilities:
- Navigate standard web UIs (forms, menus, search boxes)
- Follow multi-step instructions across 2-3 pages
- Extract information from search results and tables
- Complete simple e-commerce flows

Current limitations:
- Struggles with complex multi-site workflows
- Poor at handling authentication flows and session management
- Often fails when sites use non-standard UI patterns
- Cannot effectively handle JavaScript-heavy dynamic sites
- Weak at recovering when pages load slowly or fail

The 60% threshold would enable 'autonomous research assistant' level capabilities—could independently gather information from multiple sources and synthesize findings.""",
        "key_papers": json.dumps([
            {
                "title": "WebArena: A Realistic Web Environment for Building Autonomous Agents",
                "url": "https://arxiv.org/abs/2307.13854",
                "date": "2023-07-25",
                "summary": "Introduces 812 web tasks across e-commerce, social forums, collaborative software, content management. GPT-4 + best tools achieves 10.5%."
            },
            {
                "title": "Mind2Web: A Large-Scale Dataset for Web Agents",
                "url": "https://arxiv.org/abs/2306.06070",
                "date": "2023-06-09",
                "summary": "Training data of 2,000 web tasks with human demonstrations. Shows importance of training on web-specific navigation patterns."
            }
        ]),
        "key_announcements": json.dumps([
            {
                "title": "GPT-4V Multimodal Capabilities",
                "url": "https://openai.com/research/gpt-4v-system-card",
                "date": "2023-09-25",
                "summary": "Vision + language enables reading web interfaces from screenshots, achieving ~40% on WebArena."
            }
        ]),
        "technical_explanation": """WebArena simulates real websites in a controlled environment:

Environment:
- 4 realistic websites: e-commerce site, Reddit-like forum, GitLab instance, content management system
- Fully functional backends (not mocks)
- Real user accounts and authentication
- Dynamic content that changes based on actions

Task format:
- Natural language goal (e.g., 'Find the cheapest laptop under $800 and add to cart')
- Starting URL
- Success criteria (specific page reached, data retrieved, action completed)
- Maximum 30 actions per task

Agent actions:
- Navigation (click, type, scroll, go back)
- Information extraction (read page, find element)
- Form interactions (fill fields, submit, upload files)

Scoring:
- Binary pass/fail per task
- Must exactly match success criteria
- Partial credit for reaching intermediate states
- Timeout after 5 minutes or 30 actions

Difficulty factors:
- Multi-step reasoning across pages
- Search and filter operations
- State management (cart, sessions)
- Handling error pages and redirects"""
    },
    
    "gpqa_75": {
        "why_matters": "GPQA Diamond tests whether AI has achieved PhD-level scientific reasoning—the kind of deep analytical thinking that drives research breakthroughs. Unlike coding or computer use, these are pure reasoning tasks with no tools, internet access, or trial-and-error. Success here means AI can engage in hypothesis formation, causal reasoning, and multi-hop logical inference at expert human level. This is a crucial gateway capability because scientific reasoning underpins progress across every domain—from drug discovery to materials science to fundamental research.",
        "current_state": """As of October 2024, leading models achieve ~60% on GPQA Diamond, with OpenAI o1-preview reaching ~67% and GPT-4o at ~53%. Human PhD holders average 75%, making this one of the few benchmarks where humans still outperform AI.

Recent progress driven by:
- Chain-of-thought reasoning (especially RL-trained reasoning as in o1)
- Better scientific knowledge from pretraining
- Ability to work through multi-step derivations

Current capabilities:
- Solve single-step PhD-level problems
- Apply known formulas and concepts correctly
- Identify relevant information in complex scenarios

Current limitations:
- Weak at problems requiring novel insight or creative problem-solving
- Struggles with questions needing multiple reasoning hops
- Cannot reliably check own work for errors
- Sometimes makes basic mistakes despite sophisticated reasoning

The 75% threshold (human expert parity) would represent genuine 'research scientist' reasoning capability—can independently work through novel scientific problems.""",
        "key_papers": json.dumps([
            {
                "title": "GPQA: A Graduate-Level Google-Proof Q&A Benchmark",
                "url": "https://arxiv.org/abs/2311.12022",
                "date": "2023-11-20",
                "summary": "Introduces 546 PhD-level questions in physics, chemistry, biology. Designed so internet search doesn't help. PhD holders average 75%; domain experts 85%."
            },
            {
                "title": "Measuring Massive Multitask Language Understanding",
                "url": "https://arxiv.org/abs/2009.03300",
                "date": "2020-09-03",
                "summary": "MMLU benchmark (predecessor to GPQA) showed early models ~40% vs human 90%. Demonstrated need for harder reasoning benchmarks."
            }
        ]),
        "key_announcements": json.dumps([
            {
                "title": "OpenAI o1-preview: Advanced Reasoning",
                "url": "https://openai.com/index/learning-to-reason-with-llms/",
                "date": "2024-09-12",
                "summary": "First model trained specifically for reasoning achieves ~67% on GPQA Diamond through RL on chain-of-thought reasoning."
            }
        ]),
        "technical_explanation": """GPQA Diamond measures pure scientific reasoning:

Question design:
- Graduate-level science (physics, chemistry, biology)
- Multiple choice (4 options)
- Require deep domain knowledge + reasoning
- 'Google-proof': internet search doesn't help

Quality criteria:
- Written by PhD students
- Validated by domain experts
- Questions where PhD holders get ~75% (not trivial, not impossible)
- Wrong answers are plausible (catch blind guessing)

Diamond subset:
- Highest quality 198 questions
- All validated by multiple experts
- Clear correct answers with unambiguous reasoning

Scoring:
- Simple accuracy (% correct)
- No partial credit
- Random guessing baseline: 25%
- Non-expert humans: ~35%
- PhD holders: ~75%
- Domain experts: ~85%

Example difficulty:
'In quantum mechanics, the energy eigenvalues for a particle in a 1D box are proportional to n². If the box length doubles, what happens to the ground state energy?'
- Requires knowing E ∝ 1/L²
- Must apply to n=1 specifically
- Need to reason about quantum boundary conditions"""
    }
}


# Basic content template for non-first-class signposts
def generate_basic_content(signpost_code, name, description, category):
    """Generate basic placeholder content for non-first-class signposts."""
    return {
        "why_matters": f"{name} is a key indicator in the {category} category for tracking progress toward AGI. {description or 'This metric helps us understand capability development in this domain.'}",
        "current_state": "Current progress data is being tracked. Detailed analysis will be added as more evidence becomes available.",
        "key_papers": json.dumps([]),
        "key_announcements": json.dumps([]),
        "technical_explanation": f"Technical details and methodology for {name} measurement."
    }


def seed_rich_content():
    """Seed signpost content into database."""
    
    db = SessionLocal()
    try:
        signposts = db.query(Signpost).all()
        
        inserted_count = 0
        for signpost in signposts:
            # Check if content already exists
            existing = db.query(SignpostContent).filter_by(signpost_id=signpost.id).first()
            if existing:
                continue
            
            # Get content data
            if signpost.code in FIRST_CLASS_CONTENT:
                content_data = FIRST_CLASS_CONTENT[signpost.code]
            else:
                content_data = generate_basic_content(
                    signpost.code,
                    signpost.name,
                    signpost.description,
                    signpost.category
                )
            
            # Create content record
            content = SignpostContent(
                signpost_id=signpost.id,
                why_matters=content_data["why_matters"],
                current_state=content_data["current_state"],
                key_papers=content_data["key_papers"],
                key_announcements=content_data["key_announcements"],
                technical_explanation=content_data["technical_explanation"]
            )
            db.add(content)
            inserted_count += 1
        
        db.commit()
        print(f"✓ Inserted content for {inserted_count} signposts")
        
    except Exception as e:
        print(f"Error seeding content: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_rich_content()

