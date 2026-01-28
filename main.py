import sys
import os
sys.path.append(os.path.abspath("/Users/mirapatel/sandbox/itergen"))

import json as pyjson
from itergen.main import IterGen
from schema import Schema

device = "cpu"

iter_gen = IterGen(
    grammar="tool_call.lark",
    model_id="Qwen/Qwen3-0.6B-Base",
    device=device
)

VALID_TOOLS = {
    "get_user_info": Schema({"user_id": str}),
    "send_email": Schema({"recipient_email": str, "subject": str, "body": str}),
    "generate_report": Schema({"data": list, "report_type": str}),
    "fetch_weather": Schema({"location": str}),
    "search_web": Schema({"query": str, "num_results": int}),
    "translate_text": Schema({"text": str, "target_language": str}),
    "analyze_sentiment": Schema({"text": str}),
    "summarize_article": Schema({"article_text": str, "summary_length": int}),
    "convert_currency": Schema({"amount": float, "from_currency": str, "to_currency": str}),
    "schedule_meeting": Schema({"participants": list, "meeting_time": str, "agenda": str}),
    "check_grammar": Schema({"text": str}),
    "create_container": Schema({"container_name": str, "image": str, "ports": list})
}

prompt = (
    "Generate a tool call in JSON for the following task:\n"
    'Task: Create a container named "web_app" using the image "nginx:latest" and exposing ports [80, 443]."\n'
    #'Task: Generate a report of type "sales" using the provided sales data: [{"item": "Widget A", "quantity": 10, "price": 25.00}, {"item": "Widget B", "quantity": 5, "price": 15.00}]."\n'
    #'Task: Schedule a meeting with participants ["tony@example.com", "claire@example.com"] at "2024-07-01 14:00" with the agenda "Project Kickoff"."\n'
    #'Task: Fetch the current weather for "New York City".\n'
    f"Call one of the tools defined here with the correct tool name and arguments: ${str(VALID_TOOLS)}\n"
    "Output the JSON only."
)

iter_gen.start(prompt)

MAX_RETRIES = 20
parsed_json = None

for attempt in range(MAX_RETRIES):
    print(f"\nAttempt {attempt + 1}")

    generated = iter_gen.forward(stop_symbol= '}\n', num=1)

    json_str = "".join(generated).strip()
    print("Generated JSON:")
    print(json_str)
    print("Raw tokens:", repr(generated))

    try:
        parsed_json = pyjson.loads(json_str)
    except pyjson.JSONDecodeError as e:
        print("Invalid JSON, backtracking...")
        iter_gen.backward()
        continue

    tool_name = parsed_json.get("name")
    if tool_name not in VALID_TOOLS:
        print("Invalid tool name, backtracking...")
        iter_gen.backward("name_field", num=1)
        continue

    try:
        VALID_TOOLS[tool_name].validate(parsed_json.get("args"))
        iter_gen.backward("args_field", num=1)
    except Exception as e:
        print("Invalid arguments, backtracking...")

    break

if parsed_json is None:
    print("Valid tool call not generated")
