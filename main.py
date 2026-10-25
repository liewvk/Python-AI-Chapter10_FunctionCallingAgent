import asyncio
from decimal import Decimal

from openai import AsyncOpenAI

from semantic_kernel import Kernel

from semantic_kernel.functions import kernel_function

from semantic_kernel.contents import ChatHistory

from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion
)

from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior
)


MODEL = "qwen3.5:9b"
OLLAMA_URL = "http://localhost:11434/v1"


class ShopTools:

    PRODUCTS = {
        "laptop": ("3500.00", 15),
        "monitor": ("850.00", 30),
        "keyboard": ("120.00", 8)
    }

    def __init__(self):
        self.calls = 0

    @kernel_function(
        name="get_product",
        description=(
            "Look up the price and available stock "
            "of a product by its name."
        )
    )
    def get_product(self, product_name: str) -> str:

        self.calls += 1

        print("[Python tool executed: get_product]")

        key = product_name.strip().lower()

        item = self.PRODUCTS.get(key)

        if item is None:
            return "Product not found in the sample catalog."

        price, stock = item

        return (
            f"{key.title()}: RM{Decimal(price):,.2f}; "
            f"stock: {stock} units"
        )

    @kernel_function(
        name="calculate_total",
        description=(
            "Calculate the total cost of a product "
            "using its name and requested quantity."
        )
    )
    def calculate_total(
        self,
        product_name: str,
        quantity: int
    ) -> str:

        self.calls += 1

        print("[Python tool executed: calculate_total]")

        key = product_name.strip().lower()

        item = self.PRODUCTS.get(key)

        if item is None:
            return "Product not found in the sample catalog."

        if type(quantity) is not int or not 1 <= quantity <= 20:
            return "Quantity must be an integer from 1 to 20."

        price, stock = item

        if quantity > stock:
            return "Insufficient stock for this quantity."

        total = Decimal(price) * quantity

        return (
            f"{quantity} x {key.title()} "
            f"= RM{total:,.2f}"
        )


async def main():

    client = AsyncOpenAI(
        base_url=OLLAMA_URL,
        api_key="ollama",
        timeout=600,
        max_retries=0
    )

    kernel = Kernel()

    tools = ShopTools()

    kernel.add_plugin(
        tools,
        plugin_name="Shop"
    )

    chat = OpenAIChatCompletion(
        ai_model_id=MODEL,
        service_id="local",
        async_client=client
    )

    kernel.add_service(chat)

    settings = (
        kernel.get_prompt_execution_settings_from_service_id(
            "local"
        )
    )

    settings.temperature = 0.1
    settings.max_tokens = 500

    settings.extra_body = {
        "reasoning_effort": "none"
    }

    settings.function_choice_behavior = (
        FunctionChoiceBehavior.Auto(
            filters={
                "included_plugins": ["Shop"]
            },
            maximum_auto_invoke_attempts=3
        )
    )

    history = ChatHistory(
        system_message=(
            "You are a retail product assistant. "
            "For product prices, stock, or purchase totals, "
            "use the available Shop functions. "
            "Never invent product information. "
            "Do not claim that orders have been placed."
        )
    )

    print("PYTHON FUNCTION-CALLING AGENT")
    print("Model:", MODEL)
    print("Products: Laptop, Monitor, Keyboard")
    print("Type /exit to quit.")

    try:
        while True:

            question = input("\nYou: ").strip()

            if question.lower() == "/exit":
                break

            if not question:
                continue

            if len(question) > 500:
                print("Question is too long.")
                continue

            history.add_user_message(question)

            previous_calls = tools.calls

            try:
                response = await chat.get_chat_message_content(
                    chat_history=history,
                    settings=settings,
                    kernel=kernel
                )

                answer = (
                    response.content
                    if response is not None
                    else ""
                ) or ""

                if tools.calls == previous_calls:
                    print(
                        "[No Python tool was executed. "
                        "Product facts are unverified.]"
                    )

                print("\nAssistant:", answer or "(No answer)")

                if answer:
                    history.add_assistant_message(answer)

            except Exception as ex:
                print("Request failed:", ex)
                print("Start a fresh session if context is inconsistent.")
                history = ChatHistory(
                    system_message=(
                        "You are a retail assistant. "
                        "Use Shop functions for product facts."
                    )
                )

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

