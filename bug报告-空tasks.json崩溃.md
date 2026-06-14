# Bug 报告：空 `tasks.json` 导致程序崩溃

## 基本信息

| 项目 | 内容 |
|------|------|
| Bug ID | BUG-001 |
| 发现版本 | v0.1.0 |
| 严重程度 | 高 |
| 报告人 | 教师（模拟用户反馈） |

## 问题描述

当 `tasks.json` 文件存在但内容为空时，程序在执行任何命令时直接崩溃（`json.JSONDecodeError`），无任何错误提示。

## 复现步骤

```bash
echo "" > tasks.json
python -m campus_task list
```

预期：显示"暂无任务"
实际：程序崩溃，抛出 `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

## 根本原因

`task_storage.py` 的 `load_tasks()` 中 `json.load()` 未对空文件做防御性处理。

## 修复方案

在 `load_tasks()` 中捕获 `json.JSONDecodeError` 和 `OSError`，返回空列表 `[]`。

## 修复后结果

```python
# task_storage.py
except (json.JSONDecodeError, OSError):
    return []
```

执行 `python -m campus_task list` 正确显示"暂无任务"，不再崩溃。

## 修复版本

v0.2.1
