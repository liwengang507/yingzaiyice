"""
股市预测模块
============

结合周易理论的股市预测系统
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

from .models import IChingOracle
from .stock_data import StockDataCrawler, StockNewsAnalyzer, create_sample_stock_data

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class StockIChingPredictor:
    """股市周易预测器"""
    
    def __init__(self):
        """初始化预测器"""
        self.iching_oracle = IChingOracle()
        self.stock_crawler = StockDataCrawler()
        self.news_analyzer = StockNewsAnalyzer()
        
        # 股市特有的八卦映射
        self.stock_trigrams = {
            0: {'name': '坤', 'nature': '阴', 'trend': '平', 'value': 8, 'market_meaning': '平稳整理'},
            1: {'name': '乾', 'nature': '阳', 'trend': '平', 'value': 1, 'market_meaning': '强势上涨'},
            2: {'name': '兑', 'nature': '阴', 'trend': '降', 'value': 2, 'market_meaning': '温和下跌'},
            3: {'name': '离', 'nature': '阴', 'trend': '升', 'value': 3, 'market_meaning': '科技上涨'},
            4: {'name': '震', 'nature': '阳', 'trend': '升', 'value': 4, 'market_meaning': '震荡上涨'},
            5: {'name': '巽', 'nature': '阴', 'trend': '降', 'value': 5, 'market_meaning': '缓慢下跌'},
            6: {'name': '坎', 'nature': '阳', 'trend': '降', 'value': 6, 'market_meaning': '深度调整'},
            7: {'name': '艮', 'nature': '阳', 'trend': '升', 'value': 7, 'market_meaning': '稳健上涨'}
        }
    
    def calculate_stock_trigram(self, price, volume, date):
        """
        计算股票卦象
        
        Args:
            price (float): 股价
            volume (int): 成交量
            date (datetime): 日期
            
        Returns:
            dict: 卦象信息
        """
        # x变量数：价格因子（下卦）
        x = int(price * 100) % 8
        
        # y变量数：时间因子（上卦）
        y = (date.day + date.month * 10 + date.year) % 8
        
        # z变量数：成交量因子（变爻）
        z = int(volume / 1000000) % 6 or 6
        
        # 获取原卦
        x_trigram = self.stock_trigrams[x]
        y_trigram = self.stock_trigrams[y]
        
        # 计算变爻
        changing_line = z
        
        # 计算变卦
        if changing_line <= 3:
            # 变爻影响下卦
            changed_x = self.stock_trigrams[(x + 1) % 8]
            changed_y = y_trigram
        else:
            # 变爻影响上卦
            changed_x = x_trigram
            changed_y = self.stock_trigrams[(y + 1) % 8]
        
        return {
            'original_lower': x_trigram,
            'original_upper': y_trigram,
            'changed_lower': changed_x,
            'changed_upper': changed_y,
            'changing_line': changing_line,
            'market_interpretation': self._interpret_market_trigram(x_trigram, y_trigram, changed_x, changed_y)
        }
    
    def _interpret_market_trigram(self, x_trigram, y_trigram, changed_x, changed_y):
        """
        解释市场卦象
        
        Args:
            x_trigram: 下卦
            y_trigram: 上卦
            changed_x: 变卦下卦
            changed_y: 变卦上卦
            
        Returns:
            dict: 市场解释
        """
        # 原卦趋势
        original_trend = x_trigram['trend'] + y_trigram['trend']
        changed_trend = changed_x['trend'] + changed_y['trend']
        
        # 趋势变化
        trend_change = changed_trend - original_trend
        
        # 市场建议
        if trend_change > 0:
            advice = "市场趋势向好，可考虑适当加仓"
        elif trend_change < 0:
            advice = "市场趋势转弱，建议谨慎操作"
        else:
            advice = "市场趋势平稳，保持观望"
        
        return {
            'original_trend': original_trend,
            'changed_trend': changed_trend,
            'trend_change': trend_change,
            'advice': advice,
            'risk_level': self._assess_risk_level(original_trend, changed_trend)
        }
    
    def _assess_risk_level(self, original_trend, changed_trend):
        """
        评估风险等级
        
        Args:
            original_trend: 原卦趋势
            changed_trend: 变卦趋势
            
        Returns:
            str: 风险等级
        """
        trend_diff = abs(changed_trend - original_trend)
        
        if trend_diff >= 2:
            return "高风险"
        elif trend_diff >= 1:
            return "中风险"
        else:
            return "低风险"
    
    def generate_stock_iching_features(self, stock_data):
        """
        生成股市易卦特征
        
        Args:
            stock_data (pd.DataFrame): 股票数据
            
        Returns:
            pd.DataFrame: 易卦特征
        """
        features = []
        
        for _, row in stock_data.iterrows():
            trigram_info = self.calculate_stock_trigram(
                row['close'], row['volume'], row['date']
            )
            
            features.append([
                trigram_info['original_lower']['trend'],
                trigram_info['original_upper']['trend'],
                trigram_info['changed_lower']['trend'],
                trigram_info['changed_upper']['trend'],
                trigram_info['changing_line'],
                1 if trigram_info['original_lower']['nature'] == '阳' else 0,
                1 if trigram_info['original_upper']['nature'] == '阳' else 0,
                trigram_info['market_interpretation']['original_trend'],
                trigram_info['market_interpretation']['changed_trend'],
                trigram_info['market_interpretation']['trend_change']
            ])
        
        return pd.DataFrame(features, columns=[
            'original_lower_trend',
            'original_upper_trend', 
            'changed_lower_trend',
            'changed_upper_trend',
            'changing_line',
            'lower_yang',
            'upper_yang',
            'original_combined_trend',
            'changed_combined_trend',
            'trend_change'
        ])
    
    def predict_stock_trend(self, stock_data, news_data=None):
        """
        预测股票趋势
        
        Args:
            stock_data (pd.DataFrame): 股票数据
            news_data (list): 新闻数据
            
        Returns:
            dict: 预测结果
        """
        print("开始股市周易预测分析...")
        
        # 生成易卦特征
        iching_features = self.generate_stock_iching_features(stock_data)
        
        # 基础技术指标
        stock_data['ma5'] = stock_data['close'].rolling(5).mean()
        stock_data['ma10'] = stock_data['close'].rolling(10).mean()
        stock_data['ma20'] = stock_data['close'].rolling(20).mean()
        stock_data['rsi'] = self._calculate_rsi(stock_data['close'])
        stock_data['macd'] = self._calculate_macd(stock_data['close'])
        
        # 合并特征
        feature_cols = ['ma5', 'ma10', 'ma20', 'rsi', 'macd']
        technical_features = stock_data[feature_cols].fillna(0)
        
        # 合并所有特征
        all_features = pd.concat([technical_features, iching_features], axis=1)
        
        # 新闻情感分析
        sentiment_score = 0
        if news_data:
            sentiment_result = self.news_analyzer.analyze_news_sentiment(news_data)
            sentiment_score = sentiment_result['sentiment_score']
        
        # 预测未来趋势
        predictions = []
        for i in range(5):  # 预测未来5天
            # 使用最后的数据进行预测
            last_features = all_features.iloc[-1:].copy()
            
            # 应用周易调整
            iching_adjustment = self._apply_iching_adjustment(last_features, i)
            
            # 基础预测
            base_prediction = stock_data['close'].iloc[-1] * (1 + np.random.normal(0, 0.02))
            
            # 应用周易调整
            final_prediction = base_prediction * (1 + iching_adjustment)
            
            # 应用新闻情感调整
            news_adjustment = sentiment_score * 0.01  # 1%的情感影响
            final_prediction = final_prediction * (1 + news_adjustment)
            
            predictions.append({
                'date': stock_data['date'].iloc[-1] + timedelta(days=i+1),
                'predicted_price': final_prediction,
                'iching_adjustment': iching_adjustment,
                'news_adjustment': news_adjustment
            })
        
        return {
            'predictions': predictions,
            'iching_features': iching_features,
            'sentiment_score': sentiment_score,
            'market_analysis': self._generate_market_analysis(stock_data, iching_features)
        }
    
    def _apply_iching_adjustment(self, features, day_offset):
        """
        应用周易调整
        
        Args:
            features: 特征数据
            day_offset: 天数偏移
            
        Returns:
            float: 调整系数
        """
        # 基于易卦特征计算调整系数
        trend_change = features['trend_change'].iloc[0]
        original_trend = features['original_combined_trend'].iloc[0]
        changed_trend = features['changed_combined_trend'].iloc[0]
        
        # 调整系数计算
        adjustment = (trend_change + original_trend + changed_trend) / 3 * 0.01
        
        # 根据天数偏移调整
        adjustment = adjustment * (1 - day_offset * 0.1)
        
        return adjustment
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd.fillna(0)
    
    def _generate_market_analysis(self, stock_data, iching_features):
        """
        生成市场分析报告
        
        Args:
            stock_data: 股票数据
            iching_features: 易卦特征
            
        Returns:
            dict: 市场分析
        """
        latest_price = stock_data['close'].iloc[-1]
        price_change = stock_data['close'].iloc[-1] - stock_data['close'].iloc[-2]
        price_change_pct = (price_change / stock_data['close'].iloc[-2]) * 100
        
        # 易卦分析
        latest_trigram = iching_features.iloc[-1]
        
        return {
            'current_price': latest_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'iching_trend': latest_trigram['trend_change'],
            'risk_assessment': self._assess_risk_level(
                latest_trigram['original_combined_trend'],
                latest_trigram['changed_combined_trend']
            ),
            'recommendation': self._generate_recommendation(latest_trigram)
        }
    
    def _generate_recommendation(self, trigram_features):
        """
        生成投资建议
        
        Args:
            trigram_features: 易卦特征
            
        Returns:
            str: 投资建议
        """
        trend_change = trigram_features['trend_change']
        
        if trend_change > 1:
            return "强烈建议买入，市场趋势向好"
        elif trend_change > 0:
            return "建议适当买入，市场有上涨潜力"
        elif trend_change == 0:
            return "建议观望，市场趋势平稳"
        elif trend_change > -1:
            return "建议谨慎操作，市场有下跌风险"
        else:
            return "建议减仓或观望，市场趋势转弱"
    
    def visualize_predictions(self, stock_data, predictions, output_path="stock_predictions.png"):
        """
        可视化预测结果
        
        Args:
            stock_data: 历史股票数据
            predictions: 预测结果
            output_path: 输出路径
        """
        plt.figure(figsize=(15, 10))
        
        # 历史价格
        plt.subplot(2, 1, 1)
        plt.plot(stock_data['date'], stock_data['close'], label='历史价格', color='blue', alpha=0.7)
        
        # 预测价格
        pred_dates = [p['date'] for p in predictions]
        pred_prices = [p['predicted_price'] for p in predictions]
        plt.plot(pred_dates, pred_prices, label='预测价格', color='red', marker='o', markersize=4)
        
        plt.title('股市周易预测结果', fontsize=16, fontweight='bold')
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 易卦调整因子
        plt.subplot(2, 1, 2)
        iching_adjustments = [p['iching_adjustment'] for p in predictions]
        plt.bar(range(len(iching_adjustments)), iching_adjustments, 
                color='green', alpha=0.7, label='周易调整因子')
        plt.title('周易调整因子', fontsize=14)
        plt.xlabel('预测天数')
        plt.ylabel('调整系数')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"预测结果图表已保存到: {output_path}")
        plt.show()


def main():
    """主函数"""
    print("股市周易预测系统")
    print("=" * 50)
    
    # 创建预测器
    predictor = StockIChingPredictor()
    
    # 获取示例数据
    print("正在获取市场数据...")
    sample_data = create_sample_stock_data()
    
    # 进行预测
    print("正在进行股市预测...")
    results = predictor.predict_stock_trend(
        sample_data['stock_data'], 
        sample_data['news_data']
    )
    
    # 显示结果
    print("\n预测结果:")
    print("-" * 30)
    for i, pred in enumerate(results['predictions']):
        print(f"第{i+1}天 ({pred['date'].strftime('%Y-%m-%d')}): "
              f"预测价格 {pred['predicted_price']:.2f}, "
              f"周易调整 {pred['iching_adjustment']:.4f}")
    
    # 市场分析
    analysis = results['market_analysis']
    print(f"\n市场分析:")
    print(f"当前价格: {analysis['current_price']:.2f}")
    print(f"价格变化: {analysis['price_change']:.2f} ({analysis['price_change_pct']:.2f}%)")
    print(f"周易趋势: {analysis['iching_trend']:.2f}")
    print(f"风险评估: {analysis['risk_assessment']}")
    print(f"投资建议: {analysis['recommendation']}")
    
    # 可视化
    predictor.visualize_predictions(
        sample_data['stock_data'], 
        results['predictions']
    )
    
    print("\n股市周易预测完成！")


if __name__ == "__main__":
    main()
