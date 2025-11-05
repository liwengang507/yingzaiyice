"""
数据加载和预处理模块
==================

负责数据加载、清洗、特征工程等数据预处理工作
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from holidays import country_holidays
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """数据加载器"""
    
    def __init__(self, data_dir="Purchase Redemption Data"):
        """
        初始化数据加载器
        
        Args:
            data_dir (str): 数据文件目录
        """
        self.data_dir = data_dir
        self.cn_holidays = country_holidays('CN')
    
    def load_user_balance(self, filepath=None):
        """
        加载用户资金流水数据
        
        Args:
            filepath (str): 文件路径，如果为None则使用默认路径
            
        Returns:
            pd.DataFrame: 用户资金流水数据
        """
        if filepath is None:
            filepath = f"{self.data_dir}/user_balance_table.csv"
        
        print("正在加载用户资金流水数据...")
        df = pd.read_csv(filepath)
        df['report_date'] = pd.to_datetime(df['report_date'], format='%Y%m%d')
        print(f"用户资金流水数据加载完成，形状: {df.shape}")
        return df
    
    def load_user_profile(self, filepath=None):
        """
        加载用户信息数据
        
        Args:
            filepath (str): 文件路径，如果为None则使用默认路径
            
        Returns:
            pd.DataFrame: 用户信息数据
        """
        if filepath is None:
            filepath = f"{self.data_dir}/user_profile_table.csv"
        
        print("正在加载用户信息数据...")
        df = pd.read_csv(filepath)
        print(f"用户信息数据加载完成，形状: {df.shape}")
        return df
    
    def load_mfd_interest(self, filepath=None):
        """
        加载货币基金收益率数据
        
        Args:
            filepath (str): 文件路径，如果为None则使用默认路径
            
        Returns:
            pd.DataFrame: 货币基金收益率数据
        """
        if filepath is None:
            filepath = f"{self.data_dir}/mfd_day_share_interest.csv"
        
        print("正在加载货币基金收益率数据...")
        df = pd.read_csv(filepath)
        df['mfd_date'] = pd.to_datetime(df['mfd_date'], format='%Y%m%d')
        print(f"货币基金收益率数据加载完成，形状: {df.shape}")
        return df
    
    def load_shibor(self, filepath=None):
        """
        加载Shibor利率数据
        
        Args:
            filepath (str): 文件路径，如果为None则使用默认路径
            
        Returns:
            pd.DataFrame: Shibor利率数据
        """
        if filepath is None:
            filepath = f"{self.data_dir}/mfd_bank_shibor.csv"
        
        print("正在加载Shibor利率数据...")
        df = pd.read_csv(filepath)
        df['mfd_date'] = pd.to_datetime(df['mfd_date'], format='%Y%m%d')
        print(f"Shibor利率数据加载完成，形状: {df.shape}")
        return df
    
    def load_all_data(self):
        """
        加载所有数据
        
        Returns:
            dict: 包含所有数据表的字典
        """
        data = {}
        data['user_balance'] = self.load_user_balance()
        data['user_profile'] = self.load_user_profile()
        data['mfd_interest'] = self.load_mfd_interest()
        data['shibor'] = self.load_shibor()
        return data


class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self):
        """初始化数据预处理器"""
        self.cn_holidays = country_holidays('CN')
    
    def aggregate_daily_data(self, user_balance_df):
        """
        按日期聚合用户资金流水数据
        
        Args:
            user_balance_df (pd.DataFrame): 用户资金流水数据
            
        Returns:
            pd.DataFrame: 按日期聚合的数据
        """
        print("正在按日期聚合资金流水数据...")
        daily_data = user_balance_df.groupby('report_date').agg({
            'total_purchase_amt': 'sum',
            'total_redeem_amt': 'sum'
        }).reset_index()
        
        print(f"聚合后数据形状: {daily_data.shape}")
        print(f"日期范围: {daily_data['report_date'].min()} 至 {daily_data['report_date'].max()}")
        return daily_data
    
    def add_time_features(self, df, date_col='report_date'):
        """
        添加时间特征
        
        Args:
            df (pd.DataFrame): 数据框
            date_col (str): 日期列名
            
        Returns:
            pd.DataFrame: 添加时间特征后的数据框
        """
        print("正在添加时间特征...")
        df = df.copy()
        
        # 基础时间特征
        df['day_of_week'] = df[date_col].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['month'] = df[date_col].dt.month
        df['day_of_month'] = df[date_col].dt.day
        df['quarter'] = df[date_col].dt.quarter
        df['year'] = df[date_col].dt.year
        
        # 节假日特征
        is_chinese_holiday = lambda date: date in self.cn_holidays
        df['is_holiday'] = df[date_col].apply(is_chinese_holiday).astype(int)
        df['is_workday'] = ~(df['is_holiday'].astype(bool) | df['is_weekend'].astype(bool)).astype(int)
        
        print("时间特征添加完成")
        return df
    
    def add_lag_features(self, df, target_cols, lags=[1, 2, 3, 7, 14, 30]):
        """
        添加滞后特征
        
        Args:
            df (pd.DataFrame): 数据框
            target_cols (list): 目标列名列表
            lags (list): 滞后天数列表
            
        Returns:
            pd.DataFrame: 添加滞后特征后的数据框
        """
        print("正在添加滞后特征...")
        df = df.copy()
        
        for col in target_cols:
            for lag in lags:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        print("滞后特征添加完成")
        return df
    
    def add_rolling_features(self, df, target_cols, windows=[7, 14, 30]):
        """
        添加滚动统计特征
        
        Args:
            df (pd.DataFrame): 数据框
            target_cols (list): 目标列名列表
            windows (list): 滚动窗口大小列表
            
        Returns:
            pd.DataFrame: 添加滚动特征后的数据框
        """
        print("正在添加滚动统计特征...")
        df = df.copy()
        
        for col in target_cols:
            for window in windows:
                df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
                df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
                df[f'{col}_rolling_max_{window}'] = df[col].rolling(window=window).max()
                df[f'{col}_rolling_min_{window}'] = df[col].rolling(window=window).min()
        
        print("滚动统计特征添加完成")
        return df
    
    def merge_external_data(self, daily_data, mfd_interest_df, shibor_df):
        """
        合并外部数据（收益率、利率等）
        
        Args:
            daily_data (pd.DataFrame): 日度数据
            mfd_interest_df (pd.DataFrame): 货币基金收益率数据
            shibor_df (pd.DataFrame): Shibor利率数据
            
        Returns:
            pd.DataFrame: 合并后的数据
        """
        print("正在合并外部数据...")
        
        # 合并货币基金收益率数据
        daily_data = pd.merge(daily_data, mfd_interest_df, 
                            left_on='report_date', right_on='mfd_date', how='left')
        
        # 合并Shibor利率数据
        daily_data = pd.merge(daily_data, shibor_df, 
                            left_on='report_date', right_on='mfd_date', how='left')
        
        # 删除重复的日期列
        if 'mfd_date_x' in daily_data.columns:
            daily_data.drop(['mfd_date_x'], axis=1, inplace=True)
        if 'mfd_date_y' in daily_data.columns:
            daily_data.drop(['mfd_date_y'], axis=1, inplace=True)
        
        # 填充缺失值
        shibor_cols = ['Interest_O_N', 'Interest_1_W', 'Interest_2_W', 
                      'Interest_1_M', 'Interest_3_M', 'Interest_6_M', 
                      'Interest_9_M', 'Interest_1_Y']
        
        for col in shibor_cols:
            if col in daily_data.columns:
                daily_data[col] = daily_data[col].fillna(method='ffill')
                daily_data[col] = daily_data[col].fillna(method='bfill')
                if daily_data[col].isnull().any():
                    daily_data[col].fillna(daily_data[col].mean(), inplace=True)
        
        print(f"外部数据合并完成，最终数据形状: {daily_data.shape}")
        return daily_data
    
    def clean_data(self, df, drop_na=True):
        """
        数据清洗
        
        Args:
            df (pd.DataFrame): 数据框
            drop_na (bool): 是否删除缺失值
            
        Returns:
            pd.DataFrame: 清洗后的数据
        """
        print("正在清洗数据...")
        df = df.copy()
        
        # 删除缺失值
        if drop_na:
            initial_shape = df.shape
            df = df.dropna().reset_index(drop=True)
            print(f"删除缺失值: {initial_shape} -> {df.shape}")
        
        # 确保数值列的数据类型
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print("数据清洗完成")
        return df
    
    def get_feature_columns(self, df, target_cols=['total_purchase_amt', 'total_redeem_amt']):
        """
        获取特征列名
        
        Args:
            df (pd.DataFrame): 数据框
            target_cols (list): 目标列名列表
            
        Returns:
            list: 特征列名列表
        """
        exclude_cols = ['report_date'] + target_cols
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        return feature_cols


def create_sample_data():
    """
    创建示例数据用于测试
    
    Returns:
        dict: 包含示例数据的字典
    """
    print("正在创建示例数据...")
    
    # 创建日期范围
    dates = pd.date_range('2014-03-01', '2014-08-31', freq='D')
    
    # 创建示例用户资金流水数据
    np.random.seed(42)
    n_users = 1000
    n_days = len(dates)
    
    user_balance_data = []
    for user_id in range(1, n_users + 1):
        for i, date in enumerate(dates):
            # 模拟申购和赎回金额
            base_purchase = np.random.normal(300000, 50000)
            base_redeem = np.random.normal(280000, 45000)
            
            # 添加周期性变化
            weekday_factor = 0.8 if date.weekday() >= 5 else 1.0  # 周末减少
            month_factor = 1.0 + 0.1 * np.sin(2 * np.pi * i / 30)  # 月度周期
            
            purchase_amt = max(0, base_purchase * weekday_factor * month_factor)
            redeem_amt = max(0, base_redeem * weekday_factor * month_factor)
            
            user_balance_data.append({
                'user_id': user_id,
                'report_date': date.strftime('%Y%m%d'),
                'total_purchase_amt': int(purchase_amt),
                'total_redeem_amt': int(redeem_amt)
            })
    
    user_balance_df = pd.DataFrame(user_balance_data)
    user_balance_df['report_date'] = pd.to_datetime(user_balance_df['report_date'], format='%Y%m%d')
    
    # 创建示例货币基金收益率数据
    mfd_interest_data = []
    for date in dates:
        mfd_interest_data.append({
            'mfd_date': date.strftime('%Y%m%d'),
            'mfd_daily_yield': np.random.normal(0.0003, 0.0001),
            'mfd_7daily_yield': np.random.normal(0.002, 0.0005)
        })
    
    mfd_interest_df = pd.DataFrame(mfd_interest_data)
    mfd_interest_df['mfd_date'] = pd.to_datetime(mfd_interest_df['mfd_date'], format='%Y%m%d')
    
    # 创建示例Shibor利率数据
    shibor_data = []
    for date in dates:
        shibor_data.append({
            'mfd_date': date.strftime('%Y%m%d'),
            'Interest_O_N': np.random.normal(0.03, 0.005),
            'Interest_1_W': np.random.normal(0.031, 0.005),
            'Interest_2_W': np.random.normal(0.032, 0.005),
            'Interest_1_M': np.random.normal(0.033, 0.005),
            'Interest_3_M': np.random.normal(0.035, 0.005),
            'Interest_6_M': np.random.normal(0.037, 0.005),
            'Interest_9_M': np.random.normal(0.039, 0.005),
            'Interest_1_Y': np.random.normal(0.041, 0.005)
        })
    
    shibor_df = pd.DataFrame(shibor_data)
    shibor_df['mfd_date'] = pd.to_datetime(shibor_df['mfd_date'], format='%Y%m%d')
    
    print("示例数据创建完成")
    return {
        'user_balance': user_balance_df,
        'mfd_interest': mfd_interest_df,
        'shibor': shibor_df
    }


if __name__ == "__main__":
    # 测试数据加载和预处理
    print("测试数据模块...")
    
    # 创建示例数据
    sample_data = create_sample_data()
    
    # 测试数据预处理器
    preprocessor = DataPreprocessor()
    
    # 聚合日度数据
    daily_data = preprocessor.aggregate_daily_data(sample_data['user_balance'])
    
    # 添加时间特征
    daily_data = preprocessor.add_time_features(daily_data)
    
    # 添加滞后特征
    daily_data = preprocessor.add_lag_features(daily_data, ['total_purchase_amt', 'total_redeem_amt'])
    
    # 添加滚动特征
    daily_data = preprocessor.add_rolling_features(daily_data, ['total_purchase_amt', 'total_redeem_amt'])
    
    # 合并外部数据
    daily_data = preprocessor.merge_external_data(daily_data, sample_data['mfd_interest'], sample_data['shibor'])
    
    # 清洗数据
    daily_data = preprocessor.clean_data(daily_data)
    
    print(f"最终数据形状: {daily_data.shape}")
    print("数据模块测试完成！")
