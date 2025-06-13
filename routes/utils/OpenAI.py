from openai import OpenAI

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        # self.headers = {
        #     "HTTP-Referer": referer,
        #     "X-Title": title,
        # }

    def call_llm(self, messages: list, tools: list = None, model: str = "openai/gpt-3.5-turbo"):

        params = {
            "model": model,
            "messages": messages,
        }

        if tools:
        # Ensure tools are formatted with the required "type" key
            formatted_tools = []
            for tool in tools:
                formatted_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                formatted_tools.append(formatted_tool)
            params["tools"] = formatted_tools
            params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**params)
        message = response.choices[0].message

        if hasattr(message, "tool_calls") and message.tool_calls:
            print("🔧 Tool call detected!")
            for call in message.tool_calls:
                print("Tool name:", call.function.name)
                print("Arguments:", call.function.arguments)
        else:
            print("No tool call. Assistant replied with text.")

        return message
    
# if __name__ == "__main__":
#     import os
#     from dotenv import load_dotenv

#     load_dotenv()
#     api_key = "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"  # Make sure your .env file contains this

#     if not api_key:
#         raise ValueError("Please set the OPENROUTER_API_KEY in your .env file")

#     client = OpenRouterClient(api_key)

#     # Basic prompt
#     query = "What's the capital of France?"

#     # Optional: Dummy tools structure for testing
#     # tools = [
#     #     {
#     #         "type": "function",
#     #         "function": {
#     #             "name": "get_weather",
#     #             "description": "Get the weather information for a city",
#     #             "parameters": {
#     #                 "type": "object",
#     #                 "properties": {
#     #                     "city": {"type": "string"},
#     #                 },
#     #                 "required": ["city"],
#     #             },
#     #         },
#     #     }
#     # ]

#     # Run with or without tools
#     response = client.call_llm(query)  # , tools=tools for testing tool call

#     print("\n📨 Response:")
#     print(response)