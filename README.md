# 盈在易测 (YingZaiYiCe)

基于易经理论的智能预测系统，整合传统易经理论与现代机器学习方法，提供资金流动预测、占卜、问答等功能。

## 📋 项目结构

```
yingzaiyice/
├─ app.py                     # Streamlit主界面入口
├─ requirements.txt           # 依赖声明
├─ README.md                  # 项目介绍
├─ .gitignore                # Git忽略文件
├─ src/
│   ├─ __init__.py
│   ├─ data.py                # 示例数据生成
│   ├─ models.py              # 易经与机器学习预测器
│   ├─ pipeline.py            # 完整预测流水线
│   ├─ utils.py               # 工具函数
│   ├─ iching_enhanced_models.py
│   ├─ iching_enhanced_system.py
│   ├─ enhanced_qa_system.py  # 增强问答系统
│   ├─ enhanced_divination_system.py  # 增强解卦系统
│   ├─ api_config.py          # API配置
│   └─ api_requests.py        # API请求处理
├─ static/                    # 静态资源文件
│   ├─ emotion-detail.html    # 情感测算页面
│   ├─ fortune-detail.html    # 运势分析页面
│   └─ next-question.html     # 衍生提问页面
├─ docs/                      # 文档目录
│   ├─ 示例数据和模型说明.md  # 示例数据和模型说明
│   ├─ pdf/                    # PDF文档目录
│   │   └─ 《六爻古籍经典合集》 (1).pdf
│   └─ 京氏易精粹全5册/       # 京氏易精粹文档
│       └─ *.pdf, *.doc, *.txt
├─ knowledge_base/             # 知识库目录
│   └─ *.json, *.jsonl 等文件
└─ output/                    # 预测输出结果目录
    ├─ detailed_predictions.csv
    ├─ submission.csv
    ├─ prediction_comparison.png
    └─ historical_trends.png
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

**重要：** 必须在 `yingzaiyice` 目录下运行应用！

#### 方法 1：使用启动脚本（推荐）

Windows 批处理文件：
```bash
cd yingzaiyice
start_app.bat
```

或 PowerShell 脚本：
```powershell
cd yingzaiyice
.\start_app.ps1
```

#### 方法 2：手动启动

在 `yingzaiyice` 目录下运行：

```bash
cd yingzaiyice
streamlit run app.py --server.port 8511
```

**注意：** 不要从项目根目录运行，必须进入 `yingzaiyice` 目录！

应用将在浏览器中打开，默认地址：`http://localhost:8511`

## ✨ 主要功能

### 1. 资金流动预测
- 基于易经理论和机器学习的混合预测模型
- 支持申购和赎回金额预测
- 提供预测结果可视化和详细报告

### 2. 智能问答
- 基于RAG技术的智能问答系统
- 支持周易相关问题解答
- 集成大模型API（Qwen、DeepSeek）

### 3. 占卜功能
- 传统易经占卜
- 随机卦象抽取
- 详细的卦象解释和指导

### 4. 64卦展示
- 完整的六十四卦信息
- 卦辞、卦象解析
- 搜索和详情查看

## 📊 示例数据与模型

### 数据生成

项目包含示例数据生成功能，位于 `src/data.py`：

```python
from src.data import create_sample_data

# 创建示例数据
sample_data = create_sample_data()
```

### 模型架构

#### 1. 易经预测器 (IChingOracle)
- 基于八卦理论进行趋势预测
- 支持日期和金额的卦象计算
- 预测资金流向趋势（升/降/平）

#### 2. 机器学习预测器 (MLPredictor)
- XGBoost：主要预测模型（支持GPU加速）
- Random Forest：辅助预测模型
- Linear Regression：基础预测模型

#### 3. 混合预测器 (HybridPredictor)
- 结合易经和机器学习方法
- 根据易经趋势调整预测结果
- 调整因子：0.05

### 运行完整流水线

```bash
python -m src.pipeline
```

或使用示例数据：

```python
from src.pipeline import PredictionPipeline

# 创建预测流水线
pipeline = PredictionPipeline(
    data_dir="Purchase Redemption Data",
    use_gpu=True,
    adjustment_factor=0.05,
    output_dir="output"
)

# 使用示例数据运行流水线
results = pipeline.run_full_pipeline(use_sample_data=True, n_days=30)
```

## 📁 输出文件

运行预测流水线后，在 `output/` 目录下生成：

- `detailed_predictions.csv` - 详细预测结果
- `submission.csv` - 提交格式的预测结果
- `prediction_comparison.png` - 预测对比图
- `historical_trends.png` - 历史趋势图

