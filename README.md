# Hover Detection Agent - Automated BDD Test Generator

An AI-powered agent that automatically detects hover interactions on web applications and generates comprehensive Gherkin test scenarios using the LangGraph agentic framework.

## What You Get

Run the agent on any website and receive a complete test report with:

| Output | Description |
|--------|-------------|
| `hover_report.md` | Full report with screenshots and Gherkin scenarios |
| `tldr.md` | Executive summary for stakeholders |
| `screenshots/` | Before/after hover images as evidence |
| `scenarios/*.feature` | Individual Gherkin test files |
| `behaviors/*.json` | Raw behavior data for analysis |

> **See it in action:** [Example minto.ai report](output/084c8d35-2363-4eef-a411-940479298473/) | [View LangSmith Trace](https://smith.langchain.com/public/c36b3047-4370-4fe2-912e-b48dd91b9938/r)

### Screenshot Evidence

The agent captures before/after screenshots for each hover interaction:

| Before Hover | After Hover (Dropdown Revealed) |
|--------------|--------------------------------|
| ![Before](docs/images/001_Products_menu_item_before.png) | ![After](docs/images/002_Products_menu_item_after.png) |

### Sample TLDR Summary

```markdown
## TLDR - Executive Summary

**Website:** minto.ai
**Test Date:** 2025-12-18 13:00

### At a Glance
| Metric | Value |
|--------|-------|
| Total Elements Tested | 23 |
| Interactive Elements Found | 14 |
| Test Success Rate | 78.3% |
| Gherkin Scenarios Generated | 14 |

### Key Findings
- **Dropdowns Detected (4):** Products, Resources, Company, Contact Us menus
- **Content Revealed (1):** Explore All Applications button
- **Unreachable Elements (5):** Out of viewport or dynamically loaded
```

### Sample Gherkin Scenario

```gherkin
Feature: Hover Interaction - Products Menu
  As a user visiting the website
  I want to see dropdown content when hovering over the Products menu
  So that I can access product categories

  @hover @dropdown
  Scenario: Products menu reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Products" menu item
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | iHz - IoT system | /ihz |
      | spiderAI - Operational intelligence | /spiderai |
```

---

## Quick Start

```bash
# 1. Clone and setup
cd PlayWriterAutomation
uv sync
uv run playwright install chromium

# 2. Configure LLM (choose one in .env)
# Option A: Custom vLLM endpoint
LLM_BASE_URL=http://your-server:8908/v1
LLM_MODEL_NAME=Qwen/Qwen3-VL-30B-A3B-Instruct-FP8

# Option B: Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Option C: OpenAI
OPENAI_API_KEY=sk-...

# 3. Start LangGraph server
uv run langgraph dev --port 2024 --allow-blocking

# 4. Access Studio UI
# Open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Chat Interface

Use [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui) - LangChain's open-source web app for interacting with any LangGraph agent via a chat interface.

**Try it instantly:** [agentchat.vercel.app](https://agentchat.vercel.app/?apiUrl=http://localhost:2024&assistantId=hover_agent)

![Agent Chat UI](docs/images/agent-chat-ui.png)

**Features:**
- Streaming responses with real-time updates
- Tool call visualization
- Human-in-the-loop interrupts
- Thread management for conversation history
- Works with any LangGraph server

**Alternative:** Run locally with `npx create-agent-chat-app`

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://127.0.0.1:2024/ok` | Health check |
| `http://127.0.0.1:2024/docs` | API documentation |
| [Agent Chat UI](https://agentchat.vercel.app/?apiUrl=http://localhost:2024&assistantId=hover_agent) | Chat interface |
| [LangSmith Studio](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024) | Visual debugging UI |

---

## How It Works

### Objective

**Automatically test and document all hover events in a web application by:**

1. Navigating to any given URL
2. Detecting all hoverable elements (menus, buttons, cards, etc.)
3. Testing each element's hover behavior
4. Capturing before/after screenshots as evidence
5. Generating Gherkin BDD scenarios for interactive elements
6. Producing a comprehensive markdown report with executive summary

### Behavior Classification

| Behavior | Description | Gherkin Generated? |
|----------|-------------|-------------------|
| `dropdown` | Menu/submenu appears with links | Yes |
| `tooltip` | Tooltip or popover appears | Yes |
| `content_revealed` | New content becomes visible | Yes |
| `no_change` | No DOM changes detected | No (TLDR only) |
| `unreachable` | Element out of viewport/hidden | No (TLDR only) |

### Agent Workflow

The agent follows a structured 7-step workflow:

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Tools
    participant Browser
    participant Disk

    User->>Agent: Analyze URL

    rect rgb(200, 230, 200)
        Note over Agent,Browser: STEP 1: Navigation
        Agent->>Tools: navigate_to_url(url)
        Tools->>Browser: page.goto(url)
        Browser-->>Agent: Page title
    end

    rect rgb(200, 220, 240)
        Note over Agent,Browser: STEP 2: Page Analysis
        Agent->>Tools: get_page_structure()
        Tools->>Browser: Accessibility tree scan
        Browser-->>Agent: Menus, buttons, links, hover_candidates
    end

    rect rgb(240, 220, 200)
        Note over Agent,Browser: STEP 3: Element Discovery
        Agent->>Tools: find_hoverable_elements()
        Tools->>Browser: CSS selector scan
        Browser-->>Agent: Hoverable elements list
    end

    rect rgb(230, 200, 230)
        Note over Agent,Disk: STEP 4: Hover Testing (Loop)
        loop For each promising element
            Agent->>Tools: hover_element(selector, description)
            Tools->>Browser: Reset state, hover, capture DOM diff
            Browser-->>Tools: Behavior (dropdown/tooltip/no_change/unreachable)
            Tools->>Disk: Save behavior.json + screenshots

            alt behavior is interactive
                Agent->>Tools: save_gherkin_scenario(name, gherkin)
                Tools->>Disk: Save .feature file
            end
        end
    end

    rect rgb(200, 240, 220)
        Note over Agent,Disk: STEP 5: Executive Summary
        Agent->>Tools: generate_tldr(website_name)
        Tools->>Disk: Read all behaviors
        Tools->>Disk: Save tldr.md
    end

    rect rgb(240, 240, 200)
        Note over Agent,Disk: STEP 6: Report Generation
        Agent->>Tools: generate_report(title)
        Tools->>Disk: Read behaviors, scenarios, tldr
        Tools->>Disk: Save hover_report.md
    end

    rect rgb(220, 220, 220)
        Note over Agent,User: STEP 7: Summary
        Agent-->>User: Report path + key findings
    end
```

---

## Architecture

**Agent-Driven Playwright Orchestration** using the LangGraph Agentic Framework to automate, test multiple scenarios, and create comprehensive reports.

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Framework** | LangGraph | Orchestrates tool calls, manages state, handles workflow |
| **Browser Automation** | Playwright (Sync API) | Persistent browser session for DOM interaction |
| **LLM Backend** | Configurable (Claude/GPT/Custom) | Decision making and Gherkin generation |
| **Report Generation** | Markdown + Screenshots | Documentation with visual evidence |

### Why This Architecture?

| Challenge | Solution |
|-----------|----------|
| Browser session persistence | Custom BrowserManager with ThreadPoolExecutor |
| Windows asyncio conflicts | Sync Playwright API wrapped for async access |
| LLM state management | Disk-based behavior persistence (not LLM memory) |
| Stakeholder-friendly reports | TLDR summaries + detailed Gherkin scenarios |

### System Diagram

```mermaid
graph TB
    subgraph "LangGraph Agent"
        A[Agent Node] -->|decides| B{Should Continue?}
        B -->|has tool calls| C[Tool Node]
        B -->|no tool calls| D[END]
        C -->|returns results| A
    end

    subgraph "Available Tools"
        T1[navigate_to_url]
        T2[get_page_structure]
        T3[find_hoverable_elements]
        T4[hover_element]
        T5[save_gherkin_scenario]
        T6[generate_tldr]
        T7[generate_report]
    end

    subgraph "Browser Layer"
        BM[BrowserManager]
        PW[Playwright Chromium]
        BM --> PW
    end

    subgraph "Output Artifacts"
        O1[screenshots/]
        O2[behaviors/*.json]
        O3[scenarios/*.feature]
        O4[hover_report.md]
        O5[tldr.md]
    end

    C --> T1 & T2 & T3 & T4 & T5 & T6 & T7
    T1 & T2 & T3 & T4 --> BM
    T4 --> O1 & O2
    T5 --> O3
    T6 --> O5
    T7 --> O4

    style A fill:#4CAF50,color:white
    style C fill:#2196F3,color:white
    style BM fill:#FF9800,color:white
    style D fill:#9E9E9E,color:white
```

---

## Configuration

### Project Structure

```
PlayWriterAutomation/
├── src/
│   ├── __init__.py
│   ├── agent.py          # LangGraph agent definition + workflow
│   ├── browser.py        # Playwright session management
│   └── tools.py          # LangChain tools for hover detection
├── docs/
│   └── images/           # README screenshots and diagrams
├── tests/                # Unit tests
├── output/               # Generated artifacts (per session)
│   └── {session-id}/
│       ├── hover_report.md
│       ├── tldr.md
│       ├── screenshots/
│       ├── scenarios/
│       └── behaviors/
├── archived/             # Old/experimental code
├── langgraph.json        # LangGraph configuration
├── pyproject.toml        # Dependencies
└── README.md
```

### langgraph.json

```json
{
  "graphs": {
    "hover_agent": "src.agent:graph"
  },
  "env": ".env"
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_BASE_URL` | Custom LLM endpoint | - |
| `LLM_MODEL_NAME` | Model name for custom endpoint | Qwen/Qwen3-VL-30B |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |

### Development

```bash
# Run tests
uv run pytest -v

# Add dependency
uv add <package>

# Check server logs
# Logs appear in terminal running langgraph dev
```

---

## Observability

**Full observability powered by [LangSmith](https://smith.langchain.com/)** - Every agent run is automatically traced, providing complete visibility into:

- LLM calls and token usage
- Tool invocations and results
- Agent decision flow
- Execution timing and performance

### Example Trace

View a complete trace of the agent analyzing [minto.ai](https://minto.ai):

**[View Live Trace on LangSmith](https://smith.langchain.com/public/c36b3047-4370-4fe2-912e-b48dd91b9938/r)**

This trace shows the full agent workflow: navigation, page analysis, hover detection, Gherkin generation, and report creation.

---

## Evaluation

> **Note:** Automated evaluation pipeline is planned for future development.

### Evaluation Metrics

#### 1. Generation Metrics

| Metric | Description |
|--------|-------------|
| **Time to Generate** | Total seconds from URL input to Gherkin output |
| **Tokens Used** | LLM tokens consumed (input + output) |

#### 2. Gherkin Quality Metrics

| Metric | Description |
|--------|-------------|
| **Syntax Valid** | Pass/Fail — Does it parse correctly? |
| **Scenario Count** | Number of test scenarios generated |

#### 3. Website/Playwright Metrics

| Metric | Description |
|--------|-------------|
| **Hover Elements Found** | Count of hoverable elements detected |
| **DOM Changes Detected** | Count of elements that triggered visible changes on hover |

### Example Evaluation: minto.ai

```
URL: https://minto.ai

Generation:
  - Time: 468 seconds
  - Tokens: 630,000 (input + output)

Gherkin:
  - Syntax Valid: ✓
  - Scenarios Generated: 14

Website:
  - Hover Elements Found: 23
  - DOM Changes Detected: 14
```

---

## Technologies

| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core runtime |
| **LangGraph** | Agentic workflow orchestration |
| **LangChain** | LLM integration and tool framework |
| **Playwright** | Browser automation (Chromium) |
| **LangSmith** | Observability and tracing |
| **[Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui)** | Web chat interface for LangGraph agents |
| **vLLM** | Self-hosted LLM inference server |
| **Qwen3-VL-30B** | Vision-language model for decision making |
| **Pydantic** | Data validation and settings |

## License

MIT
