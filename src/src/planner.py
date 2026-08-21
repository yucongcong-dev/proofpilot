"""ProofPilot: evidence-driven action planning with an optional Gemini backend."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class PlanStep:
    order: int
    action: str
    evidence: str
    risk: str


def _fallback_plan(goal: str) -> dict[str, Any]:
    clean = goal.strip().rstrip("。.!！")
    if not clean:
        clean = "完成目标"
    steps = [
        PlanStep(1, f"定义“{clean}”的完成标准", "一条可检查的验收标准", "目标含糊会导致返工"),
        PlanStep(2, "收集完成任务所需的信息、权限和素材", "输入清单与来源链接", "缺少权限或隐私数据"),
        PlanStep(3, "执行最小可行步骤并记录每次结果", "时间戳、输出或截图", "操作可能改变外部状态"),
        PlanStep(4, "复核结果并处理失败分支", "通过/失败判定与修复记录", "遗漏边界情况"),
        PlanStep(5, "整理可复用的结论和下一步", "最终摘要与待办列表", "没有留下可追踪证据"),
    ]
    return {"goal": clean, "mode": "deterministic", "steps": [asdict(s) for s in steps]}


def _gemini_plan(goal: str) -> dict[str, Any] | None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        from google import genai  # type: ignore

        client = genai.Client(api_key=key)
        prompt = (
            "You are ProofPilot, an evidence-driven action planner. Return only valid JSON "
            "with keys goal and steps. steps must be an array of exactly 5 objects with "
            "order, action, evidence, risk. Keep each value concise. Goal: " + goal
        )
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        raw = response.text or ""
        raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and isinstance(parsed.get("steps"), list):
            parsed["mode"] = "gemini"
            return parsed
    except Exception:
        return None
    return None


def make_plan(goal: str) -> dict[str, Any]:
    return _gemini_plan(goal) or _fallback_plan(goal)
