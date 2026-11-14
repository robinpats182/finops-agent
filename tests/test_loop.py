from types import SimpleNamespace as NS
from src.agent.loop import run_agent


class ScriptedLLM:
    """Returns pre-written responses, one per call, and records what it saw."""
    def __init__(self, responses):
        self.responses = list(responses)
        self.seen = []

    def respond(self, instructions, items, tools):
        self.seen.append(list(items))
        return self.responses.pop(0)


class RecordingBox:
    def __init__(self):
        self.calls = []

    def call(self, name, args):
        self.calls.append((name, args))
        return []


def tool_turn(name, arguments, call_id="c1"):
    item = NS(type="function_call", name=name, arguments=arguments, call_id=call_id)
    return NS(output=[item], output_text="")


def answer(text):
    return NS(output=[NS(type="message")], output_text=text)


def test_tool_call_is_dispatched_then_answer_returned():
    llm = ScriptedLLM([tool_turn("scan_unattached_disks", "{}"), answer("done")])
    box = RecordingBox()
    assert run_agent(llm, box, "task", []) == "done"
    assert box.calls == [("scan_unattached_disks", {})]


def test_malformed_arguments_do_not_crash_and_error_goes_back_to_model():
    llm = ScriptedLLM([tool_turn("scan_unattached_disks", "{not json"), answer("done")])
    box = RecordingBox()
    assert run_agent(llm, box, "task", []) == "done"
    assert box.calls == []                       # the tool was never run
    last = llm.seen[1][-1]                       # what the model saw next turn
    assert last["type"] == "function_call_output"
    assert "invalid" in last["output"].lower()


def test_step_limit_stops_the_loop():
    llm = ScriptedLLM([tool_turn("scan_unattached_disks", "{}", f"c{i}")
                       for i in range(2)])
    result = run_agent(llm, RecordingBox(), "task", [], max_steps=2)
    assert result == "Stopped: step limit reached."