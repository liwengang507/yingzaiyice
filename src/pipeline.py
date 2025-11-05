"""
预测流水线模块
==============

整合数据加载、预处理、模型训练和预测的完整流程
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from .data import DataLoader, DataPreprocessor, create_sample_data
from .models import HybridPredictor, IChingOracle
from .utils import (
    setup_plotting, plot_time_series, plot_correlation_matrix, 
    plot_prediction_comparison, calculate_metrics, print_metrics,
    save_predictions, create_submission_format, validate_predictions,
    print_validation_results, print_data_summary, create_iching_interpretation
)


class PredictionPipeline:
    """预测流水线"""
    
    def __init__(self, data_dir="Purchase Redemption Data", use_gpu=True, 
                 adjustment_factor=0.05, output_dir="output"):
        """
        初始化预测流水线
        
        Args:
            data_dir (str): 数据目录
            use_gpu (bool): 是否使用GPU
            adjustment_factor (float): 易经调整因子
            output_dir (str): 输出目录
        """
        self.data_dir = data_dir
        self.use_gpu = use_gpu
        self.adjustment_factor = adjustment_factor
        self.output_dir = output_dir
        
        # 初始化组件
        self.data_loader = DataLoader(data_dir)
        self.preprocessor = DataPreprocessor()
        self.predictor = HybridPredictor(use_gpu=use_gpu, adjustment_factor=adjustment_factor)
        self.iching_oracle = IChingOracle()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置绘图环境
        setup_plotting()
        
        print("预测流水线初始化完成")
        print(f"数据目录: {data_dir}")
        print(f"输出目录: {output_dir}")
        print(f"GPU加速: {'是' if use_gpu else '否'}")
        print(f"易经调整因子: {adjustment_factor}")
    
    def load_data(self, use_sample_data=False):
        """
        加载数据
        
        Args:
            use_sample_data (bool): 是否使用示例数据
            
        Returns:
            dict: 数据字典
        """
        print("\n" + "="*50)
        print("开始加载数据...")
        
        if use_sample_data:
            print("使用示例数据进行测试...")
            data = create_sample_data()
        else:
            print("加载真实数据...")
            data = self.data_loader.load_all_data()
        
        print("数据加载完成")
        return data
    
    def preprocess_data(self, data, target_cols=['total_purchase_amt', 'total_redeem_amt']):
        """
        数据预处理
        
        Args:
            data (dict): 数据字典
            target_cols (list): 目标列名
            
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        print("\n" + "="*50)
        print("开始数据预处理...")
        
        # 聚合日度数据
        daily_data = self.preprocessor.aggregate_daily_data(data['user_balance'])
        
        # 添加时间特征
        daily_data = self.preprocessor.add_time_features(daily_data)
        
        # 添加滞后特征
        daily_data = self.preprocessor.add_lag_features(daily_data, target_cols)
        
        # 添加滚动特征
        daily_data = self.preprocessor.add_rolling_features(daily_data, target_cols)
        
        # 合并外部数据
        if 'mfd_interest' in data and 'shibor' in data:
            daily_data = self.preprocessor.merge_external_data(
                daily_data, data['mfd_interest'], data['shibor']
            )
        
        # 清洗数据
        daily_data = self.preprocessor.clean_data(daily_data)
        
        # 打印数据摘要
        print_data_summary(daily_data, "预处理后数据摘要")
        
        print("数据预处理完成")
        return daily_data
    
    def train_model(self, daily_data, target_cols=['total_purchase_amt', 'total_redeem_amt']):
        """
        训练模型
        
        Args:
            daily_data (pd.DataFrame): 预处理后的数据
            target_cols (list): 目标列名
            
        Returns:
            dict: 训练结果
        """
        print("\n" + "="*50)
        print("开始训练模型...")
        
        # 获取特征列
        feature_cols = self.preprocessor.get_feature_columns(daily_data, target_cols)
        X = daily_data[feature_cols]
        y_purchase = daily_data[target_cols[0]]
        y_redeem = daily_data[target_cols[1]]
        
        print(f"特征数量: {len(feature_cols)}")
        print(f"训练样本数: {len(X)}")
        
        # 训练混合模型
        self.predictor.train(X, y_purchase, y_redeem)
        
        # 评估模型性能
        metrics = self.predictor.evaluate(X, y_purchase, y_redeem, daily_data['report_date'])
        
        print("模型训练完成")
        print_metrics(metrics, "模型性能评估")
        
        return {
            'feature_cols': feature_cols,
            'metrics': metrics
        }
    
    def predict(self, daily_data, feature_cols, n_days=30):
        """
        进行预测
        
        Args:
            daily_data (pd.DataFrame): 历史数据
            feature_cols (list): 特征列名
            n_days (int): 预测天数
            
        Returns:
            pd.DataFrame: 预测结果
        """
        print("\n" + "="*50)
        print(f"开始预测未来{n_days}天...")
        
        # 创建预测特征
        last_day = daily_data.iloc[-1:].copy()
        predictions = []
        
        for i in range(1, n_days + 1):
            # 更新日期
            current_date = last_day['report_date'].values[0] + pd.Timedelta(days=i)
            last_day['report_date'] = current_date
            
            # 更新时间特征
            last_day['day_of_week'] = current_date.dayofweek
            last_day['is_weekend'] = int(current_date.weekday() >= 5)
            last_day['month'] = current_date.month
            last_day['day_of_month'] = current_date.day
            last_day['quarter'] = current_date.quarter
            last_day['year'] = current_date.year
            
            # 更新节假日特征
            from holidays import country_holidays
            cn_holidays = country_holidays('CN')
            is_chinese_holiday = lambda date: date in cn_holidays
            last_day['is_holiday'] = int(is_chinese_holiday(current_date))
            last_day['is_workday'] = int(not (is_chinese_holiday(current_date) or current_date.weekday() >= 5))
            
            # 准备特征
            X_pred = last_day[feature_cols]
            
            # 进行预测
            pred_result = self.predictor.predict(X_pred, pd.Series([current_date]))
            
            # 更新滞后特征（简单实现）
            if i == 1:
                last_day['purchase_lag_1'] = pred_result['final_purchase'].iloc[0]
                last_day['redeem_lag_1'] = pred_result['final_redeem'].iloc[0]
            
            predictions.append(pred_result.iloc[0])
        
        predictions_df = pd.DataFrame(predictions)
        
        print("预测完成")
        print(f"预测日期范围: {predictions_df['date'].min()} 至 {predictions_df['date'].max()}")
        print(f"申购金额范围: {predictions_df['final_purchase'].min():,.0f} - {predictions_df['final_purchase'].max():,.0f}")
        print(f"赎回金额范围: {predictions_df['final_redeem'].min():,.0f} - {predictions_df['final_redeem'].max():,.0f}")
        
        return predictions_df
    
    def visualize_results(self, daily_data, predictions):
        """
        可视化结果
        
        Args:
            daily_data (pd.DataFrame): 历史数据
            predictions (pd.DataFrame): 预测结果
        """
        print("\n" + "="*50)
        print("开始生成可视化图表...")
        
        # 预测对比图
        plot_prediction_comparison(
            daily_data, predictions,
            title="周易预测系统：历史 vs 预测",
            save_path=f"{self.output_dir}/prediction_comparison.png"
        )
        
        # 时间序列图
        plot_time_series(
            daily_data, 'report_date', ['total_purchase_amt', 'total_redeem_amt'],
            title="历史资金流动趋势",
            save_path=f"{self.output_dir}/historical_trends.png"
        )
        
        print("可视化图表生成完成")
    
    def save_results(self, predictions, format='csv'):
        """
        保存预测结果
        
        Args:
            predictions (pd.DataFrame): 预测结果
            format (str): 保存格式
        """
        print("\n" + "="*50)
        print("开始保存预测结果...")
        
        # 验证预测结果
        validation = validate_predictions(predictions)
        print_validation_results(validation)
        
        if not validation['is_valid']:
            print("警告：预测结果存在问题，请检查")
        
        # 创建提交格式
        submission = create_submission_format(predictions)
        
        # 保存详细结果
        detailed_path = f"{self.output_dir}/detailed_predictions.{format}"
        save_predictions(predictions, detailed_path, format)
        
        # 保存提交格式
        submission_path = f"{self.output_dir}/submission.csv"
        save_predictions(submission, submission_path, 'csv')
        
        print("预测结果保存完成")
        return submission
    
    def generate_iching_analysis(self, predictions, key_dates=None):
        """
        生成易经分析报告
        
        Args:
            predictions (pd.DataFrame): 预测结果
            key_dates (list): 关键日期列表
        """
        print("\n" + "="*50)
        print("开始生成易经分析报告...")
        
        if key_dates is None:
            # 选择几个关键日期进行分析
            key_dates = predictions['date'].iloc[::len(predictions)//5].tolist()
        
        print("\n关键日期易经分析:")
        print("-" * 50)
        
        for date in key_dates:
            if date in predictions['date'].values:
                idx = predictions[predictions['date'] == date].index[0]
                purchase = predictions.loc[idx, 'final_purchase']
                redeem = predictions.loc[idx, 'final_redeem']
                
                interpretation = create_iching_interpretation(date, purchase, redeem, self.iching_oracle)
                
                print(f"\n{interpretation['日期']}:")
                print(f"  申购趋势: {interpretation['申购趋势']}")
                print(f"  赎回趋势: {interpretation['赎回趋势']}")
                print(f"  建议: {', '.join(interpretation['建议'])}")
        
        print("\n易经分析报告生成完成")
    
    def run_full_pipeline(self, use_sample_data=False, n_days=30):
        """
        运行完整的预测流水线
        
        Args:
            use_sample_data (bool): 是否使用示例数据
            n_days (int): 预测天数
            
        Returns:
            dict: 流水线结果
        """
        print("开始运行完整的预测流水线...")
        print("="*60)
        
        try:
            # 1. 加载数据
            data = self.load_data(use_sample_data)
            
            # 2. 数据预处理
            daily_data = self.preprocess_data(data)
            
            # 3. 训练模型
            train_results = self.train_model(daily_data)
            
            # 4. 进行预测
            predictions = self.predict(daily_data, train_results['feature_cols'], n_days)
            
            # 5. 可视化结果
            self.visualize_results(daily_data, predictions)
            
            # 6. 保存结果
            submission = self.save_results(predictions)
            
            # 7. 生成易经分析
            self.generate_iching_analysis(predictions)
            
            print("\n" + "="*60)
            print("预测流水线运行完成！")
            print(f"结果已保存到: {self.output_dir}")
            
            return {
                'daily_data': daily_data,
                'predictions': predictions,
                'submission': submission,
                'train_results': train_results
            }
            
        except Exception as e:
            print(f"流水线运行失败: {e}")
            raise


def main():
    """主函数"""
    print("周易金融预测系统")
    print("="*60)
    
    # 创建预测流水线
    pipeline = PredictionPipeline(
        data_dir="Purchase Redemption Data",
        use_gpu=True,
        adjustment_factor=0.05,
        output_dir="output"
    )
    
    # 运行完整流水线
    results = pipeline.run_full_pipeline(use_sample_data=True, n_days=30)
    
    print("\n流水线运行完成！")
    print(f"预测结果保存在: {pipeline.output_dir}")


if __name__ == "__main__":
    main()


