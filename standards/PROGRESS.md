# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**: `US-3~US-6 + US-8 已完成（本地全绿），准备推分支发 PR 进 CI/CD`
- **开发策略**: 按用户要求 US-3~US-6 全部本地开发并测试完成后，再统一进 CI/CD（一条大分支一个 PR）
- **上一步完成**: US-8 质量门禁核对 + 修复 Dockerfile 模型烘焙（坑-006）；本地 75 测试全绿、ruff 全过
- **下一步 (TODO 第一条)**: git push feature/3-analysis-and-prediction → gh pr create（之后停下等你审核合并）
- **阻塞项**: 无（端口已固定 8004，见坑-005）

---

## 待办清单 (TODO,按优先级)

### 第一批：初始化项目工程化与 CI/CD（US-1）✅ 已完成
- [x] ① 建仓 + 配 Secrets
- [x] ② 开 feature 分支
- [x] ③ 本地模块化开发（8 个模块）
- [x] ④ 本地 CI 自检
- [x] ⑤ 触发 PR（PR #1）
- [x] ⑥ 人工审核 → 合并 → CD 自动部署（端口 8005）

### 第二批：数据加载与预处理模块（US-2）✅ 已完成
- [x] 实现 app/models/data_loader.py（load_train_data、load_test_data、辅助函数）
- [x] 编写 test_data_loader.py（25 个测试，100% 覆盖率）
- [x] 本地自检 + 提 PR（PR #3）
- [x] 修复 ruff 版本锁定问题
- [x] 修复 CD git ownership 问题
- [x] CD 部署成功（端口 8006）

### 第三批：数据分析交互页面（US-3）✅ 已完成（本地）
- [x] 实现数据可视化逻辑（app/models/visualizer.py，10 函数，100% 覆盖）
- [x] 实现 app/pages/01_data_analysis.py（概览/饼图/类别分析/年龄分析/数值分布，交互式）
- [x] 精简 main.py 为首页，改用 Streamlit 原生多页导航
- [x] 编写 test_visualizer.py（24 个测试）+ 真实数据冒烟验证
- [x] 顺手清理 data_loader.py 死代码、对齐 .gitignore 模型路径
- [ ] 提 PR（按策略推迟到 US-6 完成后统一进 CI/CD）

### 第四批：模型训练脚本（US-4）✅ 已完成（本地）
- [x] 实现 app/ml/train.py（ColumnTransformer+OneHot+RandomForest Pipeline，固定种子）
- [x] app/ml/model/ 已在 .gitignore（git check-ignore 验证通过）
- [x] 本地真跑训练：AUC 0.8964 / 准确率 0.8742，产出 model.pkl
- [x] 编写 test_train.py（10 个测试），CLI 支持 --overwrite/--check-auc
- [ ] 提 PR（推迟到统一进 CI/CD）

### 第五批：预测服务核心逻辑（US-5）✅ 已完成（本地）
- [x] 实现 app/models/predictor.py（load_model 带 lru_cache，predict 返回 subscribe/probability/confidence）
- [x] 编写 test_predictor.py（16 个测试，100% 覆盖）：正常/模型缺失/缺失特征/非法数值/未知类别/响应时间
- [x] 真实模型端到端验证：高意愿 0.90/high，低意愿 0.35；预热后单次 <1s
- [ ] 提 PR（推迟到统一进 CI/CD）

### 第六批：在线预测页面（US-6）✅ 已完成（本地）
- [x] 实现 app/pages/02_prediction.py（点选式表单，类别选项从数据动态取值）
- [x] 集成 predictor 模块（结果含标签/概率进度条/置信度/建议文案，含模型缺失友好提示）
- [x] 本地启动 Streamlit 验证：/_stcore/health=200、data_analysis/prediction 页面均 200
- [ ] 提 PR（推迟到统一进 CI/CD）

