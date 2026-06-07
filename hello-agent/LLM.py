from openai import OpenAI

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端
    """
    def __init__(self, model:str, api_key:str, base_url:str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt:str, system_prompt:str) -> str:
        """"调用LLM API来生成回应"""
        print("正在调用大语言模型生成回答...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content.strip()
            print("大语言模型响应成功")
            return answer
        except Exception as e:
            print(f"调用大语言模型时发生错误: {e}")
            return "抱歉，无法生成回答。"