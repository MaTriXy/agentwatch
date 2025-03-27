import logging

logging.basicConfig(level="WARNING")

from typing import Any

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool

import spyllm

logger = logging.getLogger(__name__)

ollama_llm = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434"
)


# Define dummy tools
@tool("Execute python code")
def execute_code(code: Any) -> str:
    """Python REPL tool used to execute code"""
    print("X" * 50)
    print("EXECUTING CODEEE")
    print("X" * 50)
    # In a real implementation, this would use a search API
    return "7"

# Define agents
code_agent = Agent(
    role="Coding Specialist",
    goal="Executes Python code snippets",
    backstory="""You are a specialist in executing Python code snippets.
    Your knowledge of Python is unparalleled, and you can quickly and efficiently""",
    verbose=True,
    allow_delegation=True,
    tools=[execute_code],
    llm=ollama_llm
)


# Define tasks
code_task = Task(
    description="""Create and execute python code to calculate prime numbers""",
    expected_output="4th prime number",
    agent=code_agent
)

# Set up the crew
crew = Crew(
    agents=[code_agent],
    tasks=[code_task],
    verbose=True,
    process=Process.sequential  # Tasks will be executed in sequence
)


# Execute the crew's tasks
def main():
    logger.info("Starting CrewAI demo execution")
    try:
        result = crew.kickoff()

        # Properly handle the CrewOutput object
        if hasattr(result, 'raw'):
            # If result has a raw attribute, log a preview of it
            result_str = str(result.raw)
            preview = result_str[:200] + "..." if len(result_str) > 200 else result_str
            logger.info(f"Result preview: {preview}")
        else:
            # Otherwise, log the string representation of the result
            logger.info(f"Result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error during CrewAI execution: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()