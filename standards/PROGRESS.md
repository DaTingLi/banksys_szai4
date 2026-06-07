# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2025-06-07 · by AI)

- **阶段**: `初始化规划（等待确认）`
- **上一步完成**: 填写 `00-project-context.md` 和 `01-requirements.md`，确定项目技术栈与需求
- **下一步 (TODO 第一条)**: 建仓 + 配 Secrets（第 ① 步）
- **阻塞项**: 无（等待用户确认后开始执行）

---

## 待办清单 (TODO,按优先级)

### 第一批：初始化项目工程化与 CI/CD（US-1）
- [ ] ① 建仓 + 配 Secrets
  - [ ] 使用 `gh` 创建 GitHub 仓库（banksys_szai4）
  - [ ] 初始化本地 git，提交占位结构到 main
  - [ ] **✋ 确认门**：提示配置 GitHub Secrets（SSH_PRIVATE_KEY、SSH_HOST、SSH_USER）
- [ ] ② 开 feature 分支
  - [ ] 从 main 切出 `feature/1-init-ci-cd`
  - [ ] **✋ 确认门**：报出分支名
- [ ] ③ 本地模块化开发（逐模块汇报）
  - [ ] 模块 A：创建目录结构（app/、tests/ 等）
  - [ ] 模块 B：配置 pyproject.toml（ruff）
  - [ ] 模块 C：配置 requirements.txt / requirements-dev.txt
  - [ ] 模块 D：配置 Dockerfile
  - [ ] 模块 E：配置 CI workflow（.github/workflows/ci.yml）
  - [ ] 模块 F：配置 CD workflow（.github/workflows/cd.yml）
  - [ ] 模块 G：编写基础测试（占位 test_health）
  - [ ] 模块 H：编写基础 Streamlit 应用（占位页面 + 健康检查）
  - [ ] **✋ 确认门**：每个模块完成后汇报
- [ ] ④ 本地 CI 自检
  - [ ] 执行 `ruff format --check .`
  - [ ] 执行 `ruff check .`
  - [ ] 执行 `pytest`
  - [ ] **✋ 确认门**：汇报自检结果，全绿才继续
- [ ] ⑤ 触发 PR
  - [ ] `git push` 分支
  - [ ] `gh pr create` 发起 PR
  - [ ] **✋ 确认门**：报出 PR 链接与 CI 状态
- [ ] ⑥ 人工审核 → 合并（人类） → CD 自动部署
  - [ ] **✋ AI 在此硬停**：等待人工 Review 和合并
  - [ ] 合并后 CD 自动触发
  - [ ] **✋ 确认门**：汇报部署结果（端口、健康检查）

### 第二批：数据加载与预处理模块（US-2）
- [ ] 实现 app/models/data_loader.py
- [ ] 编写 test_data_loader.py（覆盖正常/异常场景）
- [ ] 本地自检 + 提 PR

### 第三批：数据分析交互页面（US-3）
- [ ] 实现 app/pages/01_data_analysis.py
- [ ] 实现数据可视化逻辑（app/models/visualizer.py）
- [ ] 编写测试 + 提 PR

### 第四批：模型训练脚本（US-4）
- [ ] 实现 app/ml/train.py（离线训练脚本）
- [ ] 配置 ml/model/ 加入 .gitignore
- [ ] 本地运行训练，验证模型产出
- [ ] 提 PR

### 第五批：预测服务核心逻辑（US-5）
- [ ] 实现 app/models/predictor.py
- [ ] 编写 test_predictor.py
- [ ] 提 PR

### 第六批：在线预测页面（US-6）
- [ ] 实现 app/pages/02_prediction.py（点选式表单）
- [ ] 集成 predictor 模块
- [ ] 提 PR

### 第七批：测试覆盖与质量门禁完善（US-7 & US-8）
- [ ] 补充测试覆盖率到 ≥80%
- [ ] 验证 CI/CD 完整流程
- [ ] 最终验收

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2025-06-07 | 选择 Streamlit 作为 Web 框架 | 课程要求；快速构建数据应用；适合数据分析与模型演示场景 |
| 2025-06-07 | 模型训练离线，预测在线 | 训练是重操作不适合实时请求；预测是轻操作需要快速响应 |
| 2025-06-07 | 数据集进 Git，模型产物不进 Git | 教学用公开数据，方便复现；模型产物二进制大文件，不应进版本控制 |
| 2025-06-07 | 端口选择 8004 | 课程指定端口；Streamlit 默认 8501，Docker 映射到主机 8004 |

---

## 已知坑 (GOTCHAS)

- 暂无（开始开发后记录）

---

## 里程碑 (DONE)

- [x] 2025-06-07：填写 `00-project-context.md`，确定项目技术栈（Python 3.11 + Streamlit + pytest + ruff + Docker）、目录地图、质量门槛
- [x] 2025-06-07：填写 `01-requirements.md`，定义 8 个用户故事（US-1 ~ US-8），覆盖完整开发流程
- [x] 2025-06-07：初始化 `PROGRESS.md`，列出第一批 TODO

> 反臃肿:里程碑超过 15 条时,把更早内容合并成一行摘要,保持本文件可快速阅读。
