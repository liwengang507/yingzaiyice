"""
模型模块
========

包含易经预测模型和机器学习模型的实现
"""

import pandas as pd
import numpy as np
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class IChingOracle:
    """易经预测器"""
    
    def __init__(self):
        """初始化易经预测器"""
        # 八卦定义
        self.trigrams = {
            0: {'name': '坤', 'nature': '阴', 'trend': '平', 'value': 8, 'lines': [0,0,0]},
            1: {'name': '乾', 'nature': '阳', 'trend': '平', 'value': 1, 'lines': [1,1,1]},
            2: {'name': '兑', 'nature': '阴', 'trend': '降', 'value': 2, 'lines': [0,1,1]},
            3: {'name': '离', 'nature': '阴', 'trend': '升', 'value': 3, 'lines': [1,0,1]},
            4: {'name': '震', 'nature': '阳', 'trend': '升', 'value': 4, 'lines': [0,0,1]},
            5: {'name': '巽', 'nature': '阴', 'trend': '降', 'value': 5, 'lines': [1,1,0]},
            6: {'name': '坎', 'nature': '阳', 'trend': '降', 'value': 6, 'lines': [0,1,0]},
            7: {'name': '艮', 'nature': '阳', 'trend': '升', 'value': 7, 'lines': [1,0,0]}
        }
    
    def _sum_date(self, date_str):
        """计算日期的数字和"""
        date_str = str(date_str)
        return sum(int(c) if c != '0' else 8 for c in date_str)
    
    def get_trigram(self, num):
        """获取卦象"""
        remainder = num % 8
        return self.trigrams[remainder]
    
    def get_changing_line(self, num):
        """获取变爻位置(1-6)"""
        return num % 6 or 6
    
    def get_changed_trigram(self, original_trigram, changing_line):
        """
        根据变爻计算变卦
        
        Args:
            original_trigram (dict): 原卦
            changing_line (int): 变爻位置(1-6)
            
        Returns:
            dict: 变卦
        """
        trigram_lines = original_trigram['lines'].copy()
        
        if changing_line <= 3:
            # 影响下卦，变爻位置为 changing_line-1 (因为数组从0开始)
            line_pos = changing_line - 1
            trigram_lines[line_pos] = 1 - trigram_lines[line_pos]  # 实变虚，虚变实
        
        # 根据变化后的卦象找到对应的卦
        for value, trigram in self.trigrams.items():
            if trigram['lines'] == trigram_lines:
                return trigram
        
        return original_trigram  # 如果没找到匹配，返回原卦
    
    def predict_trend(self, date_str, purchase, redeem):
        """
        预测资金流向趋势
        
        Args:
            date_str (str): 日期字符串 (YYYYMMDD)
            purchase (float): 申购金额
            redeem (float): 赎回金额
            
        Returns:
            tuple: (申购趋势, 赎回趋势)
        """
        # 计算原卦
        date_sum = self._sum_date(date_str)
        x = self.get_trigram(date_sum)  # 下卦(日期)
        y_purchase = self.get_trigram(int(float(purchase) / 1e6))  # 上卦(申购)
        y_redeem = self.get_trigram(int(float(redeem) / 1e6))  # 上卦(赎回)
        
        # 计算变爻
        diff = abs(float(purchase) - float(redeem))
        z_purchase = self.get_changing_line(int(diff / 1e5))
        z_redeem = self.get_changing_line(int(diff / 1e5))
        
        # 申购预测
        purchase_trend = self._get_final_trend(x, y_purchase, z_purchase)
        
        # 赎回预测
        redeem_trend = self._get_final_trend(x, y_redeem, z_redeem)
        
        return purchase_trend, redeem_trend
    
    def _get_final_trend(self, x, y, z):
        """获取最终趋势"""
        original_trend = (x['trend'], y['trend'])
        
        # 确定变爻影响上卦还是下卦
        if z <= 3:  # 变下卦
            changing_trigram = x
        else:  # 变上卦
            changing_trigram = y
        
        # 找到变化后的卦
        new_value = (changing_trigram['value'] % 8) + 1
        changed_trigram = self.get_trigram(new_value)
        
        # 确定最终趋势
        if z <= 3:  # 下卦变化
            final_trend = (changed_trigram['trend'], y['trend'])
        else:  # 上卦变化
            final_trend = (x['trend'], changed_trigram['trend'])
        
        # 趋势判断规则
        if final_trend[0] == final_trend[1]:
            return final_trend[0]  # 上下同趋势
        elif final_trend[0] == '平':
            return final_trend[1]  # 下平看上
        elif final_trend[1] == '平':
            return final_trend[0]  # 上平看下
        else:
            return '平'  # 上下趋势相反
    
    def generate_iching_features(self, purchase_series, redeem_series, date_series):
        """
        生成易卦特征
        
        Args:
            purchase_series: 申购金额序列
            redeem_series: 赎回金额序列
            date_series: 对应的日期序列
            
        Returns:
            pd.DataFrame: 包含易卦特征的DataFrame
        """
        features = []
        
        for i, (purchase_val, redeem_val, date) in enumerate(zip(purchase_series, redeem_series, date_series)):
            # x变量数：使用申购金额（下卦为本为内）
            x = int(purchase_val / 1e6)  # 缩放避免数值过大
            
            # y变量数：使用时间因子（上卦为用为外）
            y = date.day + date.month * 10 + date.year
            
            # z变量数：使用赎回金额和时间的组合（用于计算变爻）
            z = int(redeem_val / 1e5) + date.day * date.month
            
            # 获取原卦
            x_trigram = self.get_trigram(x)  # 下卦
            y_trigram = self.get_trigram(y)  # 上卦
            
            # 计算变爻
            changing_line = self.get_changing_line(z)
            
            # 计算变卦
            if changing_line <= 3:
                # 变爻影响下卦
                changed_x = self.get_changed_trigram(x_trigram, changing_line)
                changed_y = y_trigram  # 上卦不变
            else:
                # 变爻影响上卦
                changed_x = x_trigram  # 下卦不变
                changed_y = self.get_changed_trigram(y_trigram, changing_line)
            
            # 构建特征向量
            features.append([
                x_trigram['trend'] == '升',      # 原卦下卦趋势
                y_trigram['trend'] == '升',      # 原卦上卦趋势
                changed_x['trend'] == '升',      # 变卦下卦趋势
                changed_y['trend'] == '升',      # 变卦上卦趋势
                changing_line,                  # 变爻位置
                1 if x_trigram['nature'] == "阳" else 0,  # 下卦阴阳
                1 if y_trigram['nature'] == "阳" else 0,  # 上卦阴阳
                (1 if x_trigram['trend'] == '升' else -1 if x_trigram['trend'] == '降' else 0) + 
                (1 if y_trigram['trend'] == '升' else -1 if y_trigram['trend'] == '降' else 0),  # 原卦综合趋势
                (1 if changed_x['trend'] == '升' else -1 if changed_x['trend'] == '降' else 0) + 
                (1 if changed_y['trend'] == '升' else -1 if changed_y['trend'] == '降' else 0)   # 变卦综合趋势
            ])
        
        return pd.DataFrame(features, columns=[
            'original_lower_trend_up',    # 原卦下卦趋势
            'original_upper_trend_up',    # 原卦上卦趋势
            'changed_lower_trend_up',     # 变卦下卦趋势
            'changed_upper_trend_up',     # 变卦上卦趋势
            'changing_line',              # 变爻位置
            'lower_yang',                 # 下卦阴阳
            'upper_yang',                 # 上卦阴阳
            'original_combined_trend',     # 原卦综合趋势
            'changed_combined_trend'      # 变卦综合趋势
        ])


