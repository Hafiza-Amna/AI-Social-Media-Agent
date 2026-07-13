"""
audit_schemas.py - Scans all registered tools and prints schema compatibility info.
"""
import json, sys
sys.path.insert(0, '.')

from agent import create_master_agent

agent = create_master_agent()
print(f"Total tools: {len(agent.tools)}\n")

issues = []
for tool in agent.tools:
    schema = tool.to_litellm_tool()
    params = schema.get("function", {}).get("parameters", {})
    s = json.dumps(params)
    has_defs = "defs" in s or "allOf" in s or "anyOf" in s
    flag = "ISSUE" if has_defs else "OK"
    print(f"[{flag}] {tool.name}")
    if has_defs:
        issues.append(tool.name)
        print(json.dumps(params, indent=2)[:1200])
        print()

print(f"\n=== SUMMARY: {len(issues)} tool(s) with schema issues ===")
for t in issues:
    print(f"  - {t}")
