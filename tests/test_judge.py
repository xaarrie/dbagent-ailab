
import dotenv
import pytest
from tests.judge import assert_criteria
from sql_agent import DocumentationAgentConfig
from sql_agent import create_agent
from sql_agent import run_agent, DEFAULT_INSTRUCTIONS
from sql_tools import SQLTools
from tests.utils import collect_tools, ToolCall
from time import time
dotenv.load_dotenv('env')
criteria = [
    "performs search using the 'search' tool",
    "checks the content of the 'examples/LLM_judge.mdx' using 'get_file' tool",
    "makes at least 2 tool calls",
]

@pytest.fixture()
def agent():
    t0 = time()

    tools = SQLTools()
    agent_config = DocumentationAgentConfig(        
        )
    agent_config.instructions=DEFAULT_INSTRUCTIONS

    agent = create_agent(agent_config, tools)

    t1 = time()
    print(f'loading agent took {t1 - t0}')

    return agent


@pytest.mark.asyncio
async def test_evaluate_agent_performance(agent):
    user_prompt = 'Which hour of the day has the highest average fare amount?'
    result = await run_agent(agent, user_prompt,[])

    await assert_criteria(result, [
        "the SQL query correctly calculates average fare by hour of day",
        "the result identifies a specific hour as having the highest average fare",
        "the result includes the actual average fare amount",
    ])

@pytest.mark.asyncio
async def test_evaluate_columns(agent):
    user_prompt = 'How many trips had zero passengers recorded?'
    result = await run_agent(agent, user_prompt,[])

    await assert_criteria(result, [
        "Which columns should appear in the SQL query",
        "In what order should the tools be called",
        "What specific value should the result contain",
        "Which column should the agent's SQL filter on"
    ])