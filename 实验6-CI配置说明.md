# 实验 6：持续集成与质量门禁

## 一、配置概述

本实验为 CampusTask 项目配置了 GitHub Actions 持续集成流程，实现每次 push 或 pull request 自动运行测试。

## 二、创建的文件

### 1. pyproject.toml

Python 项目配置文件，包含：
- 项目元信息（名称、版本、描述）
- Python 版本要求（>= 3.8）
- pytest 配置（测试路径、Python 路径、默认参数）
- black 代码格式化配置
- flake8 代码检查配置

### 2. .github/workflows/test.yml

GitHub Actions CI 工作流配置，包含：
- 触发条件：push 和 pull request 到 main 分支
- 运行环境：Ubuntu
- Python 版本矩阵：3.8、3.9、3.10
- 工作流程：检出代码 → 安装 Python → 安装依赖 → 运行测试

## 三、CI 流程说明

### CI 执行步骤

1. **检出代码**：使用 `actions/checkout@v4` 获取最新代码
2. **安装 Python**：根据矩阵配置安装对应版本
3. **安装依赖**：升级 pip，安装 pytest 和 pytest-cov
4. **运行测试**：执行 `pytest tests/ -v` 运行所有测试用例

### 测试覆盖范围

- `tests/test_task_model.py`：任务模型测试
- `tests/test_task_service.py`：业务逻辑测试  
- `tests/test_task_storage.py`：存储层测试

## 四、测试运行验证

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest tests/ -v
```

## 五、失败-修复流程

### 步骤 1：制造失败（观察 CI 红灯）

修改测试文件或源代码，故意引入错误，然后推送：

```bash
git add .
git commit -m "test: 故意引入测试失败"
git push origin main
```

在 GitHub 仓库的 Actions 页面观察红色失败状态。

### 步骤 2：修复问题（观察 CI 绿灯）

修复引入的错误，重新推送：

```bash
git add .
git commit -m "fix: 修复测试失败"
git push origin main
```

在 GitHub 仓库的 Actions 页面观察绿色成功状态。

## 六、交付物清单

| 文件 | 说明 |
|------|------|
| `pyproject.toml` | Python 项目配置 |
| `.github/workflows/test.yml` | GitHub Actions 工作流 |
| `实验6-CI配置说明.md` | 配置说明文档 |
| CI 失败记录截图 | 首次推送失败的 Actions 记录 |
| CI 成功记录截图 | 修复后成功的 Actions 记录 |

## 七、评分要点

| 评分项 | 权重 | 说明 |
|--------|------|------|
| CI 能正常触发 | 30% | push/pull request 时自动执行 |
| 测试能自动运行 | 30% | pytest 测试套件正常执行 |
| 失败-修复过程完整 | 25% | 有失败记录和成功记录 |
| 配置说明清楚 | 15% | 文档完整清晰 |

---

> 最后更新：2026-06-14