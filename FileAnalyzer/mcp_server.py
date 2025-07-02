from mcp.server.fastmcp import FastMCP
from insight import generate_insigths

mcp = FastMCP("this will do the file analysis")

@mcp.tool()
def analyze_file(text):
    return generate_insigths(text[:5000])

if __name__ == "__main__":
    mcp.run()