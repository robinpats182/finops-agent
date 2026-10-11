import json

SYSTEM = (
    "You are a cloud cost assistant. Use the tools to find wasteful Azure "
    "resources. Call each relevant scan tool, then give a short summary. "
    "Use only data returned by tools. Never invent resources or numbers."
)


def run_agent(llm, toolbox, task: str, schemas: list, max_steps: int = 6) -> str:
    items = [{"role": "user", "content": task}]
    for _ in range(max_steps):  # hard step limit: the agent can't loop forever
        response = llm.respond(SYSTEM, items, schemas)
        items += response.output  # keep reasoning and tool-call items in context
        calls = [i for i in response.output if i.type == "function_call"]
        if not calls:
            return response.output_text
        for c in calls:
            result = toolbox.call(c.name, json.loads(c.arguments or "{}"))
            items.append({
                "type": "function_call_output",
                "call_id": c.call_id,
                "output": json.dumps(result),
            })
    return "Stopped: step limit reached."