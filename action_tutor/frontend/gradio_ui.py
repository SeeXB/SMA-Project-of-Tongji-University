from __future__ import annotations

import json
from typing import Any, Dict, List
from urllib import error, request

import gradio as gr


def _safe_json_loads(raw: str, default: Any) -> Any:
	if not raw.strip():
		return default
	return json.loads(raw)


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	data = json.dumps(payload).encode("utf-8")
	req = request.Request(url=url, data=data, method="POST")
	req.add_header("Content-Type", "application/json")
	with request.urlopen(req, timeout=20) as resp:
		text = resp.read().decode("utf-8")
		return json.loads(text)


def run_pipeline(
	base_url: str,
	student_id: str,
	notes: str,
	exercise_logs_raw: str,
	error_history_raw: str,
) -> tuple[str, str, str]:
	try:
		trace = {
			"student_id": student_id or "stu001",
			"notes": notes,
			"exercise_logs": _safe_json_loads(exercise_logs_raw, []),
			"error_history": _safe_json_loads(error_history_raw, []),
		}
		result = _post_json(f"{base_url.rstrip('/')}/generate_nudge", trace)
		weak = result.get("weak_concepts", [])
		nudge = result.get("nudge", "")
		output_hygiene = result.get("output_hygiene", {})
		return (
			json.dumps(weak, ensure_ascii=False, indent=2),
			nudge,
			json.dumps(output_hygiene, ensure_ascii=False, indent=2),
		)
	except (json.JSONDecodeError, error.URLError, TimeoutError, ValueError) as exc:
		return "[]", f"请求失败: {exc}", "{}"


def build_ui() -> gr.Blocks:
	with gr.Blocks(title="Action-Oriented Tutor") as demo:
		gr.Markdown("# 行动导向型辅导系统（MVP）")

		base_url = gr.Textbox(value="http://127.0.0.1:6000", label="Flask Backend URL")
		student_id = gr.Textbox(value="stu001", label="Student ID")
		notes = gr.Textbox(lines=5, label="学习笔记")
		exercise_logs = gr.Code(
			value='[{"concept":"backpropagation","correct":false}]',
			language="json",
			label="exercise_logs(JSON)",
		)
		error_history = gr.Code(
			value='["forgot chain rule", "wrong derivative sign"]',
			language="json",
			label="error_history(JSON)",
		)

		run_btn = gr.Button("分析并生成 Nudge")
		weak_out = gr.Code(language="json", label="Detected Weak Concepts")
		nudge_out = gr.Textbox(label="Generated Nudge")
		output_hygiene = gr.Code(language="json", label="Output Hygiene")

		run_btn.click(
			fn=run_pipeline,
			inputs=[base_url, student_id, notes, exercise_logs, error_history],
			outputs=[weak_out, nudge_out, output_hygiene],
		)

	return demo


if __name__ == "__main__":
	app = build_ui()
	app.launch(server_name="127.0.0.1", server_port=7860)
