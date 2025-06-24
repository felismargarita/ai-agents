# ali_map_mcp.py
import contextlib
from mcp.client.sse import sse_client
from mcp import ClientSession
from dotenv import load_dotenv
import os
load_dotenv()

@contextlib.asynccontextmanager
async def amap_session():
    url = os.getenv("ALI_MAP_SSE_URL")
    async with sse_client(url) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            yield session