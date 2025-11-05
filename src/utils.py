"""
工具函数模块
============

提供各种工具函数和辅助功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def setup_plotting():
    """设置绘图环境"""
    plt.style.use('ggplot')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10


def save_plot(fig, filepath, dpi=300, bbox_inches='tight'):
    """
    保存图片
    
    Args:
        fig: matplotlib图形对象
        filepath (str): 保存路径
        dpi (int): 图片分辨率
        bbox_inches (str): 边界设置
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fig.savefig(filepath, dpi=dpi, bbox_inches=bbox_inches)
        print(f"图片已保存到: {filepath}")
    except Exception as e:
        print(f"保存图片失败: {e}")


def plot_time_series(data, x_col, y_cols, title="时间序列图", save_path=None):
    """
    绘制时间序列图
    
    Args:
        data (pd.DataFrame): 数据
        x_col (str): x轴列名
        y_cols (list): y轴列名列表
        title (str): 图表标题
        save_path (str): 保存路径
    """
    fig, ax = plt.subplots(figsize=(15, 6))
    
    for col in y_cols:
        ax.plot(data[x_col], data[col], label=col, alpha=0.7)
    
    ax.set_title(title)
    ax.set_xlabel('日期')
    ax.set_ylabel('数值')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        save_plot(fig, save_path)
    
    plt.show()


def plot_correlation_matrix(data, columns, title="相关性矩阵", save_path=None):
    """
    绘制相关性矩阵热力图
    
    Args:
        data (pd.DataFrame): 数据
        columns (list): 要分析的列名
        title (str): 图表标题
        save_path (str): 保存路径
    """
    corr_matrix = data[columns].corr()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
    ax.set_title(title)
    plt.tight_layout()
    
    if save_path:
        save_plot(fig, save_path)
    
    plt.show()


def plot_prediction_comparison(historical_data, predictions, title="预测对比图", save_path=None):
    """
    绘制预测对比图
    
    Args:
        historical_data (pd.DataFrame): 历史数据
        predictions (pd.DataFrame): 预测数据
        title (str): 图表标题
        save_path (str): 保存路径
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # 申购金额对比
    ax1.plot(historical_data['report_date'], historical_data['total_purchase_amt'],
             'o-', label='历史申购', color='blue', alpha=0.7, markersize=3)
    ax1.plot(predictions['date'], predictions['final_purchase'],
             '^-', label='预测申购', color='red', markersize=4)
    
    ax1.set_title('申购金额：历史 vs 预测')
    ax1.set_ylabel('申购金额')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 赎回金额对比
    ax2.plot(historical_data['report_date'], historical_data['total_redeem_amt'],
             'o-', label='历史赎回', color='orange', alpha=0.7, markersize=3)
    ax2.plot(predictions['date'], predictions['final_redeem'],
             '^-', label='预测赎回', color='red', markersize=4)
    
    ax2.set_title('赎回金额：历史 vs 预测')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('赎回金额')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        save_plot(fig, save_path)
    
    plt.show()


def calculate_metrics(y_true, y_pred):
    """
    计算评估指标
    
    Args:
        y_true (array): 真实值
        y_pred (array): 预测值
        
    Returns:
        dict: 评估指标字典
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs(y_true - y_pred) / y_true) * 100
    r2 = r2_score(y_true, y_pred)
    
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'MAPE': mape,
        'R²': r2
    }


def print_metrics(metrics, title="模型评估指标"):
    """
    打印评估指标
    
    Args:
        metrics (dict): 评估指标字典
        title (str): 标题
    """
    print(f"\n{title}")
    print("-" * 30)
    for metric, value in metrics.items():
        if metric == 'R²':
            print(f"{metric}: {value:.4f}")
        else:
            print(f"{metric}: {value:,.2f}")


