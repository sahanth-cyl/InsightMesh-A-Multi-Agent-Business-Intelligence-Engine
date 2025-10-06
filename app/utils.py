import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from langchain_anthropic import ChatAnthropic
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global configuration variables
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
DATABASE_FILE_PATH = os.getenv("DATABASE_FILE_PATH")

ANTHROPIC_CONFIG = {
    'model': os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
    'anthropic_api_key': os.getenv("ANTHROPIC_API_KEY"),
    'temperature': float(os.getenv("TEMPERATURE", 0)),
    'max_retries': int(os.getenv("MAX_RETRIES", 3))
}

##############################################################################
# Name : initialize_database_components
# Description : Initializes database, LLM, and agents for the application
# Parameters : None
# Return Values : Tuple containing (df, db, llm, agent_executor_SQL, pandas_agent)
#############################################################################
def initialize_database_components():
    logger.info("Initializing database components...") 

    """Initialize all database and AI components."""
    try:
        df, db = setup_database(CSV_FILE_PATH, DATABASE_FILE_PATH)
        llm = setup_llm(ANTHROPIC_CONFIG)
        agent_executor_SQL, pandas_agent = setup_agents(llm, db, df)
        logger.info("Database components initialized successfully!")
        return df, db, llm, agent_executor_SQL, pandas_agent
    except Exception as e:
        logger.error(f"Failed to initialize database components: {e}")
        raise

##############################################################################
# Name : setup_database
# Description : Setup SQLite database and load CSV data
# Parameters : 
#     csv_file_path (str): Path to the CSV file
#     database_file_path (str): Path to the SQLite database file
# Return Values : Tuple containing (DataFrame, SQLDatabase)
#############################################################################
def setup_database(csv_file_path, database_file_path):
    """Setup SQLite database and load CSV data."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(database_file_path), exist_ok=True)
        
        df = pd.read_csv(csv_file_path, low_memory=False).fillna(value=0)
        engine = create_engine(f'sqlite:///{database_file_path}')
        df.to_sql('all_states_history', con=engine, if_exists='replace', index=False)
        db = SQLDatabase.from_uri(f'sqlite:///{database_file_path}')
        
        logger.info(f"Database setup complete. Loaded {len(df)} records.")
        return df, db
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

##############################################################################
# Name : setup_llm
# Description : Initialize Anthropic LLM
# Parameters : 
#     anthropic_config (dict): Configuration dictionary for Anthropic
# Return Values : ChatAnthropic instance
#############################################################################
def setup_llm(anthropic_config):
    """Initialize Anthropic LLM."""
    try:
        return ChatAnthropic(
            model=anthropic_config['model'],
            anthropic_api_key=anthropic_config['anthropic_api_key'],
            temperature=anthropic_config['temperature'],
            max_retries=anthropic_config['max_retries']
        )
    except Exception as e:
        logger.error(f"Error setting up LLM: {e}")
        raise

##############################################################################
# Name : setup_agents
# Description : Setup SQL and Pandas agents
# Parameters : 
#     llm: Language model instance
#     db: SQL database instance
#     df: Pandas DataFrame
# Return Values : Tuple containing (SQL agent, Pandas agent)
#############################################################################
def setup_agents(llm, db, df):
    """Setup SQL and Pandas agents."""
    try:
        # Gather schema details using SQLAlchemy inspection
        table_names = db.get_table_names()
        schema_details = []
        # Get engine from db
        engine = create_engine(db._engine.url)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        for table in table_names:
            columns = [col['name'] for col in inspector.get_columns(table)]
            schema_details.append(f"Table: {table}\nColumns: {', '.join(columns)}")
        schema_str = '\n'.join(schema_details)
        # ...existing code...
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        MSSQL_AGENT_PREFIX = f"""
You are an agent designed to interact with a SQL database.
## Database Schema:
{schema_str}
## Instructions:
- ONLY respond in the format specified below. Do NOT provide general conversation, apologies, or explanations outside the format.
- If the user input is not a valid database question, respond with: 'Final Answer: Please ask a specific database-related question.'
- Never include both a Final Answer and an Action in the same response. Only provide one at a time as per the format below.
- Analyze the response while ensuring calculations consider distinct employees in all cases when mostly applicable.
- Given an input question, create a syntactically correct {{dialect}} query to run, then look at the results of the query and return the answer.
- Unless the user specifies a specific number of examples they wish to obtain, **ALWAYS** limit your query to at most {{top_k}} results.
- You can order the results by a relevant column to return the most interesting examples in the database.
- Never query for all the columns from a specific table, only ask for the relevant columns given the question.
- You have access to tools for interacting with the database.
- You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
- DO NOT make up an ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE.
"""
        MSSQL_AGENT_FORMAT_INSTRUCTIONS = """
