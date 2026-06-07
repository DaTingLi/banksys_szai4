# banksys_szai4

银行营销数据分析与认购预测系统。

## 功能

- 数据分析交互页面：可视化展示客户特征分布和营销效果
- 在线预测系统：通过点选式表单输入客户特征，预测认购意愿

## 技术栈

- Python 3.11
- Streamlit
- scikit-learn
- pytest
- ruff
- Docker

## 快速开始

### 本地运行

```bash
# 创建虚拟环境
conda create -y -n banksys python=3.11
conda activate banksys

# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app/main.py
```

### Docker 运行

```bash
docker build -t banksys:latest .
docker run -d --name banksys -p 8004:8501 banksys:latest
```

访问：http://localhost:8004

## 项目结构

```
banksys_szai4/
├── standards/           # AI 项目记忆与规范
├── app/                 # 应用主目录
│   ├── main.py         # Streamlit 主入口
│   ├── pages/          # 多页面
│   ├── models/         # 业务逻辑
│   └── ml/             # 机器学习模块
├── tests/              # 测试目录
├── data/               # 数据目录
├── requirements.txt    # 生产依赖
└── Dockerfile          # 容器镜像
```

## CI/CD

- CI: 格式检查、静态检查、单元测试、构建
- CD: 合并 main 后自动部署到服务器

## 质量门槛

- 格式检查: `ruff format --check .`
- 静态检查: `ruff check .`
- 单元测试: `pytest`
- 覆盖率: 核心逻辑 ≥80%

---

**注意**: 本项目为教学演示项目，数据集为公开教学数据。
