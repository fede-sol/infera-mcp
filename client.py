import asyncio
from fastmcp import Client

client = Client("http://localhost:8001/mcp")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("get_github_file_content", {"repository_name": name , "file_path": "manage.py"})
        print(result)

asyncio.run(call_tool("belu_api"))