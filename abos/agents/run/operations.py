"""OperationsDirector — Run stream."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.agent import BossAgent
from ...core.evidence import Evidence


class OperationsDirector(BossAgent):
    NAME = "OperationsDirector"
    STREAM = "run"
    CHANNEL = "#ops"
    TITLE = "Operations Director"
    PERSONA = ("Routes workflows, assigns tasks, and monitors SLAs. "
               "Keeps the operating tempo without touching high-impact actions.")
    PROPOSABLE_ACTIONS = ["draft_recommendation", "assign_task"]

    def analyze(self, context: Dict[str, Any],
                evidence: Optional[List[Evidence]] = None) -> Dict[str, Any]:
        open_tasks = int(context.get("open_tasks", 0))
        overdue = int(context.get("overdue_tasks", 0))
        sla_target = float(context.get("sla_target_pct", 95.0))
        completed = int(context.get("completed_tasks", 0))
        total = max(1, completed + open_tasks)
        on_time_pct = round(100.0 * (completed - overdue) / total, 1)
        flags: List[Dict[str, Any]] = []
        if on_time_pct < sla_target:
            flags.append({"title": f"SLA at {on_time_pct}% (target {sla_target}%)",
                          "severity": "high" if on_time_pct < sla_target - 10 else "medium"})
        signal = min(100.0, on_time_pct)
        return {"agent": self.NAME, "signal": signal, "on_time_pct": on_time_pct,
                "open_tasks": open_tasks, "overdue": overdue, "flags": flags,
                "summary": f"{open_tasks} open, {overdue} overdue; on-time {on_time_pct}%."}
