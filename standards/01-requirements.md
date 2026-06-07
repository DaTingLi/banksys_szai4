# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 课程作业要求 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: PR 触发 CI,至少包含格式检查(ruff)、静态检查(ruff)、单元测试(pytest)、构建检查(docker build)。
- AC3: CI 全绿后合并 main。
- AC4: 合并 main 自动触发 CD,部署后健康检查通过(端口 8004)。
- AC5: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- 首个 US 必须完整演示六步交付流程。
- 建仓后必须提示配置 GitHub Secrets (SSH_PRIVATE_KEY/SSH_HOST/SSH_USER)。

---

### US-2 数据加载与预处理模块 · 状态: Backlog

作为 **开发者**,
我想要 一个可复用的数据加载模块,
以便 支持数据分析页面和模型训练的数据需求。

验收标准:
- AC1: Given 数据文件存在,When 调用 `load_train_data()` 和 `load_test_data()`,Then 返回 pandas DataFrame。
- AC2: Given 原始数据,When 加载数据,Then 列包含 21 个特征(id/age/job/.../subscribe)。
- AC3: Given 数据加载,When 访问数据,Then 能正确处理中英文列名、缺失值。
- AC4: Given 数据加载模块,When 编写单元测试,Then 覆盖正常加载、文件不存在、空文件场景。
- AC5: Given 数据目录,When 部署,Then data/ 目录在镜像内正确挂载。

技术备注:
- 数据文件是 UTF-8 编码的 CSV。
- 需要处理可能的缺失值标记为 'unknown'/'nonexistent'。

---

### US-3 数据分析交互页面 · 状态: Backlog

作为 **业务分析师**,
我想要 通过可视化界面探索银行营销数据,
以便 快速理解客户特征分布和营销效果。

验收标准:
- AC1: Given 访问应用首页或导航到"数据分析",When 页面加载,Then 显示数据概览(总记录数、认购率)。
- AC2: Given 数据分析页面,When 选择分析维度,Then 展示对应图表(年龄分布饼图、职业认购率柱状图、教育水平热力图等)。
- AC3: Given 数据分析页面,When 进行交互操作(选择/筛选),Then 图表实时更新。
- AC4: Given 页面存在,When 访问非本地环境,Then 页面在 Docker 容器中正常渲染。
- AC5: Given 页面功能,When 编写测试,Then 核心可视化逻辑有单元测试覆盖。

技术备注:
- 使用 Streamlit 的 st.metric/st.pyplot/st.plotly_chart 等组件。
- 图表包括但不限于：年龄分布、职业分布、婚姻状况、教育水平、认购率分析。

---

### US-4 模型训练脚本与流程 · 状态: Backlog

作为 **开发者**,
我想要 一个离线训练脚本,
以便 从历史数据中学习认购预测模型。

验收标准:
- AC1: Given 训练数据,When 执行 `python -m app.ml.train`,Then 在 ml/model/ 目录输出模型文件(model.pkl)。
- AC2: Given 训练过程,When 训练完成,Then 打印关键指标(AUC、准确率、分类报告)到日志。
- AC3: Given 模型文件,When 模型已存在,Then 训练脚本可选择覆盖或跳过(命令行参数)。
- AC4: Given 训练脚本,When 在 CI 环境运行,Then 训练可复现(固定随机种子)。
- AC5: Given 模型产物,When 提交代码,Then ml/model/ 在 .gitignore 中,不进 Git。

技术备注:
- 使用 scikit-learn(LogisticRegression/RandomForest/XGBoost 任选其一)。
- 需要处理类别特征编码(OneHot/LabelEncoding)。
- 固定 random_state 保证可复现性。

---

### US-5 预测服务核心逻辑 · 状态: Backlog

作为 **系统**,
我想要 一个预测服务模块,
以便 根据输入特征返回认购概率。

验收标准:
- AC1: Given 模型文件存在,When 调用 `predict(features_dict)`,Then 返回预测结果(是否认购、概率)。
- AC2: Given 特征输入,When 输入合法特征,Then 正确编码并调用模型。
- AC3: Given 特征输入,When 输入缺失或非法值,Then 返回友好错误或默认处理。
- AC4: Given 预测模块,When 编写测试,Then 覆盖正常预测、模型文件缺失、非法输入场景。
- AC5: Given 预测服务,When 响应请求,Then 单次预测响应时间 <1s。

技术备注:
- 特征编码必须与训练时一致(建议保存 encoder)。
- 返回格式：{"subscribe": bool, "probability": float, "confidence": str}。

---

### US-6 在线预测页面 · 状态: Backlog

作为 **营销人员**,
我想要 通过点选式表单输入客户特征,
以便 快速预测该客户的认购意愿。

验收标准:
- AC1: Given 访问"预测系统"页面,When 页面加载,Then 显示点选式表单(年龄段、职业、婚姻、教育等选择器)。
- AC2: Given 表单填写完成,When 点击"预测"按钮,Then 页面显示预测结果(是否认购、概率、置信度)。
- AC3: Given 预测结果,When 显示结果,Then 提供可视化进度条或仪表盘展示概率。
- AC4: Given 表单,When 用户操作,Then 表单支持重置、重新预测。
- AC5: Given 预测页面,When 在生产环境,Then 预测功能在 Docker 容器中正常工作。

技术备注:
- 使用 Streamlit 的 st.selectbox/st.slider/st.button 组件。
- 特征选项参考训练数据中的唯一值分布。
- 结果展示包括：预测标签、概率进度条、建议文案。

---

### US-7 健康检查与监控 · 状态: Backlog

作为 **运维/CD 流水线**,
我想要 一个健康检查端点,
以便 验证服务是否正常运行。

验收标准:
- AC1: Given 服务运行,When 访问 `/_stcore/health`,Then 返回 200 状态码。
- AC2: Given 模型加载,When 服务启动,Then 模型文件成功加载,预测功能可用。
- AC3: Given 部署脚本,When CD 执行,Then 健康检查失败时 CD 流水线报错。

技术备注:
- Streamlit 默认提供 `/_stcore/health` 端点。
- 可选：添加自定义监控指标(请求计数、模型版本)。

---

### US-8 测试覆盖与质量门禁 · 状态: Backlog

作为 **CI 流水线**,
我想要 完整的测试覆盖,
以便 保证代码质量。

验收标准:
- AC1: Given 核心业务逻辑,When 运行 `pytest --cov`,Then 覆盖率 ≥80%。
- AC2: Given CI 触发,When PR 提交,Then CI 执行格式检查、静态检查、单元测试、构建。
- AC3: Given 任意检查失败,When CI 红灯,Then PR 不能合并。
- AC4: Given 本地开发,When 提交前,Then 开发者本地执行自检并全绿。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑必须有单元测试。
- **可部署**:部署后必须有健康检查或等价验证。
- **性能**:单次预测响应 <1s,页面首屏加载 <3s。
