from fastmcp import FastMCP
from typing import Any, List
from dashscope.audio.asr import Transcription
from http import HTTPStatus
import json
import dashscope
import requests
from dotenv import load_dotenv
import os
from db import execute

load_dotenv()


mcp = FastMCP('report-tools')


@mcp.tool(
    name="execute_mysql_sql",
    description="执行任何mysql命令",
    tags=["report data database"]
  )
def execute_mysql_sql(sql: str) -> str:
  print(sql)
  return execute(sql)

if __name__ == "__main__":
  mcp.run(
    transport="streamable-http",
    host="0.0.0.0",           # Bind to all interfaces
    port=9500,                # Custom port
    log_level="DEBUG",        # Override global log level
  )