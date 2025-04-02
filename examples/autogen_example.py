import logging
import os
import time
from typing import Annotated, Literal

import autogen
from dotenv import load_dotenv

from agentwatch.core import initialize

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

Operator = Literal["+", "-", "*", "/"]

ollama_config_list = [
{
    "model": "llama3.1",
    "base_url": "http://127.0.0.1:11434/v1",
    "api_key": "ollama"
}]

claude_config_list = [{
    "model": "claude-3-5-sonnet-20240620",
    "api_key": os.environ["ANTHROPIC_API_KEY"],
    "api_type": "anthropic"
}
]

llm_config = {
    "config_list": claude_config_list, # Or use ollama_config_list
    "timeout": 120,
}

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="For currency exchange tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)


CurrencySymbol = Literal["USD", "EUR"]


def exchange_rate(base_currency: CurrencySymbol, quote_currency: CurrencySymbol) -> float:
    if base_currency == quote_currency:
        return 1.0
    elif base_currency == "USD" and quote_currency == "EUR":
        return 1 / 1.1
    elif base_currency == "EUR" and quote_currency == "USD":
        return 1.1
    else:
        raise ValueError(f"Unknown currencies {base_currency}, {quote_currency}")


@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Currency exchange calculator.")
def currency_calculator(
    base_amount: Annotated[float, "Amount of currency in base_currency"],
    base_currency: Annotated[CurrencySymbol, "Base currency"] = "USD",
    quote_currency: Annotated[CurrencySymbol, "Quote currency"] = "EUR",
) -> str:
    quote_amount = exchange_rate(base_currency, quote_currency) * base_amount
    return f"{quote_amount} {quote_currency}"

if __name__ == "__main__":
    initialize()

    chat_result = user_proxy.initiate_chat(chatbot, message="How much is 123.45 USD in EUR?", summary_method="reflection_with_llm")

    time.sleep(30)