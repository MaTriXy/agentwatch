import logging
from time import sleep
from typing import Any

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

import agentspy

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@tool
def retrieve_emails(employee_name: list[str]) -> list[dict[str, Any]]:
    """
    Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.
    """
    sleep(6)
    return [
        {
            "sender_email": "john.doe@company.com",
            "body": "I would like to request vacation from 2024-02-01 to 2024-02-15"
        },
        {
            "sender_email": "jane.smith@company.com",
            "body": "Requesting time off from March 1st, 2024 until March 10th, 2024"
        }
    ]

@tool
def retrieve_vacation_details(emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.
    """
    sleep(5)
    result = [
        {
            "sender_email": "john.doe@company.com",
            "start_date": "2024-02-01",
            "end_date": "2024-02-15",
            "total_vacation_days": 14
        },
        {
            "sender_email": "jane.smith@company.com",
            "start_date": "2024-03-01",
            "end_date": "2024-03-10",
            "total_vacation_days": 9
        }
    ]
    return result

@tool
def create_hr_system_http_requests(vacation_details: list[dict[str, Any]]) -> list[str]:
    """
    Used to create HTTP requests to the HR SYSTEM API in order to submit the requested vacation days 
    """
    results = []
    for details in vacation_details:
        start_date = details["start_date"]
        end_date = details["end_date"]
        total_vacation_days = details["total_vacation_days"]
        print(f"Requesting vacation from {start_date} to {end_date} for a total of {total_vacation_days} days")
        results.append({
            "method": "POST",
            "url": "https://api.hr.com/vacation_requests",
            "body": {
                "start_date": start_date,
                "end_date": end_date,
                "total_vacation_days": total_vacation_days,
                "employee_email": details["sender_email"]
            }
        })
    
    return results

@tool
def execute_hr_system_http_requests(http_requests: list[dict[str, Any]]) -> None:
    """
    Used to execute HTTP requests to the HR SYSTEM vacation API.
    """
    sleep(10)

    for request in http_requests:
        method = request["method"]
        url = request["url"]
        body = request["body"]
        print(f"Sending {method} request to {url} with body: {body}")


tools = [retrieve_emails, retrieve_vacation_details, create_hr_system_http_requests, execute_hr_system_http_requests]
#tools = [retrieve_emails]

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            pass

load_dotenv()

if __name__ == "__main__":
    # Choose between Ollama, Anthropic or OpenAI
    
    #model = ChatOllama(model="llama3.1")
    #model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
    model = ChatOpenAI(model="gpt-4o-2024-08-06")

    graph = create_react_agent(model, tools=tools)
    inputs = {"messages": [("user", "Retrieve emails for user John Doe and update his vacation dates in HR SYSTEM")]}
    print_stream(graph.stream(inputs, stream_mode="values"))

    sleep(99999)
