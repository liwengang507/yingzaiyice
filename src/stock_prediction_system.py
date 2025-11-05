"""
整合的股市预测系统
结合周易理论、机器学习模型和实时数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 导入自定义模块
from .data import DataLoader, DataPreprocessor
from .models import IChingOracle, HybridPredictor
from .stock_data import StockDataCrawler
from .news_crawler import StockNewsCrawler
from .utils import calculate_metrics, format_number, print_data_summary, create_iching_interpretation

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockPredictionSystem:
    """整合的股市预测系统"""
    
    def __init__(self):
        """初始化预测系统"""
        self.data_loader = DataLoader()
        self.data_preprocessor = DataPreprocessor()
        self.iching_oracle = IChingOracle()
        self.hybrid_predictor = HybridPredictor()
        self.stock_data_provider = StockDataCrawler()
        self.news_crawler = StockNewsCrawler()
        
        # 系统状态
        self.is_trained = False
        self.last_prediction = None
        self.prediction_history = []
        
        logger.info("股市预测系统初始化完成")
    
    def prepare_training_data(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        准备训练数据
        """
        logger.info("开始准备训练数据...")
        
        # 获取历史数据
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 加载数据
        data = self.data_loader.load_all_data()
        
        if data is None or data.empty:
            logger.warning("未找到历史数据，使用模拟数据")
            from .data import create_sample_data
            data = create_sample_data()
        
        # 数据预处理
        processed_data = self.data_preprocessor.clean_data(data)
        
        logger.info(f"训练数据准备完成，数据量: {len(processed_data)}")
        return processed_data
    
    def train_models(self, data: pd.DataFrame = None) -> Dict:
        """
        训练预测模型
        """
        logger.info("开始训练模型...")
        
        if data is None:
            data = self.prepare_training_data()
        
        # 训练混合预测器
        training_results = self.hybrid_predictor.train(data)
        
        self.is_trained = True
        logger.info("模型训练完成")
        
        return training_results
    
    def predict_stock_trend(self, stock_code: str = "000001", days: int = 5) -> Dict:
        """
        预测股票趋势
        """
        if not self.is_trained:
            logger.warning("模型未训练，开始训练...")
            self.train_models()
        
        logger.info(f"开始预测股票 {stock_code} 未来 {days} 天的趋势...")
        
        # 获取实时股票数据
        try:
            real_time_data = self.stock_data_provider.get_stock_data(stock_code)
            if real_time_data is None:
                logger.warning("无法获取实时数据，使用历史数据")
                real_time_data = self.prepare_training_data()
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            real_time_data = self.prepare_training_data()
        
        # 获取新闻数据
        try:
            news_data = self.news_crawler.crawl_all_news(max_pages=2)
            news_sentiment = self.news_crawler.analyze_news_sentiment(news_data)
        except Exception as e:
            logger.error(f"获取新闻数据失败: {e}")
            news_sentiment = {'positive_count': 0, 'negative_count': 0, 'neutral_count': 0}
        
        # 生成预测
        predictions = []
        iching_interpretations = []
        
        for i in range(days):
            # 计算预测日期
            pred_date = datetime.now() + timedelta(days=i+1)
            pred_date_str = pred_date.strftime('%Y%m%d')
            
            # 使用混合模型预测
            if hasattr(self.hybrid_predictor, 'predict'):
                pred_result = self.hybrid_predictor.predict(real_time_data)
                if isinstance(pred_result, dict) and 'predictions' in pred_result:
                    pred_purchase = pred_result['predictions'].get('purchase', 0)
                    pred_redeem = pred_result['predictions'].get('redeem', 0)
                else:
                    pred_purchase = 0
                    pred_redeem = 0
            else:
                pred_purchase = 0
                pred_redeem = 0
            
            # 周易预测
            iching_result = self.iching_oracle.predict_trend(pred_date_str, pred_purchase, pred_redeem)
            
            # 创建周易解释
            iching_interpretation = create_iching_interpretation(
                pred_date, pred_purchase, pred_redeem, self.iching_oracle
            )
            
            predictions.append({
                'date': pred_date,
                'purchase_prediction': pred_purchase,
                'redeem_prediction': pred_redeem,
                'iching_trend': iching_result,
                'iching_interpretation': iching_interpretation
            })
            
            iching_interpretations.append(iching_interpretation)
        
        # 整合预测结果
        prediction_result = {
            'stock_code': stock_code,
            'prediction_date': datetime.now(),
            'prediction_days': days,
            'predictions': predictions,
            'news_sentiment': news_sentiment,
            'market_summary': self.news_crawler.get_market_summary(news_data) if news_data else "暂无新闻数据",
            'iching_interpretations': iching_interpretations
        }
        
        self.last_prediction = prediction_result
        self.prediction_history.append(prediction_result)
        
        logger.info(f"股票 {stock_code} 预测完成")
        return prediction_result
    
    def get_prediction_summary(self, prediction_result: Dict = None) -> str:
        """
        获取预测摘要
        """
        if prediction_result is None:
            prediction_result = self.last_prediction
        
        if prediction_result is None:
            return "暂无预测结果"
        
        summary = f"""
股市预测摘要
===============================================
股票代码: {prediction_result['stock_code']}
预测日期: {prediction_result['prediction_date'].strftime('%Y-%m-%d %H:%M:%S')}
预测天数: {prediction_result['prediction_days']}

预测结果:
"""
        
        for i, pred in enumerate(prediction_result['predictions'], 1):
            summary += f"""
第{i}天 ({pred['date'].strftime('%Y-%m-%d')}):
  申购预测: {format_number(pred['purchase_prediction'])}
  赎回预测: {format_number(pred['redeem_prediction'])}
  周易趋势: {pred['iching_trend']}
"""
        
        # 添加新闻情感分析
        if 'news_sentiment' in prediction_result:
            sentiment = prediction_result['news_sentiment']
            summary += f"""
新闻情感分析:
  正面新闻: {sentiment.get('positive_count', 0)}
  负面新闻: {sentiment.get('negative_count', 0)}
  中性新闻: {sentiment.get('neutral_count', 0)}
"""
        
        return summary
    
    def save_prediction_results(self, prediction_result: Dict = None, filename: str = None):
        """
        保存预测结果
        """
        if prediction_result is None:
            prediction_result = self.last_prediction
        
        if prediction_result is None:
            logger.warning("没有预测结果可保存")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stock_prediction_{prediction_result['stock_code']}_{timestamp}.csv"
        
        # 准备保存数据
        save_data = []
        for pred in prediction_result['predictions']:
            save_data.append({
                'date': pred['date'].strftime('%Y-%m-%d'),
                'purchase_prediction': pred['purchase_prediction'],
                'redeem_prediction': pred['redeem_prediction'],
                'iching_trend': pred['iching_trend'],
                'iching_interpretation': pred['iching_interpretation']
            })
        
        df = pd.DataFrame(save_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"预测结果已保存到: {filename}")
    
    def get_system_status(self) -> Dict:
        """
        获取系统状态
        """
        return {
            'is_trained': self.is_trained,
            'last_prediction_time': self.last_prediction['prediction_date'] if self.last_prediction else None,
            'prediction_count': len(self.prediction_history),
            'system_components': {
                'data_processor': '已加载',
                'iching_oracle': '已加载',
                'hybrid_predictor': '已加载',
                'stock_data_provider': '已加载',
                'news_crawler': '已加载'
            }
        }

def main():
    """主函数 - 演示系统使用"""
    print("=" * 60)
    print("股市预测系统演示")
    print("=" * 60)
    
    # 初始化系统
    system = StockPredictionSystem()
    
    # 显示系统状态
    status = system.get_system_status()
    print(f"\n系统状态:")
    print(f"模型训练状态: {'已训练' if status['is_trained'] else '未训练'}")
    print(f"预测次数: {status['prediction_count']}")
    
    # 训练模型
    print("\n开始训练模型...")
    training_results = system.train_models()
    print("模型训练完成")
    
    # 进行预测
    print("\n开始预测股票趋势...")
    prediction_result = system.predict_stock_trend("000001", days=3)
    
    # 显示预测摘要
    summary = system.get_prediction_summary(prediction_result)
    print(summary)
    
    # 保存结果
    system.save_prediction_results(prediction_result)
    
    # 显示周易解释
    print("\n周易解释:")
    for i, interpretation in enumerate(prediction_result['iching_interpretations'], 1):
        print(f"\n第{i}天预测:")
        print(interpretation)
    
    print("\n系统演示完成!")

if __name__ == "__main__":
    main()
