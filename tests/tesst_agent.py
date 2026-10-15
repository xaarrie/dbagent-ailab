import dotenv
dotenv.load_dotenv('env')
import pytest
from time import time

from sql_agent import DocumentationAgentConfig, DEFAULT_INSTRUCTIONS,create_agent,run_agent,SQLResult
from utils import collect_tools
from sql_tools import SQLTools

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
async def test_more_than_5_passengers(agent):    
    user_prompt = 'How many trips had more than 5 passengers?'
    result = await run_agent(agent, user_prompt, [])
    assert result.sql_query is not None
    assert  22413 in result.result_text

@pytest.mark.asyncio
async def test_most_common_oayment(agent):    
    user_prompt = 'What is the most common payment type?'
    result = await run_agent(agent, user_prompt,[])
    tools = collect_tools(result.new_messages())
    get_schema = tools[0]
    assert get_schema.name == 'get_schema'
    assert any(tool.name == "run_sql" for tool in tools)
    
    
