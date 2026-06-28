"""
AI Harness for CampusTask — 用自然语言管理校园任务。

流水线: user_input → prompt_builder → mock_model → parser → guardrail → tool_executor
全程通过 trace_logger 写入 trace.jsonl。
不依赖真实大模型 API，mock_model() 使用规则匹配模拟意图识别。
"""

from __future__ import annotations

import json
import re
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_service import (
    add_task, get_all_tasks, get_pending_tasks, get_done_tasks,
    get_overdue_tasks, complete_task, search_tasks,
)

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

TRACE_FILE = "trace.jsonl"
EVAL_FILE = "eval_cases.json"
DANGEROUS_ACTIONS = {"delete_all_tasks", "delete_task"}

SYSTEM_PROMPT = """你是一个校园任务管理助手。根据用户输入输出 JSON 格式的操作指令。
支持的操作类型:
- add_task: 添加任务, args: {title, deadline(可选), priority(可选)}
- list_tasks: 列出任务, args: {filter(可选: pending/done/all)}
- complete_task: 完成任务, args: {task_id}
- search_tasks: 搜索任务, args: {keyword}
- get_overdue: 查看过期任务, args: {}
- delete_all_tasks: 删除所有任务, args: {}
- export_tasks: 导出任务, args: {filename(可选)}
输出格式严格为单行 JSON，不要输出其他内容。"""


# ===================================================================
# 1. prompt_builder — 构造发给模型的完整 prompt
# ===================================================================

def prompt_builder(user_input: str, task_state: dict | None = None) -> str:
    """构造包含系统指令、任务上下文和用户输入的完整 prompt。"""
    parts = [SYSTEM_PROMPT]
    if task_state:
        pending = task_state.get("pending", [])
        if pending:
            parts.append(f"\n当前待完成任务 ({len(pending)} 项):")
            for t in pending:
                dl = f", 截止: {t['deadline']}" if t.get("deadline") else ""
                parts.append(
                    f"  #{t['id']} [{t.get('priority', 'medium')}] {t['title']}{dl}"
                )
        parts.append(f"今日日期: {date.today().isoformat()}")
    parts.append(f"\n用户输入: {user_input}")
    return "\n".join(parts)


# ===================================================================
# 2. mock_model — 规则驱动的意图识别（不调用真实 API）
# ===================================================================

def _parse_date_delta(text: str) -> str | None:
    """将中文日期表达转换为 YYYY-MM-DD。"""
    today = date.today()
    for word, delta in {"今天": 0, "明天": 1, "后天": 2, "大后天": 3,
                         "昨天": -1, "昨日": -1, "前天": -2}.items():
        if word in text:
            return (today + timedelta(days=delta)).isoformat()
    m = re.search(r"(\d+)天后", text)
    if m:
        return (today + timedelta(days=int(m.group(1)))).isoformat()
    m = re.search(r"下周([一二三四五六日天])", text)
    if m:
        wmap = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
        days_ahead = wmap[m.group(1)] - today.weekday() + 7
        return (today + timedelta(days=days_ahead)).isoformat()
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else None


def _extract_title(text: str) -> str:
    """从自然语言中提取任务标题。"""
    text = re.sub(r"(帮我|请|帮忙|替我|一下|添加|加一个?|一个|给)\s*", "", text)
    text = re.sub(r"(高|中|低)优先级", "", text)
    text = re.sub(r"(明天|后天|今天|昨天|\d+天后|下周[一二三四五六日天]|\d{4}-\d{2}-\d{2})", "", text)
    text = text.strip().rstrip("。，,.").strip()
    return text[:100] if text else "未命名任务"


def _extract_priority(text: str) -> str:
    if "高" in text or "high" in text.lower():
        return "high"
    if "低" in text or "low" in text.lower():
        return "low"
    return "medium"


def _extract_task_id(text: str) -> int | None:
    for pattern in [r"第\s*(\d+)\s*个", r"(\d+)\s*号", r"编号\s*(\d+)", r"#\s*(\d+)"]:
        m = re.search(pattern, text)
        if m:
            return int(m.group(1))
    m = re.search(r"\b(\d+)\b", text)
    return int(m.group(1)) if m else None


