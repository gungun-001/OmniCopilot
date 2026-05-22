import json
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from tools.all_tools import OMNI_TOOLS
from typing import Dict, Optional, AsyncGenerator
import os
import logging

# Store memory instances per session (rudimentary in-memory storage)
memory_store: Dict[str, ConversationBufferMemory] = {}

def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
    return memory_store[session_id]


def _make_llm(groq_api_key: str, model: str) -> ChatGroq:
    return ChatGroq(
        model=model,
        temperature=0,
        groq_api_key=groq_api_key,
    )


def _make_executor(llm, memory) -> AgentExecutor:
    from datetime import datetime
    current_time = datetime.now().astimezone().isoformat()

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are Omni Copilot, an AI-powered unified workspace assistant. "
                   f"The current date and local time is {current_time}. "
                   "CRITICAL TIMEZONE RULE: When providing 'start_time' and 'end_time' for meetings, ALWAYS use strict ISO 8601 format INCLUDING the local timezone offset shown in the current time string (e.g., 2026-04-16T16:00:00+05:30). NEVER use 'Z' (UTC) unless mathematically offset.\n\n"
                   "## ⚠️ GitHub Strict Rules\n"
                   "- NEVER say you don't have access to GitHub.\n"
                   "- ALWAYS assume GitHub access is available via token.\n"
                   "- ALWAYS use the GitHub tool (e.g., get_github_repos) for repository-related queries.\n"
                   "- DO NOT fallback to generic LLM answers for GitHub questions.\n"
                   "- If asked for the latest repository or github link, call get_github_repos, sort by updated_at, and present the most recent one with its GitHub URL beautifully.\n\n"
                   "## 📧 Professional HTML Email Formatting Rules\n"
                   "- The `send_email_tool` supports HTML body formatting! Therefore, you MUST draft gorgeous, premium-looking, and corporate-grade HTML emails rather than basic plain text.\n"
                   "- Use clean inline CSS styles with a modern aesthetic:\n"
                   "  - Use premium fonts (e.g., family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;).\n"
                   "  - Create a clean card layout with a white or soft off-white background, subtle border-radius (8px), a light gray outer border, and a shadow feel.\n"
                   "  - Include a styled top banner or header with a premium deep indigo/navy blue background (`#1e293b` or `#4f46e5`) and white text.\n"
                   "  - Structure meeting details in a beautiful table or bulleted list with ample padding and modern margins.\n"
                   "  - For links (especially Google Meet), ALWAYS design a gorgeous, high-contrast, rounded CSS button (e.g., background color: `#4f46e5`, color: `#ffffff`, padding: `12px 24px`, border-radius: `6px`, text-decoration: `none`, display: `inline-block`, font-weight: `bold`) so it looks incredibly premium and invitation-ready.\n"
                   "  - Conclude with a clear sign-off, signature, and professional footer styling.\n\n"
                   "You can help the user schedule meetings, send emails, read files, send messages to slack/discord, and fetch github files. "
                   "CRITICAL DECISION RULE: Once you have obtained the specific information requested by the user, STOP and provide the answer immediately. Do NOT call more tools if you already have the data.\n\n"
                   "CRITICAL INSTRUCTION FOR MEETINGS & EMAILS:\n"
                   "- If the user asks to schedule a meeting but does NOT explicitly ask to send an email, use only `schedule_meeting_tool`. Google Calendar will natively invite any attendees.\n"
                   "- If the user explicitly asks to send an email with the meeting or Google Meet link, you MUST execute this sequentially: first call `schedule_meeting_tool` (or `create_google_meet_tool`) to obtain the real Google Meet link, and once you have the link from the tool's response, call `send_email_tool` in the next turn to send the email containing that link. NEVER call them in parallel or at the same time, as you need the generated link to compose the HTML email body."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, OMNI_TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=OMNI_TOOLS,
        memory=memory,
        verbose=True,
        max_iterations=15,
        handle_parsing_errors=True,
        early_stopping_method="force",
        return_intermediate_steps=True, # Critical for streaming thoughts
    )


async def stream_agent_handler(user_input: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator that streams agent events as JSON chunks.
    Handles rate-limits and errors internally.
    """
    logger = logging.getLogger("omni_copilot.orchestrator")
    
    try:
        executor = create_agent_executor(session_id)
        
        # Using astream_events for granular control
        async for event in executor.astream_events(
            {"input": user_input},
            version="v2"
        ):
            kind = event["event"]
            
            # 1. Capture Thoughts / LLM start
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield json.dumps({"type": "token", "content": content}) + "\n"
            
            # 2. Capture Tool Calls
            elif kind == "on_tool_start":
                yield json.dumps({"type": "tool_start", "tool": event["name"], "input": event["data"].get("input")}) + "\n"
            
            # 3. Capture Tool Outputs
            elif kind == "on_tool_end":
                yield json.dumps({"type": "tool_end", "tool": event["name"], "output": str(event["data"].get("output"))[:1000]}) + "\n"
            
            # 4. Final Result
            elif kind == "on_chain_end" and event["name"] == "AgentExecutor":
                output = event["data"]["output"].get("output")
                if output:
                    yield json.dumps({"type": "final_answer", "content": output}) + "\n"

    except Exception as e:
        error_str = str(e)
        logger.error(f"Streaming error: {error_str}")
        
        if "rate_limit_exceeded" in error_str.lower() or "429" in error_str:
            yield json.dumps({"type": "error", "content": "⚠️ Rate limit hit. I'll be back in a moment."}) + "\n"
        else:
            yield json.dumps({"type": "error", "content": f"System error: {error_str}"}) + "\n"


def safe_invoke(agent_executor: AgentExecutor, user_input: str, session_id: str) -> Optional[Dict]:
    """
    Legacy sync wrapper. Still useful for non-streaming paths.
    """
    logger = logging.getLogger("omni_copilot.orchestrator")

    try:
        return agent_executor.invoke({"input": user_input})
    except Exception as e:
        error_str = str(e)
        if "rate_limit_exceeded" in error_str.lower() or "429" in error_str:
            logger.warning("Primary model rate limited. Falling back to llama-3.1-8b-instant...")
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            fallback_llm = _make_llm(groq_api_key, "llama-3.1-8b-instant")
            memory = get_memory(session_id)
            fallback_executor = _make_executor(fallback_llm, memory)
            
            return fallback_executor.invoke({"input": user_input})
        raise e


def create_agent_executor(session_id: str) -> AgentExecutor:
    """Creates and returns an AgentExecutor bound to our tools and memory."""
    from dotenv import load_dotenv
    load_dotenv()

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing from environment. Set it in your .env file.")

    model = "qwen/qwen3-32b"
    llm = _make_llm(groq_api_key, model)
    memory = get_memory(session_id)
    executor = _make_executor(llm, memory)

    return executor