### 第七批：测试覆盖与质量门禁完善（US-7 & US-8）
- [x] 核心逻辑覆盖率：data_loader/visualizer/predictor 均 100%（UI 页面按规范不计）
- [x] 注册 pytest unit marker，消除测试告警
- [x] 修复 Dockerfile：构建时训练模型 + 装 curl + 健康检查端点 /_stcore/health（坑-006）
- [ ] 推分支 + 发 PR，CI 复检（含 docker build）
- [ ] 人工审核 → 合并 → CD 部署 → 验证端口 8004 健康检查

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

- **坑-001**: Dockerfile ARG 作用域问题
  - 现象: CI 构建时 `PIP_INDEX_URL` 为空字符串，pip 安装失败
  - 根因: ARG 在 FROM 之前定义，作用域在 FROM 后结束
  - 解决: 在 FROM 后重新声明 ARG，使用 `--index-url` 替代 `-i`
  - 验证: CI Docker 构建步骤通过

- **坑-002**: CD 部署 git 目录检查
  - 现象: 首次部署时 `/opt/banksys` 存在但不是 git 仓库，`git clone || git pull` 失败
  - 根因: 目录存在非空时 `git clone` 失败；非 git 目录时 `git pull` 失败
  - 解决: 先检查是否为 git 目录（`[ -d .git ]`），是则 pull，否则删除后重新克隆
  - 验证: CD 部署成功，端口 8005，健康检查 ok

- **坑-003**: ruff 版本不一致导致 CI 格式检查失败
  - 现象: 本地 `ruff format --check` 通过，CI 失败（1 file would be reformatted）
  - 根因: CI runner 和本地 ruff 版本不同（0.1.0 vs 0.6.4）
  - 解决: 固定 requirements-dev.txt 中 ruff 版本为 `==0.6.4`，CI 中显式安装相同版本
  - 验证: CI 格式检查通过

- **坑-004**: CD git ownership 错误
  - 现象: `fatal: detected dubious ownership in repository at '/opt/banksys'`
  - 根因: Docker 容器操作后目录所有权变化，git 检测到可疑所有权
  - 解决: CD 脚本开头添加 `git config --global --add safe.directory /opt/banksys`
  - 验证: CD 部署成功

- **坑-006**: 模型产物不进镜像导致生产预测失效（已修复）
  - 现象: model.pkl 被 .gitignore 排除，CD 克隆代码后镜像内无模型，预测页报"模型未找到"
  - 根因: 模型是离线产物不进 Git，但 Dockerfile 未在构建时训练
  - 解决: Dockerfile 在 COPY app/ 与 data/ 后增加 `RUN python -m app.ml.train --overwrite`，把模型烤进镜像；同时 slim 镜像补装 curl、HEALTHCHECK 端点改为 /_stcore/health
  - 验证: 待 CI docker build 与 CD 部署确认

- **坑-005**: 端口回退问题（已修复）
  - 现象: 每次部署端口不同（8004→8005→8006），端口递增
  - 根因: 端口检查在容器删除之前；多个旧容器占用不同端口
  - 解决: 先停止所有占用 8000-8010 端口的容器，等待释放，固定使用 8004
  - 验证: CD 成功，固定部署在端口 8004

---

## 里程碑 (DONE)

- [x] 2025-06-07：填写项目规范文档（00/01/PROGRESS）
- [x] 2025-06-07：创建 GitHub 仓库（banksys_szai4）
- [x] 2025-06-07：US-1 完成 - 初始化项目工程化与 CI/CD
  - 完整跑通六步交付流程
  - CI/CD 流水线配置完成
  - CD 成功部署到服务器（端口 8005）
- [x] 2025-06-07：US-2 完成 - 数据加载与预处理模块
  - 实现 data_loader.py 模块（4 个函数，100% 覆盖率）
  - 编写 25 个测试用例
  - 修复 ruff 版本锁定问题
  - 修复 CD git ownership 问题
  - CD 部署成功（端口 8006）

> 反臃肿:里程碑超过 15 条时,把更早内容合并成一行摘要,保持本文件可快速阅读。
