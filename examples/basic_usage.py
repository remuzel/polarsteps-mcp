#!/usr/bin/env python3
"""
Basic usage example for Polarsteps MCP Server

This example shows how to test the MCP server functionality without running it as a full server.
For actual MCP usage, use the command-line tool or integrate with Claude Desktop.
"""

import asyncio
import os
from mcp.types import (
    CallToolRequest,
    CallToolRequestParams,
    ListToolsRequest,
    ListResourcesRequest
)
from polarsteps_mcp.server import PolarstepsMCPServer, PolarstepsMCPSettings


async def test_server_functionality():
    """Test the MCP server functionality"""
    
    # Set up configuration
    settings = PolarstepsMCPSettings(
        remember_token=os.getenv("POLARSTEPS_REMEMBER_TOKEN"),
        base_url="https://www.polarsteps.com"
    )
    
    # Create and configure the server
    server = PolarstepsMCPServer(settings)
    
    print("🚀 Polarsteps MCP Server Test")
    print("=" * 40)
    
    # Test listing tools
    print("\n📋 Available Tools:")
    tools_request = ListToolsRequest(method="tools/list", params={})
    tools_result = await server.list_tools(tools_request)
    
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test listing resources
    print("\n📚 Available Resources:")
    resources_request = ListResourcesRequest(method="resources/list", params={})
    resources_result = await server.list_resources(resources_request)
    
    for resource in resources_result.resources:
        print(f"  - {resource.name}: {resource.description}")
    
    # Test a simple tool call (this will try to make an API call)
    print("\n🔍 Testing get_user tool with username 'remuzel':")
    try:
        user_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="get_user",
                arguments={"username": "remuzel"}
            )
        )
        user_result = await server.call_tool(user_request)
        
        if user_result.isError:
            print(f"  ❌ Error: {user_result.content[0].text}")
        else:
            print(f"  ✅ Success! Got user data:")
            # Show first few lines of the result
            lines = user_result.content[0].text.split('\n')[:10]
            for line in lines:
                print(f"    {line}")
            if len(user_result.content[0].text.split('\n')) > 10:
                print("    ...")
                
    except Exception as e:
        print(f"  ❌ Error testing user call: {e}")
    
    print("\n✅ MCP Server functionality test complete!")
    print("\n💡 To use with Claude Desktop, add this to your config:")
    print('   "polarsteps": {')
    print('     "command": "polarsteps-mcp",')
    print('     "env": {')
    print('       "POLARSTEPS_REMEMBER_TOKEN": "your_token_here"')
    print('     }')
    print('   }')


if __name__ == "__main__":
    # Make sure you have set the POLARSTEPS_REMEMBER_TOKEN environment variable
    if not os.getenv("POLARSTEPS_REMEMBER_TOKEN"):
        print("ERROR: POLARSTEPS_REMEMBER_TOKEN environment variable is required")
        print("Set it with: export POLARSTEPS_REMEMBER_TOKEN='your_token_here'")
        exit(1)
    
    asyncio.run(test_server_functionality())