"""
易卦增强预测模型
基于易卦预测模型说明文档的完整实现
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class IChingEnhancedOracle:
    """易卦增强预测器"""
    
    def __init__(self):
        """初始化易卦预测器"""
        # 八卦映射规则
        self.trigram_mapping = {
            0: {'name': '坤卦', 'trend': 0, 'description': '平和，全虚，老母'},
            1: {'name': '乾卦', 'trend': 0, 'description': '平和，全实，老父'},
            2: {'name': '兑卦', 'trend': -1, 'description': '下降，上虚，小女'},
            3: {'name': '离卦', 'trend': 1, 'description': '上升，中虚，中女'},
            4: {'name': '震卦', 'trend': 1, 'description': '上升，下实，长子'},
            5: {'name': '巽卦', 'trend': -1, 'description': '下降，下虚，大女'},
            6: {'name': '坎卦', 'trend': -1, 'description': '下降，中实，中男'},
            7: {'name': '艮卦', 'trend': 1, 'description': '上升，上实，小儿'}
        }
        
        # 变爻位置描述
        self.changing_line_desc = {
            1: '下卦最下爻',
            2: '下卦中爻', 
            3: '下卦最上爻',
            4: '上卦最下爻',
            5: '上卦中爻',
            6: '上卦最上爻'
        }
    
    def get_trigram(self, value: int) -> Dict:
        """获取卦象信息"""
        remainder = value % 8
        return self.trigram_mapping[remainder]
    
    def get_changing_line(self, value: int) -> int:
        """获取变爻位置"""
        remainder = value % 6
        return 6 if remainder == 0 else remainder
    
    def calculate_iching_features(self, date_str: str, purchase: float, redeem: float) -> Dict:
        """
        计算易卦特征
        基于易卦预测模型说明文档的算法
        """
        # 解析日期
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        
        # 计算变量数
        # x变量数（下卦）：申购金额/1e6，代表内在资金需求
        x_var = int(purchase / 1e6)
        
        # y变量数（上卦）：日期+月份*10+年份，代表外在市场环境
        y_var = day + month * 10 + year
        
        # z变量数（变爻）：赎回金额/1e5+日*月，代表变化动力
        z_var = int(redeem / 1e5) + day * month
        
        # 获取原卦信息
        lower_trigram = self.get_trigram(x_var)  # 下卦
        upper_trigram = self.get_trigram(y_var)  # 上卦
        
        # 计算变爻位置
        changing_line = self.get_changing_line(z_var)
        
        # 计算变卦
        # 根据变爻位置计算变卦
        if changing_line <= 3:  # 影响下卦
            # 下卦变爻
            if changing_line == 1:
                changed_lower = self.get_trigram(x_var + 1)
            elif changing_line == 2:
                changed_lower = self.get_trigram(x_var + 2)
            else:  # changing_line == 3
                changed_lower = self.get_trigram(x_var + 4)
            changed_upper = upper_trigram
        else:  # 影响上卦
            # 上卦变爻
            if changing_line == 4:
                changed_upper = self.get_trigram(y_var + 1)
            elif changing_line == 5:
                changed_upper = self.get_trigram(y_var + 2)
            else:  # changing_line == 6
                changed_upper = self.get_trigram(y_var + 4)
            changed_lower = lower_trigram
        
        # 计算阴阳属性
        lower_yang = 1 if x_var % 2 == 1 else 0
        upper_yang = 1 if y_var % 2 == 1 else 0
        
        # 计算综合趋势
        original_combined_trend = lower_trigram['trend'] + upper_trigram['trend']
        changed_combined_trend = changed_lower['trend'] + changed_upper['trend']
        
        # 生成9个易卦特征
        features = {
            'original_lower_trend': lower_trigram['trend'],
            'original_upper_trend': upper_trigram['trend'],
            'changed_lower_trend': changed_lower['trend'],
            'changed_upper_trend': changed_upper['trend'],
            'changing_line': changing_line,
            'lower_yang': lower_yang,
            'upper_yang': upper_yang,
            'original_combined_trend': original_combined_trend,
            'changed_combined_trend': changed_combined_trend
        }
        
        # 生成详细解释
        interpretation = {
            'date': date_str,
            'purchase': purchase,
            'redeem': redeem,
            'original_lower': lower_trigram,
            'original_upper': upper_trigram,
            'changed_lower': changed_lower,
            'changed_upper': changed_upper,
            'changing_line': changing_line,
            'changing_line_desc': self.changing_line_desc[changing_line],
            'features': features
        }
        
        return interpretation
    
    def predict_trend(self, date_str: str, purchase: float, redeem: float) -> Tuple[str, str]:
        """
        预测趋势
        返回 (申购趋势, 赎回趋势)
        """
        interpretation = self.calculate_iching_features(date_str, purchase, redeem)
        
        # 基于易卦特征判断趋势
        original_trend = interpretation['features']['original_combined_trend']
        changed_trend = interpretation['features']['changed_combined_trend']
        
        # 申购趋势判断
        if original_trend > 0:
            purchase_trend = '上升'
        elif original_trend < 0:
            purchase_trend = '下降'
        else:
            purchase_trend = '平稳'
        
        # 赎回趋势判断
        if changed_trend > 0:
            redeem_trend = '上升'
        elif changed_trend < 0:
            redeem_trend = '下降'
        else:
            redeem_trend = '平稳'
        
        return purchase_trend, redeem_trend
    
    def get_iching_interpretation(self, date_str: str, purchase: float, redeem: float) -> str:
        """
        获取易卦解释
        """
        interpretation = self.calculate_iching_features(date_str, purchase, redeem)
        
        result = f"""
