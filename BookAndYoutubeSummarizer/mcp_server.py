from mcp.server.fastmcp import FastMCP
from youtube_summary import summarize_youtube_video

mcp = FastMCP()

@mcp.tool()
def summarize_youtube_video(url: str):
    return summarize_youtube_video(url)

if __name__ == "__main__":
    mcp.run()