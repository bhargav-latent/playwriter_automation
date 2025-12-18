"""
LangGraph agent for hover detection.
Uses an LLM to dynamically call tools and analyze web pages.
Exposes a graph that can be served via LangGraph CLI.
"""

import os
from pathlib import Path
from typing import Annotated, TypedDict, Literal

# Load .env file from project root
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.tools import get_all_tools, set_session_id
from src.browser import close_browser


# State definition
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# System prompt for the agent
SYSTEM_PROMPT = """You are an AI agent that MUST use tools to detect hover interactions on web pages.

IMPORTANT: You MUST call tools to perform actions. Do NOT make assumptions or generate responses without using tools first.

Your workflow (you MUST follow this exactly):

STEP 1: Call navigate_to_url with the provided URL
STEP 2: Call get_page_structure to understand the page using accessibility tree
         - This shows menus, buttons, links, and hover_candidates
         - Use this to identify which elements are likely to have hover effects
STEP 3: Call find_hoverable_elements to get CSS-based hoverable elements
STEP 4: For EACH element that looks promising:
         a) Call hover_element(selector, description) to test the hover interaction
            - This automatically saves behavior data to disk for the final report
            - Screenshots are captured automatically (before/after)

         b) Check the hover result behavior type:
            - If behavior is "dropdown", "tooltip", or "content_revealed" → call save_gherkin_scenario
            - If behavior is "no_change" or "unreachable" → DO NOT call save_gherkin_scenario (skip to next element)

         IMPORTANT: Only create Gherkin scenarios for INTERACTIVE behaviors!
         Elements with no_change or unreachable will be summarized in the TLDR only.
         Note: "unreachable" means the element couldn't be hovered (out of viewport, hidden, or dynamically loaded) - this is normal for modern websites.

         Example Gherkin format (ONLY for dropdown/tooltip/content_revealed):
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
               | Category A | /products/category-a |
               | Category B | /products/category-b |
         ```

         Customize based on behavior type:
         - For dropdowns: Include the actual revealed links from the hover result
         - For tooltips: Describe the tooltip content
         - For content_revealed: Describe what new content appeared
         - Add relevant tags (@hover, @dropdown, @tooltip, @content_revealed)

STEP 5: After testing ALL elements and saving individual scenarios, call generate_tldr with:
         - website_name: The name of the website (e.g., "minto.ai")
         This creates an executive summary with key metrics and findings.

STEP 6: Call generate_report with:
         - report_title: A descriptive title like "Hover Detection Report for {website_name}"
         (Note: Behaviors and TLDR are automatically loaded from disk)

STEP 7: Provide your summary with the report path and key findings

Available tools:
- navigate_to_url(url): Navigate to a URL - MUST be called first
- get_page_structure(): Get accessibility tree analysis - shows menus, buttons, links, hover candidates
- find_hoverable_elements(): Get CSS-based hoverable elements with selectors
- hover_element(selector, description): Test hover - captures screenshots AND saves behavior to disk automatically
- save_gherkin_scenario(element_name, gherkin_content): Save YOUR custom Gherkin scenario for the element
- generate_tldr(website_name): Generate executive summary with key metrics and findings - call BEFORE generate_report
- generate_report(report_title): Generate markdown report (auto-loads behaviors, scenarios, and TLDR from disk)

CRITICAL: You must ALWAYS start by calling navigate_to_url.
CRITICAL: Only call save_gherkin_scenario for behaviors: dropdown, tooltip, content_revealed. SKIP scenarios for no_change and unreachable behaviors.
CRITICAL: After testing all hovers, you MUST call generate_tldr FIRST, then generate_report to create the full documentation."""


# Global LLM instance (lazy loaded)
_llm_instance: BaseChatModel | None = None


def get_llm() -> BaseChatModel:
    """Get the LLM instance based on available configuration."""
    global _llm_instance

    if _llm_instance is not None:
        return _llm_instance

    # Try custom vLLM/OpenAI-compatible endpoint first
    custom_base_url = os.environ.get("LLM_BASE_URL")
    if custom_base_url:
        from langchain_openai import ChatOpenAI
        _llm_instance = ChatOpenAI(
            model=os.environ.get("LLM_MODEL_NAME", "Qwen/Qwen3-VL-30B-A3B-Instruct-FP8"),
            temperature=0,
            base_url=custom_base_url,
            api_key=os.environ.get("LLM_API_KEY", "EMPTY"),
        )
        return _llm_instance

    # Try Anthropic
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        from langchain_anthropic import ChatAnthropic
        _llm_instance = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0,
            api_key=anthropic_key,
        )
        return _llm_instance

    # Try OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        from langchain_openai import ChatOpenAI
        _llm_instance = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=openai_key,
        )
        return _llm_instance

    raise ValueError(
        "No LLM configured. Set LLM_BASE_URL for custom endpoint, or ANTHROPIC_API_KEY/OPENAI_API_KEY."
    )


