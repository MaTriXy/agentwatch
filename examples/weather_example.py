import datetime
import logging
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Uncomment this to use agentwatch
#import agentwatch

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
load_dotenv()

@tool
def get_current_date() -> str:
    """
    Used to get the current date.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")

@tool
def get_coords_for_city(city_name: str) -> dict[str, Any]:
    """
    Used to get the latitude and longitude for a specific city by it's name.
    """
    return {
        "lat": 40.7128,
        "lon": -74.0060
    }

@tool
def get_weather(coords: dict[str, float], date: str) -> dict[str, Any]:
    """
    Used to get the weather for a coordinate on a specific date.
    """
    return {
        "date": date,
        "temperature": 72,
        "weather": "Sunny"
    }

tools = [get_current_date, get_coords_for_city, get_weather]

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, AIMessage):
            if message.content:
                print(message.content)

if __name__ == "__main__":
    model = ChatOpenAI(model="gpt-4o-2024-08-06")
    graph = create_react_agent(model, tools=tools)
    
    question = "What is the weather today in San Francisco?"
    inputs = {"messages": [("user", question)]}

    print_stream(graph.stream(inputs, stream_mode="values"))