class MLPredictor:
    """机器学习预测器"""
    
    def __init__(self, use_gpu=True):
        """
        初始化机器学习预测器
        
        Args:
            use_gpu (bool): 是否使用GPU加速
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
        self.use_gpu = use_gpu and torch.cuda.is_available()
        
        # XGBoost参数
        self.xgb_params = {
            'n_estimators': 200,
            'learning_rate': 0.05,
            'max_depth': 5,
            'random_state': 42,
            'n_jobs': -1
        }
        
        if self.use_gpu:
            self.xgb_params['tree_method'] = 'gpu_hist'
            print("XGBoost将使用GPU加速")
        else:
            print("XGBoost将使用CPU")
    
    def train_models(self, X, y_purchase, y_redeem):
        """
        训练机器学习模型
        
        Args:
            X (pd.DataFrame): 特征矩阵
            y_purchase (pd.Series): 申购目标
            y_redeem (pd.Series): 赎回目标
        """
        print("正在训练机器学习模型...")
        
        # 申购模型
        self.purchase_model = XGBRegressor(**self.xgb_params)
        self.purchase_model.fit(X, y_purchase)
        
        # 赎回模型
        self.redeem_model = XGBRegressor(**self.xgb_params)
        self.redeem_model.fit(X, y_redeem)
        
        print("机器学习模型训练完成")
    
    def predict(self, X):
        """
        进行预测
        
        Args:
            X (pd.DataFrame): 特征矩阵
            
        Returns:
            tuple: (申购预测, 赎回预测)
        """
        purchase_pred = self.purchase_model.predict(X)
        redeem_pred = self.redeem_model.predict(X)
        return purchase_pred, redeem_pred


class HybridPredictor:
    """混合预测器（易经+机器学习）"""
    
    def __init__(self, use_gpu=True, adjustment_factor=0.05):
        """
        初始化混合预测器
        
        Args:
            use_gpu (bool): 是否使用GPU加速
            adjustment_factor (float): 易经调整因子
        """
        self.iching_oracle = IChingOracle()
        self.ml_predictor = MLPredictor(use_gpu=use_gpu)
        self.adjustment_factor = adjustment_factor
        self.is_trained = False
    
    def train(self, X, y_purchase, y_redeem):
        """
        训练混合模型
        
        Args:
            X (pd.DataFrame): 特征矩阵
            y_purchase (pd.Series): 申购目标
            y_redeem (pd.Series): 赎回目标
        """
        print("正在训练混合预测模型...")
        
        # 训练机器学习模型
        self.ml_predictor.train_models(X, y_purchase, y_redeem)
        
        self.is_trained = True
        print("混合预测模型训练完成")
    
    def predict(self, X, dates=None):
        """
        进行混合预测
        
        Args:
            X (pd.DataFrame): 特征矩阵
            dates (pd.Series): 日期序列，如果为None则使用默认日期
            
        Returns:
            pd.DataFrame: 预测结果
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用train方法")
        
        print("正在进行混合预测...")
        
        # 机器学习预测
        ml_purchase, ml_redeem = self.ml_predictor.predict(X)
        
        # 易经调整
        if dates is None:
            dates = pd.date_range('2014-09-01', periods=len(X), freq='D')
        
        predictions = []
        for i, (purchase_pred, redeem_pred, date) in enumerate(zip(ml_purchase, ml_redeem, dates)):
            # 易经预测趋势
            date_str = date.strftime('%Y%m%d')
            iching_purchase_trend, iching_redeem_trend = self.iching_oracle.predict_trend(
                date_str, purchase_pred, redeem_pred
            )
            
            # 应用易经调整
            if iching_purchase_trend == '升':
                final_purchase = purchase_pred * (1 + self.adjustment_factor)
            elif iching_purchase_trend == '降':
                final_purchase = purchase_pred * (1 - self.adjustment_factor)
            else:
                final_purchase = purchase_pred
            
            if iching_redeem_trend == '升':
                final_redeem = redeem_pred * (1 + self.adjustment_factor)
            elif iching_redeem_trend == '降':
                final_redeem = redeem_pred * (1 - self.adjustment_factor)
            else:
                final_redeem = redeem_pred
            
            predictions.append({
                'date': date,
                'ml_purchase': purchase_pred,
                'ml_redeem': redeem_pred,
                'iching_purchase_trend': iching_purchase_trend,
                'iching_redeem_trend': iching_redeem_trend,
                'final_purchase': final_purchase,
                'final_redeem': final_redeem
            })
        
        return pd.DataFrame(predictions)
    
    def evaluate(self, X, y_purchase, y_redeem, dates=None):
        """
        评估模型性能
        
        Args:
            X (pd.DataFrame): 特征矩阵
            y_purchase (pd.Series): 申购真实值
            y_redeem (pd.Series): 赎回真实值
            dates (pd.Series): 日期序列
            
        Returns:
            dict: 评估指标
        """
        predictions = self.predict(X, dates)
        
        # 计算评估指标
        purchase_mae = mean_absolute_error(y_purchase, predictions['final_purchase'])
        redeem_mae = mean_absolute_error(y_redeem, predictions['final_redeem'])
        
        purchase_mape = np.mean(np.abs(y_purchase - predictions['final_purchase']) / y_purchase) * 100
        redeem_mape = np.mean(np.abs(y_redeem - predictions['final_redeem']) / y_redeem) * 100
        
        return {
            'purchase_mae': purchase_mae,
            'redeem_mae': redeem_mae,
            'purchase_mape': purchase_mape,
            'redeem_mape': redeem_mape
        }