def create_graph():
    """Create the LangGraph workflow with LLM tool calling."""
    # Get tools
    tools = get_all_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    # Custom tool execution node that doesn't use LangGraph's ToolNode
    # This avoids any asyncio issues on Windows
    async def tool_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
        """Execute tools (async wrapper for sync execution)."""
        import structlog
        log = structlog.get_logger("tool_node")

        # Extract thread_id from config and set it for output organization
        thread_id = None
        if config:
            configurable = config.get("configurable", {})
            thread_id = configurable.get("thread_id")
            if thread_id:
                set_session_id(thread_id)

        messages = state["messages"]
        last_message = messages[-1]

        # Debug: Log what we received (only tool names to avoid Unicode encoding issues)
        has_attr = hasattr(last_message, "tool_calls")
        tool_calls_value = getattr(last_message, "tool_calls", None) if has_attr else None
        tool_call_names = [tc.get("name", "unknown") for tc in tool_calls_value] if tool_calls_value else []
        log.info("tool_node received",
                 has_tool_calls_attr=has_attr,
                 tool_call_names=tool_call_names,
                 message_type=type(last_message).__name__,
                 thread_id=thread_id)

        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            log.warning("No tool calls found, returning empty messages")
            return {"messages": []}

        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name in tools_by_name:
                tool = tools_by_name[tool_name]
                try:
                    # Use ainvoke for async tools
                    result = await tool.ainvoke(tool_args)
                    tool_messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id,
                        name=tool_name
                    ))
                except Exception as e:
                    tool_messages.append(ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_id,
                        name=tool_name
                    ))
            else:
                tool_messages.append(ToolMessage(
                    content=f"Error: Unknown tool {tool_name}",
                    tool_call_id=tool_id,
                    name=tool_name
                ))

        return {"messages": tool_messages}

    # Define the agent node
    async def agent_node(state: AgentState) -> AgentState:
        """The agent decides what to do next."""
        # Get LLM lazily
        llm = get_llm()
        llm_with_tools = llm.bind_tools(tools)

        messages = state["messages"]

        # Add system message if not present
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Define routing logic
    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        """Determine if we should continue or end."""
        import structlog
        log = structlog.get_logger("routing")

        messages = state["messages"]
        last_message = messages[-1]

        has_attr = hasattr(last_message, "tool_calls")
        tool_calls = getattr(last_message, "tool_calls", None) if has_attr else None

        # Safely extract tool call names for logging (avoid Unicode encoding issues on Windows)
        tool_call_names = [tc.get("name", "unknown") for tc in tool_calls] if tool_calls else []
        log.info("should_continue check",
                 has_tool_calls_attr=has_attr,
                 tool_call_names=tool_call_names,
                 tool_calls_len=len(tool_calls) if tool_calls else 0,
                 message_type=type(last_message).__name__)

        # If the LLM made tool calls, continue to tool execution
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            log.info("Routing to tools")
            return "tools"

        # Otherwise, end the conversation
        log.info("Routing to END")
        return "__end__"

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "__end__": END,
        }
    )

    # Tools always return to agent
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Export the graph for LangGraph CLI with recursion limit set to 500
graph = create_graph().with_config({"recursion_limit": 500})


async def run_agent(url: str) -> str:
    """
    Run the hover detection agent on a URL.

    Args:
        url: The URL to analyze

    Returns:
        The agent's final response with Gherkin tests
    """
    try:
        initial_state = {
            "messages": [
                HumanMessage(content=f"Please analyze the hover interactions on this website: {url}")
            ]
        }

        final_state = await graph.ainvoke(initial_state, {"recursion_limit": 500})

        # Get the last AI message
        for msg in reversed(final_state["messages"]):
            if hasattr(msg, "content") and msg.content:
                return msg.content

        return "Agent completed but no response was generated."
    finally:
        # Clean up browser
        await close_browser()
