from pydantic import BaseModel

class WebGenModel(BaseModel):
  design: str #参考的设计风格
  theme: str #主题
  color: str #颜色
  industry: str #行业
  complex: str #是否页面复杂
  prompt: str