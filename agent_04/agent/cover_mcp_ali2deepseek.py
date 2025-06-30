def cover_mcp_ali2deepseek(ali_tools):
    result = []
    for ali_tool in ali_tools:
        result.append({
            "type": "function",
            "function": {
                "name": ali_tool.name,
                "description": ali_tool.description,
                "parameters": ali_tool.inputSchema
            }
        })
    print(result)
    return result