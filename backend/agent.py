import os
import sys
from google import adk
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioServerParameters, StdioConnectionParams
from dotenv import load_dotenv

load_dotenv()

# Define the path to the MCP server
mcp_server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")

# Create the MCP Toolset using stdio transport with increased timeout
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[mcp_server_path]
        ),
        timeout=60.0  # Increase timeout to 60 seconds
    )
)

# Create the ADK Agent
github_card_agent = adk.Agent(
    name="github_card_agent",
    model="gemini-flash-lite-latest",
    instruction="""You are a GitHub profile analyst and dev card generator. When a user gives you a GitHub username, you ALWAYS follow this exact sequence: first call scrape_github, then analyze_profile with the result, then generate_card_html with all three inputs, then save_card. Never skip steps. Be enthusiastic about developers' work. If the profile is private or doesn't exist, say so clearly.""",
    tools=[mcp_toolset]
)

# Exported run function
async def run_agent(prompt: str):
    """Run the github_card_agent with a prompt."""
    response = await github_card_agent.run(prompt)
    return response.text
