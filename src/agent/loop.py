import json

SYSTEM = (
    "You are a cloud cost assistant. Use the tools to find wasteful Azure "
    "resources. Call each relevant scan tool, then give a short summary. "
    "Use only data returned by tools. Never invent resources or numbers."
)

def _parse_args(raw):
    """Return a dict of arguments, or None if the model sent garbage."""
    try:
        args = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return None
    return args if isinstance(args, dict) else None

def run_agent(llm, toolbox, task: str, schemas: list, max_steps: int = 6) -> str:
    items = [{"role": "user", "content": task}]
    for _ in range(max_steps):  # hard step limit: the agent can't loop forever
        response = llm.respond(SYSTEM, items, schemas)
        items += response.output  # keep reasoning and tool-call items in context
        calls = [i for i in response.output if i.type == "function_call"]
        if not calls:
            return response.output_text
        for c in calls:
            args = _parse_args(c.arguments)
            if args is None:
                result = {"error": "invalid JSON arguments; send a JSON object"}
            else:
                result = toolbox.call(c.name, args)
                
            items.append({
                "type": "function_call_output",
                "call_id": c.call_id,
                "output": json.dumps(result),
            })
    return "Stopped: step limit reached."