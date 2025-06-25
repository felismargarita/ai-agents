from fastmcp import FastMCP
from typing import Any, List
from dashscope.audio.asr import Transcription
from http import HTTPStatus
import json
import dashscope
import requests
from dotenv import load_dotenv
import os

load_dotenv()


mcp = FastMCP('web-development-filesystem-tools')


@mcp.tool
def replace_web_file(__filename: str, content: str) -> str:
  filename = os.path.join(os.getenv("DIRECTORY_PATH"),  __filename)
  try:
    # 创建目录结构（如果不存在）
    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        
    # 原子写入（先写入临时文件再重命名）
    temp_file = filename + '.tmp'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 替换原文件（Windows需特殊处理）
    if os.name == 'nt':  # Windows系统
      if os.path.exists(filename):
          os.remove(filename)
      os.rename(temp_file, filename)
    else:  # Unix/Linux/MacOS
      os.replace(temp_file, filename)
  except PermissionError as pe:
      raise PermissionError(f"权限不足: {pe}") from pe
  except OSError as ose:
      raise OSError(f"系统错误: {ose}") from ose
  except Exception as e:
      raise RuntimeError(f"未知错误: {e}") from e
  return content


def read_file(path: str) -> str:
  if not os.path.exists(path):
      raise FileNotFoundError(f"file not found at {path}")
  
  try:
      with open(path, 'r', encoding='utf-8') as file:
          html_content = file.read()
  except UnicodeDecodeError:
      with open(path, 'r', encoding='latin-1') as file:
          html_content = file.read()
  
  return html_content

@mcp.tool
def read_template_html():
  directory_path = os.getenv("DIRECTORY_PATH")
  if not directory_path:
      raise EnvironmentError("DIRECTORY_PATH environment variable not set")
  
  template_file_path = os.path.join(directory_path, "index_template_html")
  return read_file(template_file_path)

@mcp.tool
def read_current_html():
  directory_path = os.getenv("DIRECTORY_PATH")
  if not directory_path:
      raise EnvironmentError("DIRECTORY_PATH environment variable not set")
  
  file_path = os.path.join(directory_path, "index.html")
  return read_file(file_path)

@mcp.tool
def read_current_css():
  directory_path = os.getenv("DIRECTORY_PATH")
  if not directory_path:
      raise EnvironmentError("DIRECTORY_PATH environment variable not set")
  file_path = os.path.join(directory_path, "styles.css")
  return read_file(file_path)

if __name__ == "__main__":
  mcp.run(
    transport="streamable-http",
    host="0.0.0.0",           # Bind to all interfaces
    port=9500,                # Custom port
    log_level="DEBUG",        # Override global log level
  )