## 🔧 配置说明

### API配置

如需使用智能问答功能，需要配置API密钥。编辑 `src/api_config.py` 或设置环境变量：

```bash
export QWEN_API_KEY="your_qwen_api_key"
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

### 模型配置

在 `src/pipeline.py` 中可以配置：

- `use_gpu`: 是否使用GPU加速（默认：True）
- `adjustment_factor`: 易经调整因子（默认：0.05）
- `n_days`: 预测天数（默认：30）

## 📦 依赖包

主要依赖包：

- `streamlit>=1.28.0` - Web界面框架
- `pandas>=1.5.0` - 数据处理
- `numpy>=1.24.0` - 数值计算
- `xgboost>=1.7.0` - 机器学习模型
- `scikit-learn>=1.3.0` - 机器学习工具
- `torch>=2.0.0` - 深度学习框架
- `matplotlib>=3.7.0` - 数据可视化
- `requests>=2.11.0` - HTTP请求

完整依赖列表请查看 `requirements.txt`

## 🎯 使用示例

### 1. 运行Streamlit应用

```bash
streamlit run app.py --server.port 8511
```

### 2. 使用预测流水线

```python
from src.pipeline import PredictionPipeline

pipeline = PredictionPipeline(
    data_dir="Purchase Redemption Data",
    use_gpu=True,
    adjustment_factor=0.05,
    output_dir="output"
)

# 使用真实数据
results = pipeline.run_full_pipeline(use_sample_data=False, n_days=30)

# 使用示例数据
results = pipeline.run_full_pipeline(use_sample_data=True, n_days=30)
```

### 3. 单独使用模块

```python
from src.data import DataLoader, DataPreprocessor, create_sample_data
from src.models import HybridPredictor, IChingOracle
from src.utils import plot_time_series, calculate_metrics

# 创建示例数据
sample_data = create_sample_data()

# 数据预处理
preprocessor = DataPreprocessor()
daily_data = preprocessor.aggregate_daily_data(sample_data['user_balance'])
daily_data = preprocessor.add_time_features(daily_data)

# 训练模型
predictor = HybridPredictor()
feature_cols = preprocessor.get_feature_columns(daily_data)
predictor.train(
    daily_data[feature_cols],
    daily_data['total_purchase_amt'],
    daily_data['total_redeem_amt']
)

# 进行预测
predictions = predictor.predict(daily_data[feature_cols], daily_data['report_date'])
```

## 🔍 易经预测原理

系统基于传统易经理论进行预测：

1. **八卦映射**: 将数值映射到八卦（乾、坤、震、巽、坎、离、艮、兑）
2. **变爻计算**: 根据数值变化计算变爻位置
3. **趋势判断**: 结合原卦和变卦判断资金流向趋势
4. **调整因子**: 根据易经预测结果调整机器学习预测值

## 📈 模型性能

示例数据训练结果：

- **训练数据量**: 154条
- **测试数据量**: 54条
- **申购MAE**: 9,625,236
- **赎回MAE**: 8,902,419
- **申购MAPE**: 3.42%
- **赎回MAPE**: 3.41%

## 🛠️ 开发说明

### 项目结构说明

- `app.py`: Streamlit主应用，包含UI界面和主要功能
- `src/data.py`: 数据加载、预处理和示例数据生成
- `src/models.py`: 易经预测器、机器学习预测器和混合预测器
- `src/pipeline.py`: 完整的预测流水线，整合数据、模型和评估
- `src/utils.py`: 工具函数，包括可视化、评估指标等
- `src/iching_enhanced_models.py`: 增强易经模型
- `src/iching_enhanced_system.py`: 增强易经系统

### 扩展功能

项目支持：

- 自定义特征工程
- 多种机器学习模型
- 实时预测
- 批量预测
- 结果可视化

## ⚠️ 注意事项

1. 系统支持GPU加速，需要安装CUDA版本的PyTorch
2. 中文输出可能存在编码问题，建议使用UTF-8编码
3. 示例数据仅用于测试，实际使用时请替换为真实数据
4. 预测结果需要根据实际情况进行调整和验证
5. API密钥需要妥善保管，不要提交到版本控制系统

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 完整的64卦展示功能
- 占卜功能实现
- RAG问答系统集成
- 资金流动预测功能
- 传统中国风界面设计

## 📄 许可证

本项目采用MIT许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件反馈

---

**享受您的周易预测之旅！** ☯