if __name__ == "__main__":
    # 测试模型模块
    print("测试模型模块...")
    
    # 创建示例数据
    np.random.seed(42)
    n_samples = 100
    
    # 创建特征数据
    X = pd.DataFrame({
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.randn(n_samples),
        'feature3': np.random.randn(n_samples)
    })
    
    # 创建目标数据
    y_purchase = np.random.normal(300000, 50000, n_samples)
    y_redeem = np.random.normal(280000, 45000, n_samples)
    
    # 测试易经预测器
    print("\n测试易经预测器...")
    iching = IChingOracle()
    trend1, trend2 = iching.predict_trend('20140901', 300000, 280000)
    print(f"易经预测结果: 申购趋势={trend1}, 赎回趋势={trend2}")
    
    # 测试机器学习预测器
    print("\n测试机器学习预测器...")
    ml_predictor = MLPredictor(use_gpu=False)
    ml_predictor.train_models(X, y_purchase, y_redeem)
    pred_purchase, pred_redeem = ml_predictor.predict(X[:5])
    print(f"机器学习预测结果: 申购={pred_purchase[:3]}, 赎回={pred_redeem[:3]}")
    
    # 测试混合预测器
    print("\n测试混合预测器...")
    hybrid = HybridPredictor(use_gpu=False)
    hybrid.train(X, y_purchase, y_redeem)
    
    dates = pd.date_range('2014-09-01', periods=5, freq='D')
    predictions = hybrid.predict(X[:5], dates)
    print("混合预测结果:")
    print(predictions[['date', 'final_purchase', 'final_redeem']].head())
    
    print("模型模块测试完成！")
