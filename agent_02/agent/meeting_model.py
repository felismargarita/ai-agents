from pydantic import BaseModel

class Meeting(BaseModel):
  content: str