## Use the following format (do NOT deviate):
Question: the input question you must answer.
Thought: you should always think about what to do.
Action: the action to take, should be one of [{tool_names}].
Action Input: the input to the action.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Final Answer: the final answer to the original input question.
## If the user input is not a valid database question, respond ONLY with:
Final Answer: Please ask a specific database-related question.
"""
        agent_executor_SQL = create_sql_agent(
            prefix=MSSQL_AGENT_PREFIX,
            format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
            llm=llm,
            toolkit=toolkit,
            top_k=30,
            verbose=True,
            handle_parsing_errors=True
        )
        pandas_agent = create_pandas_dataframe_agent(
            llm=llm,
            df=df,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True
        )
        logger.info("Agents setup successfully!")
        return agent_executor_SQL, pandas_agent
    except Exception as e:
        logger.error(f"Error setting up agents: {e}")
        raise
        
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent_executor_SQL = create_sql_agent(
            prefix=MSSQL_AGENT_PREFIX,
            format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
            llm=llm,
            toolkit=toolkit,
            top_k=30,
            verbose=True,
            handle_parsing_errors=True
        )
        
        pandas_agent = create_pandas_dataframe_agent(
            llm=llm,
            df=df,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True
        )
        
        logger.info("Agents setup successfully!")
        return agent_executor_SQL, pandas_agent
    except Exception as e:
        logger.error(f"Error setting up agents: {e}")
        raise

##############################################################################
# Name : decision_prompt
# Description : Decides whether to return a text response or generate a plot
# Parameters : 
#     user_question (str): The user's question
#     initial_response (str): Initial response from SQL agent
#     pandas_agent: Pandas agent instance
# Return Values : Decision result as string
#############################################################################
def decision_prompt(user_question, initial_response, pandas_agent):
    """Decides whether to return a text response or generate a plot."""
    prompt_temp = """
    You are a helpful AI assistant expert that writes Python scripts to analyze data and generate plots.
    Your task is to analyze the data and write a Python script to create the appropriate plot based on the user's question.
    Always consider distinct employee numbers in all cases when mostly applicable while calculating metrics like gender distribution, number of associates left, and joined.

    1. **Text**: If the response requires explanation, reasoning, or is more understandable as text or if explicitly asked for text give textual answer only.
    2. **Plot**: If the response involves numerical comparisons, distributions, or trends that would be clearer as a visual plot.
    Follow a structured approach:

    Question: {user_question}
    Response: '{initial_response}'

    Thought: you should always think about what to do, what action to take.
    - Analyze the response while ensuring calculations consider distinct employees in all cases when mostly applicable.
    - If the response is numeric-based (e.g., counts, trends, comparisons), a plot is more suitable.
    - If it requires detailed analysis or explanation, a text-based response is better.

    Action: Decide whether the response should be:
    1. **Text response**
    2. **Plot**

    If a **plot** is chosen:
    Thought: you should always think about what to do, what action to take

    Action: python_repl_ast
    Action Input: the input to the action, never add backticks "" around 
    the action input. When using aggregate functions such as sum, ensure 
    to use the correct number of parenthesis. Always check the required 
    number of parenthesis. Before using plt.show(), save the image 
    using plt.savefig('img.png') and then close the plot with plt.close(). 
    Make sure the name is 'img.png'.After saving the plot, print("PLOT_SAVED").
    If you encounter errors related to brackets more than once, change your 
    approach and start from scratch.
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question.
    """
    
    prompt = prompt_temp.format(user_question=user_question, initial_response=initial_response)
    
    try:
        decision = pandas_agent.invoke(prompt, handle_parsing_errors=True)
        if isinstance(decision, dict) and 'output' in decision:
            decision = decision['output']
    except ValueError as e:
        logger.error(f"An error occurred while deciding: {e}")
        decision = "Error in decision-making process."
    
    return decision.strip()


##############################################################################
# Name : process_chat_query
# Description : Main chat function that processes user questions and generates responses/plots
# Parameters : 
#     question (str): User's question
#     agent_executor_SQL: SQL agent instance
#     pandas_agent: Pandas agent instance
# Return Values : Final answer as string and path to generated image (if any)
#############################################################################
def process_chat_query(question, agent_executor_SQL, pandas_agent):
    """Main chat function that processes user questions and generates responses/plots."""
    logger.info(f"Processing question: {question}")
    
    # Clean up any existing image
    if os.path.exists('img.png'):
        os.remove('img.png')
    
    # Fetch Initial Response from SQL Agent
    try:
        initial_response = agent_executor_SQL.invoke(question, handle_parsing_errors=True)
    except ValueError as e:
        logger.error(f"An error occurred: {e}")
        initial_response = agent_executor_SQL.invoke(question, handle_parsing_errors=True)

    # Ensure the output is correctly formatted
    if isinstance(initial_response, dict) and 'output' in initial_response:
        initial_response = initial_response['output']

    initial_response = str(initial_response).strip()
    logger.info(f"Initial SQL response: {initial_response}")

    # Decision Making Process
    try:
        decision = decision_prompt(question, initial_response, pandas_agent)
    except ValueError as e:
        logger.error(f"An error occurred while deciding: {e}")
        decision = decision_prompt(question, initial_response, pandas_agent)  # Retry

    # Extract Final Answer
    if "Final Answer:" in decision:
        final_answer = decision.split("Final Answer:")[1].strip()
    else:
        final_answer = decision
    
    # Check if a plot was generated
    image_path = None
    if os.path.exists('img.png'):
        image_path = 'img.png'
        logger.info("Plot saved as 'img.png'")
    
    logger.info(f"Final Answer: {final_answer}")
    return final_answer, image_path

##############################################################################
# Name : validate_configuration
# Description : Validates that all required configuration is present
# Parameters : None
# Return Values : Boolean indicating if configuration is valid
#############################################################################
def validate_configuration():
    """Validates that all required configuration is present."""
    required_configs = [
        'ANTHROPIC_MODEL',
        'ANTHROPIC_API_KEY'
    ]
    
    missing_configs = []
    for config in required_configs:
        if not os.getenv(config):
            missing_configs.append(config)
    
    if missing_configs:
        logger.error(f"Missing required environment variables: {missing_configs}")
        return False
    
    if not os.path.exists(CSV_FILE_PATH):
        logger.error(f"CSV file not found: {CSV_FILE_PATH}")
        return False
    
    return True