易卦分析 - {date_str}
===============================================

基本信息:
  申购金额: {purchase:,.0f}
  赎回金额: {redeem:,.0f}

原卦分析:
  下卦: {interpretation['original_lower']['name']} ({interpretation['original_lower']['description']})
  上卦: {interpretation['original_upper']['name']} ({interpretation['original_upper']['description']})
  综合趋势: {interpretation['features']['original_combined_trend']} ({'上升' if interpretation['features']['original_combined_trend'] > 0 else '下降' if interpretation['features']['original_combined_trend'] < 0 else '平稳'})

变卦分析:
  下卦: {interpretation['changed_lower']['name']} ({interpretation['changed_lower']['description']})
  上卦: {interpretation['changed_upper']['name']} ({interpretation['changed_upper']['description']})
  综合趋势: {interpretation['features']['changed_combined_trend']} ({'上升' if interpretation['features']['changed_combined_trend'] > 0 else '下降' if interpretation['features']['changed_combined_trend'] < 0 else '平稳'})

变爻分析:
  变爻位置: {interpretation['changing_line']} ({interpretation['changing_line_desc']})
  阴阳属性: 下卦{'阳' if interpretation['features']['lower_yang'] else '阴'}, 上卦{'阳' if interpretation['features']['upper_yang'] else '阴'}

投资建议:
"""
        
        # 根据卦象给出建议
        if interpretation['features']['original_combined_trend'] > 0:
            result += "  原卦显示上升趋势，适合积极策略\n"
        elif interpretation['features']['original_combined_trend'] < 0:
            result += "  原卦显示下降趋势，建议保守策略\n"
        else:
            result += "  原卦显示平稳趋势，适合稳健策略\n"
        
        if interpretation['features']['changed_combined_trend'] != interpretation['features']['original_combined_trend']:
            result += "  变卦显示趋势发生变化，需要关注市场动向\n"
        
        if interpretation['changing_line'] in [1, 6]:
            result += "  关键变爻位置，注意趋势转折点\n"
        
        return result

class IChingEnhancedPredictor:
    """易卦增强预测器"""
    
    def __init__(self):
        """初始化预测器"""
        self.oracle = IChingEnhancedOracle()
        self.feature_columns = [
            'original_lower_trend', 'original_upper_trend',
            'changed_lower_trend', 'changed_upper_trend',
            'changing_line', 'lower_yang', 'upper_yang',
            'original_combined_trend', 'changed_combined_trend'
        ]
    
    def add_iching_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        为数据框添加易卦特征
        """
        df = df.copy()
        
        # 确保日期列是字符串格式
        if 'report_date' in df.columns:
            df['date_str'] = df['report_date'].dt.strftime('%Y%m%d')
        else:
            df['date_str'] = df.index.strftime('%Y%m%d')
        
        # 计算易卦特征
        iching_features = []
        for idx, row in df.iterrows():
            features = self.oracle.calculate_iching_features(
                row['date_str'],
                row.get('total_purchase_amt', 0),
                row.get('total_redeem_amt', 0)
            )['features']
            iching_features.append(features)
        
        # 添加易卦特征到数据框
        iching_df = pd.DataFrame(iching_features)
        for col in self.feature_columns:
            df[col] = iching_df[col]
        
        return df
    
    def predict_with_iching(self, df: pd.DataFrame, target_cols: List[str] = None) -> Dict:
        """
        使用易卦特征进行预测
        """
        if target_cols is None:
            target_cols = ['total_purchase_amt', 'total_redeem_amt']
        
        # 添加易卦特征
        df_with_features = self.add_iching_features(df)
        
        # 选择特征列
        feature_cols = self.feature_columns + ['weekday', 'day_of_month']
        if 'total_purchase_amt' in df_with_features.columns:
            feature_cols.append('total_purchase_amt')
        if 'total_redeem_amt' in df_with_features.columns:
            feature_cols.append('total_redeem_amt')
        
        # 过滤存在的列
        available_cols = [col for col in feature_cols if col in df_with_features.columns]
        X = df_with_features[available_cols]
        
        # 生成预测结果
        predictions = {}
        for target in target_cols:
            if target in df_with_features.columns:
                # 使用易卦特征进行简单预测
                # 这里可以使用更复杂的模型，如随机森林或XGBoost
                predictions[target] = df_with_features[target].mean()
            else:
                predictions[target] = 0
        
        return {
            'predictions': predictions,
            'features': df_with_features[available_cols],
            'iching_features': df_with_features[self.feature_columns]
        }
    
    def get_enhanced_interpretation(self, date_str: str, purchase: float, redeem: float) -> str:
        """
        获取增强的易卦解释
        """
        return self.oracle.get_iching_interpretation(date_str, purchase, redeem)

def main():
    """主函数 - 演示易卦增强预测"""
    print("易卦增强预测模型演示")
    print("=" * 60)
    
    # 初始化预测器
    predictor = IChingEnhancedPredictor()
    
    # 测试案例
    test_cases = [
        ("20241201", 1000000, 800000),
        ("20241202", 1200000, 900000),
        ("20241203", 800000, 1100000)
    ]
    
    for date, purchase, redeem in test_cases:
        print(f"\n测试案例: {date}")
        print(f"申购: {purchase:,}, 赎回: {redeem:,}")
        
        # 获取易卦解释
        interpretation = predictor.get_enhanced_interpretation(date, purchase, redeem)
        print(interpretation)
        print("-" * 60)

if __name__ == "__main__":
    main()

