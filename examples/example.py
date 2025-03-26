import asyncio
import json
import logging
from http import HTTPMethod
from time import sleep
from unittest.mock import Mock

import httpx

from spyllm.core import initialize
from spyllm.enums import CommandAction, HookEventType
from spyllm.hooks.http.httpx_hook import HttpxHook
from spyllm.hooks.http.models import HTTPResponseData
from spyllm.hooks.models import HookEvent
from spyllm.models import Command
from spyllm.processing.http_processing import HttpProcessor

#lala = auto_initialize()
#lala.process_data("lala")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

req = {
   "max_tokens":1024,
   "messages":[
      {
         "role":"user",
         "content":"Update vacations dates in HILAN for john doe"
      }
   ],
   "model":"claude-3-5-sonnet-latest",
   "tools":[
      {
         "name":"retrieve_emails",
         "description":"Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.",
         "input_schema":{
            "properties":{
               "employee_name":{
                  "items":{
                     "type":"string"
                  },
                  "type":"array"
               }
            },
            "required":[
               "employee_name"
            ],
            "type":"object"
         }
      },
      {
         "name":"retrieve_vacation_details",
         "description":"Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.",
         "input_schema":{
            "properties":{
               "emails":{
                  "items":{
                     "type":"object"
                  },
                  "type":"array"
               }
            },
            "required":[
               "emails"
            ],
            "type":"object"
         }
      },
      {
         "name":"create_hilan_http_requests",
         "description":"Used to create HTTP requests to the HILAN API in order to submit the requested vacation days",
         "input_schema":{
            "properties":{
               "vacation_details":{
                  "items":{
                     "type":"object"
                  },
                  "type":"array"
               }
            },
            "required":[
               "vacation_details"
            ],
            "type":"object"
         }
      },
      {
         "name":"execute_hilan_http_requests",
         "description":"Used to execute HTTP requests to the HILAN vacation API.",
         "input_schema":{
            "properties":{
               "http_requests":{
                  "items":{
                     "type":"object"
                  },
                  "type":"array"
               }
            },
            "required":[
               "http_requests"
            ],
            "type":"object"
         }
      }
   ]
}

