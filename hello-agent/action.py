import os
import re

from LLM import OpenAICompatibleClient
from prompt import AGENT_SYSTEM_PROMPT
from tools封装 import available_tools

# 1.配置LLM客户端
API_KEY = "你自己的api_key"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
MODEL_ID = "glm-4-0520" #可以根据你的实际情况来修改模型
TAVILY_API_KEY = "你自己的tavily_api_key"
os.environ["TAVILY_API_KEY"] = "你自己的tavily_api_key"

llm = OpenAICompatibleClient(
    model = MODEL_ID,
    api_key = API_KEY,
    base_url = BASE_URL
)

# 2.初始化
user_prompt = "你好，请帮我查询一下今天长沙的天气，如何根据天气推荐一个合适的旅游景点"
prompt_history = [f'用户请求：{user_prompt}']

print(f"用户输入: {user_prompt}\n" + "="*40)

# 3.运行主循环
for i in range(5):
    print(f"=== 循环第 {i+1} 轮 ===\n")

    # 3.1 构建prompt
    full_prompt = "\n".join(prompt_history)

    # 3.2 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)

    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)( ≥\n\s*( :Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)

    # 3.3 解析并执行行动
    action_match = re.search(r"Action:(.*)",llm_output, re.DOTALL)
    if not action_match:
        if not action_match:
            observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循'Thought: … Action: …' 的格式。"
            observation_str = f"Observation: {observation}"
            print(f"{observation_str}\n" + "="*40)
            prompt_history.append(observation_str)
            continue
    action_str = action_match.group(1).strip()

    # if action_str.startswith("Finish"):
    #     final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
    #     print(f"任务完成，最终答案: {final_answer}")
    #     break

    if action_str.startswith("Finish"):
        # 修复：用search匹配（不强制开头）+ 容错处理 + 提取内容
        result = re.search(r"Finish\[(.*?)\]", action_str)
        if result:
            final_answer = result.group(1).strip()
            print(f"任务完成，最终答案: {final_answer}")
        else:
            final_answer = action_str.replace("Finish", "").strip("[] ")
            print(f"任务完成，最终答案: {final_answer}")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误:未定义的⼯具 '{tool_name}'"

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)
