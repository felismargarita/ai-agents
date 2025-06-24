from fastapi import FastAPI
from reminderModel import Item
from openai import OpenAI
from fastmcp import Client
import json
import uvicorn
from ali_map_mcp import amap_session
from cover_mcp_ali2deepseek import cover_mcp_ali2deepseek
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_URL")
)

async def recursive_call_tool(messages, tools, session):
  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,  # 关键：传入工具定义
    tool_choice="auto"  # 让模型自主决定是否调用工具
  )
  message = response.choices[0].message
  tool_calls = message.tool_calls
  if not tool_calls:
    print("The model did not request any tool calls.")
    if message.content:
        print(f"Final response: {message.content}")
    return message.content
  for call in tool_calls:
    print(call.function.name)
    args = json.loads(call.function.arguments)
    res = await session.call_tool(call.function.name, args)
    print(res)
    result = res.content[0].text
    messages.append({
      "role": "assistant",
      "content": None,
      "tool_calls": [
          {
              "id": call.id,
              "type": "function",
              "function": {
                  "name": call.function.name,
                  "arguments": (
                    call.function.arguments
                    if isinstance(call.function.arguments, str)
                    else json.dumps(call.function.arguments)
                )
              }
          }
      ]
    })
    messages.append({"role": "tool", "content": result, "tool_call_id": call.id})
  return await recursive_call_tool(messages, tools, session)

  

@app.post("/plan")
async def plan(body: Item):
    async with amap_session() as session:
      tools = await session.list_tools()
      # 调用DeepSeek并启用工具调用
      userPrompt = f"我在{body.start},准备去{body.destination},我的性别是{body.gender},年龄是{body.age}, 根据当时的天气和我的个人画像和行程距离,规划一个最合适的出行方案"
      systemPrompt = """
      你是一个专业的出行规划师，请根据用户的需求，给出最优的出行方案.

      返回格式要求:
      - 只返回有效的JSON字符串
      - 禁止使用Markdown代码块包裹,比如 ```json xxxxx ```这种格式
      - 不要包含任何额外文本

      客观考量:
      - 此次是单人出行
      - 严格保证安全性的前提下做出谨慎规划
      - 如果客观情况不佳或者出行人年龄过大或者过小,可拒绝做出具体安排,并在reason字段中说明原因

      返回的JSON对象需要包含以下字段:
      - reason: 规划理由, 类型为字符串
      - start: 出发地, 类型为字符串
      - destination: 目的地, 类型为字符串
      - gender: 性别, 类型为字符串
      - age: 年龄, 类型为数字
      - vehicle: 交通工具, 类型为字符串, 交通工具必须是具体的内容,比如自行车或者自行车或者高铁等等,或者是它们的组合
      - steps: 出行步骤, 类型为字符串数组
      """
      messages = [
        {"role": "user", "content": userPrompt },
        {"role": "system", "content": systemPrompt }
        ]
      result = await recursive_call_tool(messages, cover_mcp_ali2deepseek(tools.tools), session)
      return json.loads(result)

    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)