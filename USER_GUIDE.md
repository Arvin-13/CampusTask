# CampusTask 用户手册

## 概述

CampusTask 是一款轻量级的命令行任务管理工具，专为校园学习场景设计。它帮助学生高效管理日常学习任务，支持任务的添加、查看、完成、搜索和导出等功能。

## 安装与运行

### 前置要求

- Python 3.8 或更高版本

### 运行方式

```bash
python -m campus_task <命令> [参数]
```

## 命令参考

### 1. add - 添加任务

**语法：**
```bash
python -m campus_task add "任务标题" [--deadline YYYY-MM-DD] [--priority high|medium|low]
```

**参数：**
- `title`: 任务标题（必填）
- `--deadline`: 截止日期，格式 YYYY-MM-DD（可选）
- `--priority`: 优先级，可选值 high/medium/low，默认 medium（可选）

**示例：**
```bash
python -m campus_task add "复习软件工程"
python -m campus_task add "提交实验报告" --deadline 2026-06-20 --priority high
```

### 2. list - 列出任务

**语法：**
```bash
python -m campus_task list
```

**功能：**
- 显示所有待完成和已完成的任务
- 按优先级排序显示
- 显示任务统计信息（总数、待完成、已完成、已过期）

### 3. done - 标记任务完成

**语法：**
```bash
python -m campus_task done <任务编号>
```

**参数：**
- `id`: 任务编号（从 list 命令中获取）

**示例：**
```bash
python -m campus_task done 1
```

### 4. export - 导出任务

**语法：**
```bash
python -m campus_task export <输出文件名>
```

**参数：**
- `output`: 输出文件名，建议使用 .csv 扩展名

**示例：**
```bash
python -m campus_task export tasks.csv
```

### 5. overdue - 查看过期任务

**语法：**
```bash
python -m campus_task overdue
```

**功能：**
- 列出所有已过期且未完成的任务

### 6. search - 搜索任务

**语法：**
```bash
python -m campus_task search "关键词"
```

**参数：**
- `keyword`: 搜索关键词

**功能：**
- 支持模糊匹配任务标题
- 不区分大小写

**示例：**
```bash
python -m campus_task search "报告"
```

### 7. priority - 按优先级筛选

**语法：**
```bash
python -m campus_task priority <high|medium|low>
```

**参数：**
- `level`: 优先级级别

**示例：**
```bash
python -m campus_task priority high
```

### 8. deadline - 按截止日期排序

**语法：**
```bash
python -m campus_task deadline
```

**功能：**
- 按截止日期从近到远排序显示任务
- 无截止日期的任务排在最后

## 全局参数

### --version

显示当前版本号：
```bash
python -m campus_task --version
```

### --help

显示帮助信息：
```bash
python -m campus_task --help
```

## 任务状态说明

| 状态 | 说明 |
|------|------|
| pending | 待完成 |
| done | 已完成 |

## 优先级说明

| 优先级 | 标记 | 说明 |
|--------|------|------|
| high | 🔴 | 高优先级 |
| medium | 🟡 | 中优先级（默认） |
| low | 🟢 | 低优先级 |

## 数据存储

任务数据存储在当前目录的 `tasks.json` 文件中，采用 JSON 格式保存。

## 日志记录

程序运行过程中发生的错误会自动记录到 `campus_task.log` 文件中，便于问题排查。

## 常见问题

### Q: 任务编号是如何分配的？

A: 任务编号从 1 开始自动递增，删除任务后编号不会重新分配。

### Q: 如何删除任务？

A: 当前版本不支持删除任务功能，已完成的任务会保留在列表中以便统计。

### Q: 如果 tasks.json 文件为空或损坏怎么办？

A: 程序会自动处理这种情况，将其视为空任务列表，不会导致崩溃。

## 示例工作流

```bash
# 添加任务
python -m campus_task add "复习数据结构" --deadline 2026-06-25 --priority high
python -m campus_task add "写课程论文" --priority medium

# 查看任务列表
python -m campus_task list

# 标记任务完成
python -m campus_task done 1

# 导出任务
python -m campus_task export my_tasks.csv
```

---

*CampusTask v0.2.1*
