from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import uvicorn
from fastmcp import Client
from fastapi.staticfiles import StaticFiles
from web_gen_model import WebGenModel
from fastapi.middleware.cors import CORSMiddleware
from web_modify_model import WebModifyModel

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_URL")
)

app = FastAPI()

app.mount("/develop-web", StaticFiles(directory=os.getenv("DIRECTORY_PATH"), html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
mcp_tools = [
  {
    "type": "function",
    "function": {
      "name": "replace_web_file",
      "description": "向操作系统上写入或者替换文件,文件类型只能是合法的html和css文件",
      "parameters": {
        "type": "object", 
        "properties": {     
          "__filename": {  
            "type": "string",
            "description": "纯文件名和后缀,不包含操作系统路径"
          },
          "content": {  
            "type": "string",
            "description": "文件内容,必须是合法的html文件或者css文件内容"
          }
        },
        "required": ["__filename", "content"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_template_html",
      "description": "读取html的样例文件, 可以用来准确生成特定样板的html",
      "properties": {}
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_current_html",
      "description": "读取当前网站最新的html文件内容",
      "properties": {}
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_current_css",
      "description": "读取当前网站最新的css文件内容",
      "properties": {}
    }
  }
]

@app.post("/generate-web")
async def generateWeb(body: WebGenModel) -> str:
  messages = [
     {
        "role": "system",
        "content": '''
          角色描述:
          - 你是一个资深的web前端开发工程师,非常擅长HTML,JS,CSS技术栈.
          - 你只会做开发网页相关工作,别的工作全部拒绝

          输入概况:
          - 你会收到一个详细的网页描述,基于描述,仅使用HTML,JS,CSS技术栈开发一个静态网页
          - 生成html文件的之前,先读取样例文件,你只能替换掉两处<!---LLM PLACEHOLDER REPLACEMENT HERE ONLY--->, 其余均不可修改

          输出格式:
          - 输出一个名称为styles.css的文件到操作系统上
          - 输出一个名称为index.html的文件到操作系统上,该html文件引用的样式文件是styles.css
        '''
     },
     {
        "role": "user",
        "content": f"帮我开发一个网站, 设计风格参考:{body.design}, 主题: {body.theme}, 主色: {body.color}, 行业: {body.industry}, 内容复杂度: {body.complex}, 额外提示: {body.prompt}"
     }
  ]

  
  while True:
    response = client.chat.completions.create(
      model="deepseek-chat",
      messages=messages,
      tools=mcp_tools,
      tool_choice="auto"
    )
    res_message = response.choices[0].message
    if not res_message.tool_calls:
      break
    async with Client(os.getenv("INTERNAL_MCP_URL")) as mcp_client:
      for call in res_message.tool_calls:
        args = call.function.arguments
        contents = await mcp_client.call_tool(call.function.name, json.loads(args))

        params = ""
        if call.function.name == "read_template_html":
          params = ""
        if call.function.name == "replace_web_file":
          params = (
            call.function.arguments
            if isinstance(call.function.arguments, str)
            else json.dumps(call.function.arguments)
          )
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
  return "success"


@app.put("/modify-web")
async def modifyWeb(body: WebModifyModel):
  messages = [
    {
        "role": "system",
        "content": '''
          角色描述:
          - 你是一个资深的web前端开发工程师,非常擅长HTML,JS,CSS技术栈.
          - 你只会做开发网页相关工作,别的工作全部拒绝

          输入概况:
          - 你会收到3个信息. 1, 此次修改很有可能对应的html路径元素,这个路径是冒泡的全路径  2, 此次修改很有可能对应的html元素内嵌文本 3, 用户的修改描述
          - 优先基于上述描述的1和2两点来优先判断是否可以达成3描述的目标,如果不能达到目标则再考虑修改其他元素路径
          - 生成html文件的之前,先读取样例文件,你只能替换掉两处<!---LLM PLACEHOLDER REPLACEMENT HERE ONLY--->, 其余均不可修改

          工作逻辑:
          - 修改必须基于当前最新的html和css文件, 必须依赖外部的tool来读取文件
          - 修改需要遵循最小改动原则
          - 基于最新文件修改完成后替换掉当前的html和css文件
          - 修改范围是html文件的body标签内的内容, css文件全部内容都可以修改

          输出格式:
          - 输出一个名称为styles.css的文件到操作系统上
          - 输出一个名称为index.html的文件到操作系统上,该html文件引用的样式文件是styles.css
        '''
    },
    {
      "role": "user",
      "content": f"帮我基于当前的网站做出如下修改: {body.prompt}, html元素路径: {body.selectorPath}, html元素内容: {body.textContent}"
    } 
  ]
  while True:
    response = client.chat.completions.create(
      model="deepseek-chat",
      messages=messages,
      tools=mcp_tools,
      tool_choice="auto"
    )
    res_message = response.choices[0].message
    if not res_message.tool_calls:
      break
    async with Client(os.getenv("INTERNAL_MCP_URL")) as mcp_client:
      for call in res_message.tool_calls:
        args = call.function.arguments
        contents = await mcp_client.call_tool(call.function.name, json.loads(args))

        params = ""
        if call.function.name == "read_current_html":
          params = ""
        if call.function.name == "read_current_css":
          params = ""
        if call.function.name == "replace_web_file":
          params = (
            call.function.arguments
            if isinstance(call.function.arguments, str)
            else json.dumps(call.function.arguments)
          )
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