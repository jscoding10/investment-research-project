from typing import Optional, Type, Union, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from util.logger import get_logger

logger = get_logger(__name__)


def run_agent_with_tools(
    llm: BaseChatModel,
    prompt: str,
    tools: List[BaseTool] = [],
    output_schema: Optional[Type[BaseModel]] = None,
):
    """
    Generic agent executor that handles tool calling flow.

    Args:
        llm: The llm model to use for the agent
        prompt: The prompt to send to the LLM
        tools: List of tools to bind to the LLM
        output_schema: Optional Pydantic model for structured output


    Returns:
        The final LLM response (structured if output_schema provided, else content string)
    """
    try:
        # Generate lookup dictionary so can find tools by name
        # Example: {"get_technical_analysis_tool": <actual function >}
        tools_map = {tool.name: tool for tool in tools}

        # Tell the LLM: "You are allowed to use these tools if you need data"
        # This is like giving the AI a toolbox
        llm_with_tools = llm.bind_tools(tools) if tools else llm

        # Initial invocation — send the user's question
        response = llm_with_tools.invoke(prompt)

        # Check for tool calls
        # Groq returns a special field called "tool_calls" when this happens
        if getattr(response, "tool_calls", None) and response.tool_calls:
            # Grab the first (and usually only) tool request
            tool_call = response.tool_calls[0]

            # Look up which tool the LLM requested
            # What tool did the AI ask for? e.g., "get_technical_analysis_tool"
            requested_tool_name = tool_call["name"]
            requested_tool = tools_map[requested_tool_name]

            # Look up the actual Python function from map
            tool_args = tool_call["args"]

            # Call the actual tool function
            # Example: call yfinance, FRED, or Tavily search
            tool_result = requested_tool.func(**tool_args)

            # Create messages for the second LLM call with tool results
            messages = [
                # Original user question
                {"role": "user", "content": prompt},

                # What the AI said: "I want to call a tool"
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [response.tool_calls[0]],
                },
                # The result of running the tool
                {
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call["id"],
                },
            ]

            # Second LLM call with tool results to get the analysis
            if output_schema:
                structured_llm = llm.with_structured_output(output_schema)
                final_response = structured_llm.invoke(messages)
                return final_response
            else:
                final_response = llm_with_tools.invoke(messages)
                return final_response.content
        else:
            if output_schema:
                structured_llm = llm.with_structured_output(output_schema)
                final_response = structured_llm.invoke(prompt)
                return final_response
            else:
                return response.content
    except Exception as e:
        # If anything goes wrong (bad ticker, API down, etc.)
        logger.error(f"Error in run_agent_with_tools: {e}", exc_info=True)
        return f"Error executing agent: {str(e)}"