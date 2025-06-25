from fastapi import FastAPI
import os
from openai import OpenAI
import json
import uvicorn
from fastmcp import Client
from openai import OpenAI
from meeting_model import Meeting
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_URL")
)

app = FastAPI()

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
      "name": "transform_media_text",
      "description": "输入一个音频文件的url地址，自动转换成文字输出",
      "parameters": {
        "type": "object", 
        "properties": {     
          "audio_url": {  
            "type": "string",
            "description": "音频文件的URL地址"
          }
        },
        "required": ["audio_url"]
      }
    }
  }
]

@app.post("/meeting_markdown")
async def meeting_markdown(meeting: Meeting) -> str:
  messages = [
     {
        "role": "system",
        "content": '''
          工具描述:
          - 你是一个根据音频文件生成会议纪要的工具.

          输入概况:
          - 你会收到一个会议概况记录,其中包含文本和若干录音文件URL

          输出格式:
          - 仅仅需要本次会议的会议纪要markdown
          - 不需要在回答中包含任何除了会议纪要内容外的任何引言
          - 需要包括但不限于如下几个内容:
            - 会议主题
            - 会议关键内容
            - 会议后的行动列表
        '''
     },
     {
        "role": "user",
        "content": f"我提供给你的会议内容如下: {meeting.content}, 其中包含文本和若干录音文件, 整理成会议纪要"
     }
  ]
  response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=mcp_tools,
    tool_choice="auto"
  )
  res_message = response.choices[0].message
  tool_calls = res_message.tool_calls

  if not tool_calls:
     print("无需音频转换,直接生成会议纪要")
     return res_message.content
  async with Client(os.getenv("ALI_TRANSPITION_MCP_URL")) as mcp_client:
     for call in tool_calls:
        if call.function.name == "transform_media_text":
          args = call.function.arguments
          transcription_rst = await mcp_client.call_tool(call.function.name, json.loads(args))
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
          messages.append({"role": "tool", "content": transcription_rst[0].text, "tool_call_id": call.id})
  final_response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=mcp_tools,
    tool_choice="auto" 
  )
  return final_response.choices[0].message.content

    
  

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)