res = {"id":"msg_01ViHSQjFnsztzXso9o2Vnny","type":"message","role":"assistant","model":"claude-3-5-sonnet-latest","content":[{"type":"text","text":"I\'ll help you update vacation dates in HILAN for John Doe. Let me break this down into steps:\\n\\n1. First, I\'ll retrieve emails for John Doe\\n2. Then extract vacation details from those emails\\n3. Create HTTP requests for HILAN\\n4. Finally execute those requests\\n\\nLet\'s start:"},{"type":"tool_use","id":"toolu_01C5zNk5UJqHSp7RmJogfa4t","name":"retrieve_emails","input":{"employee_name":["john doe"]}}],"stop_reason":"tool_use","stop_sequence":None,"usage":{"input_tokens":666,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":128}}

all_requests = [
{'max_tokens': 1024, 'messages': [{'role': 'user', 'content': 'Update vacations dates in HILAN for john doe'}], 'model': 'claude-3-5-sonnet-latest', 'tools': [{'name': 'retrieve_emails', 'description': "Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.", 'input_schema': {'properties': {'employee_name': {'items': {'type': 'string'}, 'type': 'array'}}, 'required': ['employee_name'], 'type': 'object'}}, {'name': 'retrieve_vacation_details', 'description': "Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.", 'input_schema': {'properties': {'emails': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['emails'], 'type': 'object'}}, {'name': 'create_hilan_http_requests', 'description': 'Used to create HTTP requests to the HILAN API in order to submit the requested vacation days', 'input_schema': {'properties': {'vacation_details': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['vacation_details'], 'type': 'object'}}, {'name': 'execute_hilan_http_requests', 'description': 'Used to execute HTTP requests to the HILAN vacation API.', 'input_schema': {'properties': {'http_requests': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['http_requests'], 'type': 'object'}}]}
,{'id': 'msg_01FV8yhkMTWRa3c6oPAiQGzg', 'type': 'message', 'role': 'assistant', 'model': 'claude-3-5-sonnet-latest', 'content': [{'type': 'text', 'text': "I'll help you update vacation dates in HILAN for John Doe. Let me break this down into steps:\n\n1. First, I'll retrieve John Doe's emails to find vacation-related information\n2. Then extract vacation details from those emails\n3. Create and execute HILAN HTTP requests to submit the vacation days\n\nLet's start by retrieving John Doe's emails:"}, {'type': 'tool_use', 'id': 'toolu_011ytLa3coW1E4FceLuTnY8D', 'name': 'retrieve_emails', 'input': {'employee_name': ['John Doe']}}], 'stop_reason': 'tool_use', 'stop_sequence': None, 'usage': {'input_tokens': 666, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'output_tokens': 142}}
,{'max_tokens': 1024, 'messages': [{'role': 'user', 'content': 'Update vacations dates in HILAN for john doe'}, {'role': 'assistant', 'content': [{'text': "I'll help you update vacation dates in HILAN for John Doe. Let me break this down into steps:\n\n1. First, I'll retrieve John Doe's emails to find vacation-related information\n2. Then extract vacation details from those emails\n3. Create and execute HILAN HTTP requests to submit the vacation days\n\nLet's start by retrieving John Doe's emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_emails', 'input': {'employee_name': ['John Doe']}, 'id': 'toolu_011ytLa3coW1E4FceLuTnY8D'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "body": "I would like to request vacation from 2024-02-01 to 2024-02-15"}, {"sender_email": "jane.smith@company.com", "body": "Requesting time off from March 1st, 2024 until March 10th, 2024"}]', 'tool_use_id': 'toolu_011ytLa3coW1E4FceLuTnY8D', 'is_error': False}]}], 'model': 'claude-3-5-sonnet-latest', 'tools': [{'name': 'retrieve_emails', 'description': "Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.", 'input_schema': {'properties': {'employee_name': {'items': {'type': 'string'}, 'type': 'array'}}, 'required': ['employee_name'], 'type': 'object'}}, {'name': 'retrieve_vacation_details', 'description': "Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.", 'input_schema': {'properties': {'emails': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['emails'], 'type': 'object'}}, {'name': 'create_hilan_http_requests', 'description': 'Used to create HTTP requests to the HILAN API in order to submit the requested vacation days', 'input_schema': {'properties': {'vacation_details': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['vacation_details'], 'type': 'object'}}, {'name': 'execute_hilan_http_requests', 'description': 'Used to execute HTTP requests to the HILAN vacation API.', 'input_schema': {'properties': {'http_requests': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['http_requests'], 'type': 'object'}}]}
,{'id': 'msg_017w4PVhWTLjNGEXUkAzzozj', 'type': 'message', 'role': 'assistant', 'model': 'claude-3-5-sonnet-latest', 'content': [{'type': 'text', 'text': "Now, let's extract the vacation details from these emails:"}, {'type': 'tool_use', 'id': 'toolu_01RjdjoREUeBunCSwruPUnhX', 'name': 'retrieve_vacation_details', 'input': {'emails': [{'sender_email': 'john.doe@company.com', 'body': 'I would like to request vacation from 2024-02-01 to 2024-02-15'}, {'sender_email': 'jane.smith@company.com', 'body': 'Requesting time off from March 1st, 2024 until March 10th, 2024'}]}}], 'stop_reason': 'tool_use', 'stop_sequence': None, 'usage': {'input_tokens': 905, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'output_tokens': 155}}
,{'max_tokens': 1024, 'messages': [{'role': 'user', 'content': 'Update vacations dates in HILAN for john doe'}, {'role': 'assistant', 'content': [{'text': "I'll help you update vacation dates in HILAN for John Doe. Let me break this down into steps:\n\n1. First, I'll retrieve John Doe's emails to find vacation-related information\n2. Then extract vacation details from those emails\n3. Create and execute HILAN HTTP requests to submit the vacation days\n\nLet's start by retrieving John Doe's emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_emails', 'input': {'employee_name': ['John Doe']}, 'id': 'toolu_011ytLa3coW1E4FceLuTnY8D'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "body": "I would like to request vacation from 2024-02-01 to 2024-02-15"}, {"sender_email": "jane.smith@company.com", "body": "Requesting time off from March 1st, 2024 until March 10th, 2024"}]', 'tool_use_id': 'toolu_011ytLa3coW1E4FceLuTnY8D', 'is_error': False}]}, {'role': 'assistant', 'content': [{'text': "Now, let's extract the vacation details from these emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_vacation_details', 'input': {'emails': [{'sender_email': 'john.doe@company.com', 'body': 'I would like to request vacation from 2024-02-01 to 2024-02-15'}, {'sender_email': 'jane.smith@company.com', 'body': 'Requesting time off from March 1st, 2024 until March 10th, 2024'}]}, 'id': 'toolu_01RjdjoREUeBunCSwruPUnhX'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "start_date": "2024-02-01", "end_date": "2024-02-15", "total_vacation_days": 14}, {"sender_email": "jane.smith@company.com", "start_date": "2024-03-01", "end_date": "2024-03-10", "total_vacation_days": 9}]', 'tool_use_id': 'toolu_01RjdjoREUeBunCSwruPUnhX', 'is_error': False}]}], 'model': 'claude-3-5-sonnet-latest', 'tools': [{'name': 'retrieve_emails', 'description': "Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.", 'input_schema': {'properties': {'employee_name': {'items': {'type': 'string'}, 'type': 'array'}}, 'required': ['employee_name'], 'type': 'object'}}, {'name': 'retrieve_vacation_details', 'description': "Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.", 'input_schema': {'properties': {'emails': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['emails'], 'type': 'object'}}, {'name': 'create_hilan_http_requests', 'description': 'Used to create HTTP requests to the HILAN API in order to submit the requested vacation days', 'input_schema': {'properties': {'vacation_details': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['vacation_details'], 'type': 'object'}}, {'name': 'execute_hilan_http_requests', 'description': 'Used to execute HTTP requests to the HILAN vacation API.', 'input_schema': {'properties': {'http_requests': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['http_requests'], 'type': 'object'}}]}
,{'id': 'msg_01U8NnfGs93WdNSCYSn4r4gV', 'type': 'message', 'role': 'assistant', 'model': 'claude-3-5-sonnet-latest', 'content': [{'type': 'text', 'text': "Now, let's create the HTTP requests for HILAN:"}, {'type': 'tool_use', 'id': 'toolu_01W5yonhhDyiwLgbjo29G25P', 'name': 'create_hilan_http_requests', 'input': {'vacation_details': [{'sender_email': 'john.doe@company.com', 'start_date': '2024-02-01', 'end_date': '2024-02-15', 'total_vacation_days': 14}]}}], 'stop_reason': 'tool_use', 'stop_sequence': None, 'usage': {'input_tokens': 1172, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'output_tokens': 126}}
,{'max_tokens': 1024, 'messages': [{'role': 'user', 'content': 'Update vacations dates in HILAN for john doe'}, {'role': 'assistant', 'content': [{'text': "I'll help you update vacation dates in HILAN for John Doe. Let me break this down into steps:\n\n1. First, I'll retrieve John Doe's emails to find vacation-related information\n2. Then extract vacation details from those emails\n3. Create and execute HILAN HTTP requests to submit the vacation days\n\nLet's start by retrieving John Doe's emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_emails', 'input': {'employee_name': ['John Doe']}, 'id': 'toolu_011ytLa3coW1E4FceLuTnY8D'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "body": "I would like to request vacation from 2024-02-01 to 2024-02-15"}, {"sender_email": "jane.smith@company.com", "body": "Requesting time off from March 1st, 2024 until March 10th, 2024"}]', 'tool_use_id': 'toolu_011ytLa3coW1E4FceLuTnY8D', 'is_error': False}]}, {'role': 'assistant', 'content': [{'text': "Now, let's extract the vacation details from these emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_vacation_details', 'input': {'emails': [{'sender_email': 'john.doe@company.com', 'body': 'I would like to request vacation from 2024-02-01 to 2024-02-15'}, {'sender_email': 'jane.smith@company.com', 'body': 'Requesting time off from March 1st, 2024 until March 10th, 2024'}]}, 'id': 'toolu_01RjdjoREUeBunCSwruPUnhX'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "start_date": "2024-02-01", "end_date": "2024-02-15", "total_vacation_days": 14}, {"sender_email": "jane.smith@company.com", "start_date": "2024-03-01", "end_date": "2024-03-10", "total_vacation_days": 9}]', 'tool_use_id': 'toolu_01RjdjoREUeBunCSwruPUnhX', 'is_error': False}]}, {'role': 'assistant', 'content': [{'text': "Now, let's create the HTTP requests for HILAN:", 'type': 'text'}, {'type': 'tool_use', 'name': 'create_hilan_http_requests', 'input': {'vacation_details': [{'sender_email': 'john.doe@company.com', 'start_date': '2024-02-01', 'end_date': '2024-02-15', 'total_vacation_days': 14}]}, 'id': 'toolu_01W5yonhhDyiwLgbjo29G25P'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"method": "POST", "url": "https://api.hilan.com/vacation_requests", "body": {"start_date": "2024-02-01", "end_date": "2024-02-15", "total_vacation_days": 14, "employee_email": "john.doe@company.com"}}]', 'tool_use_id': 'toolu_01W5yonhhDyiwLgbjo29G25P', 'is_error': False}]}], 'model': 'claude-3-5-sonnet-latest', 'tools': [{'name': 'retrieve_emails', 'description': "Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.", 'input_schema': {'properties': {'employee_name': {'items': {'type': 'string'}, 'type': 'array'}}, 'required': ['employee_name'], 'type': 'object'}}, {'name': 'retrieve_vacation_details', 'description': "Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.", 'input_schema': {'properties': {'emails': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['emails'], 'type': 'object'}}, {'name': 'create_hilan_http_requests', 'description': 'Used to create HTTP requests to the HILAN API in order to submit the requested vacation days', 'input_schema': {'properties': {'vacation_details': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['vacation_details'], 'type': 'object'}}, {'name': 'execute_hilan_http_requests', 'description': 'Used to execute HTTP requests to the HILAN vacation API.', 'input_schema': {'properties': {'http_requests': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['http_requests'], 'type': 'object'}}]}
,{'id': 'msg_01TBKjUAMKr567TneekAqubu', 'type': 'message', 'role': 'assistant', 'model': 'claude-3-5-sonnet-latest', 'content': [{'type': 'text', 'text': "Finally, let's execute these requests:"}, {'type': 'tool_use', 'id': 'toolu_01N5hvhSos7L2kXHcPsPGeFo', 'name': 'execute_hilan_http_requests', 'input': {'http_requests': [{'method': 'POST', 'url': 'https://api.hilan.com/vacation_requests', 'body': {'start_date': '2024-02-01', 'end_date': '2024-02-15', 'total_vacation_days': 14, 'employee_email': 'john.doe@company.com'}}]}}], 'stop_reason': 'tool_use', 'stop_sequence': None, 'usage': {'input_tokens': 1387, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'output_tokens': 148}}
,{'max_tokens': 1024, 'messages': [{'role': 'user', 'content': 'Update vacations dates in HILAN for john doe'}, {'role': 'assistant', 'content': [{'text': "I'll help you update vacation dates in HILAN for John Doe. Let me break this down into steps:\n\n1. First, I'll retrieve John Doe's emails to find vacation-related information\n2. Then extract vacation details from those emails\n3. Create and execute HILAN HTTP requests to submit the vacation days\n\nLet's start by retrieving John Doe's emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_emails', 'input': {'employee_name': ['John Doe']}, 'id': 'toolu_011ytLa3coW1E4FceLuTnY8D'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "body": "I would like to request vacation from 2024-02-01 to 2024-02-15"}, {"sender_email": "jane.smith@company.com", "body": "Requesting time off from March 1st, 2024 until March 10th, 2024"}]', 'tool_use_id': 'toolu_011ytLa3coW1E4FceLuTnY8D', 'is_error': False}]}, {'role': 'assistant', 'content': [{'text': "Now, let's extract the vacation details from these emails:", 'type': 'text'}, {'type': 'tool_use', 'name': 'retrieve_vacation_details', 'input': {'emails': [{'sender_email': 'john.doe@company.com', 'body': 'I would like to request vacation from 2024-02-01 to 2024-02-15'}, {'sender_email': 'jane.smith@company.com', 'body': 'Requesting time off from March 1st, 2024 until March 10th, 2024'}]}, 'id': 'toolu_01RjdjoREUeBunCSwruPUnhX'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"sender_email": "john.doe@company.com", "start_date": "2024-02-01", "end_date": "2024-02-15", "total_vacation_days": 14}, {"sender_email": "jane.smith@company.com", "start_date": "2024-03-01", "end_date": "2024-03-10", "total_vacation_days": 9}]', 'tool_use_id': 'toolu_01RjdjoREUeBunCSwruPUnhX', 'is_error': False}]}, {'role': 'assistant', 'content': [{'text': "Now, let's create the HTTP requests for HILAN:", 'type': 'text'}, {'type': 'tool_use', 'name': 'create_hilan_http_requests', 'input': {'vacation_details': [{'sender_email': 'john.doe@company.com', 'start_date': '2024-02-01', 'end_date': '2024-02-15', 'total_vacation_days': 14}]}, 'id': 'toolu_01W5yonhhDyiwLgbjo29G25P'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': '[{"method": "POST", "url": "https://api.hilan.com/vacation_requests", "body": {"start_date": "2024-02-01", "end_date": "2024-02-15", "total_vacation_days": 14, "employee_email": "john.doe@company.com"}}]', 'tool_use_id': 'toolu_01W5yonhhDyiwLgbjo29G25P', 'is_error': False}]}, {'role': 'assistant', 'content': [{'text': "Finally, let's execute these requests:", 'type': 'text'}, {'type': 'tool_use', 'name': 'execute_hilan_http_requests', 'input': {'http_requests': [{'method': 'POST', 'url': 'https://api.hilan.com/vacation_requests', 'body': {'start_date': '2024-02-01', 'end_date': '2024-02-15', 'total_vacation_days': 14, 'employee_email': 'john.doe@company.com'}}]}, 'id': 'toolu_01N5hvhSos7L2kXHcPsPGeFo'}]}, {'role': 'user', 'content': [{'type': 'tool_result', 'content': 'null', 'tool_use_id': 'toolu_01N5hvhSos7L2kXHcPsPGeFo', 'is_error': False}]}], 'model': 'claude-3-5-sonnet-latest', 'tools': [{'name': 'retrieve_emails', 'description': "Used to retrieve emails from the company's email server. If employee_name is empty, retrieve all emails.", 'input_schema': {'properties': {'employee_name': {'items': {'type': 'string'}, 'type': 'array'}}, 'required': ['employee_name'], 'type': 'object'}}, {'name': 'retrieve_vacation_details', 'description': "Used to extract vacation details from emails. The input is a list of email objects, consisting of the sender's email and the email body.", 'input_schema': {'properties': {'emails': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['emails'], 'type': 'object'}}, {'name': 'create_hilan_http_requests', 'description': 'Used to create HTTP requests to the HILAN API in order to submit the requested vacation days', 'input_schema': {'properties': {'vacation_details': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['vacation_details'], 'type': 'object'}}, {'name': 'execute_hilan_http_requests', 'description': 'Used to execute HTTP requests to the HILAN vacation API.', 'input_schema': {'properties': {'http_requests': {'items': {'type': 'object'}, 'type': 'array'}}, 'required': ['http_requests'], 'type': 'object'}}]}
,{'id': 'msg_01TCoJd9fVYLxR1A3yhMv7py', 'type': 'message', 'role': 'assistant', 'model': 'claude-3-5-sonnet-latest', 'content': [{'type': 'text', 'text': "I've completed the process of updating John Doe's vacation dates in HILAN. Based on the emails, the following vacation request has been submitted:\n- Start date: February 1st, 2024\n- End date: February 15th, 2024\n- Total vacation days: 14\n\nThe request has been successfully processed in HILAN. Is there anything else you need assistance with?"}], 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 1547, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'output_tokens': 90}}
]

def moshe():
    spyllm = initialize()
    import time

    #time.sleep(2)
    #spyllm.send_command("lala", {"moshe": "lala"})
    #response = spyllm.send_command_wait("lala", {"moshe": "lala"})
    #print(response)
    for r in [req]:
        httpx.post('https://httpbin.org/post', json=req)
        time.sleep(2)
    
    sleep(200)

if __name__ == "__main__":
    #asyncio.run(main())
    #main_sync()
    moshe()
    

