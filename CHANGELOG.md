# Changelog

所有重要的项目变更都将记录在此文件中。

---

## [0.2.1] - 2026-06-14

### Bug 修复

- 修复空 `tasks.json` 文件导致程序崩溃的问题
- 增强错误处理，所有异常信息写入 `campus_task.log`

### 新增

- 新增 `export` 命令：支持将任务导出为 CSV 文件
- 新增 `--version` 参数：显示版本号
- 新增 `--help` 参数：显示帮助信息
- 添加日志系统，错误信息自动记录到 `campus_task.log`

### 修改

- 重构为可发布的命令行工具，支持 `python -m campus_task` 运行方式
- 使用 `argparse` 替代自定义参数解析
- 创建 `campus_task` 包结构（`__init__.py`, `__main__.py`）

### 文档

- 创建 `USER_GUIDE.md`：完整的用户操作手册
- 更新项目版本号为 `0.2.1`

---

## [0.2.0] - 2026-06-14

### 新增

- 新增 `deadline` 命令：按截止日期排序显示任务（近→远），无截止日期的任务排在最后
- 新增 `search` 命令：支持关键词模糊搜索任务标题，不区分大小写

### 修改

- 更新 `README.md`：添加新命令的使用说明
- 更新 `main.py`：添加 `deadline` 和 `search` 命令处理函数
- 更新 `task_service.py`：添加 `get_tasks_sorted_by_deadline()` 和 `search_tasks()` 函数
- 更新 `tests/test_task_service.py`：添加新功能的测试用例

### 文档

- 创建 `变更请求表.md`：记录用户反馈收集和变更选择理由

---

## [0.1.0] - 2026-06-14

### 初始版本

- 基础任务管理功能（添加、查看、完成任务）
- 任务优先级支持（high/medium/low）
- 截止日期支持
- 过期任务检测
- 数据持久化（JSON 文件）
- 单元测试覆盖