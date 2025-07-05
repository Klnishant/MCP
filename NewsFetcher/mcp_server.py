from mcp.server.fastmcp import FastMCP
from app import fetch_news, generate_video_transcription

mcp = FastMCP()

@mcp.tool()
def generate_news(query: str) -> str:
    return fetch_news(query)

@mcp.tool()
def generate_script(query: str) -> str:
    news = fetch_news(query)
    return generate_video_transcription(news)

if __name__ == "__main__":
    mcp.run()