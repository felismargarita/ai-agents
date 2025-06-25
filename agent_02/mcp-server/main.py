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

dashscope.api_key = os.getenv("ALI_DASHSCOPE_KEY")

mcp = FastMCP('ali-transformer-mcp')

def remove_words_from_sentence(sentence) -> str:
  return sentence["text"]


def remove_words_from_transcript(transcript: Any) -> List[str]:
  sentences = map(remove_words_from_sentence, transcript["sentences"])
  return list(sentences)


@mcp.tool
def transform_media_text(audio_url: str) -> List[str]:
  task_response = Transcription.async_call(
    model='paraformer-v2',
    file_urls=[audio_url],
    language_hints=['zh', 'en']
  )

  transcribe_response = Transcription.wait(task=task_response.output.task_id)
  if transcribe_response.status_code == HTTPStatus.OK:
    print(transcribe_response.output)
    output_json_url = transcribe_response.output.results[0]["transcription_url"]
    try:
      response = requests.get(output_json_url, timeout=5)
      response.raise_for_status()
      textJson = response.json()
      sentences = remove_words_from_transcript(textJson["transcripts"][0])
      return sentences

    except requests.exceptions.RequestException as e:
      print("json文件解析失败", audio_url, e)
      return {}


if __name__ == "__main__":
  mcp.run(
    transport="streamable-http",
    host="0.0.0.0",           # Bind to all interfaces
    port=9500,                # Custom port
    log_level="DEBUG",        # Override global log level
  )