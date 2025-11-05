# 周易金融预测系统

基于易经理论的金融资金流动预测系统，整合传统易经理论与现代机器学习方法。

## 系统架构

```
src/
├── __init__.py          # 模块初始化
├── data.py              # 数据加载和预处理
├── models.py            # 易经和机器学习模型
├── pipeline.py          # 完整的预测流程
├── utils.py             # 工具函数
└── README.md            # 使用说明
```

## 主要功能

### 1. 数据模块 (data.py)
- **DataLoader**: 数据加载器，支持加载用户资金流水、用户信息、货币基金收益率、Shibor利率等数据
- **DataPreprocessor**: 数据预处理器，提供时间特征、滞后特征、滚动统计特征等功能
- **create_sample_data()**: 创建示例数据用于测试

### 2. 模型模块 (models.py)
- **IChingOracle**: 易经预测器，基于八卦理论进行趋势预测
- **MLPredictor**: 机器学习预测器，使用XGBoost进行预测
- **HybridPredictor**: 混合预测器，结合易经和机器学习方法

### 3. 流水线模块 (pipeline.py)
- **PredictionPipeline**: 完整的预测流水线，整合数据加载、预处理、模型训练和预测

### 4. 工具模块 (utils.py)
- 可视化功能：时间序列图、相关性矩阵、预测对比图
- 评估指标：MAE、MSE、RMSE、MAPE、R²
- 数据验证和格式化功能

## 使用方法

### 基本使用

```python
# 运行完整的预测流水线
python -m src.pipeline
```

### 自定义使用

```python
from src import PredictionPipeline

# 创建预测流水线
pipeline = PredictionPipeline(
    data_dir="Purchase Redemption Data",
    use_gpu=True,
    adjustment_factor=0.05,
    output_dir="output"
)

# 运行完整流水线
results = pipeline.run_full_pipeline(use_sample_data=True, n_days=30)
```

### 单独使用模块

```python
from src.data import DataLoader, DataPreprocessor
from src.models import HybridPredictor
from src.utils import plot_time_series, calculate_metrics

# 加载数据
loader = DataLoader()
data = loader.load_all_data()

# 预处理数据
preprocessor = DataPreprocessor()
daily_data = preprocessor.aggregate_daily_data(data['user_balance'])
daily_data = preprocessor.add_time_features(daily_data)

# 训练模型
predictor = HybridPredictor()
feature_cols = preprocessor.get_feature_columns(daily_data)
predictor.train(daily_data[feature_cols], daily_data['total_purchase_amt'], daily_data['total_redeem_amt'])

# 进行预测
predictions = predictor.predict(daily_data[feature_cols], daily_data['report_date'])
```

## 输出文件

运行流水线后，会在输出目录生成以下文件：

- `detailed_predictions.csv`: 详细预测结果
- `submission.csv`: 提交格式的预测结果
- `prediction_comparison.png`: 预测对比图
- `historical_trends.png`: 历史趋势图

## 易经预测原理

系统基于传统易经理论进行预测：

1. **八卦映射**: 将数值映射到八卦（乾、坤、震、巽、坎、离、艮、兑）
2. **变爻计算**: 根据数值变化计算变爻位置
3. **趋势判断**: 结合原卦和变卦判断资金流向趋势
4. **调整因子**: 根据易经预测结果调整机器学习预测值

## 依赖包

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost torch holidays
```

## 注意事项

1. 系统支持GPU加速，需要安装CUDA版本的PyTorch
2. 中文输出可能存在编码问题，建议使用UTF-8编码
3. 示例数据仅用于测试，实际使用时请替换为真实数据
4. 预测结果需要根据实际情况进行调整和验证

## 扩展功能

- 支持自定义特征工程
- 支持多种机器学习模型
- 支持实时预测
- 支持批量预测
- 支持结果可视化

## 联系方式

如有问题或建议，请联系开发团队。








