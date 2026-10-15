from typing import Literal
from pydantic import BaseModel, Field
from sql_tools import SQLTools
from pydantic_ai import Agent, AgentRunResult, ModelRequestNode,UserPromptNode, AgentRun, CallToolsNode,FunctionToolCallEvent

class SQLResult(BaseModel):
        """
        This model provides a structured result of a database operation
        Including the query, the result and the total rows count        
        """

        sql_quer:str = Field(description="The sql query executed against the database")
        result_text:str = Field(description="The result of the query executed against the database")
        row_count:int = Field(description="The number of rows returned by the executed query")

DEFAULT_INSTRUCTIONS = """
You are an agent specialized in quering agains duckdb database.
To perform a query you must do following steps
1) always get the schema using the tool get_schema
2) translate the user request to a sql query based on the schema returned 
3) execute the query agains the database using the tool run_sql
"""
class DocumentationAgentConfig:
    model = 'openai:gpt-4o-mini'
    name = 'sqlagent'
    instructions = DEFAULT_INSTRUCTIONS

def create_agent(
        config: DocumentationAgentConfig,
        search_tools: SQLTools
    ) -> Agent:
    tools = [search_tools.get_schema, search_tools.run_sql]

    sqlagent = Agent(
        name=config.name,
        model=config.model,
        instructions=config.instructions,
        tools=tools
    )

    return sqlagent
async def run_agent(
    agent: Agent,
    user_prompt:str,
    message_history:None
)-> AgentRunResult:
    callback = NamedCallback(agent)
    result =await agent.run(user_prompt=user_prompt,
                            event_stream_handler=callback,
                            message_history=message_history,
                            output_type=SQLResult)
    return result

class NamedCallback:

    def __init__(self, agent):
        self.agent_name = agent.name

    async def print_function_calls(self, ctx, event):
        # Detect nested streams
        if hasattr(event, "__aiter__"):
            async for sub in event:
                await self.print_function_calls(ctx, sub)
            return

        if isinstance(event, FunctionToolCallEvent):
            tool_name = event.part.tool_name
            args = event.part.args
            print(f"TOOL CALL ({self.agent_name}): {tool_name}({args})")

    async def __call__(self, ctx, event):
        return await self.print_function_calls(ctx, event)