def mock_model(prompt: str) -> dict:
    """
    规则驱动的模拟模型，不调用真实 API。
    返回格式: {"action": "...", "args": {...}}
    """
    # 只对用户输入部分做意图匹配，避免 SYSTEM_PROMPT 中列出的 action 名称干扰
    user_line = prompt.split("用户输入:")[-1].strip() \
        if "用户输入:" in prompt else prompt
    ui = user_line.lower()

    # 危险操作优先匹配
    if any(w in ui for w in ["删除所有", "删除全部", "清除所有", "清空",
                               "delete all", "remove all"]):
        return {"action": "delete_all_tasks", "args": {}}

    # 各意图匹配（按优先级）
    if any(w in ui for w in ["添加", "新增", "创建", "加一个", "增加", "add task",
                               "add a"]):
        return {"action": "add_task", "args": {
            "title": _extract_title(user_line),
            "deadline": _parse_date_delta(user_line),
            "priority": _extract_priority(user_line),
        }}

    if any(w in ui for w in ["完成", "标记", "搞定", "done", "complete", "finish"]):
        # 排除否定语境: "没完成", "未完成", "还没完成" 不是完成指令
        if not re.search(r"(没|未|不|还没有)\s*完成", ui):
            tid = _extract_task_id(user_line)
            return {"action": "complete_task", "args": {"task_id": tid or 1}}

    if any(w in ui for w in ["搜索", "查找", "找", "search", "find", "有没有"]):
        kw = re.sub(r"(搜索|查找|找|search|find|有没有)\s*", "", ui).strip()
        return {"action": "search_tasks", "args": {"keyword": kw or "任务"}}

    if any(w in ui for w in ["过期", "超期", "overdue"]):
        return {"action": "get_overdue", "args": {}}

    if any(w in ui for w in ["导出", "export"]):
        m = re.search(r"(\w+\.csv)", ui)
        return {"action": "export_tasks",
                "args": {"filename": m.group(1) if m else "tasks.csv"}}

    if any(w in ui for w in ["列出", "查看", "显示", "看看", "list", "show",
                               "ls", "还有什么", "清单", "有哪些"]):
        return {"action": "list_tasks", "args": {}}

    # 兜底: 较长输入当作添加任务
    if len(user_line) > 3:
        return {"action": "add_task", "args": {
            "title": _extract_title(user_line),
            "deadline": _parse_date_delta(user_line),
            "priority": _extract_priority(user_line),
        }}
    return {"action": "list_tasks", "args": {}}


# ===================================================================
# 3. parser — 验证并规范化模型输出
# ===================================================================

def parse_model_output(model_output: dict) -> dict:
    """验证模型输出的 JSON 结构是否合法。"""
    if not isinstance(model_output, dict):
        raise ValueError(f"模型输出不是 dict: {type(model_output)}")
    if "action" not in model_output:
        raise ValueError("模型输出缺少 'action' 字段")
    action = model_output["action"]
    if not isinstance(action, str):
        raise ValueError(f"action 不是字符串: {action}")
    args = model_output.get("args", {})
    if not isinstance(args, dict):
        args = {}
    return {"action": action, "args": args}


# ===================================================================
# 4. guardrail — 安全检查，阻止危险操作
# ===================================================================

def guardrail(action: dict) -> tuple[bool, str]:
    """
    安全检查。返回 (通过, 原因)。
    - 危险操作 (delete_all_tasks) → 不通过，需人工确认
    - 参数校验 (空标题, 缺编号) → 不通过
    """
    action_name = action.get("action", "")
    if action_name in DANGEROUS_ACTIONS:
        return False, (
            f"⚠ 操作 '{action_name}' 可能造成不可逆的数据丢失，需要人工确认。"
        )
    if action_name == "add_task":
        title = action.get("args", {}).get("title", "")
        if not title or not title.strip():
            return False, "任务标题不能为空"
    if action_name == "complete_task":
        if action.get("args", {}).get("task_id") is None:
            return False, "缺少任务编号"
    return True, "通过"


def request_human_approval(action: dict) -> bool:
    """模拟人工审批（Human-in-the-Loop）。"""
    print(f"\n{'='*50}")
    print(f"  ⚠ 需要人工确认")
    print(f"  操作: {action['action']}")
    print(f"  参数: {json.dumps(action.get('args', {}), ensure_ascii=False)}")
    print(f"{'='*50}")
    try:
        answer = input("  确认执行? [y/N]: ").strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


