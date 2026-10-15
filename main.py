import dotenv
from sql_tools import setup_database, SQLTools
from sql_agent import create_agent,run_agent,DocumentationAgentConfig,DEFAULT_INSTRUCTIONS

dotenv.load_dotenv('env')

async def run_agent_question():
    agent_config = DocumentationAgentConfig()
    agent_config.instructions=DEFAULT_INSTRUCTIONS
    sqltools = SQLTools()
    result =sqltools.run_sql("SELECT * from trips where passenger_count > 5")
    print(result)
    agent =  create_agent(agent_config,sqltools)
    #query = "What's the average trip distance for rides with 2 passengers?"
    query = "How many trips had more than 5 passengers?"
    answer = await run_agent(agent,query,[])
    print(answer)

if __name__ == "__main__":
    import asyncio
    setup_database()
    
    asyncio.run(run_agent_question())

    