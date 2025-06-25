from pydantic import BaseModel

class WebModifyModel(BaseModel):
  selectorPath: str
  textContent: str
  prompt: str