# ===================================================================
# 5. tool_executor — 调用 CampusTask 已有功能
# ===================================================================

def execute_tool(action: dict, interactive: bool = True) -> dict:
    """
    调用 CampusTask 已有功能执行操作。
    返回 {"success": bool, "result": Any, "error": str|None}
    """
    action_name = action["action"]
    args = action.get("args", {})
    try:
        if action_name == "add_task":
            task = add_task(
                args.get("title", ""),
                args.get("deadline"),
                args.get("priority", "medium"),
            )
            return {"success": True, "result": task, "error": None}

        if action_name == "list_tasks":
            return {"success": True, "result": get_all_tasks(), "error": None}

        if action_name == "complete_task":
            tid = args.get("task_id")
            if tid is None:
                return {"success": False, "result": None, "error": "缺少 task_id"}
            task = complete_task(int(tid))
            return {"success": True, "result": task, "error": None}

        if action_name == "search_tasks":
            return {"success": True,
                    "result": search_tasks(args.get("keyword", "")), "error": None}

        if action_name == "get_overdue":
            return {"success": True, "result": get_overdue_tasks(), "error": None}

        if action_name == "export_tasks":
            import csv
            filename = args.get("filename", "tasks.csv")
            tasks = get_all_tasks()
            with open(filename, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["ID", "标题", "状态", "优先级", "截止日期", "创建时间"])
                for t in tasks:
                    w.writerow([
                        t["id"], t["title"],
                        "已完成" if t["status"] == "done" else "待完成",
                        t.get("priority", "中"), t.get("deadline", ""),
                        t.get("created_at", ""),
                    ])
            return {"success": True, "result": f"已导出到 {filename}", "error": None}

        if action_name == "delete_all_tasks":
            if interactive:
                if not request_human_approval(action):
                    return {"success": False, "result": None,
                            "error": "用户拒绝执行删除操作"}
            from task_storage import save_tasks
            save_tasks([])
            return {"success": True, "result": "所有任务已删除", "error": None}

        return {"success": False, "result": None,
                "error": f"未知操作: {action_name}"}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


# ===================================================================
# 6. trace_logger — 写入 JSONL 日志
# ===================================================================

def write_trace(event: dict) -> None:
    """将事件追加写入 trace.jsonl。"""
    record = {"timestamp": datetime.now().isoformat(), **event}
    try:
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ===================================================================
# 7. 主流程 — 端到端流水线
# ===================================================================

def run_harness(user_input: str, interactive: bool = True) -> dict:
    """执行完整的 AI Harness 流水线。"""
    trace: dict = {"user_input": user_input}

    # Step 1: 获取上下文 → 构造 prompt
    tasks = get_all_tasks()
    task_state = {
        "pending": [t for t in tasks if t["status"] == "pending"],
        "done": [t for t in tasks if t["status"] == "done"],
    }
    prompt = prompt_builder(user_input, task_state)
    trace["prompt"] = prompt

    # Step 2: 调用模型
    model_output = mock_model(prompt)
    trace["model_output"] = model_output

    # Step 3: 解析
    try:
        parsed = parse_model_output(model_output)
    except ValueError as e:
        trace["parse_error"] = str(e)
        trace["guardrail_passed"] = False
        trace["execution_result"] = {
            "success": False, "error": f"解析失败: {e}"}
        write_trace(trace)
        return trace["execution_result"]
    trace["parsed_action"] = parsed

    # Step 4: 安全检查
    passed, reason = guardrail(parsed)
    trace["guardrail_passed"] = passed
    trace["guardrail_reason"] = reason

    if not passed:
        trace["execution_result"] = {"success": False, "error": reason}
        write_trace(trace)
        print(f"\n  护栏拦截: {reason}")
        if parsed["action"] in DANGEROUS_ACTIONS and interactive:
            if request_human_approval(parsed):
                result = execute_tool(parsed, interactive=True)
                trace["execution_result"] = result
                write_trace(trace)
                return result
        return trace["execution_result"]

    # Step 5: 执行
    result = execute_tool(parsed, interactive=interactive)
    trace["execution_result"] = result
    write_trace(trace)

    # 输出结果
    if result["success"]:
        res = result["result"]
        if isinstance(res, list):
            print(f"\n  共 {len(res)} 项任务")
            for t in res[:20]:
                s = "✓" if t.get("status") == "done" else "○"
                print(f"    [{t['id']}] {s} {t['title']}")
        elif isinstance(res, dict):
            print(f"\n  ✅ {res.get('title', res)}")
        elif isinstance(res, str):
            print(f"\n  {res}")
    else:
        print(f"\n  ❌ 错误: {result['error']}")
    return result


