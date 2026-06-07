# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。
> **填写方式**:把 `<...>` 替换成真实内容;用不到的行删掉。

---

## 1. 项目是什么

- **项目名称**: `banksys_szai4`
- **一句话目标**: 基于银行营销数据构建可视化分析与认购预测的 Web 应用
- **使用者/受益者**: 银行营销团队、数据分析师、业务决策者
- **核心功能**:
  - 数据分析交互页面：展示客户特征分布、营销效果分析、数据探索
  - 在线预测系统：基于训练模型,通过点选式表单输入客户特征,预测认购意愿
- **输入/数据**: 银行营销数据集（data/train.csv、data/test.csv），包含 21 个特征（年龄、职业、婚姻、教育、联系方式、经济指标等），目标变量为 subscribe（是否认购定期存款）。**数据进 Git，非敏感教学数据**

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程指定版本，生态成熟 |
| Web/API 框架 | Streamlit 1.x | 快速构建数据应用，适合数据分析与模型演示 |
| 测试 | pytest | Python 标准测试框架，配合插件强大 |
| 格式/静态检查 | ruff | 极速 Python linter/formatter，一统格式与 lint |
| 打包/运行 | Docker | 标准容器化，CI/CD 友好 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |
| 机器学习 | scikit-learn、pandas | 离线训练预测模型、数据处理 |

## 3. 目录地图

```text
banksys_szai4/
├── standards/                 # AI 项目记忆与通用规范
├── app/                       # 应用主目录
│   ├── __init__.py
│   ├── main.py               # Streamlit 主入口
│   ├── pages/                # 多页面结构
│   │   ├── __init__.py
│   │   ├── 01_data_analysis.py    # 数据分析页面
│   │   └── 02_prediction.py        # 预测系统页面
│   ├── models/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── data_loader.py         # 数据加载
│   │   ├── predictor.py           # 预测逻辑
│   │   └── visualizer.py         # 可视化逻辑
│   ├── ml/                   # 机器学习模块
│   │   ├── __init__.py
│   │   ├── train.py               # 离线训练脚本
│   │   └── model/                 # 模型产物目录（.gitignore）
│   └── utils/                # 工具函数
│       └── __init__.py
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_predictor.py
│   ├── test_visualizer.py
│   └── conftest.py
├── data/                      # 数据目录
│   ├── train.csv              # 训练数据
│   └── test.csv               # 测试数据
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖
├── Dockerfile                  # 容器镜像定义
├── .github/workflows/
│   ├── ci.yml                 # 持续集成
│   └── cd.yml                 # 持续交付
├── .gitignore
├── README.md
└── pyproject.toml              # ruff 配置
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | 核心逻辑 ≥80%；UI 页面无覆盖率要求 |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | 训练脚本输出模型指标（AUC、准确率等），预测服务响应时间 <1s |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- **数据集进 Git**（教学用公开数据），但 **模型产物不进 Git**（ml/model/ 目录加入 .gitignore）。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 模型训练是离线操作（本地/CI 执行训练脚本），预测服务加载已训练模型。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys` | 服务器部署目录 |
| `<PORT>` | `8004` | 服务端口（Streamlit 默认 8501，映射到主机 8004） |
| `<PORT_MAX>` | `8010` | 端口回退上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 健康检查端点 |
| `<SSH_USER>` | `root` | 部署用户（按实际环境调整） |
| `<SSH_HOST>` | `<待配置>` | 服务器公网 IP 或域名 |
