from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import uvicorn
from fastmcp import Client
from fastapi.middleware.cors import CORSMiddleware
from cover_mcp_ali2deepseek import cover_mcp_ali2deepseek
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_URL")
)

app = FastAPI()

@app.get('/')
async def test():
  messages = [
    {
      "role": "system",
      "content": '''
          你是一个报表管理专家, 非常擅长通过执行mysql的sql做数据统计.
          - 每次执行数据查询语言之前必须查询数据库的表结构和comments
          - 根据数据库的表结构和字段的comments来制定后续的查询sql语句
        '''
    },
    {
      "role": "user",
      "content": '''
          帮我查询公司的原材料库存数据, 根据已有的数据, 评估工人的劳动情况, 分析劳工工作负荷, 指定休假建议
          - 通过入库时间判断工人的工作情况是否合理, 正常的工作时间是工作日的9:00 - 18:00
          - 由于库存数量较多你每次取1000条进行处理, 计算分析并得出阶段性结论
          - 无需向我确认,直接继续分析后续1000条物料
          - 分析完毕后统一输出结论, 结论要是落实到具体的员工, 给出具体休假计划
        '''
    }
  ]
          # 帮我查询公司的原材料库存数据, 根据已有的数据, 综合分析可能潜在的物料风险

  async with Client(os.getenv("INTERNAL_MCP_URL")) as mcp_client:
    mcp_tools = await mcp_client.list_tools()
    while True:
      response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=cover_mcp_ali2deepseek(mcp_tools),
        tool_choice="auto"
      )
      res_message = response.choices[0].message
      print(response.choices)
      if not res_message.tool_calls:
        return res_message.content
      for call in res_message.tool_calls:
        fnName = call.function.name
        args = call.function.arguments
        contents = await mcp_client.call_tool(fnName, json.loads(args))
        print(contents)
        params = ""
        # if call.function.name == "read_template_html":
        #   params = ""
        # if call.function.name == "replace_web_file":
        #   params = (
        #     call.function.arguments
        #     if isinstance(call.function.arguments, str)
        #     else json.dumps(call.function.arguments)
        #   )
        messages.append({
          "role": "assistant",
          "content": "",
          "tool_calls": [
              {
                  "id": call.id,
                  "type": "function",
                  "function": {
                      "name": call.function.name,
                      "arguments": params
                  }
              }
          ]
        })
        messages.append({"role": "tool", "content": contents[0].text, "tool_call_id": call.id})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)