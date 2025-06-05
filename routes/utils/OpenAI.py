from openai import OpenAI

class OpenRouterClient:
    def __init__(self, api_key: str, referer: str = "", title: str = ""):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.headers = {
            "HTTP-Referer": referer,
            "X-Title": title,
        }

    def call_llm(self, query: str, tools: list = None, model: str = "openai/gpt-3.5-turbo"):
        messages = [{"role": "user", "content": query}]
        params = {
            "model": model,
            "messages": messages,
            "extra_headers": self.headers
        }

        if tools:
            params["tools"] = tools
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