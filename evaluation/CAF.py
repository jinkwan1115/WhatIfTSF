"""Text-only bridge to Salesforce's Moirai Agent."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys


# Run from the upstream directory: its MCP server opens cwd-relative files.
# Keeping imports in this subprocess also isolates its optional dependencies.
_WORKER = r'''
import asyncio
import copy
import json
import runpy
import sys

from src.ctx_forecast.mcp_client import MCPClient

request = json.load(sys.stdin)
config = copy.deepcopy(runpy.run_path("src/ctx_forecast/config.py")["CONFIG"])
config["llm"]["model_name"] = request["llm_model"]
if request["llm_model"].startswith("gpt-4o"):
    config["llm"]["model_params_type"].pop("reasoning", None)
    config["llm"]["model_params_type"].update(
        temperature=1.0, top_p=1.0, max_output_tokens=512
    )
# The current upstream config calls this max_iterations; MCPClient reads max_steps.
config.setdefault("max_steps", config.get("max_iterations", 5))
for server in config["servers"].values():
    if server.get("command") in ("python", "python3"):
        server["command"] = sys.executable

async def forecast():
    client = MCPClient(config)
    try:
        await client.connect_to_servers()
        values, _, _, _ = await client.make_forecast(
            history_info=json.dumps(request["history_info"]),
            user_instruct=request["user_instruct"],
            image_path=None,
        )
        return values
    finally:
        await client.cleanup()

values = asyncio.run(forecast())
print("WHATIFTSF_FORECAST=" + json.dumps(values))
'''


class MoiraiAgent:
    """Run the upstream MCP agent from a uni2ts or ctx_forecast checkout."""

    def __init__(self, repo_path, llm_model="gpt-4o", timeout=300):
        path = Path(repo_path).expanduser().resolve()
        nested = path / "project" / "moirai-agent" / "ctx_forecast"
        self.repo_path = nested if nested.is_dir() else path
        if not (self.repo_path / "src/ctx_forecast/mcp_client.py").is_file():
            raise FileNotFoundError(
                "Moirai Agent checkout not found: expected "
                f"{self.repo_path / 'src/ctx_forecast/mcp_client.py'}. "
                "Use a uni2ts checkout containing project/moirai-agent/ctx_forecast."
            )
        self.llm_model = llm_model
        self.timeout = timeout

    def predict(self, *, history, background, scenario, horizon):
        if (
            not isinstance(history, list)
            or not history
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in history)
        ):
            raise ValueError("history must be a nonempty list of finite numbers")
        if type(horizon) is not int or horizon <= 0:
            raise ValueError("horizon must be a positive integer")
        context = f"Domain background:\n{background}"
        if scenario is not None:
            context += f"\n\nFuture scenario:\n{scenario}"
        condition = (
            "Condition the forecast on the supplied future scenario. "
            if scenario is not None
            else "Make a neutral forecast using only history and domain background; "
            "no future scenario is supplied. "
        )
        request = {
            "llm_model": self.llm_model,
            "history_info": {"history_values": history, "context_info": context},
            "user_instruct": (
                condition
                + f"Predict exactly {horizon} future values after the supplied history, "
                "in the original units and observation order. No calendar dates or "
                "sampling frequency are provided. The final result must be enclosed "
                "by '\\boxed{' and '}', with numbers separated by commas."
            ),
        }
        result = subprocess.run(
            [sys.executable, "-c", _WORKER],
            input=json.dumps(request, allow_nan=False),
            text=True,
            capture_output=True,
            cwd=self.repo_path,
            timeout=self.timeout,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Moirai Agent failed; check upstream dependencies, OPENAI_API_KEY "
                "and tool services.\n" + result.stderr[-2000:]
            )
        prefix = "WHATIFTSF_FORECAST="
        lines = [line for line in result.stdout.splitlines() if line.startswith(prefix)]
        if not lines:
            raise RuntimeError("Moirai Agent did not return a forecast")
        values = json.loads(lines[-1][len(prefix):])
        if (
            not isinstance(values, list)
            or len(values) != horizon
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in values)
        ):
            raise ValueError(
                f"Moirai Agent must return {horizon} finite numbers; got {values!r}. "
                "An empty result can indicate an upstream API or tool failure."
            )
        return [float(x) for x in values]
