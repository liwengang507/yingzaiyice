"""
股市数据抓取模块
================

实时抓取股市数据、新闻和相关信息
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import re
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

class StockDataCrawler:
    """股市数据爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 主要股票指数代码
        self.stock_indices = {
            '上证指数': '000001.SH',
            '深证成指': '399001.SZ', 
            '创业板指': '399006.SZ',
            '沪深300': '000300.SH',
            '中证500': '000905.SH',
            '科创50': '000688.SH'
        }
        
        # 热门股票代码
        self.popular_stocks = {
            '贵州茅台': '600519.SH',
            '宁德时代': '300750.SZ',
            '比亚迪': '002594.SZ',
            '招商银行': '600036.SH',
            '中国平安': '601318.SH',
            '五粮液': '000858.SZ',
            '隆基绿能': '601012.SH',
            '东方财富': '300059.SZ'
        }
    
    def get_stock_realtime_data(self, stock_code):
        """
        获取股票实时数据
        
        Args:
            stock_code (str): 股票代码
            
        Returns:
            dict: 股票实时数据
        """
        try:
            # 使用新浪财经API
            url = f"http://hq.sinajs.cn/list={stock_code}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                data = response.text
                # 解析数据
                if 'var hq_str_' in data:
                    # 提取数据部分
                    data_part = data.split('"')[1]
                    fields = data_part.split(',')
                    
                    if len(fields) >= 32:
                        return {
                            'name': fields[0],
                            'open': float(fields[1]) if fields[1] else 0,
                            'yesterday_close': float(fields[2]) if fields[2] else 0,
                            'current': float(fields[3]) if fields[3] else 0,
                            'high': float(fields[4]) if fields[4] else 0,
                            'low': float(fields[5]) if fields[5] else 0,
                            'volume': int(fields[8]) if fields[8] else 0,
                            'amount': float(fields[9]) if fields[9] else 0,
                            'date': fields[30],
                            'time': fields[31]
                        }
            
            return None
            
        except Exception as e:
            print(f"获取股票数据失败 {stock_code}: {e}")
            return None
    
    def get_market_overview(self):
        """
        获取市场概览数据
        
        Returns:
            pd.DataFrame: 市场概览数据
        """
        print("正在获取市场概览数据...")
        
        market_data = []
        for name, code in self.stock_indices.items():
            data = self.get_stock_realtime_data(code)
            if data:
                data['type'] = '指数'
                market_data.append(data)
            time.sleep(0.5)  # 避免请求过快
        
        # 获取热门股票数据
        for name, code in self.popular_stocks.items():
            data = self.get_stock_realtime_data(code)
            if data:
                data['type'] = '股票'
                market_data.append(data)
            time.sleep(0.5)
        
        if market_data:
            df = pd.DataFrame(market_data)
            df['change'] = df['current'] - df['yesterday_close']
            df['change_pct'] = (df['change'] / df['yesterday_close'] * 100).round(2)
            df['timestamp'] = datetime.now()
            
            print(f"成功获取 {len(market_data)} 只股票/指数数据")
            return df
        else:
            print("未能获取任何市场数据")
            return pd.DataFrame()
    
    def get_financial_news(self, limit=20):
        """
        获取财经新闻
        
        Args:
            limit (int): 新闻数量限制
            
        Returns:
            list: 新闻列表
        """
        print("正在获取财经新闻...")
        
        news_list = []
        
        try:
            # 获取新浪财经新闻
            url = "https://finance.sina.com.cn/stock/"
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找新闻链接
                news_links = soup.find_all('a', href=True)
                
                for link in news_links[:limit]:
                    href = link.get('href')
                    title = link.get_text().strip()
                    
                    if href and title and len(title) > 10:
                        # 过滤有效的财经新闻
                        if any(keyword in title for keyword in ['股市', '股票', 'A股', '涨停', '跌停', '上涨', '下跌', '投资', '基金']):
                            news_list.append({
                                'title': title,
                                'url': href,
                                'source': '新浪财经',
                                'timestamp': datetime.now()
                            })
            
            print(f"成功获取 {len(news_list)} 条财经新闻")
            return news_list
            
        except Exception as e:
            print(f"获取财经新闻失败: {e}")
            return []
    
    def get_market_sentiment(self):
        """
        获取市场情绪指标
        
        Returns:
            dict: 市场情绪数据
        """
        print("正在分析市场情绪...")
        
        try:
            # 获取涨停跌停数据
            url = "http://quote.eastmoney.com/center/gridlist.html#hs_a_board"
            response = self.session.get(url, timeout=10)
            
            sentiment_data = {
                'timestamp': datetime.now(),
                'market_sentiment': 'neutral',  # 默认中性
                'bullish_signals': 0,
                'bearish_signals': 0,
                'volatility': 'normal'
            }
            
            # 这里可以添加更复杂的情绪分析逻辑
            # 比如分析新闻情感、技术指标等
            
            return sentiment_data
            
        except Exception as e:
            print(f"分析市场情绪失败: {e}")
            return {
                'timestamp': datetime.now(),
                'market_sentiment': 'unknown',
                'bullish_signals': 0,
                'bearish_signals': 0,
                'volatility': 'unknown'
            }
    
    def save_market_data(self, market_data, news_data, sentiment_data, output_dir="stock_data"):
        """
        保存市场数据
        
        Args:
            market_data (pd.DataFrame): 市场数据
            news_data (list): 新闻数据
            sentiment_data (dict): 情绪数据
            output_dir (str): 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存市场数据
        if not market_data.empty:
            market_file = f"{output_dir}/market_data_{timestamp}.csv"
            market_data.to_csv(market_file, index=False, encoding='utf-8-sig')
            print(f"市场数据已保存到: {market_file}")
        
        # 保存新闻数据
        if news_data:
            news_file = f"{output_dir}/news_data_{timestamp}.json"
            with open(news_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"新闻数据已保存到: {news_file}")
        
        # 保存情绪数据
        sentiment_file = f"{output_dir}/sentiment_data_{timestamp}.json"
        with open(sentiment_file, 'w', encoding='utf-8') as f:
            json.dump(sentiment_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"情绪数据已保存到: {sentiment_file}")


class StockNewsAnalyzer:
    """股市新闻分析器"""
    
    def __init__(self):
        """初始化分析器"""
        # 正面关键词
        self.positive_keywords = [
            '上涨', '涨停', '大涨', '突破', '创新高', '利好', '增长', '盈利', '收益',
            '买入', '推荐', '看好', '乐观', '积极', '强势', '反弹', '复苏'
        ]
        
        # 负面关键词
        self.negative_keywords = [
            '下跌', '跌停', '大跌', '破位', '创新低', '利空', '亏损', '风险', '警告',
            '卖出', '减持', '看空', '悲观', '消极', '弱势', '调整', '危机'
        ]
        
        # 中性关键词
        self.neutral_keywords = [
            '平稳', '震荡', '整理', '观望', '中性', '维持', '不变', '稳定'
        ]
    
    def analyze_news_sentiment(self, news_list):
        """
        分析新闻情感
        
        Args:
            news_list (list): 新闻列表
            
        Returns:
            dict: 情感分析结果
        """
        if not news_list:
            return {
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'sentiment_score': 0,
                'overall_sentiment': 'neutral'
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for news in news_list:
            title = news.get('title', '')
            
            # 计算情感得分
            pos_score = sum(1 for keyword in self.positive_keywords if keyword in title)
            neg_score = sum(1 for keyword in self.negative_keywords if keyword in title)
            neu_score = sum(1 for keyword in self.neutral_keywords if keyword in title)
            
            if pos_score > neg_score and pos_score > neu_score:
                positive_count += 1
            elif neg_score > pos_score and neg_score > neu_score:
                negative_count += 1
            else:
                neutral_count += 1
        
        total_news = len(news_list)
        sentiment_score = (positive_count - negative_count) / total_news if total_news > 0 else 0
        
        if sentiment_score > 0.1:
            overall_sentiment = 'positive'
        elif sentiment_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_score': round(sentiment_score, 3),
            'overall_sentiment': overall_sentiment,
            'total_news': total_news
        }


def create_sample_stock_data():
    """
    创建示例股市数据
    
    Returns:
        dict: 示例数据
    """
    print("正在创建示例股市数据...")
    
    # 创建示例股票数据
    np.random.seed(42)
    n_days = 30
    
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    
    # 模拟股票价格数据
    base_price = 100
    stock_data = []
    
    for i, date in enumerate(dates):
        # 模拟价格波动
        change_pct = np.random.normal(0, 0.02)  # 2%标准差
        price = base_price * (1 + change_pct)
        base_price = price
        
        stock_data.append({
            'date': date,
            'open': price * (1 + np.random.normal(0, 0.005)),
            'high': price * (1 + abs(np.random.normal(0, 0.01))),
            'low': price * (1 - abs(np.random.normal(0, 0.01))),
            'close': price,
            'volume': np.random.randint(1000000, 10000000),
            'amount': np.random.randint(100000000, 1000000000)
        })
    
    # 创建示例新闻数据
    news_data = [
        {
            'title': 'A股市场今日上涨，科技股表现强势',
            'url': 'http://example.com/news1',
            'source': '示例财经',
            'timestamp': datetime.now()
        },
        {
            'title': '央行降准释放流动性，市场情绪乐观',
            'url': 'http://example.com/news2', 
            'source': '示例财经',
            'timestamp': datetime.now()
        },
        {
            'title': '部分板块出现调整，投资者需谨慎',
            'url': 'http://example.com/news3',
            'source': '示例财经',
            'timestamp': datetime.now()
        }
    ]
    
    # 创建示例情绪数据
    sentiment_data = {
        'timestamp': datetime.now(),
        'market_sentiment': 'positive',
        'bullish_signals': 3,
        'bearish_signals': 1,
        'volatility': 'normal'
    }
    
    return {
        'stock_data': pd.DataFrame(stock_data),
        'news_data': news_data,
        'sentiment_data': sentiment_data
    }


if __name__ == "__main__":
    # 测试股市数据抓取模块
    print("测试股市数据抓取模块...")
    
    # 创建示例数据
    sample_data = create_sample_stock_data()
    
    # 测试新闻分析器
    analyzer = StockNewsAnalyzer()
    sentiment_result = analyzer.analyze_news_sentiment(sample_data['news_data'])
    
    print("新闻情感分析结果:")
    print(f"正面新闻: {sentiment_result['positive_count']}")
    print(f"负面新闻: {sentiment_result['negative_count']}")
    print(f"中性新闻: {sentiment_result['neutral_count']}")
    print(f"情感得分: {sentiment_result['sentiment_score']}")
    print(f"整体情感: {sentiment_result['overall_sentiment']}")
    
    print("股市数据抓取模块测试完成！")


