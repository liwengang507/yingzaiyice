"""
股市新闻抓取模块
用于实时抓取股市新闻和市场信息
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockNewsCrawler:
    """股市新闻抓取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def crawl_sina_finance_news(self, max_pages: int = 5) -> List[Dict]:
        """
        抓取新浪财经新闻
        """
        news_list = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"https://finance.sina.com.cn/stock/stockzx/stockzx_{page}.shtml"
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找新闻链接
                    news_links = soup.find_all('a', href=True)
                    
                    for link in news_links:
                        href = link.get('href')
                        title = link.get_text().strip()
                        
                        if href and title and 'stock' in href and len(title) > 10:
                            news_list.append({
                                'title': title,
                                'url': href,
                                'source': '新浪财经',
                                'crawl_time': datetime.now()
                            })
                
                time.sleep(1)  # 避免请求过快
                
        except Exception as e:
            logger.error(f"抓取新浪财经新闻失败: {e}")
        
        return news_list
    
    def crawl_eastmoney_news(self, max_pages: int = 3) -> List[Dict]:
        """
        抓取东方财富新闻
        """
        news_list = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"https://finance.eastmoney.com/news/cjxw_{page}.html"
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找新闻链接
                    news_links = soup.find_all('a', href=True)
                    
                    for link in news_links:
                        href = link.get('href')
                        title = link.get_text().strip()
                        
                        if href and title and 'news' in href and len(title) > 10:
                            news_list.append({
                                'title': title,
                                'url': href,
                                'source': '东方财富',
                                'crawl_time': datetime.now()
                            })
                
                time.sleep(1)  # 避免请求过快
                
        except Exception as e:
            logger.error(f"抓取东方财富新闻失败: {e}")
        
        return news_list
    
    def crawl_tencent_finance_news(self, max_pages: int = 3) -> List[Dict]:
        """
        抓取腾讯财经新闻
        """
        news_list = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"https://finance.qq.com/stock/stockzx/stockzx_{page}.htm"
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找新闻链接
                    news_links = soup.find_all('a', href=True)
                    
                    for link in news_links:
                        href = link.get('href')
                        title = link.get_text().strip()
                        
                        if href and title and 'stock' in href and len(title) > 10:
                            news_list.append({
                                'title': title,
                                'url': href,
                                'source': '腾讯财经',
                                'crawl_time': datetime.now()
                            })
                
                time.sleep(1)  # 避免请求过快
                
        except Exception as e:
            logger.error(f"抓取腾讯财经新闻失败: {e}")
        
        return news_list
    
    def crawl_all_news(self, max_pages: int = 3) -> List[Dict]:
        """
        抓取所有新闻源
        """
        all_news = []
        
        # 抓取新浪财经
        logger.info("开始抓取新浪财经新闻...")
        sina_news = self.crawl_sina_finance_news(max_pages)
        all_news.extend(sina_news)
        logger.info(f"新浪财经新闻数量: {len(sina_news)}")
        
        # 抓取东方财富
        logger.info("开始抓取东方财富新闻...")
        eastmoney_news = self.crawl_eastmoney_news(max_pages)
        all_news.extend(eastmoney_news)
        logger.info(f"东方财富新闻数量: {len(eastmoney_news)}")
        
        # 抓取腾讯财经
        logger.info("开始抓取腾讯财经新闻...")
        tencent_news = self.crawl_tencent_finance_news(max_pages)
        all_news.extend(tencent_news)
        logger.info(f"腾讯财经新闻数量: {len(tencent_news)}")
        
        # 去重
        unique_news = []
        seen_titles = set()
        
        for news in all_news:
            if news['title'] not in seen_titles:
                unique_news.append(news)
                seen_titles.add(news['title'])
        
        logger.info(f"去重后新闻总数: {len(unique_news)}")
        return unique_news
    
    def analyze_news_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        分析新闻情感
        """
        positive_keywords = ['上涨', '利好', '增长', '突破', '创新高', '强势', '看好', '乐观']
        negative_keywords = ['下跌', '利空', '下降', '跌破', '创新低', '弱势', '看空', '悲观']
        
        sentiment_analysis = {
            'total_news': len(news_list),
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_news': [],
            'negative_news': [],
            'neutral_news': []
        }
        
        for news in news_list:
            title = news['title']
            positive_score = sum(1 for keyword in positive_keywords if keyword in title)
            negative_score = sum(1 for keyword in negative_keywords if keyword in title)
            
            if positive_score > negative_score:
                sentiment_analysis['positive_count'] += 1
                sentiment_analysis['positive_news'].append(news)
            elif negative_score > positive_score:
                sentiment_analysis['negative_count'] += 1
                sentiment_analysis['negative_news'].append(news)
            else:
                sentiment_analysis['neutral_count'] += 1
                sentiment_analysis['neutral_news'].append(news)
        
        return sentiment_analysis
    
    def save_news_to_csv(self, news_list: List[Dict], filename: str = None):
        """
        保存新闻到CSV文件
        """
        if not filename:
            filename = f"stock_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df = pd.DataFrame(news_list)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"新闻已保存到: {filename}")
    
    def get_market_summary(self, news_list: List[Dict]) -> str:
        """
        生成市场摘要
        """
        if not news_list:
            return "暂无新闻数据"
        
        sentiment_analysis = self.analyze_news_sentiment(news_list)
        
        summary = f"""
市场新闻摘要 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
===============================================

总新闻数: {sentiment_analysis['total_news']}
正面新闻: {sentiment_analysis['positive_count']} ({sentiment_analysis['positive_count']/sentiment_analysis['total_news']*100:.1f}%)
负面新闻: {sentiment_analysis['negative_count']} ({sentiment_analysis['negative_count']/sentiment_analysis['total_news']*100:.1f}%)
中性新闻: {sentiment_analysis['neutral_count']} ({sentiment_analysis['neutral_count']/sentiment_analysis['total_news']*100:.1f}%)

市场情绪: {'乐观' if sentiment_analysis['positive_count'] > sentiment_analysis['negative_count'] else '悲观' if sentiment_analysis['negative_count'] > sentiment_analysis['positive_count'] else '中性'}
        """
        
        return summary

def main():
    """主函数"""
    print("开始抓取股市新闻...")
    
    crawler = StockNewsCrawler()
    
    # 抓取新闻
    news_list = crawler.crawl_all_news(max_pages=2)
    
    if news_list:
        # 分析情感
        sentiment_analysis = crawler.analyze_news_sentiment(news_list)
        
        # 生成摘要
        summary = crawler.get_market_summary(news_list)
        print(summary)
        
        # 保存新闻
        crawler.save_news_to_csv(news_list)
        
        # 显示部分新闻
        print("\n最新新闻标题:")
        for i, news in enumerate(news_list[:10], 1):
            print(f"{i}. {news['title']} ({news['source']})")
    else:
        print("未获取到新闻数据")

if __name__ == "__main__":
    main()