# ===================================================================
# 8. eval_runner — 评测
# ===================================================================

DEFAULT_EVAL_CASES: list[dict] = [
    {"input": "帮我添加一个复习软件工程的任务", "expected_action": "add_task"},
    {"input": "添加一个明天下午交的软件工程实验报告", "expected_action": "add_task"},
    {"input": "列出我还没完成的任务", "expected_action": "list_tasks"},
    {"input": "把第2个任务标记为完成", "expected_action": "complete_task"},
    {"input": "删除所有任务", "expected_action": "delete_all_tasks"},
    {"input": "查看所有任务", "expected_action": "list_tasks"},
    {"input": "搜索关于报告的作业", "expected_action": "search_tasks"},
    {"input": "有什么过期的任务吗", "expected_action": "get_overdue"},
    {"input": "加一个高优先级的准备期末考试任务", "expected_action": "add_task"},
    {"input": "完成1号任务", "expected_action": "complete_task"},
    {"input": "帮我导出任务到 my_tasks.csv", "expected_action": "export_tasks"},
    {"input": "有没有关于实验的任务", "expected_action": "search_tasks"},
]


def load_eval_cases(path: str = EVAL_FILE) -> list[dict]:
    """加载评测用例，若文件不存在则自动生成。"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_EVAL_CASES, f, ensure_ascii=False, indent=2)
    return list(DEFAULT_EVAL_CASES)


def run_eval(eval_cases: list[dict] | None = None,
             verbose: bool = True) -> dict:
    """运行评测，输出准确率。"""
    if eval_cases is None:
        eval_cases = load_eval_cases()

    passed = 0
    details: list[dict] = []
    for i, case in enumerate(eval_cases):
        p = prompt_builder(case["input"])
        out = mock_model(p)
        try:
            actual = parse_model_output(out)["action"]
        except ValueError:
            actual = None
        ok = actual == case["expected_action"]
        if ok:
            passed += 1
        details.append({
            "index": i + 1,
            "input": case["input"],
            "expected": case["expected_action"],
            "actual": actual,
            "passed": ok,
        })
        if verbose:
            s = "✅" if ok else "❌"
            print(f"  [{i+1:02d}] {s} '{case['input']}' → "
                  f"期望:{case['expected_action']} 实际:{actual}")

    total = len(eval_cases)
    acc = passed / total if total > 0 else 0.0
    print(f"\n{'='*50}")
    print(f"  评测结果: {total} cases, {passed} passed, accuracy = {acc:.2f}")
    print(f"{'='*50}")
    result = {"total": total, "passed": passed, "accuracy": acc,
              "details": details}
    write_trace({"event": "eval_complete", **result})
    return result


# ===================================================================
# CLI 入口
# ===================================================================

def main():
    if len(sys.argv) < 2:
        print("AI Harness for CampusTask")
        print("用法:")
        print("  python ai_harness.py chat       — 交互式对话模式")
        print("  python ai_harness.py eval       — 运行评测")
        print('  python ai_harness.py run "输入"  — 单次执行')
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "eval":
        run_eval(load_eval_cases())
    elif cmd == "run":
        if len(sys.argv) < 3:
            print("请提供输入")
            sys.exit(1)
        run_harness(" ".join(sys.argv[2:]))
    elif cmd == "chat":
        print("CampusTask AI 助手 (输入 'quit' 退出)")
        print("-" * 40)
        while True:
            try:
                ui = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见!")
                break
            if not ui:
                continue
            if ui.lower() in ("quit", "exit", "q"):
                print("再见!")
                break
            run_harness(ui)
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