def save_predictions(predictions, filepath, format='csv'):
    """
    保存预测结果
    
    Args:
        predictions (pd.DataFrame): 预测结果
        filepath (str): 保存路径
        format (str): 保存格式 ('csv' 或 'excel')
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if format == 'csv':
            predictions.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format == 'excel':
            predictions.to_excel(filepath, index=False)
        
        print(f"预测结果已保存到: {filepath}")
    except Exception as e:
        print(f"保存预测结果失败: {e}")


def create_submission_format(predictions, date_col='date', purchase_col='final_purchase', redeem_col='final_redeem'):
    """
    创建提交格式的预测结果
    
    Args:
        predictions (pd.DataFrame): 预测结果
        date_col (str): 日期列名
        purchase_col (str): 申购列名
        redeem_col (str): 赎回列名
        
    Returns:
        pd.DataFrame: 提交格式的预测结果
    """
    submission = pd.DataFrame({
        'report_date': predictions[date_col].dt.strftime('%Y%m%d'),
        'purchase': predictions[purchase_col].round().astype(int).clip(lower=0),
        'redeem': predictions[redeem_col].round().astype(int).clip(lower=0)
    })
    
    # 确保申购 > 赎回
    mask = submission['purchase'] <= submission['redeem']
    submission.loc[mask, 'purchase'] = submission.loc[mask, 'redeem'] * 1.05
    
    return submission


def validate_predictions(predictions):
    """
    验证预测结果的合理性
    
    Args:
        predictions (pd.DataFrame): 预测结果
        
    Returns:
        dict: 验证结果
    """
    validation_results = {
        'is_valid': True,
        'issues': []
    }
    
    # 检查负值
    if (predictions['final_purchase'] < 0).any():
        validation_results['is_valid'] = False
        validation_results['issues'].append("存在负的申购金额")
    
    if (predictions['final_redeem'] < 0).any():
        validation_results['is_valid'] = False
        validation_results['issues'].append("存在负的赎回金额")
    
    # 检查申购是否大于赎回
    if (predictions['final_purchase'] <= predictions['final_redeem']).any():
        validation_results['is_valid'] = False
        validation_results['issues'].append("存在申购金额小于等于赎回金额的情况")
    
    # 检查数值范围
    purchase_range = (predictions['final_purchase'].min(), predictions['final_purchase'].max())
    redeem_range = (predictions['final_redeem'].min(), predictions['final_redeem'].max())
    
    if purchase_range[0] < 100000 or purchase_range[1] > 1000000000:
        validation_results['issues'].append(f"申购金额范围异常: {purchase_range}")
    
    if redeem_range[0] < 100000 or redeem_range[1] > 1000000000:
        validation_results['issues'].append(f"赎回金额范围异常: {redeem_range}")
    
    return validation_results


def print_validation_results(validation_results):
    """
    打印验证结果
    
    Args:
        validation_results (dict): 验证结果
    """
    print("\n预测结果验证:")
    print("-" * 30)
    
    if validation_results['is_valid']:
        print("预测结果验证通过")
    else:
        print("预测结果验证失败")
        for issue in validation_results['issues']:
            print(f"  - {issue}")


def format_number(num):
    """
    格式化数字显示
    
    Args:
        num (float): 数字
        
    Returns:
        str: 格式化后的字符串
    """
    if num >= 1e8:
        return f"{num/1e8:.2f}亿"
    elif num >= 1e4:
        return f"{num/1e4:.2f}万"
    else:
        return f"{num:.2f}"


def get_date_range_info(dates):
    """
    获取日期范围信息
    
    Args:
        dates (pd.Series or pd.DatetimeIndex): 日期序列
        
    Returns:
        dict: 日期范围信息
    """
    # 如果是DatetimeIndex，转换为Series
    if hasattr(dates, 'dt'):
        date_series = dates
    else:
        date_series = pd.Series(dates)
    
    return {
        'start_date': date_series.min(),
        'end_date': date_series.max(),
        'total_days': len(date_series),
        'weekdays': len(date_series[date_series.dt.weekday < 5]),
        'weekends': len(date_series[date_series.dt.weekday >= 5])
    }


def print_data_summary(data, title="数据摘要"):
    """
    打印数据摘要
    
    Args:
        data (pd.DataFrame): 数据
        title (str): 标题
    """
    print(f"\n{title}")
    print("=" * 50)
    print(f"数据形状: {data.shape}")
    print(f"列名: {list(data.columns)}")
    
    if 'report_date' in data.columns:
        date_info = get_date_range_info(data['report_date'])
        print(f"日期范围: {date_info['start_date']} 至 {date_info['end_date']}")
        print(f"总天数: {date_info['total_days']}")
        print(f"工作日: {date_info['weekdays']}, 周末: {date_info['weekends']}")
    
    print("\n数值列统计:")
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        print(f"{col}: 均值={format_number(data[col].mean())}, "
              f"标准差={format_number(data[col].std())}, "
              f"范围=[{format_number(data[col].min())}, {format_number(data[col].max())}]")


def create_iching_interpretation(date, purchase, redeem, oracle):
    """
    创建易经解释
    
    Args:
        date: 日期
        purchase: 申购金额
        redeem: 赎回金额
        oracle: 易经预测器
        
    Returns:
        dict: 易经解释
    """
    date_str = date.strftime('%Y%m%d')
    # 确保purchase和redeem是标量值
    if hasattr(purchase, 'iloc'):
        purchase_val = float(purchase.iloc[0])
    else:
        purchase_val = float(purchase)
    
    if hasattr(redeem, 'iloc'):
        redeem_val = float(redeem.iloc[0])
    else:
        redeem_val = float(redeem)
    purchase_trend, redeem_trend = oracle.predict_trend(date_str, purchase_val, redeem_val)
    
    interpretation = {
        "日期": date_str,
        "申购趋势": purchase_trend,
        "赎回趋势": redeem_trend,
        "建议": []
    }
    
    # 根据趋势添加建议
    if purchase_trend == '升' and redeem_trend == '降':
        interpretation["建议"].append("资金流入增加，适合投资")
    elif purchase_trend == '降' and redeem_trend == '升':
        interpretation["建议"].append("资金流出增加，注意风险")
    elif purchase_trend == '升' and redeem_trend == '升':
        interpretation["建议"].append("资金流动活跃，市场活跃")
    elif purchase_trend == '降' and redeem_trend == '降':
        interpretation["建议"].append("资金流动减少，市场平稳")
    else:
        interpretation["建议"].append("市场趋势平稳，保持观望")
    
    return interpretation


if __name__ == "__main__":
    # 测试工具函数模块
    print("测试工具函数模块...")
    
    # 创建示例数据
    np.random.seed(42)
    dates = pd.date_range('2014-09-01', periods=30, freq='D')
    
    data = pd.DataFrame({
        'report_date': dates,
        'total_purchase_amt': np.random.normal(300000, 50000, 30),
        'total_redeem_amt': np.random.normal(280000, 45000, 30)
    })
    
    # 测试数据摘要
    print_data_summary(data)
    
    # 测试评估指标
    y_true = np.random.normal(300000, 50000, 10)
    y_pred = y_true + np.random.normal(0, 10000, 10)
    metrics = calculate_metrics(y_true, y_pred)
    print_metrics(metrics)
    
    # 测试预测结果验证
    predictions = pd.DataFrame({
        'date': dates[:10],
        'final_purchase': np.random.normal(300000, 50000, 10),
        'final_redeem': np.random.normal(280000, 45000, 10)
    })
    
    validation = validate_predictions(predictions)
    print_validation_results(validation)
    
    print("工具函数模块测试完成！")
