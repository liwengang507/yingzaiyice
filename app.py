import streamlit as st
import random
import time
import requests
import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import numpy as np


# 导入增强问答系统
try:
    from src.enhanced_qa_system import enhanced_qa
    ENHANCED_QA_AVAILABLE = True
except ImportError:
    ENHANCED_QA_AVAILABLE = False
    print("增强问答系统不可用，使用默认问答")

# 导入增强解卦系统
try:
    from src.enhanced_divination_system import enhanced_divination
    ENHANCED_DIVINATION_AVAILABLE = True
except ImportError:
    ENHANCED_DIVINATION_AVAILABLE = False
    print("增强解卦系统不可用，使用默认解卦")

# 设置页面配置
st.set_page_config(
    page_title="盈在易测系统",
    page_icon="☯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 整体布局 - 米黄色背景 */
    .main-container {
        background: linear-gradient(135deg, #F5F5DC 0%, #FFF8DC 50%, #F0E68C 100%);
        padding: 0;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        max-width: 800px;
        margin: 0 auto;
        font-family: "Microsoft YaHei", "SimHei", sans-serif;
        overflow: hidden;
        position: relative;
    }
    
    .main-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 80%, rgba(139, 0, 0, 0.03) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(218, 165, 32, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: 1;
    }
    
    .main-container > * {
        position: relative;
        z-index: 2;
    }
    
    /* 顶部标题区域 */
    .header-section {
        background: linear-gradient(135deg, #8B0000, #DAA520);
        color: white;
        padding: 30px 20px;
        text-align: center;
    }
    
    .main-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 8px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .sub-title {
        font-size: 16px;
        opacity: 0.95;
        font-weight: 300;
    }
    
    /* 主体内容区域 - 米黄色背景 */
    .content-section {
        padding: 30px 20px;
        background: linear-gradient(180deg, rgba(255, 248, 220, 0.8) 0%, rgba(245, 245, 220, 0.9) 100%);
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .content-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 10% 20%, rgba(139, 0, 0, 0.02) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(218, 165, 32, 0.03) 0%, transparent 40%);
        pointer-events: none;
        z-index: 1;
    }
    
    .content-section > * {
        position: relative;
        z-index: 2;
    }
    
    .section-title {
        color: #8B0000;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* 只移除emoji图标周围的边框 */
    .stMarkdown span:focus,
    .stMarkdown span:focus-visible,
    .stMarkdown h3:focus,
    .stMarkdown h3:focus-visible,
    .stMarkdown h3:has(span):focus,
    .stMarkdown h3:has(span):focus-visible {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* 移除emoji字符本身的边框 */
    .stMarkdown:has(span) span,
    .stMarkdown h3:has(span) {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* 表单样式 - 添加层次感 */
    .form-container {
        background: linear-gradient(135deg, rgba(255, 248, 220, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%);
        border: 2px solid rgba(218, 165, 32, 0.3);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(218, 165, 32, 0.1);
        backdrop-filter: blur(5px);
        position: relative;
    }
    
    .form-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(218, 165, 32, 0.05) 0%, transparent 70%);
        border-radius: 10px;
        pointer-events: none;
        z-index: 1;
    }
    
    .form-container > * {
        position: relative;
        z-index: 2;
    }
    
    /* 硬币样式 - 终极真实乾隆通宝古币 */
    .coin-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .coin {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: 
            radial-gradient(circle at 15% 15%, rgba(255, 255, 255, 0.4) 0%, transparent 30%),
            radial-gradient(circle at 85% 85%, rgba(0, 0, 0, 0.4) 0%, transparent 30%),
            linear-gradient(135deg, 
                #8B4513 0%, 
                #A0522D 5%, 
                #CD7F32 10%, 
                #8B4513 15%, 
                #B87333 20%, 
                #8B4513 25%, 
                #A0522D 30%, 
                #CD7F32 35%, 
                #8B4513 40%, 
                #B87333 45%, 
                #8B4513 50%, 
                #A0522D 55%, 
                #CD7F32 60%, 
                #8B4513 65%, 
                #B87333 70%, 
                #8B4513 75%, 
                #A0522D 80%, 
                #CD7F32 85%, 
                #8B4513 90%, 
                #B87333 95%, 
                #8B4513 100%);
        border: 8px solid #8B4513;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: spin 2s linear infinite;
        box-shadow: 
            0 15px 30px rgba(0, 0, 0, 0.8),
            inset 0 8px 16px rgba(255, 255, 255, 0.3),
            inset 0 -8px 16px rgba(0, 0, 0, 0.7),
            0 0 0 4px rgba(139, 69, 19, 0.5),
            inset 0 0 25px rgba(0, 0, 0, 0.4);
        position: relative;
        font-family: "SimSun", serif;
        overflow: visible;
    }
    
    
    .coin-hole {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 26px;
        height: 26px;
        border-radius: 4px;
        background: 
            linear-gradient(135deg, 
                #000000 0%, 
                #1A0E0A 25%, 
                #000000 50%, 
                #1A0E0A 75%, 
                #000000 100%);
        border: 4px solid #2F1B14;
        box-shadow: 
            inset 0 5px 10px rgba(0, 0, 0, 1),
            inset 0 2px 4px rgba(255, 255, 255, 0.1),
            0 4px 8px rgba(0, 0, 0, 0.9),
            0 0 0 2px rgba(0, 0, 0, 1);
        z-index: 5;
    }
    
    .coin-surface {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 50%;
        background: 
            radial-gradient(circle at 15% 15%, rgba(255, 255, 255, 0.4) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(0, 0, 0, 0.3) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 0.2) 0%, transparent 60%);
        pointer-events: none;
        z-index: 2;
    }
    
    .coin.stopped {
        animation: none;
        transform: rotateY(0deg);
    }
    
    @keyframes spin {
        0% { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }
    
    /* 六爻显示 */
    .yao-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 20px 0;
    }
    
    .yao-line {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px;
        background-color: #ffffff;
        border: 1px solid #DAA520;
        border-radius: 5px;
    }
    
    .yao-label {
        width: 80px;
        font-weight: bold;
        color: #8B0000;
    }
    
    .yao-symbol {
        font-size: 18px;
        color: #8B0000;
    }
    
    /* 结果区域 - 添加层次感 */
    .result-section {
        background: linear-gradient(135deg, rgba(255, 248, 220, 0.9) 0%, rgba(255, 255, 255, 0.95) 100%);
        border: 2px solid rgba(218, 165, 32, 0.4);
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 6px 20px rgba(218, 165, 32, 0.15);
        backdrop-filter: blur(8px);
        position: relative;
    }
    
    .result-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 20%, rgba(139, 0, 0, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(218, 165, 32, 0.05) 0%, transparent 50%);
        border-radius: 12px;
        pointer-events: none;
        z-index: 1;
    }
    
    .result-section > * {
        position: relative;
        z-index: 2;
    }
    
    .result-title {
        color: #8B0000;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .gua-info {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .gua-name {
        font-size: 24px;
        font-weight: bold;
        color: #8B0000;
        margin-bottom: 15px;
    }
    
    .gua-symbol {
        margin: 15px 0;
        font-size: 18px;
        line-height: 1.5;
    }
    
    .gua-text {
        font-size: 16px;
        color: #8B4513;
        margin: 10px 0;
        font-weight: 500;
    }
    
    .gua-interpretation {
        font-size: 14px;
        color: #654321;
        line-height: 1.6;
        text-align: left;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #DAA520;
    }
    
    /* 结语特殊样式 - 红色边框框体 */
    .conclusion-box {
        border: 3px solid #8B0000;
        border-radius: 10px;
        padding: 12px 15px;
        margin: 20px 0;
        background: linear-gradient(135deg, rgba(255, 248, 220, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%);
        box-shadow: 0 4px 15px rgba(139, 0, 0, 0.2);
        position: relative;
    }
    
    .conclusion-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(139, 0, 0, 0.03) 0%, transparent 70%);
        border-radius: 10px;
        pointer-events: none;
        z-index: 1;
    }
    
    .conclusion-box > * {
        position: relative;
        z-index: 2;
    }
    
    .conclusion-title {
        color: #8B0000;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(139, 0, 0, 0.3);
    }
    
    .conclusion-content {
        font-size: 16px;
        color: #654321;
        line-height: 1.8;
        text-align: left;
        margin: 0;
        padding: 0;
    }
    
    /* 智能引导卡片样式 */
    .smart-guide-card {
        margin: 30px 0;
        padding: 30px;
        background: linear-gradient(135deg, rgba(255, 248, 220, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%);
        border: 2px solid #DAA520;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(218, 165, 32, 0.2);
        opacity: 0;
        animation: fadeIn 1s ease-in forwards;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .smart-guide-title {
        color: #8B0000;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .smart-guide-text {
        color: #654321;
        font-size: 16px;
        line-height: 1.8;
        text-align: center;
        margin-bottom: 25px;
    }
    
    .smart-guide-buttons {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-top: 20px;
    }
    
    /* 按钮样式 */
    .action-button {
        background-color: #8B0000;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 10px 0;
    }
    
    .action-button:hover {
        background-color: #A52A2A;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 0, 0, 0.4);
    }
    
    .secondary-button {
        background-color: #DAA520;
        color: #8B0000;
    }
    
    .secondary-button:hover {
        background-color: #B8860B;
    }
    
    /* Streamlit按钮样式增强 - 确保所有按钮都是红色 */
    .stButton > button,
    button[data-testid],
    div[data-testid="baseButton-secondary"] > button,
    div[data-testid="baseButton-primary"] > button {
        background-color: #8B0000 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover,
    button[data-testid]:hover,
    div[data-testid="baseButton-secondary"] > button:hover,
    div[data-testid="baseButton-primary"] > button:hover {
        background-color: #A52A2A !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(139, 0, 0, 0.4) !important;
    }
    
    /* 确保所有按钮文字为白色 */
    .stButton > button > p,
    button > p,
    button > div {
        color: white !important;
    }
    
    /* 导航栏按钮样式 */
    .nav-button {
        background: linear-gradient(135deg, rgba(139, 0, 0, 0.8) 0%, rgba(218, 165, 32, 0.9) 100%);
        color: white;
        border: 2px solid rgba(218, 165, 32, 0.5);
        border-radius: 6px;
        padding: 10px 15px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        background: linear-gradient(135deg, rgba(139, 0, 0, 1) 0%, rgba(218, 165, 32, 1) 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 0, 0, 0.4);
    }
    
    /* 底部版权信息 - 添加层次感 */
    .footer-section {
        text-align: center;
        padding: 20px;
        font-size: 12px;
        color: #666;
        border-top: 1px solid rgba(240, 240, 240, 0.5);
        background: linear-gradient(180deg, rgba(250, 250, 250, 0.8) 0%, rgba(245, 245, 245, 0.9) 100%);
        backdrop-filter: blur(5px);
        position: relative;
    }
    
    .footer-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(139, 0, 0, 0.02) 0%, transparent 70%);
        pointer-events: none;
        z-index: 1;
    }
    
    .footer-section > * {
        position: relative;
        z-index: 2;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 阴阳爻线样式 - 真实卦象效果 */
    .hexagram-container {
        display: flex;
        justify-content: center;
        gap: 50px;
        margin: 30px 0;
        padding: 30px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 248, 220, 0.5) 100%);
        border: 2px solid rgba(218, 165, 32, 0.3);
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(139, 0, 0, 0.15);
    }
    
    .hexagram {
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        min-width: 120px;
    }
    
    .hexagram-title {
        font-size: 18px;
        font-weight: bold;
        color: #8B0000;
        margin-bottom: 15px;
        padding: 8px;
        background: rgba(255, 248, 220, 0.5);
        border-radius: 6px;
    }
    
    .hexagram-lines {
        display: flex;
        flex-direction: column;
        gap: 10px;
        align-items: center;
        padding: 10px;
    }
    
    .yin-line, .yang-line {
        display: block;
        width: 80px;
        height: 10px;
        margin: 2px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .yin-line {
        background: #000;
        position: relative;
    }
    
    .yin-line::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 30px;
        height: 3px;
        background: #F5F5DC;
        border-radius: 2px;
    }
    
    .yang-line {
        background: #8B0000;
    }
    
    .changing-line {
        background: #FF0000 !important;
        box-shadow: 0 0 8px rgba(255, 0, 0, 0.5) !important;
    }
    
    /* 页面整体背景层次感 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 900px;
        background: linear-gradient(135deg, rgba(248, 248, 248, 0.3) 0%, rgba(255, 255, 255, 0.5) 50%, rgba(240, 240, 240, 0.3) 100%);
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .main .block-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 10% 10%, rgba(139, 0, 0, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 90% 90%, rgba(218, 165, 32, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 1;
    }
    
    .main .block-container > * {
        position: relative;
        z-index: 2;
    }
    
    /* 页面背景 - 米黄色 */
    .stApp {
        background: linear-gradient(135deg, #F5F5DC 0%, #FFF8DC 50%, #F0E68C 100%);
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 20%, rgba(139, 0, 0, 0.01) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(218, 165, 32, 0.02) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }
</style>
""", unsafe_allow_html=True)

# 易经六十四卦数据
gua_data = [
    {"id": 1, "name": "乾卦", "symbol": "111111", "description": "天行健，君子以自强不息", 
     "text": "元亨利贞", "interpretation": "乾卦象征天，具有创始、亨通、和谐、贞正四种德性。表示阳刚之气，主动、进取、强健。君子应当效法天的刚健，自强不息，不断进取。"},
    
    {"id": 2, "name": "坤卦", "symbol": "000000", "description": "地势坤，君子以厚德载物", 
     "text": "元亨，利牝马之贞", "interpretation": "坤卦象征地，具有顺从、包容、滋养万物的特性。表示阴柔之美，被动、守成、柔顺。君子应当效法地的厚德，包容万物，以德载物。"},
    
    {"id": 3, "name": "屯卦", "symbol": "100010", "description": "云雷屯，君子以经纶", 
     "text": "元亨利贞，勿用有攸往", "interpretation": "屯卦象征万物始生时的艰难，需要耐心经营，不可轻举妄动。此时应当积蓄力量，等待时机，不可急于求成。"},
    
    {"id": 4, "name": "蒙卦", "symbol": "010001", "description": "山下出泉，蒙；君子以果行育德", 
     "text": "亨。匪我求童蒙，童蒙求我", "interpretation": "蒙卦象征启蒙教育，需要启发引导，循序渐进。教育者应当有耐心，被教育者应当主动求学。"},
    
    {"id": 5, "name": "需卦", "symbol": "111011", "description": "云上于天，需；君子以饮食宴乐", 
     "text": "有孚，光亨，贞吉，利涉大川", "interpretation": "需卦象征等待，需要耐心和信心，时机成熟自然成功。君子应当保持诚信，等待时机，不可急躁。"},
    
    {"id": 6, "name": "讼卦", "symbol": "011111", "description": "天与水违行，讼；君子以作事谋始", 
     "text": "有孚窒惕，中吉，终凶", "interpretation": "讼卦象征争讼，提醒人们做事要谨慎，避免争端。君子应当从开始就避免争端，以和为贵。"},
    
    {"id": 7, "name": "师卦", "symbol": "010000", "description": "地中有水，师；君子以容民畜众", 
     "text": "贞，丈人吉，无咎", "interpretation": "师卦象征军队，强调纪律和领导。君子应当以德服人，团结群众，建立良好的秩序。"},
    
    {"id": 8, "name": "比卦", "symbol": "000010", "description": "水在地上，比；先王以建万国，亲诸侯", 
     "text": "吉。原筮元永贞，无咎", "interpretation": "比卦象征亲近、团结，强调和谐关系。君子应当亲近贤人，团结众人，建立良好的关系。"},
    
    {"id": 9, "name": "小畜卦", "symbol": "110111", "description": "风行天上，小畜；君子以懿文德", 
     "text": "亨。密云不雨，自我西郊", "interpretation": "小畜卦象征小有积蓄，需要继续努力。君子应当修养品德，积蓄力量，为更大的发展做准备。"},
    
    {"id": 10, "name": "履卦", "symbol": "111011", "description": "天泽履，君子以辨上下，定民志", 
     "text": "履虎尾，不咥人，亨", "interpretation": "履卦象征谨慎行事，如履薄冰。君子应当明辨是非，谨慎行事，避免危险。"},
    
    {"id": 11, "name": "泰卦", "symbol": "000111", "description": "天地交，泰；后以财成天地之道，辅相天地之宜", 
     "text": "小往大来，吉亨", "interpretation": "泰卦象征通泰，天地交合，万物亨通。君子应当顺应自然，把握时机，实现和谐发展。"},
    
    {"id": 12, "name": "否卦", "symbol": "111000", "description": "天地不交，否；君子以俭德辟难，不可荣以禄", 
     "text": "否之匪人，不利君子贞，大往小来", "interpretation": "否卦象征闭塞，天地不交，万物不通。君子应当节俭修身，避免奢华，等待时机。"}
]

# 爻的类型
yao_types = {
    "老阳": {"symbol": "111", "value": 1, "name": "老阳"},
    "少阳": {"symbol": "110", "value": 1, "name": "少阳"},
    "老阴": {"symbol": "000", "value": 0, "name": "老阴"},
    "少阴": {"symbol": "001", "value": 0, "name": "少阴"}
}

def render_gua_symbol(symbol):
    """渲染卦象符号 - 真实卦象效果"""
    lines = []
    for char in symbol:
        if char == '1':
            lines.append('<div class="yang-line"></div>')
        else:
            lines.append('<div class="yin-line"></div>')
    return ''.join(lines)

def render_hexagram_display(gua, show_loading=False):
    """渲染完整的卦象显示"""
    symbol_html = render_gua_symbol(gua["symbol"])
    
    # 生成变卦（随机改变一爻）
    changing_symbol = list(gua["symbol"])
    change_pos = random.randint(0, 5)
    changing_symbol[change_pos] = '0' if changing_symbol[change_pos] == '1' else '1'
    changing_symbol_html = render_gua_symbol(''.join(changing_symbol))
    
    # 获取变卦名称
    changing_gua_name = f"{gua['name']}变卦"
    
    # 如果显示加载提示，在卦象容器内显示
    loading_html = ""
    if show_loading:
        loading_html = '''
        <div style="text-align: center; padding: 15px; margin-top: 15px; background-color: rgba(139, 0, 0, 0.1); border-radius: 8px; border: 2px solid #8B0000;">
            <div style="color: #8B0000; font-size: 14px; font-weight: bold;">○ 正在使用AI大模型生成详细的解卦内容，预计10-15秒...</div>
        </div>
        '''
    
    return f'''
    <div class="hexagram-container">
        <div class="hexagram">
            <div class="hexagram-title">{gua['name']} (本卦)</div>
            <div class="hexagram-lines">
                {symbol_html}
            </div>
        </div>
        <div class="hexagram">
            <div class="hexagram-title">{changing_gua_name} (变卦)</div>
            <div class="hexagram-lines">
                {changing_symbol_html}
            </div>
        </div>
        {loading_html}
    </div>
    '''

def toss_coins(divination_content=""):
    """投掷三枚硬币 - 基于占卜内容和日期生成确定性结果"""
    # 获取今天的日期字符串
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 基于占卜内容和日期生成确定性种子
    seed_str = f"{today}_{divination_content}"
    seed_hash = hash(seed_str)
    random.seed(seed_hash)
    
    results = []
    for i in range(3):
        result = random.choice([0, 1])  # 0为阴，1为阳
        results.append(result)
    
    # 重置随机种子
    random.seed()
    return results

def get_yao_type(coin_results):
    """根据硬币结果确定爻的类型"""
    yang_count = sum(coin_results)
    if yang_count == 3:
        return "老阳"
    elif yang_count == 2:
        return "少阳"
    elif yang_count == 1:
        return "少阴"
    else:
        return "老阴"

def calculate_gua(yao_results, divination_content=""):
    """根据六爻结果计算卦象 - 如果同一天内相同问题，结果一致"""
    gua_symbol = ""
    for yao in yao_results:
        if yao in ["老阳", "少阳"]:
            gua_symbol += "1"
        else:
            gua_symbol += "0"
    
    # 调试信息
    print(f"六爻结果: {yao_results}")
    print(f"生成的卦象符号: {gua_symbol}")
    
    # 查找对应的卦
    for gua in gua_data:
        if gua["symbol"] == gua_symbol:
            print(f"找到匹配的卦: {gua['name']}")
            return gua
    
    # 如果没有找到精确匹配，尝试找到最接近的卦
    print(f"未找到精确匹配的卦象: {gua_symbol}")
    
    # 如果找不到匹配的卦，返回一个默认的卦
    if gua_symbol == "111111":
        return gua_data[0]  # 乾卦
    elif gua_symbol == "000000":
        return gua_data[1]  # 坤卦
    else:
        # 返回一个通用的卦
        return gua_data[2]  # 屯卦


def show_thinking_process(message="正在处理中..."):
    """显示思考过程（类似图三样式）"""
    st.markdown("---")
    st.markdown("### 回答:")
    
    # 思考过程容器
    st.markdown("### 智能思考过程:")
    
    # 显示步骤（模拟多步骤思考）
    thinking_steps = [
        "第一步:信息收集 收集用户输入的占卜内容和起卦方式信息。",
        "第二步:数据解析 解析占卜内容，提取关键信息点。",
        "第三步:卦象计算 根据起卦方式计算对应的卦象。",
        "第四步:卦辞匹配 从知识库中匹配对应的卦辞、象辞和爻辞。",
        "第五步:方案制定 基于分析结果，提供具体可行的生活建议和注意事项。包括具体的实施步骤、时间安排、预期效果、风险控制等详细指导。"
    ]
    
    # 显示当前步骤
    for i, step in enumerate(thinking_steps):
        if i < len(thinking_steps) - 1:
            st.markdown(f"**{step}**")
        else:
            st.markdown(f"**{step}**")
            break
    
    # 显示加载状态
    with st.spinner("正在生成答案..."):
        # 模拟AI模型调用
        st.markdown('<div style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">', unsafe_allow_html=True)
        st.markdown('<div style="width: 24px; height: 24px; border: 3px solid #1e88e5; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #666;">{message}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 添加旋转动画CSS
    st.markdown("""
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 短暂延迟以显示思考过程
    time.sleep(0.5)

def call_deepseek_api(prompt, max_tokens=3000):
    """调用DeepSeek API（优化版：支持更丰满的内容生成）"""
    try:
        from src.api_config import APIConfig
        import requests
        
        api_key = APIConfig.DEEPSEEK_API_KEY
        api_url = APIConfig.DEEPSEEK_API_URL
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位精通易经的专家，擅长详细、深入、全面地解读卦象的含义。请提供详细、丰富、实用的解答，每个方面200-300字，内容要精炼但有深度。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": max_tokens
        }
        
        # 优化超时时间到15秒以加快响应速度
        response = requests.post(api_url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return None
    except requests.Timeout:
        print("DeepSeek API调用超时（15秒）")
        return None
    except Exception as e:
        print(f"DeepSeek API调用失败: {e}")
        return None

def call_qwen_api(prompt, max_tokens=3000):
    """调用Qwen API（通义千问）- 支持更丰满的内容生成"""
    try:
        from src.api_config import APIConfig
        import requests
        
        api_key = APIConfig.QWEN_API_KEY
        # DashScope API 标准格式
        api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # DashScope 标准格式
        data = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一位精通易经的专家，擅长详细、深入、全面地解读卦象的含义。请提供详细、丰富、实用的解答，每个方面200-300字，内容要精炼但有深度。"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.8,
                "max_tokens": max_tokens
            }
        }
        
        # 优化超时时间到15秒以加快响应速度
        response = requests.post(api_url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        
        # DashScope 返回格式
        if "output" in result:
            if "choices" in result["output"] and len(result["output"]["choices"]) > 0:
                return result["output"]["choices"][0]["message"]["content"]
            elif "text" in result["output"]:
                return result["output"]["text"]
        return None
    except requests.Timeout:
        print("Qwen API调用超时（15秒）")
        return None
    except Exception as e:
        print(f"Qwen API调用失败: {e}")
        return None

def identify_relevant_categories(divination_event):
    """根据占卜问题识别相关的解卦方面"""
    if not divination_event:
        return ["时运（运势分析）"]  # 默认返回时运
    
    divination_event_lower = divination_event.lower()
    relevant_categories = []
    
    # 识别关键词
    if any(keyword in divination_event_lower for keyword in ["事业", "工作", "职业", "职场", "升职", "跳槽", "创业"]):
        relevant_categories.append("事业（事业发展）")
    
    if any(keyword in divination_event_lower for keyword in ["感情", "爱情", "恋爱", "婚姻", "结婚", "分手", "复合", "桃花"]):
        relevant_categories.append("感情（感情运势）")
    
    if any(keyword in divination_event_lower for keyword in ["财运", "财富", "投资", "理财", "赚钱", "收入", "经济"]):
        relevant_categories.append("财运（财富运势）")
    
    if any(keyword in divination_event_lower for keyword in ["健康", "身体", "疾病", "生病", "养生", "调理"]):
        relevant_categories.append("身体（健康建议）")
    
    if any(keyword in divination_event_lower for keyword in ["家宅", "家庭", "家居", "房屋", "搬家", "装修"]):
        relevant_categories.append("家宅（家庭和谐）")
    
    if any(keyword in divination_event_lower for keyword in ["运势", "运程", "时运", "运气", "未来", "前景"]):
        relevant_categories.append("时运（运势分析）")
    
    # 如果没有识别到任何相关类别，默认返回时运
    if not relevant_categories:
        relevant_categories.append("时运（运势分析）")
    
    return relevant_categories

def generate_conclusion(gua_name, gua_text, gua_description, divination_event="", enhanced_result=None):
    """生成丰满、有总结性的结语，根据用户问题给出详细解释"""
    # 根据占卜问题生成针对性的总结
    divination_event_lower = divination_event.lower() if divination_event else ""
    
    # 判断卦象的吉凶倾向（简化判断）
    auspicious_keywords = ["吉", "亨", "利", "泰", "乾", "坤", "大有", "谦", "豫", "随", "临", "观", "噬嗑", "贲", "复", "无妄", "大畜", "颐", "大过", "坎", "离", "咸", "恒", "遁", "大壮", "晋", "明夷", "家人", "睽", "蹇", "解", "损", "益", "夬", "姤", "萃", "升", "困", "井", "革", "鼎", "震", "艮", "渐", "归妹", "丰", "旅", "巽", "兑", "涣", "节", "中孚", "小过", "既济"]
    inauspicious_keywords = ["凶", "否", "剥", "困", "坎", "蹇", "损", "否"]
    
    is_auspicious = any(keyword in gua_name for keyword in auspicious_keywords)
    
    # 根据占卜问题类型生成针对性的丰满总结
    if "事业" in divination_event_lower or "工作" in divination_event_lower:
        if is_auspicious:
            core_summary = f"{gua_name}卦象显示，当前事业发展方面宜把握机遇，顺势而为。卦辞「{gua_text}」揭示了当前阶段的关键特征，表明事业发展正处于有利时机。从象辞「{gua_description}」来看，此卦象反映了您在事业发展过程中所处的积极状态，内外环境相对和谐，有利于推进目标。卦象的阴阳变化体现了事物发展的内在规律，当前阶段机遇与挑战并存，但整体趋势向好。建议您充分把握当前的有利条件，积极争取关键机会，同时保持理性思考，避免因过度乐观而忽视潜在风险。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析当前形势：</strong>将卦象指导与实际情况相结合，深入分析自身优势和外部环境，识别关键机遇点，制定切实可行的发展计划；<br>2) <strong>把握有利时机，积极行动：</strong>在机会来临时果断行动，但需审慎评估风险，确保决策的合理性和可执行性，避免盲目冒进；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到事物发展的脉络和变化趋势，及时调整策略。"
        else:
            core_summary = f"{gua_name}卦象显示，当前事业发展方面需审慎应对，稳中求进。卦辞「{gua_text}」揭示了当前阶段的关键特征，表明事业发展面临一定的挑战和阻力。从象辞「{gua_description}」来看，此卦象反映了您在事业发展过程中所处的状态，可能遇到内部协调不足或外部环境不利的情况。卦象的阴阳变化体现了事物发展的内在规律，当前阶段需要更加谨慎和耐心。建议您保持冷静理性，不要急于求成，先稳固基础，逐步推进，等待更合适的时机再做大动作。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析当前形势：</strong>将卦象指导与实际情况相结合，深入分析当前面临的困难和挑战，找出问题的根源，制定稳健的应对策略；<br>2) <strong>保持耐心，稳扎稳打：</strong>避免急躁冒进，先解决内部问题，稳固基础，逐步推进，在合适的时机再采取更大行动；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到事物发展的脉络和变化趋势，及时调整策略。"
    elif "感情" in divination_event_lower or "爱情" in divination_event_lower or "婚姻" in divination_event_lower:
        if is_auspicious:
            core_summary = f"{gua_name}卦象显示，当前感情方面宜以诚相待，用心经营。卦辞「{gua_text}」揭示了当前感情关系的核心特征，表明感情发展处于良好状态。从象辞「{gua_description}」来看，此卦象反映了您在感情生活中所处的和谐状态，双方关系融洽，沟通顺畅。卦象的阴阳变化体现了感情发展的内在规律，当前阶段是加深感情、增进理解的好时机。建议您珍惜当下的感情状态，用心经营关系，通过真诚的沟通和贴心的行动，让感情更加稳固和美好。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析感情现状：</strong>将卦象指导与实际情况相结合，深入了解双方的需求和期望，识别关系中需要加强的方面，制定改善计划；<br>2) <strong>以积极心态面对，用心经营关系：</strong>增进沟通和理解，多表达关心和爱意，创造浪漫时刻，共同参与有意义的活动，让感情持续升温；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到感情发展的脉络和变化趋势，及时调整相处方式。"
        else:
            core_summary = f"{gua_name}卦象显示，当前感情方面需冷静思考，理性处理。卦辞「{gua_text}」揭示了当前感情关系的核心特征，表明感情发展可能遇到一些困难或分歧。从象辞「{gua_description}」来看，此卦象反映了您在感情生活中所处的状态，可能面临沟通不畅、理解不足或外部干扰等问题。卦象的阴阳变化体现了感情发展的内在规律，当前阶段需要更加理性和耐心。建议您保持冷静，不要情绪化处理问题，通过真诚的沟通和理性的分析，找出问题的根源，逐步改善关系。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析感情现状：</strong>将卦象指导与实际情况相结合，深入分析当前面临的问题和分歧，找出矛盾的根源，制定解决方案；<br>2) <strong>保持耐心，理性处理分歧：</strong>避免情绪化决策，多倾听对方的想法，用理解代替争执，寻找共同点，逐步化解矛盾；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到感情发展的脉络和变化趋势，及时调整相处方式。"
    elif "财运" in divination_event_lower or "投资" in divination_event_lower or "理财" in divination_event_lower:
        if is_auspicious:
            core_summary = f"{gua_name}卦象显示，当前财运方面宜审时度势，稳健投资。卦辞「{gua_text}」揭示了当前财运状况的核心特征，表明财运发展处于有利阶段。从象辞「{gua_description}」来看，此卦象反映了您在财务管理方面所处的状态，可能有机会获得收益或改善财务状况。卦象的阴阳变化体现了财运发展的内在规律，当前阶段是理性投资和理财的好时机。建议您审慎分析市场情况，把握合适的投资机会，但需控制风险，确保资金安全，避免盲目跟风。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析财务状况：</strong>将卦象指导与实际情况相结合，深入分析自身财务状况和市场环境，识别合适的投资机会，制定合理的理财计划；<br>2) <strong>把握有利时机，但需控制风险：</strong>理性分析投资机会，分散投资降低风险，避免将资金集中在单一项目，确保资金安全和收益的平衡；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到财运发展的脉络和变化趋势，及时调整投资策略。"
        else:
            core_summary = f"{gua_name}卦象显示，当前财运方面需谨慎理财，避免冒险。卦辞「{gua_text}」揭示了当前财运状况的核心特征，表明财运发展可能面临一些挑战或风险。从象辞「{gua_description}」来看，此卦象反映了您在财务管理方面所处的状态，可能需要更加谨慎和保守。卦象的阴阳变化体现了财运发展的内在规律，当前阶段不宜大举投资或冒险。建议您保持谨慎态度，以稳健为主，避免盲目投资和冒险行为，先稳固现有财务状况，等待更合适的时机。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析财务状况：</strong>将卦象指导与实际情况相结合，深入分析当前财务状况和市场风险，识别潜在风险点，制定保守的理财策略；<br>2) <strong>保持谨慎，稳健为主：</strong>避免盲目投资和冒险行为，以保值为主，选择低风险的投资方式，确保资金安全；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到财运发展的脉络和变化趋势，及时调整理财策略。"
    elif "健康" in divination_event_lower or "身体" in divination_event_lower:
        if is_auspicious:
            core_summary = f"{gua_name}卦象显示，当前健康方面宜注重调养，保持平衡。卦辞「{gua_text}」揭示了当前健康状况的核心特征，表明身体健康状态良好。从象辞「{gua_description}」来看，此卦象反映了您在身体健康方面所处的状态，身体机能相对稳定，但需要注意保持平衡。卦象的阴阳变化体现了健康发展的内在规律，当前阶段是调养身体、增强体质的好时机。建议您保持良好习惯，适度运动，注重身心平衡，通过规律的生活方式和适当的调养，让身体更加健康。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析身体状况：</strong>将卦象指导与实际情况相结合，了解自己的身体状况和健康需求，制定合理的调养计划；<br>2) <strong>保持良好习惯，适度运动：</strong>注重身心平衡，规律作息，适度运动，合理饮食，保持心情愉悦，增强身体抵抗力；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到健康发展的脉络和变化趋势，及时调整调养方式。"
        else:
            core_summary = f"{gua_name}卦象显示，当前健康方面需及时关注，适当调理。卦辞「{gua_text}」揭示了当前健康状况的核心特征，表明身体健康可能需要关注。从象辞「{gua_description}」来看，此卦象反映了您在身体健康方面所处的状态，可能有一些不适或需要调理的地方。卦象的阴阳变化体现了健康发展的内在规律，当前阶段需要更加重视健康问题。建议您及时关注身体变化，适当调理，必要时寻求专业帮助，不要忽视身体发出的信号。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析身体状况：</strong>将卦象指导与实际情况相结合，仔细关注身体的各种信号，识别需要关注的问题，制定针对性的调理计划；<br>2) <strong>及时关注身体变化，适当调理：</strong>必要时寻求专业帮助，不要忽视身体不适，通过科学的医疗和调理方法，改善身体状况；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到健康发展的脉络和变化趋势，及时调整调理方式。"
    else:
        # 通用总结
        if is_auspicious:
            core_summary = f"{gua_name}卦象显示，当前宜把握时机，顺势而为。卦辞「{gua_text}」揭示了当前阶段的关键特征，表明您所问问题处于有利时机。从象辞「{gua_description}」来看，此卦象反映了您所问问题上所处的状态，整体趋势向好，有利于推进目标。卦象的阴阳变化体现了事物发展的内在规律，当前阶段机遇与挑战并存，但整体环境相对有利。建议您充分把握当前的有利条件，积极行动，但需审慎评估，确保决策的合理性和可执行性。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析当前形势：</strong>将卦象指导与实际情况相结合，深入分析自身情况和外部环境，识别关键机遇点，制定切实可行的计划；<br>2) <strong>把握有利时机，积极行动：</strong>但需审慎评估，确保决策的合理性和可执行性，避免盲目冒进，在机会来临时果断行动；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到事物发展的脉络和变化趋势，及时调整策略。"
        else:
            core_summary = f"{gua_name}卦象显示，当前需审慎应对，稳中求进。卦辞「{gua_text}」揭示了当前阶段的关键特征，表明您所问问题可能面临一些挑战或阻力。从象辞「{gua_description}」来看，此卦象反映了您所问问题上所处的状态，可能需要更加谨慎和耐心。卦象的阴阳变化体现了事物发展的内在规律，当前阶段需要更加稳健和理性。建议您保持冷静理性，不要急于求成，先稳固基础，逐步推进，等待更合适的时机再做大动作。"
            action_advice = f"<strong>具体行动建议：</strong><br>1) <strong>理性分析当前形势：</strong>将卦象指导与实际情况相结合，深入分析当前面临的困难和挑战，找出问题的根源，制定稳健的应对策略；<br>2) <strong>保持耐心，稳扎稳打：</strong>避免急躁冒进，先解决内部问题，稳固基础，逐步推进，在合适的时机再采取更大行动；<br>3) <strong>持续观察与调整：</strong>至少间隔15天再占同一问题，通过多次占卜的对比，可以更清晰地看到事物发展的脉络和变化趋势，及时调整策略。"
    
    summary = f"<strong>【核心总结】</strong>{core_summary}<br><br><strong>【行动建议】</strong>{action_advice}"
    
    return summary

def get_enriched_divination_content(gua_name, gua_symbol, gua_text, gua_description, divination_event=""):
    """根据占卜问题生成相关方面的解卦内容（只生成相关方面，内容更丰满）"""
    # 识别需要生成的相关方面
    relevant_categories = identify_relevant_categories(divination_event)
    
    # 构建针对性的提示词，优化为更精简的内容（200-300字）以加快响应速度
    categories_list = "、".join(relevant_categories)
    prompt = f"""请根据以下信息，详细解读{gua_name}在占卜问题相关方面的含义：

卦名：{gua_name}
卦象：{gua_symbol}
卦辞：{gua_text}
象辞：{gua_description}
占卜问题：{divination_event if divination_event else "未指定具体问题"}

请针对以下方面提供详细、丰富、深入的解释（每个方面200-300字），要求：
1. 深入分析该卦象在此方面的象征意义和深层含义，结合易经原理详细阐述
2. 结合卦辞、象辞和爻辞进行详细解读，引用相关爻辞说明
3. 提供具体的指导建议、行动步骤和注意事项，要有可操作性
4. 结合占卜问题给出针对性的分析和建议，直接回答用户的问题
5. 语言通俗易懂，具有实用价值，可以举例说明
6. 可以从历史典故、易学原理、实际应用、时间周期等多个角度阐述
7. 内容要丰满充实，逻辑清晰，层次分明
8. 可以引用相关易学典籍和传统智慧，但要用现代语言解释

请按照以下格式输出，每个类别用"##"分隔：

{chr(10).join([f'## {cat}{chr(10)}[这里写{cat}方面的详细解读，200-300字，要深入、全面、实用，直接回答占卜问题]{chr(10)}' for cat in relevant_categories])}
"""
    
    # 初始化结果字典（只包含相关方面）
    result_categories = {cat: "" for cat in relevant_categories}
    
    # 尝试调用DeepSeek和Qwen，优化token数量以加快响应速度
    content = None
    max_tokens = 2000  # 优化token数量以支持精简但完整的内容（200-300字），加快响应速度
    
    # 优先使用DeepSeek
    try:
        content = call_deepseek_api(prompt, max_tokens=max_tokens)
        if content:
            print(f"DeepSeek成功生成内容，长度: {len(content)}")
    except Exception as e:
        print(f"DeepSeek调用失败或超时: {e}")
    
    # 如果DeepSeek失败或内容不够丰满，使用Qwen
    if not content or len(content) < 200:
        try:
            content = call_qwen_api(prompt, max_tokens=max_tokens)
            if content:
                print(f"Qwen成功生成内容，长度: {len(content)}")
        except Exception as e:
            print(f"Qwen调用失败或超时: {e}")
    
    # 如果两个都失败了，尝试再次调用（备用方案）
    if not content or len(content) < 200:
        try:
            # 使用简化的prompt再次尝试Qwen
            simplified_prompt = f"""请详细解读{gua_name}关于"{divination_event}"这个问题的含义。

卦名：{gua_name}
卦象：{gua_symbol}
卦辞：{gua_text}
象辞：{gua_description}

请针对以下方面提供详细解释（每个方面200-300字）：
{chr(10).join([f'- {cat}' for cat in relevant_categories])}

要求：深入分析、结合卦辞爻辞、提供具体建议、直接回答用户问题、内容丰富充实。

请按照以下格式输出，每个类别用"##"分隔：
{chr(10).join([f'## {cat}{chr(10)}[详细解读内容]{chr(10)}' for cat in relevant_categories])}
"""
            content = call_qwen_api(simplified_prompt, max_tokens=max_tokens)
            if content:
                print(f"Qwen备用方案成功生成内容，长度: {len(content)}")
        except Exception as e:
            print(f"Qwen备用方案调用失败: {e}")
    
    # 解析返回的内容
    if content and content.strip():
        # 按"##"分隔解析内容
        parts = content.split("##")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            for category in relevant_categories:
                if category in part:
                    # 提取该类别的内容
                    category_content = part.split(category, 1)
                    if len(category_content) > 1:
                        result_categories[category] = category_content[1].strip()
                        break
    
    # 为空的类别填充更详细的默认内容（基于卦象特性）
    for category in relevant_categories:
        if not result_categories[category] or not result_categories[category].strip() or len(result_categories[category]) < 200:
            # 生成更详细的默认内容，基于卦象特性
            category_name = category.split("（")[0]  # 提取类别名称
            
            # 根据卦名生成更针对性的内容
            if "屯" in gua_name:
                default_analysis = f"""**卦象核心含义：**
屯卦象征万物始生之艰难，在{category_name}方面意味着当前正处于初始阶段，虽然充满希望，但也面临诸多挑战。卦辞"{gua_text}"提醒我们，此时需要耐心经营，不可轻举妄动。

**深度解析：**
屯卦的卦象"{gua_symbol}"（上坎下震，水下雷上）体现了初创时期的困难与机遇并存。在{category_name}方面，此卦象提醒我们：
- 当前阶段需要积蓄力量，为未来发展做准备
- 虽然困难重重，但蕴含着成长和发展的契机
- 需要保持耐心，等待合适的时机再行动
- 要注重基础建设，稳固根基才能长久发展

**具体建议：**
• 不要急于求成，先稳固基础，做好准备工作
• 保持积极心态，将挑战视为成长的机会
• 寻找合适的时机，不可盲目行动
• 注重积累经验和资源，为未来发展奠定基础
• 寻求贵人相助，建立良好的人际关系网络

**针对您的问题：**
关于"{divination_event}"这个问题，屯卦提醒我们当前需要耐心等待，不可急躁。虽然现状可能不尽如人意，但只要稳扎稳打，循序渐进，未来一定会有好的发展。建议至少等待三个月后再做重大决策，让形势更加明朗。"""
            else:
                default_analysis = f"""**卦象核心含义：**
{gua_name}的卦象"{gua_symbol}"体现了阴阳变化的规律。从卦辞"{gua_text}"和象辞"{gua_description}"可以看出，此卦象在{category_name}方面具有深刻的指导意义。

**深度解析：**
此卦象反映了当前在{category_name}方面的状态和趋势。卦象的阴阳组合显示了事物发展的规律，提醒我们需要理性思考，既要顺应时势，也要发挥主观能动性。

**具体建议：**
• 保持内心的平衡和稳定，顺应自然规律
• 在决策时综合考虑各方面因素，不可偏执一端
• 注意把握时机，不可急躁冒进，也不可消极等待
• 结合自身实际情况灵活应用卦象的指导
• 注重长期规划，不要只看眼前利益

**针对您的问题：**
关于"{divination_event}"这个问题，{gua_name}提醒我们需要理性思考，既要顺应时势，也要发挥主观能动性。在具体行动中，要审时度势，把握关键时机，同时保持耐心和坚持。建议根据实际情况灵活调整策略，不可固守一成不变的方法。"""
            
            result_categories[category] = default_analysis
    
    return result_categories

def generate_follow_up_questions(question, answer):
    """根据用户问题和答案生成深入或衍生问题（逻辑思维链）"""
    follow_ups = []
    
    # 根据问题类型生成相关衍生问题
    question_lower = question.lower()
    
    # 风水相关问题
    if any(keyword in question for keyword in ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房"]):
        follow_ups = [
            "如何布置这个空间的财位？",
            "这个方位的五行属性是什么？",
            "如何通过调整家具位置改善运势？",
            "这个空间适合摆放什么颜色的装饰品？"
        ]
    
    # 解梦相关问题
    elif any(keyword in question for keyword in ["梦", "梦见", "周公", "解梦"]):
        follow_ups = [
            "这个梦境的吉凶程度如何？",
            "梦境中的细节有什么特殊含义？",
            "我应该如何应对这个梦境所预示的情况？",
            "这个梦境和我的现实生活有什么关联？"
        ]
    
    # 感情相关问题
    elif any(keyword in question for keyword in ["感情", "爱情", "恋爱", "婚姻", "伴侣"]):
        follow_ups = [
            "如何改善当前的感情状况？",
            "这个感情问题的根本原因是什么？",
            "我应该如何与对方沟通？",
            "这段感情的未来发展会如何？"
        ]
    
    # 事业相关问题
    elif any(keyword in question for keyword in ["事业", "工作", "职业", "升职", "跳槽"]):
        follow_ups = [
            "我应该在事业上注意什么？",
            "如何提升我的职场运势？",
            "这个工作机会是否适合我？",
            "我应该如何规划职业发展？"
        ]
    
    # 健康相关问题
    elif any(keyword in question for keyword in ["健康", "身体", "疾病", "养生", "饮食"]):
        follow_ups = [
            "如何改善我的健康状况？",
            "这个健康问题需要注意什么？",
            "我应该如何调整生活方式？",
            "有什么预防措施可以采取？"
        ]
    
    # 财运相关问题
    elif any(keyword in question for keyword in ["财运", "财富", "投资", "理财", "收入"]):
        follow_ups = [
            "如何提升我的财运？",
            "这个投资机会是否合适？",
            "我应该如何规划财务？",
            "有什么需要注意的财务风险？"
        ]
    
    # 默认综合问题
    else:
        # 从答案中提取关键词，生成相关问题
        if "建议" in answer or "应该" in answer:
            follow_ups = [
                "具体应该如何实施这个建议？",
                "这个建议的预期效果如何？",
                "实施过程中需要注意什么？",
                "有什么风险需要防范？"
            ]
        elif "运势" in question or "运势" in answer:
            follow_ups = [
                "如何改善当前的运势？",
                "这个运势的持续时间有多长？",
                "我应该如何把握时机？",
                "需要注意哪些不利因素？"
            ]
        else:
            follow_ups = [
                "这个问题还有其他需要注意的方面吗？",
                "我可以从哪些角度深入理解这个问题？",
                "如何将这个问题应用到实际生活中？",
                "还有其他相关的问题值得探讨吗？"
            ]
    
    # 限制返回3个最相关的问题
    return follow_ups[:3]

def rag_qa_answer(question):
    """RAG问答系统"""
    try:
        # 尝试导入RAG系统
        from src.rag_qa_system import IChingRAGSystem
        
        # 获取知识库路径（相对于 app.py 的位置）
        base_dir = os.path.dirname(os.path.abspath(__file__))
        knowledge_base_dir = os.path.join(base_dir, "knowledge_base")
        
        # 初始化RAG系统（会自动加载知识库）
        rag_system = IChingRAGSystem(knowledge_base_path=knowledge_base_dir)
        
        # 生成答案
        answer = rag_system.answer_question(question)
        
        if answer and isinstance(answer, dict):
            return f"""
**分步分析：**
{answer.get('step_by_step_analysis', '正在分析中...')}

**推理总结：**
{answer.get('reasoning_summary', '正在推理中...')}

**相关来源：**
{', '.join(answer.get('relevant_sources', [])) if answer.get('relevant_sources') else '暂无相关来源'}

**最终答案：**
{answer.get('final_answer', '根据易经理论，这个问题涉及到阴阳平衡的智慧。建议您保持中庸之道，顺应自然规律。')}
"""
        else:
            return "根据易经理论，这个问题涉及到阴阳平衡的智慧。建议您保持中庸之道，顺应自然规律。"
    
    except Exception as e:
        # 如果RAG系统不可用，使用备用答案
        backup_answers = [
            "根据易经理论，这个问题涉及到阴阳平衡的智慧。从周易的角度来看，需要结合天时地利人和来考虑。",
            "易经告诉我们，变化是永恒的，需要顺应自然规律。根据卦象分析，建议保持中庸之道，不可偏激。",
            "从传统易经理论出发，这个问题体现了阴阳互动的哲学思想。建议您保持内心的平衡，顺应时势变化。",
            "根据周易的智慧，万物皆有定数，但也需要人为的努力。建议您既要有耐心，也要有行动力。"
        ]
        return random.choice(backup_answers)

def main():
    # 初始化session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    if 'tossing' not in st.session_state:
        st.session_state.tossing = False
    if 'yao_results' not in st.session_state:
        st.session_state.yao_results = []
    if 'current_gua' not in st.session_state:
        st.session_state.current_gua = None
    if 'divination_event' not in st.session_state:
        st.session_state.divination_event = ""
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'last_divination_content' not in st.session_state:
        st.session_state.last_divination_content = ""

    # 主界面布局
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 顶部标题区域
    st.markdown('''
    <div class="header-section">
        <div class="main-title">盈在易测系统</div>
        <div class="sub-title">传承千年智慧，服务现代生活</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 导航栏只在首页显示
    if st.session_state.current_page == "home":
        show_navigation_bar()
    
    # 主体内容区域
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "divination":
        show_divination_page()
    elif st.session_state.current_page == "qa":
        show_qa_page()
    elif st.session_state.current_page == "fortune_detail":
        show_fortune_detail_page()
    elif st.session_state.current_page == "emotion_detail":
        show_emotion_detail_page()
    elif st.session_state.current_page == "next_question":
        show_next_question_page()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部版权信息
    st.markdown('''
    <div class="footer-section">
        <div class="footer-text">©2025 盈在易测系统</div>
        <div class="footer-text">传承千年智慧，服务现代生活</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_navigation_bar():
    """显示导航栏"""
    st.markdown('<div style="padding: 10px 20px; background: linear-gradient(135deg, rgba(255, 248, 220, 0.9) 0%, rgba(245, 245, 220, 0.95) 100%); border-bottom: 2px solid rgba(218, 165, 32, 0.3);">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("首页", key="nav_home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    
    with col2:
        if st.button("占卜", key="nav_divination", use_container_width=True):
            st.session_state.current_page = "divination"
            st.rerun()
    
    with col3:
        if st.button("问答", key="nav_qa", use_container_width=True):
            st.session_state.current_page = "qa"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def clear_divination_data():
    """清除所有占卜相关的数据，用于返回首页时使用"""
    st.session_state.show_result = False
    st.session_state.current_gua = None
    st.session_state.yao_results = []
    st.session_state.tossing = False
    st.session_state.generating_content = False
    st.session_state.enhanced_result = None
    st.session_state.enriched_content = None
    st.session_state.divination_event = ""
    st.session_state.gua_summary = {}
    st.session_state.generating_deep_content = False
    st.session_state.deep_result = None
    st.session_state.deep_question = None
    st.session_state.last_divination_content = None

def show_home_page():
    """显示首页"""
    # 欢迎信息
    st.markdown('<div class="section-title">欢迎使用盈在易测系统</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 20px; margin: 20px 0; background: rgba(255, 255, 255, 0.8); border-radius: 10px;">
        <p style="font-size: 16px; color: #654321; line-height: 1.8;">
            传承千年智慧，服务现代生活。请使用顶部导航栏选择您需要的功能。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能说明
    st.markdown("---")
    st.markdown("### 功能说明")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        **开始占卜**
        
        通过投掷硬币的方式进行传统六爻占卜，获得卦象和详细解释。
        支持多种起卦方式：手动摇卦、报数起卦、时间起卦、电脑自动。
        """)
    
    with info_col2:
        st.markdown("""
        **智能问答**
        
        基于RAG技术的智能问答系统，可以回答关于风水、解梦、日常生活等各类问题。
        结合传统易经智慧和现代AI技术。
        """)

def show_divination_page():
    """显示占卜页面"""
    # 初始化session_state（仅在第一次访问时）
    if 'yao_results' not in st.session_state:
        st.session_state.yao_results = []
    if 'current_gua' not in st.session_state:
        st.session_state.current_gua = None
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'tossing' not in st.session_state:
        st.session_state.tossing = False
    if 'generating_content' not in st.session_state:
        st.session_state.generating_content = False
    if 'enhanced_result' not in st.session_state:
        st.session_state.enhanced_result = None
    if 'enriched_content' not in st.session_state:
        st.session_state.enriched_content = None
    
    # 如果有结果，立即跳转到只显示结果的页面，隐藏所有占卜表单
    # 无论是否正在生成内容，都跳转到结果页面（生成中显示加载动画，生成完成后显示结果）
    if st.session_state.show_result and st.session_state.current_gua:
        show_divination_result()
        # 智能引导卡片中已包含按钮，无需额外显示
        return  # 直接返回，不显示占卜表单
    
    # 没有结果时显示占卜表单
    st.markdown('<div class="section-title">周易占卜</div>', unsafe_allow_html=True)
    
    # 占卜内容输入（类似DeepSeek界面）
    divination_content = st.text_area(
        "占卜内容", 
        placeholder="请输入您要占卜的内容，例如：我今年的事业运势如何？我的感情发展会怎样？",
        height=100,
        key="divination_content_input"
    )
    
    # 保存占卜内容到session state
    if divination_content:
        st.session_state.divination_event = divination_content
    
    # 检测占卜内容变化，清除之前的结果
    if 'last_divination_content' not in st.session_state:
        st.session_state.last_divination_content = divination_content
    elif st.session_state.last_divination_content != divination_content:
        st.session_state.last_divination_content = divination_content
        st.session_state.yao_results = []
        st.session_state.current_gua = None
        st.session_state.show_result = False
        st.session_state.tossing = False
    
    # 占卜前的准备说明（在起卦方式上方）
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #FFF8DC; padding: 20px; border-radius: 8px; border-left: 4px solid #8B0000; margin: 20px 0;">
        <h4 style="color: #8B0000; margin-top: 0;">占卜前的准备</h4>
        <ol style="margin: 10px 0; padding-left: 20px; line-height: 1.8;">
            <li>找一个安静的地方，排除干扰。</li>
            <li>深呼吸，让自己平静下来。</li>
            <li>点击下方的投掷硬币六次，心中默念你的问题。</li>
        </ol>
        <p style="margin: 15px 0 10px 0; font-weight: bold; color: #654321;">此时，你需要在心中清晰地默念一段话，内容应包括：</p>
        <div style="background-color: #F5F5DC; padding: 15px; border-radius: 5px; margin: 10px 0; font-style: italic; color: #654321; border: 1px solid #DAA520;">
            "八卦祖师在上，弟子XXX（你的名字）今日因【此处清晰地说出你要占问的具体事情】，心中迷惑，诚心祈求祖师赐卦，指点迷津，明示吉凶。"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 起卦方式
    st.markdown("**起卦方式：**")
    divination_method = st.radio("起卦方式", ["手动摇卦", "报数起卦"], horizontal=True, label_visibility="collapsed")
    
    # 检测起卦方式变化，更新记录
    if 'last_divination_method' not in st.session_state:
        st.session_state.last_divination_method = divination_method
    elif st.session_state.last_divination_method != divination_method:
        st.session_state.last_divination_method = divination_method
        # 只有在起卦方式变化时才清除结果
        st.session_state.yao_results = []
        st.session_state.current_gua = None
        st.session_state.show_result = False
        st.session_state.tossing = False
    
    # 显示占卜表单
    if divination_method == "手动摇卦":
        show_combined_divination()
    elif divination_method == "报数起卦":
        show_number_divination()
    
    # 返回首页按钮
    st.markdown("---")
    if st.button("返回首页", key="back_home_divination", use_container_width=True):
        clear_divination_data()
        st.session_state.current_page = "home"
        st.rerun()

def show_combined_divination():
    """手动摇卦起卦方式"""
    st.markdown("**投掷硬币：**")
    
    # 只有在填写了占卜内容后才显示投掷硬币按钮
    divination_content = st.session_state.get("divination_event", "")
    if not divination_content or divination_content.strip() == "":
        st.info("请先填写占卜内容，然后才能进行投掷硬币起卦。")
        return
    
    # 检查六爻是否完整
    is_complete = len(st.session_state.yao_results) == 6
    
    # 显示六爻结果
    if st.session_state.yao_results:
        st.markdown("**六爻结果：**")
        for i, yao in enumerate(st.session_state.yao_results):
            st.write(f"第{6-i}爻: {yao}")
        
        # 如果不足6爻，显示剩余次数
        if not is_complete:
            remaining = 6 - len(st.session_state.yao_results)
            st.info(f"还需要投掷 {remaining} 次硬币")
        else:
            # 6爻完整后显示成功信息
            st.success("六爻已完整！")
    
    # 投掷硬币按钮 - 在六爻完整前或者想重新开始时可点击
    # 如果六爻完整，点击投掷硬币会重置并重新开始
    if is_complete:
        button_text = "重新投掷硬币"
        button_help = "六爻已完整，点击将清空结果并重新开始投掷"
    else:
        button_text = "投掷硬币"
        button_help = "点击开始投掷硬币"
    
    if st.button(button_text, key="toss_coins", use_container_width=True, help=button_help):
        # 如果六爻已完整，重置结果
        if is_complete:
            st.session_state.yao_results = []
            st.session_state.current_gua = None
            st.session_state.show_result = False
        st.session_state.tossing = True
        st.rerun()
    
    if st.session_state.tossing:
        # 显示旋转的硬币
        st.markdown('<div class="coin-container">', unsafe_allow_html=True)
        for i in range(3):
            st.markdown(f'''
            <div class="coin">
                <div class="coin-surface"></div>
                <div class="coin-hole"></div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("停止", key="stop_toss"):
            # 投掷硬币并显示结果 - 基于占卜内容生成确定性结果
            divination_content = st.session_state.get("divination_event", "")
            # 基于当前投掷次数和占卜内容生成确定性结果
            toss_index = len(st.session_state.yao_results)
            coin_results = toss_coins_deterministic(divination_content, toss_index)
            yao_type = get_yao_type(coin_results)
            
            if len(st.session_state.yao_results) < 6:
                st.session_state.yao_results.append(yao_type)
                st.session_state.tossing = False
                st.rerun()
    
    # 马上看结果按钮 - 只有6爻完整时才显示
    if is_complete:
        if st.button("马上看结果", key="view_result", use_container_width=True):
            # 基于占卜内容生成确定性卦象（如果同一天内相同问题，结果一致）
            divination_content = st.session_state.get("divination_event", "")
            gua = calculate_gua(st.session_state.yao_results, divination_content)
            if gua:
                st.session_state.current_gua = gua
                st.session_state.generating_content = True  # 标记正在生成内容
                st.session_state.show_result = True  # 立即跳转到结果页面
                st.session_state.enhanced_result = None  # 清空之前的结果
                st.session_state.enriched_content = None  # 清空之前的结果
                st.rerun()
            else:
                st.error("无法计算卦象，请重新投掷硬币")
    
    # 重置按钮
    if st.session_state.yao_results or st.session_state.show_result:
        if st.button("重新开始", key="reset_divination"):
            st.session_state.yao_results = []
            st.session_state.current_gua = None
            st.session_state.show_result = False
            st.session_state.tossing = False
            st.session_state.divination_cleared = False
            st.rerun()
    

def show_manual_divination_old():
    """手动摇卦"""
    st.markdown("**投掷硬币：**")
    
    # 显示三枚硬币
    col1, col2, col3 = st.columns(3)
    
    with col2:
        if st.button("投掷硬币", key="toss_coins"):
            st.session_state.tossing = True
            st.rerun()
    
    if st.session_state.tossing:
        # 显示旋转的硬币
        st.markdown('<div class="coin-container">', unsafe_allow_html=True)
        for i in range(3):
            st.markdown(f'''
            <div class="coin">
                <div class="coin-surface"></div>
                <div class="coin-hole"></div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("停止", key="stop_toss"):
            # 投掷硬币并显示结果 - 基于占卜内容生成确定性结果
            divination_content = st.session_state.get("divination_event", "")
            # 基于当前投掷次数和占卜内容生成确定性结果
            toss_index = len(st.session_state.yao_results)
            coin_results = toss_coins_deterministic(divination_content, toss_index)
            yao_type = get_yao_type(coin_results)
            
            if len(st.session_state.yao_results) < 6:
                st.session_state.yao_results.append(yao_type)
                st.session_state.tossing = False
                st.rerun()
    
    # 显示六爻结果
    if st.session_state.yao_results:
        st.markdown("**六爻结果：**")
        for i, yao in enumerate(st.session_state.yao_results):
            st.write(f"第{6-i}爻: {yao}")
        
        # 如果不足6爻，显示剩余次数
        if len(st.session_state.yao_results) < 6:
            remaining = 6 - len(st.session_state.yao_results)
            st.info(f"还需要投掷 {remaining} 次硬币")
        
        # 始终显示"马上看结果"按钮
        if st.button("马上看结果", key="view_result"):
            if len(st.session_state.yao_results) == 6:
                gua = calculate_gua(st.session_state.yao_results)
            else:
                # 如果不足6爻，用随机结果补充
                complete_results = st.session_state.yao_results.copy()
                while len(complete_results) < 6:
                    complete_results.append(random.choice(list(yao_types.keys())))
                gua = calculate_gua(complete_results)
            
            if gua:
                st.session_state.current_gua = gua
                st.session_state.show_result = True
                st.rerun()

def show_number_divination():
    """报数起卦"""
    st.markdown("**报数起卦：**")
    
    # 只有在填写了占卜内容后才能进行报数起卦
    divination_content = st.session_state.get("divination_event", "")
    if not divination_content or divination_content.strip() == "":
        st.info("请先填写占卜内容，然后才能进行报数起卦。")
        return
    
    st.markdown("请输入任意随机数字进行起卦")
    
    # 初始化session_state（仅在第一次访问时）
    if 'yao_results' not in st.session_state:
        st.session_state.yao_results = []
    if 'current_gua' not in st.session_state:
        st.session_state.current_gua = None
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'tossing' not in st.session_state:
        st.session_state.tossing = False
    
    # 允许输入任意数字
    number = st.number_input("请输入一个数字", min_value=1, value=1, step=1, key="number_input")
    
    if st.button("马上看结果", key="view_number_result", use_container_width=True):
        # 根据数字生成确定性的卦象 - 基于日期+数字+占卜内容
        divination_content = st.session_state.get("divination_event", "")
        gua = generate_gua_by_number(int(number), divination_content)
        st.session_state.current_gua = gua
        st.session_state.generating_content = True  # 标记正在生成内容
        st.session_state.show_result = True  # 立即跳转到结果页面
        st.session_state.enhanced_result = None  # 清空之前的结果
        st.session_state.enriched_content = None  # 清空之前的结果
        st.rerun()

def generate_gua_by_number(number, divination_content=""):
    """根据数字生成确定性的卦象 - 基于日期+数字+占卜内容生成1天内一致的结果"""
    # 获取今天的日期字符串
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 基于日期+数字+占卜内容生成确定性种子
    seed_str = f"{today}_{number}_{divination_content}"
    seed_hash = hash(seed_str)
    random.seed(seed_hash)
    
    # 根据数字映射到64卦（使用模运算支持任意数字）
    gua_index = (number - 1) % len(gua_data)
    gua = gua_data[gua_index]
    
    # 重置随机种子，避免影响其他功能
    random.seed()
    
    return gua

def toss_coins_deterministic(divination_content, toss_index):
    """基于占卜内容和投掷次数生成确定性的硬币结果"""
    # 获取今天的日期字符串
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 基于日期+占卜内容+投掷次数生成确定性种子
    seed_str = f"{today}_{divination_content}_{toss_index}"
    seed_hash = hash(seed_str)
    random.seed(seed_hash)
    
    results = []
    for i in range(3):
        result = random.choice([0, 1])  # 0为阴，1为阳
        results.append(result)
    
    # 重置随机种子
    random.seed()
    return results

def show_divination_result():
    """显示占卜结果 - 增强版（立即跳转到结果页，生成完成后一次性显示）"""
    if st.session_state.current_gua:
        gua = st.session_state.current_gua
        
        # 在结果页面顶部添加返回首页和重新占卜按钮
        # 检查是否有返回请求（避免显示结果）
        should_return = False
        return_page = None
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("返回首页", key="back_home_from_result", use_container_width=True):
                clear_divination_data()
                should_return = True
                return_page = "home"
        
        with col2:
            if st.button("重新占卜", key="re_divination_from_result", use_container_width=True):
                clear_divination_data()
                should_return = True
                return_page = "divination"
        
        # 如果点击了返回按钮，立即返回，不显示结果
        if should_return:
            st.session_state.current_page = return_page
            st.rerun()
            return
        
        st.markdown("---")
        
        # 如果正在生成内容，显示加载动画
        if st.session_state.get("generating_content", False):
            # 显示加载动画和提示
            st.markdown("""
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-container {
                text-align: center;
                padding: 60px 20px;
                min-height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .loading-spinner {
                width: 60px;
                height: 60px;
                border: 6px solid rgba(139, 0, 0, 0.1);
                border-top-color: #8B0000;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 30px;
            }
            .loading-text {
                color: #8B0000;
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="loading-container">', unsafe_allow_html=True)
            st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
            st.markdown('<div class="loading-text">正在生成占卜结果，请稍候…</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 检查是否已经生成过内容（避免重复生成）
            if st.session_state.get("enhanced_result") is None and st.session_state.get("enriched_content") is None:
                # 在后台生成所有内容（不显示额外的spinner，避免重复提示）
                try:
                    enhanced_result = None
                    enriched_content = None
                    
                    if ENHANCED_DIVINATION_AVAILABLE:
                        try:
                            enhanced_result = enhanced_divination.get_enhanced_divination_result(
                                gua["name"], gua["symbol"], st.session_state.get("divination_event", "")
                            )
                            
                            # 生成大模型丰富内容
                            try:
                                enriched_content = get_enriched_divination_content(
                                    gua["name"], 
                                    gua["symbol"], 
                                    gua["text"], 
                                    gua["description"],
                                    st.session_state.get("divination_event", "")
                                )
                            except Exception as e:
                                print(f"大模型生成内容时出错: {e}")
                                enriched_content = None
                        except Exception as e:
                            print(f"增强解卦系统出错: {e}")
                    
                    # 保存生成的内容到session state
                    st.session_state.enhanced_result = enhanced_result
                    st.session_state.enriched_content = enriched_content
                    
                except Exception as e:
                    print(f"生成内容时出错: {e}")
                    # 即使出错也设置空值
                    st.session_state.enhanced_result = None
                    st.session_state.enriched_content = None
                
                # 生成完成后，标记生成完成并刷新页面
                st.session_state.generating_content = False
                st.rerun()
            else:
                # 如果已经生成过内容，直接标记完成并刷新
                st.session_state.generating_content = False
                st.rerun()
            
            return  # 生成中，不显示结果
        
        # 生成完成后，一次性显示所有内容
        enhanced_result = st.session_state.get("enhanced_result", None)
        enriched_content = st.session_state.get("enriched_content", None)
        
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">占卜结果</div>', unsafe_allow_html=True)
        
        # 卦名
        st.markdown(f'<div class="gua-name">{gua["name"]}</div>', unsafe_allow_html=True)
        
        # 卦象显示（不带加载提示）
        hexagram_html = render_hexagram_display(gua, show_loading=False)
        st.markdown(hexagram_html, unsafe_allow_html=True)
        
        # 基础卦辞和象辞
        st.markdown(f'<div class="gua-text"><strong>卦辞：</strong>{gua["text"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gua-text"><strong>象辞：</strong>{gua["description"]}</div>', unsafe_allow_html=True)
        
        # 使用增强解卦系统获取详细解释
        if enhanced_result:
            # 白话文解释
            st.markdown("### 白话文解释")
            st.markdown(f"{enhanced_result['plain_explanation']}")
            
            # 解卦内容 - 根据占卜问题只显示相关方面
            divination_event = st.session_state.get("divination_event", "")
            relevant_categories = identify_relevant_categories(divination_event)
            
            if enriched_content:
                st.markdown("### 解卦内容")
                
                # 只显示相关的解卦内容（enriched_content已经只包含相关方面）
                for category in relevant_categories:
                    if category in enriched_content and enriched_content[category] and enriched_content[category].strip():
                        st.markdown(f"#### {category}")
                        st.markdown(enriched_content[category])
            else:
                # 回退到默认内容，但只显示相关方面
                handbook = enhanced_result.get('fu_peirong_handbook', {})
                if handbook:
                    for category in relevant_categories:
                        # 映射类别名称到handbook键
                        category_key = category.split("（")[0]
                        category_map = {
                            "时运": "时运",
                            "财运": "财运",
                            "家宅": "家宅",
                            "身体": "身体",
                            "事业": "事业",
                            "感情": "感情"
                        }
                        key = category_map.get(category_key, "")
                        if key and handbook.get(key):
                            st.markdown(f"#### {category}")
                            st.markdown(f"**{handbook.get(key, '')}**")
            
            # 结语 - 特殊展现（红色边框框体）
            st.markdown('<div class="conclusion-box">', unsafe_allow_html=True)
            st.markdown('<div class="conclusion-title">结语</div>', unsafe_allow_html=True)
            conclusion_text = generate_conclusion(
                gua["name"], 
                gua["text"], 
                gua["description"], 
                divination_event,
                enhanced_result
            )
            st.markdown(f'<div class="conclusion-content">{conclusion_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 智能引导卡片 - 在结语后显示（只显示一次）
            show_smart_guide_card(gua)
        else:
            # 使用默认解释
            show_default_divination_result(gua)
            # 即使使用默认解释，也显示智能引导（只显示一次）
            show_smart_guide_card(gua)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_smart_guide_card(gua):
    """显示智能引导卡片 - 动态生成个性化引导文本，具备衍生提问能力"""
    divination_event = st.session_state.get("divination_event", "")
    enhanced_result = st.session_state.get("enhanced_result", None)
    enriched_content = st.session_state.get("enriched_content", None)
    
    # 根据卦象和结果动态生成个性化引导文本
    guide_text = generate_personalized_guide_text(gua, divination_event, enhanced_result, enriched_content)
    
    # 保存卦象摘要到session_state（用于后续页面）
    gua_summary = {
        "gua_name": gua["name"],
        "gua_text": gua["text"],
        "gua_description": gua["description"],
        "divination_event": divination_event,
        "symbol": gua["symbol"]
    }
    st.session_state.gua_summary = gua_summary
    
    # 显示智能引导卡片
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .smart-guide-card {
        margin: 30px 0;
        padding: 30px;
        background: linear-gradient(135deg, rgba(255, 248, 220, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%);
        border: 2px solid #DAA520;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(218, 165, 32, 0.2);
        opacity: 0;
        animation: fadeIn 0.6s ease-in forwards;
    }
    .smart-guide-title {
        color: #8B0000;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    .smart-guide-text {
        color: #654321;
        font-size: 16px;
        line-height: 1.8;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    <script>
    // 保存卦象摘要到localStorage
    (function() {
        const guaSummary = {
            guaName: """ + json.dumps(gua["name"]) + """,
            guaText: """ + json.dumps(gua["text"]) + """,
            guaDescription: """ + json.dumps(gua["description"]) + """,
            divinationEvent: """ + json.dumps(divination_event) + """,
            guaSymbol: """ + json.dumps(gua["symbol"]) + """
        };
        localStorage.setItem('lastGuaSummary', JSON.stringify(guaSummary));
    })();
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="smart-guide-card">', unsafe_allow_html=True)
    st.markdown('<div class="smart-guide-title">智能引导</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="smart-guide-text">{guide_text}</div>', unsafe_allow_html=True)
    
    # 两个按钮：下一步提问和返回首页（使用HTML和Streamlit混合方案）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("下一步提问", key="next_question_btn", use_container_width=True):
            st.session_state.current_page = "next_question"
            st.rerun()
    
    with col2:
        if st.button("返回首页", key="back_home_from_guide", use_container_width=True):
            clear_divination_data()
            st.session_state.current_page = "home"
            st.rerun()
    
    # 同时添加HTML按钮以便直接跳转到HTML页面（可选）
    st.markdown("""
    <script>
    // 为HTML按钮添加点击事件（如果页面是HTML）
    if (typeof window !== 'undefined' && window.location.protocol === 'file:') {
        const buttons = document.querySelectorAll('button[data-action]');
        buttons.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.getAttribute('data-action');
                if (action === 'next-question') {
                    window.location.href = 'next-question.html';
                } else if (action === 'home') {
                    window.location.href = 'index.html';
                }
            });
        });
    }
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_personalized_guide_text(gua, divination_event, enhanced_result, enriched_content):
    """根据卦象和结果生成个性化的引导文本"""
    # 分析关键词
    keywords = []
    if enhanced_result:
        handbook = enhanced_result.get('fu_peirong_handbook', {})
        if handbook.get('时运'):
            keywords.append('时运')
        if handbook.get('财运'):
            keywords.append('财运')
        if handbook.get('事业'):
            keywords.append('事业')
        if handbook.get('感情'):
            keywords.append('感情')
    
    # 根据占卜内容和关键词生成引导文本
    if "事业" in divination_event or "工作" in divination_event or "事业" in keywords:
        return f"根据{gua['name']}卦象显示，您的事业运势处于关键阶段，是否想进一步探讨具体的突破方向和行动策略？"
    elif "感情" in divination_event or "爱情" in divination_event or "恋爱" in divination_event or "婚姻" in divination_event or "感情" in keywords:
        return f"根据{gua['name']}卦象显示，您的情感卦象出现波动，是否想继续深入了解感情走向和改善方法？"
    elif "财运" in divination_event or "财富" in divination_event or "投资" in divination_event or "财运" in keywords:
        return f"根据{gua['name']}卦象显示，您的财运处于调整期，是否想进一步探讨具体的理财策略和投资方向？"
    elif "健康" in divination_event or "身体" in divination_event:
        return f"根据{gua['name']}卦象显示，您的健康状况需要关注，是否想进一步探讨具体的调养方法和注意事项？"
    else:
        return f"根据{gua['name']}卦象显示，您的运势处于调整期，是否想进一步探讨具体的突破方向和行动建议？"

def show_fortune_detail_page():
    """显示详细运势分析页面"""
    st.markdown('<div class="section-title">详细运势分析</div>', unsafe_allow_html=True)
    
    # 页面说明
    st.markdown("""
    <div style="padding: 20px; background: rgba(255, 248, 220, 0.3); border-radius: 10px; margin: 20px 0;">
        <h3 style="color: #8B0000; margin-bottom: 15px;">运势分析说明</h3>
        <p style="color: #654321; line-height: 1.8; font-size: 16px;">
        基于您刚才的占卜结果，我们将为您提供更详细的运势分析。运势分析包括：
        </p>
        <ul style="color: #654321; line-height: 2; font-size: 16px;">
            <li><strong>事业运势：</strong>分析事业发展趋势、关键时机和注意事项</li>
            <li><strong>财运分析：</strong>评估财富积累机会、投资建议和理财策略</li>
            <li><strong>健康运势：</strong>了解身体状况、养生建议和健康管理</li>
            <li><strong>感情运势：</strong>分析感情发展趋势、关系维护和相处之道</li>
            <li><strong>综合运势：</strong>整体运势评估和未来规划建议</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取之前的占卜结果
    if st.session_state.get("current_gua"):
        gua = st.session_state.current_gua
        divination_event = st.session_state.get("divination_event", "")
        
        st.markdown("### 基于您的占卜结果")
        st.markdown(f"**卦名：** {gua['name']}")
        st.markdown(f"**占卜问题：** {divination_event if divination_event else '未指定'}")
        
        # 显示详细的运势分析
        if st.session_state.get("enhanced_result"):
            enhanced_result = st.session_state.enhanced_result
            st.markdown("### 详细运势分析")
            
            # 时运分析
            st.markdown("#### 📈 时运（运势分析）")
            handbook = enhanced_result.get('fu_peirong_handbook', {})
            if handbook.get('时运'):
                st.markdown(f"**{handbook['时运']}**")
                st.markdown("""
                根据当前卦象，您的时运处于关键转折期。建议：
                - 把握有利时机，果断行动
                - 保持谨慎态度，避免冒进
                - 关注人际关系，寻求合作机会
                - 保持积极心态，应对挑战
                """)
            
            # 财运分析
            st.markdown("#### 💰 财运（财富运势）")
            if handbook.get('财运'):
                st.markdown(f"**{handbook['财运']}**")
                st.markdown("""
                财务规划建议：
                - 稳健理财，避免高风险投资
                - 合理分配资金，留足应急储备
                - 关注长期投资机会
                - 谨慎处理借贷关系
                """)
            
            # 事业分析
            st.markdown("#### 💼 事业（事业发展）")
            if handbook.get('事业'):
                st.markdown(f"**{handbook['事业']}**")
                st.markdown("""
                事业发展指导：
                - 稳扎稳打，不可急于求成
                - 加强团队协作，发挥集体智慧
                - 持续学习，提升专业能力
                - 把握机遇，适时展现才能
                """)
        else:
            st.info("暂无详细的运势分析数据，建议返回占卜页面重新占卜。")
    
    # 返回按钮
    st.markdown("---")
    if st.button("返回首页", key="back_home_fortune", use_container_width=True):
        clear_divination_data()
        st.session_state.current_page = "home"
        st.rerun()

def show_emotion_detail_page():
    """显示情感测算页面"""
    st.markdown('<div class="section-title">情感测算</div>', unsafe_allow_html=True)
    
    # 页面说明
    st.markdown("""
    <div style="padding: 20px; background: rgba(255, 248, 220, 0.3); border-radius: 10px; margin: 20px 0;">
        <h3 style="color: #8B0000; margin-bottom: 15px;">情感测算说明</h3>
        <p style="color: #654321; line-height: 1.8; font-size: 16px;">
        基于您刚才的占卜结果，我们将为您提供详细的情感测算分析。情感测算包括：
        </p>
        <ul style="color: #654321; line-height: 2; font-size: 16px;">
            <li><strong>感情趋势：</strong>分析感情发展的方向和趋势</li>
            <li><strong>性格匹配：</strong>评估双方性格的契合度和相处模式</li>
            <li><strong>沟通建议：</strong>提供改善沟通和增进感情的方法</li>
            <li><strong>关系维护：</strong>了解如何维护和深化感情关系</li>
            <li><strong>未来展望：</strong>预测感情发展的可能走向</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取之前的占卜结果
    if st.session_state.get("current_gua"):
        gua = st.session_state.current_gua
        divination_event = st.session_state.get("divination_event", "")
        
        st.markdown("### 基于您的占卜结果")
        st.markdown(f"**卦名：** {gua['name']}")
        st.markdown(f"**占卜问题：** {divination_event if divination_event else '未指定'}")
        
        # 显示详细的情感测算
        if st.session_state.get("enhanced_result"):
            enhanced_result = st.session_state.enhanced_result
            st.markdown("### 详细情感测算")
            
            # 感情分析
            st.markdown("#### ❤️ 感情（感情运势）")
            handbook = enhanced_result.get('fu_peirong_handbook', {})
            if handbook.get('感情'):
                st.markdown(f"**{handbook['感情']}**")
                st.markdown("""
                感情发展建议：
                - 保持真诚相待，以心换心
                - 顺其自然，不强求也不急躁
                - 加强沟通，理解对方的需求
                - 创造浪漫时刻，增进感情
                - 尊重彼此独立，保持适当空间
                """)
            
            # 关系维护
            st.markdown("#### 🤝 关系维护")
            st.markdown("""
            根据当前卦象，您的感情关系需要注意：
            - **沟通之道：** 多倾听，少指责，用理解代替争执
            - **相处方式：** 求同存异，尊重彼此的差异
            - **情感表达：** 适时表达爱意，让对方感受到关怀
            - **矛盾处理：** 遇到分歧时冷静处理，寻找共同点
            - **未来规划：** 共同制定目标，携手向前
            """)
            
            # 性格分析
            st.markdown("#### 性格匹配分析")
            st.markdown("""
            性格匹配建议：
            - 了解彼此的性格特点，找到互补之处
            - 尊重对方的性格差异，不强求改变
            - 发挥性格优势，共同成长
            - 通过性格分析，找到最佳相处模式
            """)
        else:
            st.info("暂无详细的情感测算数据，建议返回占卜页面重新占卜。")
    
    # 返回按钮
    st.markdown("---")
    if st.button("返回首页", key="back_home_emotion", use_container_width=True):
        clear_divination_data()
        st.session_state.current_page = "home"
        st.rerun()

def get_gua_detailed_analysis(gua_name, gua_symbol, gua_text, gua_description):
    """获取卦象的详细解析，包括六爻爻辞、五行属性等"""
    # 根据卦名获取详细的爻辞和解析
    gua_details = {
        "屯卦": {
            "gua_structure": "上坎下震，水下雷上",
            "symbol_meaning": "象征万物始生之艰难",
            "current_state": "机遇与挑战并存，需稳扎稳打",
            "yao_interpretations": [
                {"position": "初九", "text": "磐桓，利居贞", "meaning": "宜坚守正道，不可轻动"},
                {"position": "六二", "text": "屯如邅如，乘马班如", "meaning": "婚事暂缓，等待时机"},
                {"position": "六三", "text": "即鹿无虞，惟入于林中", "meaning": "无引导勿冒险"},
                {"position": "六四", "text": "乘马班如，求婚媾", "meaning": "积极行动，寻求合作"},
                {"position": "九五", "text": "屯其膏，小贞吉，大贞凶", "meaning": "小有积蓄，不可贪大"},
                {"position": "上六", "text": "乘马班如，泣血涟如", "meaning": "困境将过，保持耐心"}
            ],
            "wuxing": "水雷屯（坎水震木，水生木）",
            "trend_analysis": "前期困难重重，中期渐入佳境，后期可得发展",
            "action_advice": "积蓄实力，择机而动，重要决策宜在春季考虑",
            "time_cycle": "三个月内可见初步成效，半年后有显著改善"
        },
        "乾卦": {
            "gua_structure": "上乾下乾，纯阳之卦",
            "symbol_meaning": "象征天，具有创始、亨通、和谐、贞正四种德性",
            "current_state": "强健有力，主动进取，气势如虹",
            "yao_interpretations": [
                {"position": "初九", "text": "潜龙勿用", "meaning": "力量未显，宜积蓄待发"},
                {"position": "九二", "text": "见龙在田，利见大人", "meaning": "初露锋芒，得贵人相助"},
                {"position": "九三", "text": "君子终日乾乾，夕惕若厉", "meaning": "勤勉谨慎，居安思危"},
                {"position": "九四", "text": "或跃在渊，无咎", "meaning": "进退有据，审时度势"},
                {"position": "九五", "text": "飞龙在天，利见大人", "meaning": "大展宏图，成就事业"},
                {"position": "上九", "text": "亢龙有悔", "meaning": "过犹不及，知进知退"}
            ],
            "wuxing": "乾为天（纯阳金）",
            "trend_analysis": "运势强劲，但需注意物极必反",
            "action_advice": "把握时机，积极进取，但不可过于刚强",
            "time_cycle": "近期即可行动，秋冬季节更佳"
        },
        "坤卦": {
            "gua_structure": "上坤下坤，纯阴之卦",
            "symbol_meaning": "象征地，具有顺从、包容、滋养万物的特性",
            "current_state": "柔顺守成，以静制动，厚德载物",
            "yao_interpretations": [
                {"position": "初六", "text": "履霜，坚冰至", "meaning": "见微知著，防微杜渐"},
                {"position": "六二", "text": "直方大，不习无不利", "meaning": "正直宽厚，自然无咎"},
                {"position": "六三", "text": "含章可贞，或从王事", "meaning": "内敛才华，跟随领导"},
                {"position": "六四", "text": "括囊，无咎无誉", "meaning": "谨慎收敛，避免锋芒"},
                {"position": "六五", "text": "黄裳，元吉", "meaning": "中庸之道，大吉大利"},
                {"position": "上六", "text": "龙战于野，其血玄黄", "meaning": "阴阳相争，需要调和"}
            ],
            "wuxing": "坤为地（纯阴土）",
            "trend_analysis": "运势平稳，适合守成，不宜妄动",
            "action_advice": "以柔克刚，顺势而为，春季行动较佳",
            "time_cycle": "长期稳定，短期宜守"
        },
        "师卦": {
            "gua_structure": "上坤下坎，地中有水",
            "symbol_meaning": "象征军队，强调纪律和领导",
            "current_state": "需要组织和纪律，以德服人，团结群众",
            "yao_interpretations": [
                {"position": "初六", "text": "师出以律，否臧凶", "meaning": "行动需有纪律，否则凶险"},
                {"position": "九二", "text": "在师中，吉无咎，王三锡命", "meaning": "居中得位，大吉，得上级信任"},
                {"position": "六三", "text": "师或舆尸，凶", "meaning": "轻率行动，必遭失败"},
                {"position": "六四", "text": "师左次，无咎", "meaning": "退守待时，无咎"},
                {"position": "六五", "text": "田有禽，利执言，无咎", "meaning": "把握时机，主动出击"},
                {"position": "上六", "text": "大君有命，开国承家，小人勿用", "meaning": "功成受命，但需远离小人"}
            ],
            "wuxing": "地水师（坤土坎水，土克水）",
            "trend_analysis": "需要组织和纪律，前期准备充分，中期可获成功",
            "action_advice": "以德服人，团结众人，建立良好秩序，宜在夏季行动",
            "time_cycle": "需要充分准备，三个月内可组织行动，半年后可见成效"
        }
    }
    
    # 如果找到详细解析，返回；否则返回通用解析
    if gua_name in gua_details:
        return gua_details[gua_name]
    else:
        # 通用解析
        return {
            "gua_structure": "根据卦象结构分析",
            "symbol_meaning": gua_description,
            "current_state": "需要根据具体卦象分析",
            "yao_interpretations": [
                {"position": "初爻", "text": "基础阶段", "meaning": "宜稳固基础"},
                {"position": "二爻", "text": "发展阶段", "meaning": "稳步前进"},
                {"position": "三爻", "text": "转折阶段", "meaning": "谨慎决策"},
                {"position": "四爻", "text": "上升阶段", "meaning": "把握时机"},
                {"position": "五爻", "text": "鼎盛阶段", "meaning": "保持优势"},
                {"position": "上爻", "text": "完成阶段", "meaning": "总结反思"}
            ],
            "wuxing": "需根据卦象确定五行属性",
            "trend_analysis": "需要结合具体卦象分析趋势",
            "action_advice": "建议根据卦象特性采取相应行动",
            "time_cycle": "需要结合卦象确定时间周期"
        }

def show_next_question_page():
    """显示衍生提问页面 - 智能推荐问题版本（扩展版摘要）"""
    st.markdown('<div class="section-title">衍生提问</div>', unsafe_allow_html=True)
    
    # 从session_state获取上一次卦象摘要
    gua_summary = st.session_state.get("gua_summary", {})
    current_gua = st.session_state.get("current_gua", None)
    
    # 显示扩展版占卜结果摘要（使用Streamlit原生格式，不使用HTML）
    if gua_summary and current_gua:
        gua_name = gua_summary.get("gua_name", "未知")
        gua_text = gua_summary.get("gua_text", "未知")
        gua_description = gua_summary.get("gua_description", "未知")
        divination_event = gua_summary.get("divination_event", "未指定")
        gua_symbol = current_gua.get("symbol", "")
        
        # 获取详细解析
        detailed_analysis = get_gua_detailed_analysis(gua_name, gua_symbol, gua_text, gua_description)
        
        # 显示扩展版摘要（使用Streamlit原生格式）
        st.markdown("### 上一次占卜结果摘要（扩展版）")
        
        # 使用expander或container来组织内容
        with st.container():
            st.markdown(f"#### {gua_name}（{detailed_analysis['gua_structure']}）")
            
            st.markdown(f"**核心卦辞：** {gua_text}")
            st.markdown(f"**象辞深解：** {gua_description} - {detailed_analysis['symbol_meaning']}")
            st.markdown(f"**占卜问题：** {divination_event}")
            
            st.markdown("---")
            
            st.markdown("##### 详细解析")
            
            st.markdown(f"• **卦象特征：** {detailed_analysis['gua_structure']}，{detailed_analysis['symbol_meaning']}")
            st.markdown(f"• **当前状态分析：** {detailed_analysis['current_state']}")
            st.markdown(f"• **五行属性：** {detailed_analysis['wuxing']}")
            
            st.markdown("##### 关键爻位解读")
            
            for yao in detailed_analysis['yao_interpretations'][:3]:  # 显示前三个关键爻位
                st.markdown(f"• **{yao['position']}** \"{yao['text']}\"：{yao['meaning']}")
            
            st.markdown("---")
            
            st.markdown(f"• **运势走势：** {detailed_analysis['trend_analysis']}")
            st.markdown(f"• **行动建议：** {detailed_analysis['action_advice']}")
            st.markdown(f"• **时间周期：** {detailed_analysis['time_cycle']}")
    elif gua_summary:
        # 如果没有current_gua，显示简化版摘要（使用Streamlit原生格式）
        st.markdown("### 上一次占卜结果摘要")
        
        with st.container():
            st.markdown(f"**卦名：** {gua_summary.get('gua_name', '未知')}")
            st.markdown(f"**卦辞：** {gua_summary.get('gua_text', '未知')}")
            st.markdown(f"**象辞：** {gua_summary.get('gua_description', '未知')}")
            st.markdown(f"**占卜问题：** {gua_summary.get('divination_event', '未指定')}")
    else:
        st.info("暂无上一次占卜结果，建议先进行占卜。")
    
    # 生成智能推荐问题
    recommended_questions = generate_recommended_questions(gua_summary)
    
    # 显示推荐问题和输入选项
    st.markdown("### 请选择或输入你想进一步探讨的问题")
    
    # 显示推荐问题（单选按钮）
    if recommended_questions:
        st.markdown("**智能推荐问题：**")
        selected_question = st.radio(
            "选择推荐问题",
            options=recommended_questions + ["自定义输入"],
            key="recommended_question_radio",
            label_visibility="collapsed"
        )
        
        # 如果选择了自定义输入，显示输入框
        if selected_question == "自定义输入":
            question = st.text_area(
                "请输入你的问题",
                placeholder="例如：我该如何抓住本卦中的机遇？我应该如何改善当前的感情状况？",
                height=120,
                key="next_question_input"
            )
        else:
            question = selected_question
            # 隐藏输入框（通过设置空值）
            st.session_state.next_question_input = question
    else:
        # 如果没有推荐问题，直接显示输入框
        question = st.text_area(
            "请输入你的问题",
            placeholder="例如：我该如何抓住本卦中的机遇？我应该如何改善当前的感情状况？",
            height=120,
            key="next_question_input"
        )
    
    # 生成按钮
    if st.button("生成深化结果", key="generate_deep_result", use_container_width=True):
        if question and question.strip():
            # 设置生成状态
            st.session_state.generating_deep_content = True
            st.session_state.deep_question = question.strip()
            st.rerun()
        else:
            st.warning("请输入您想探讨的问题！")
    
    # 如果正在生成，显示加载动画
    if st.session_state.get("generating_deep_content", False):
        st.markdown("""
        <div style="text-align: center; padding: 40px; margin: 30px 0;">
            <div style="display: inline-block; width: 60px; height: 60px; border: 6px solid rgba(139, 0, 0, 0.1); border-top-color: #8B0000; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;"></div>
            <div style="color: #8B0000; font-size: 20px; font-weight: bold;">正在生成深化解卦内容，请稍候…</div>
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            </style>
        </div>
        """, unsafe_allow_html=True)
        
        # 生成深化结果
        deep_question = st.session_state.get("deep_question", "")
        gua_summary = st.session_state.get("gua_summary", {})
        
        # 调用后端生成接口（标记为已生成）
        deep_result = generate_deep_divination_result(gua_summary, deep_question)
        
        # 保存结果标记
        st.session_state.deep_result = deep_result
        st.session_state.generating_deep_content = False
        st.rerun()
    
    # 显示深化结果（使用Streamlit原生格式，不使用HTML）
    if st.session_state.get("deep_result") and not st.session_state.get("generating_deep_content", False):
        # 从session_state获取结果，但不使用HTML格式
        deep_question = st.session_state.get("deep_question", "")
        gua_summary = st.session_state.get("gua_summary", {})
        current_gua = st.session_state.get("current_gua", None)
        
        st.markdown("### 深化解卦结果")
        
        # 显示基于用户问题的信息
        st.markdown("**基于您的问题：** " + deep_question)
        if gua_summary:
            st.markdown("**基于卦象：** " + gua_summary.get("gua_name", "未知"))
        
        st.markdown("---")
        
        # 显示卦象深度分析（使用Streamlit原生格式）
        show_deep_analysis_result(gua_summary, deep_question, current_gua)
        
        # 添加持续对话功能
        st.markdown("---")
        st.markdown("### 继续提问")
        st.markdown("您可以继续提问，我会基于您的卦象和之前的对话，持续为您提供深入的解答。")
        
        # 初始化对话历史（如果不存在）
        if "divination_conversation_history" not in st.session_state:
            st.session_state.divination_conversation_history = []
        
        # 显示对话历史
        if st.session_state.divination_conversation_history:
            st.markdown("#### 对话历史")
            for i, (msg_question, msg_answer) in enumerate(st.session_state.divination_conversation_history[-5:], 1):
                with st.expander(f"对话 {i}: {msg_question[:50]}..."):
                    st.markdown(f"**问题：** {msg_question}")
                    st.markdown(f"**回答：** {msg_answer}")
        
        # 输入框
        continue_question = st.text_area(
            "请输入您的问题：",
            key="divination_continue_question",
            height=100,
            placeholder="例如：这个卦象对我的事业发展有什么具体指导？"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            # 检查是否正在生成答案
            is_generating_answer = st.session_state.get("divination_generating_answer", False)
            
            if st.button("发送", key="send_divination_question", use_container_width=True, disabled=is_generating_answer):
                if continue_question.strip():
                    # 保存问题到session state
                    st.session_state.divination_pending_question = continue_question
                    # 设置生成状态
                    st.session_state.divination_generating_answer = True
                    st.session_state.divination_continue_question = ""
                    st.rerun()
                else:
                    st.warning("请输入您的问题")
        
        # 如果正在生成答案，显示加载动画
        if st.session_state.get("divination_generating_answer", False):
            st.markdown("""
            <div style="text-align: center; padding: 40px; margin: 30px 0;">
                <div style="display: inline-block; width: 60px; height: 60px; border: 6px solid rgba(139, 0, 0, 0.1); border-top-color: #8B0000; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;"></div>
                <div style="color: #8B0000; font-size: 20px; font-weight: bold;">正在生成占卜结果，请稍候...</div>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
            </div>
            """, unsafe_allow_html=True)
            
            # 获取最后一个问题
            last_question = st.session_state.get("divination_pending_question", "")
            if not last_question and st.session_state.divination_conversation_history:
                last_question = st.session_state.divination_conversation_history[-1][0]
            
            if last_question:
                # 添加到对话历史（如果还没有）
                if not st.session_state.divination_conversation_history or st.session_state.divination_conversation_history[-1][1] != "":
                    if st.session_state.divination_conversation_history:
                        st.session_state.divination_conversation_history.append((last_question, ""))
                    else:
                        st.session_state.divination_conversation_history = [(last_question, "")]
                
                # 构建上下文（包含卦象信息和对话历史）
                context = f"原始占卜卦象：{gua_summary.get('gua_name', '未知')} - {gua_summary.get('gua_description', '')}\n"
                context += f"原始问题：{deep_question}\n\n"
                if st.session_state.divination_conversation_history:
                    context += "对话历史：\n"
                    for q, a in st.session_state.divination_conversation_history[:-1]:
                        context += f"Q: {q}\nA: {a}\n\n"
                
                # 调用问答系统（传入完整上下文）
                try:
                    # 构建完整的问题上下文
                    full_question = f"{context}\n当前问题：{last_question}"
                    result = enhanced_qa.answer_question(full_question)
                    answer = result.get("answer", "抱歉，暂时无法回答这个问题。")
                    
                    # 更新对话历史
                    if st.session_state.divination_conversation_history:
                        st.session_state.divination_conversation_history[-1] = (last_question, answer)
                    
                    # 清除生成状态和临时问题
                    st.session_state.divination_generating_answer = False
                    if "divination_pending_question" in st.session_state:
                        del st.session_state.divination_pending_question
                    st.rerun()
                except Exception as e:
                    st.error(f"处理问题时出错：{str(e)}")
                    # 如果出错，从对话历史中移除未完成的问题
                    if st.session_state.divination_conversation_history and st.session_state.divination_conversation_history[-1][1] == "":
                        st.session_state.divination_conversation_history.pop()
                    # 清除生成状态和临时问题
                    st.session_state.divination_generating_answer = False
                    if "divination_pending_question" in st.session_state:
                        del st.session_state.divination_pending_question
                    st.rerun()
    
    # 返回按钮
    st.markdown("---")
    if st.button("返回首页", key="back_home_from_next_question", use_container_width=True):
        clear_divination_data()
        st.session_state.current_page = "home"
        st.rerun()

def generate_recommended_questions(gua_summary):
    """基于卦象和原始问题生成智能推荐问题"""
    gua_name = gua_summary.get("gua_name", "")
    divination_event = gua_summary.get("divination_event", "")
    gua_text = gua_summary.get("gua_text", "")
    gua_description = gua_summary.get("gua_description", "")
    
    # 推荐问题列表
    recommended = []
    
    # 基于卦象特性的推荐问题
    if "屯" in gua_name:
        recommended.append("如何在当前运势下把握机遇？")
        recommended.append("需要注意哪些方面的挑战？")
        recommended.append("什么时间段运势会好转？")
        recommended.append("如何改善当前的困境？")
    elif "蒙" in gua_name:
        recommended.append("如何提升自己的认知水平？")
        recommended.append("当前的学习方向是否正确？")
    elif "需" in gua_name:
        recommended.append("何时行动最为有利？")
        recommended.append("应该如何等待和准备？")
    elif "讼" in gua_name:
        recommended.append("如何化解当前的矛盾冲突？")
        recommended.append("应该如何维护自己的权益？")
    elif "师" in gua_name:
        recommended.append("如何组织和管理团队？")
        recommended.append("当前是否适合采取行动？")
    elif "比" in gua_name:
        recommended.append("如何建立良好的人际关系？")
        recommended.append("当前是否适合合作？")
    elif "小畜" in gua_name or "大畜" in gua_name:
        recommended.append("如何积累资源和能力？")
        recommended.append("当前的投资方向是否正确？")
    elif "履" in gua_name:
        recommended.append("如何谨慎行事避免风险？")
        recommended.append("当前的行为是否恰当？")
    elif "泰" in gua_name:
        recommended.append("如何保持当前的良好状态？")
        recommended.append("如何进一步扩大优势？")
    elif "否" in gua_name:
        recommended.append("如何扭转当前的不利局面？")
        recommended.append("何时会出现转机？")
    else:
        # 通用推荐问题
        recommended.append("如何在当前运势下把握机遇？")
        recommended.append("需要注意哪些方面的挑战？")
        recommended.append("什么时间段运势会好转？")
    
    # 基于原始问题语境的推荐问题
    if "运势" in divination_event or "运程" in divination_event:
        recommended.append("如何改善运势？")
        recommended.append("运势的关键转折点在哪里？")
    elif "事业" in divination_event or "工作" in divination_event:
        recommended.append("事业发展的关键时机是什么时候？")
        recommended.append("如何提升事业运势？")
    elif "感情" in divination_event or "爱情" in divination_event or "恋爱" in divination_event:
        recommended.append("感情发展的关键因素是什么？")
        recommended.append("如何改善感情关系？")
    elif "财运" in divination_event or "财富" in divination_event:
        recommended.append("如何提升财运？")
        recommended.append("投资理财的最佳时机是什么时候？")
    elif "健康" in divination_event or "身体" in divination_event:
        recommended.append("如何改善健康状况？")
        recommended.append("需要注意哪些健康问题？")
    
    # 去重并限制数量
    unique_questions = []
    for q in recommended:
        if q not in unique_questions:
            unique_questions.append(q)
    
    # 返回3-5个推荐问题
    return unique_questions[:5]

def show_deep_analysis_result(gua_summary, question, current_gua):
    """显示深化解卦结果（使用Streamlit原生格式，不使用HTML）"""
    gua_name = gua_summary.get("gua_name", "当前卦象")
    gua_symbol = current_gua.get("symbol", "") if current_gua else ""
    
    # 获取详细解析
    detailed_analysis = get_gua_detailed_analysis(
        gua_name, 
        gua_symbol, 
        gua_summary.get("gua_text", ""), 
        gua_summary.get("gua_description", "")
    )
    
    # 根据问题类型生成针对性分析
    analysis_content = generate_targeted_analysis(gua_name, question, detailed_analysis)
    
    # 使用Streamlit原生格式显示
    st.markdown("#### 卦象深度分析")
    st.markdown(analysis_content["gua_analysis"])
    
    st.markdown("#### 具体把握策略")
    
    st.markdown("**1. 识别机遇特征：**")
    st.markdown(analysis_content["opportunity_identification"])
    
    st.markdown("**2. 行动时机选择：**")
    st.markdown(analysis_content["timing_guidance"])
    
    st.markdown("**3. 关键实施步骤：**")
    for i, step in enumerate(analysis_content["action_steps"], 1):
        st.markdown(f"   - **第{i}步：** {step}")
    
    st.markdown("#### 注意事项")
    for note in analysis_content["precautions"]:
        st.markdown(f"   • {note}")
    
    st.markdown("#### 时机把握指导")
    st.markdown(f"**近期重要时间点：** {analysis_content['time_guidance']}")

def generate_targeted_analysis(gua_name, question, detailed_analysis):
    """根据卦象和问题生成针对性分析（使用AI生成）"""
    # 如果session_state中已有AI生成的分析内容，直接使用
    if 'deep_analysis_content' in st.session_state and st.session_state.get('deep_analysis_content'):
        return st.session_state.deep_analysis_content
    
    # 获取当前实时日期和时间信息
    from datetime import datetime, timedelta
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day
    
    # 中文星期几
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    current_weekday = weekdays[current_date.weekday()]
    
    # 计算未来时间点（基于当前日期）
    next_month = current_date + timedelta(days=30)
    next_three_months = current_date + timedelta(days=90)
    next_six_months = current_date + timedelta(days=180)
    
    # 构建AI生成提示词
    gua_text = detailed_analysis.get('gua_text', '')
    gua_description = detailed_analysis.get('gua_description', '')
    symbol_meaning = detailed_analysis.get('symbol_meaning', '')
    current_state = detailed_analysis.get('current_state', '')
    action_advice = detailed_analysis.get('action_advice', '')
    time_cycle = detailed_analysis.get('time_cycle', '')
    
    prompt = f"""你是一位精通易经的专家。请基于以下信息，针对用户的具体问题生成详细的深化解卦分析。

【重要】当前实时日期信息：
- 当前日期：{current_year}年{current_month}月{current_day}日（{current_weekday}）
- 当前月份：{current_month}月
- 当前年份：{current_year}年
- 未来1个月：{next_month.year}年{next_month.month}月
- 未来3个月：{next_three_months.year}年{next_three_months.month}月
- 未来6个月：{next_six_months.year}年{next_six_months.month}月

卦象信息：
- 卦名：{gua_name}
- 卦辞：{gua_text}
- 象辞：{gua_description}
- 象征含义：{symbol_meaning}
- 当前状态：{current_state}
- 行动建议：{action_advice}
- 时间周期：{time_cycle}

用户问题：{question}

请生成以下结构的详细分析内容（每个部分200-300字，内容要精炼但有深度，要紧密结合用户的问题）：

1. 卦象深度分析：结合卦象和用户问题，深入分析当前情况
2. 识别机遇特征：针对用户问题，说明如何识别相关机遇
3. 行动时机选择：给出具体的行动时机建议（必须基于当前日期{current_year}年{current_month}月{current_day}日，给出未来1-3个月的具体时间建议，例如"建议在{next_month.month}月至{next_three_months.month}月之间"）
4. 关键实施步骤：提供3个具体的实施步骤
5. 注意事项：列出3-5条需要注意的事项
6. 时机把握指导：给出近期重要时间点的建议（必须基于当前日期，给出未来1-6个月的具体日期范围，例如"建议在{current_year}年{next_month.month}月{next_month.day}日至{next_three_months.month}月{next_three_months.day}日之间"）

【重要要求】：
- 所有时间建议必须基于当前实际日期：{current_year}年{current_month}月{current_day}日
- 不要使用过去的时间（如5月、6月等已过期的月份）
- 时间建议必须是从当前日期开始的未来时间
- 行动时机选择中的月份必须是当前月份或未来月份
- 时机把握指导中的日期范围必须是从当前日期开始的未来日期

请以JSON格式返回，格式如下：
{{
    "gua_analysis": "卦象深度分析内容",
    "opportunity_identification": "识别机遇特征内容",
    "timing_guidance": "行动时机选择内容（必须包含基于当前日期{current_year}年{current_month}月的具体时间建议）",
    "action_steps": ["步骤1", "步骤2", "步骤3"],
    "precautions": ["注意事项1", "注意事项2", "注意事项3"],
    "time_guidance": "时机把握指导内容（必须包含基于当前日期{current_year}年{current_month}月{current_day}日的具体未来日期范围）"
}}

请确保所有内容都紧密结合用户的问题"{question}"，给出针对性的建议。所有时间建议必须基于当前实际日期。"""
    
    # 调用DeepSeek API生成分析
    deepseek_result = call_deepseek_api(prompt, max_tokens=2000)
    
    # 如果DeepSeek失败，尝试Qwen
    if not deepseek_result:
        deepseek_result = call_qwen_api(prompt, max_tokens=2000)
    
    # 解析AI返回的内容
    analysis = None
    if deepseek_result:
        try:
            import json
            import re
            
            # 尝试提取JSON格式的内容
            json_match = re.search(r'\{[\s\S]*\}', deepseek_result, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
            else:
                # 如果AI返回的不是JSON格式，尝试从文本中提取结构化内容
                # 提取卦象深度分析
                gua_match = re.search(r'卦象深度分析[：:]\s*([^\n]+(?:\n(?!识别|行动|关键|注意|时机)[^\n]+)*)', deepseek_result, re.DOTALL)
                gua_analysis = gua_match.group(1).strip() if gua_match else ""
                
                # 提取识别机遇特征
                opp_match = re.search(r'识别机遇特征[：:]\s*([^\n]+(?:\n(?!行动|关键|注意|时机)[^\n]+)*)', deepseek_result, re.DOTALL)
                opportunity = opp_match.group(1).strip() if opp_match else ""
                
                # 提取行动时机选择
                timing_match = re.search(r'行动时机选择[：:]\s*([^\n]+(?:\n(?!关键|注意|时机)[^\n]+)*)', deepseek_result, re.DOTALL)
                timing = timing_match.group(1).strip() if timing_match else ""
                
                # 提取关键实施步骤
                steps_match = re.search(r'关键实施步骤[：:]\s*([^\n]+(?:\n(?!注意|时机)[^\n]+)*)', deepseek_result, re.DOTALL)
                steps_text = steps_match.group(1).strip() if steps_match else ""
                # 尝试提取步骤列表
                steps_list = re.findall(r'[第\d步：:]\s*([^\n]+)', steps_text) or re.findall(r'[1-3]\.\s*([^\n]+)', steps_text)
                if not steps_list:
                    steps_list = [s.strip() for s in steps_text.split('\n') if s.strip()][:3]
                
                # 提取注意事项
                prec_match = re.search(r'注意事项[：:]\s*([^\n]+(?:\n(?!时机)[^\n]+)*)', deepseek_result, re.DOTALL)
                prec_text = prec_match.group(1).strip() if prec_match else ""
                precautions_list = re.findall(r'[•·▪]\s*([^\n]+)', prec_text) or re.findall(r'[1-5]\.\s*([^\n]+)', prec_text)
                if not precautions_list:
                    precautions_list = [p.strip() for p in prec_text.split('\n') if p.strip()][:5]
                
                # 提取时机把握指导
                time_match = re.search(r'时机把握指导[：:]\s*([^\n]+(?:\n[^\n]+)*)', deepseek_result, re.DOTALL)
                time_guidance = time_match.group(1).strip() if time_match else ""
                
                if gua_analysis or opportunity or timing or steps_list:
                    analysis = {
                        "gua_analysis": gua_analysis or f"{gua_name}象征{symbol_meaning}。当前运势虽有挑战，但蕴含成长契机。{current_state}",
                        "opportunity_identification": opportunity or "关注新出现的小迹象，特别是人际关系和技能提升领域。注意观察周围环境的变化，把握有利时机。",
                        "timing_guidance": timing or f"最佳行动时间为辰时（7-9点）或午时（11-13点）。{action_advice}",
                        "action_steps": steps_list[:3] if steps_list else ["巩固现有基础，避免盲目扩张", "建立支持网络，寻求贵人相助", "小规模试错，验证可行性后再全面推进"],
                        "precautions": precautions_list[:5] if precautions_list else ["避免急于求成，需循序渐进", f"重要决策建议在{time_cycle}后考虑", "注意健康管理，保持身心平衡"],
                        "time_guidance": time_guidance or time_cycle
                    }
        except Exception as e:
            print(f"解析AI返回内容时出错: {e}")
            pass
    
    # 如果AI生成失败，使用模板内容作为后备（也需要基于实时时间）
    if not analysis:
        # 生成基于实时时间的建议
        month_names = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
        current_month_name = month_names[current_month - 1] if current_month <= 12 else str(current_month)
        next_month_name = month_names[next_month.month - 1] if next_month.month <= 12 else str(next_month.month)
        next_three_months_name = month_names[next_three_months.month - 1] if next_three_months.month <= 12 else str(next_three_months.month)
        
        analysis = {
            "gua_analysis": f"{gua_name}象征{symbol_meaning}。当前运势虽有挑战，但蕴含成长契机。{current_state}",
            "opportunity_identification": "关注新出现的小迹象，特别是人际关系和技能提升领域。注意观察周围环境的变化，把握有利时机。",
            "timing_guidance": f"根据当前时间（{current_year}年{current_month}月），建议在{next_month.month}月至{next_three_months.month}月之间采取行动。最佳行动时间为辰时（7-9点）或午时（11-13点）。{action_advice}",
            "action_steps": [
                "巩固现有基础，避免盲目扩张",
                "建立支持网络，寻求贵人相助",
                "小规模试错，验证可行性后再全面推进"
            ],
            "precautions": [
                "避免急于求成，需循序渐进",
                f"重要决策建议在{time_cycle}后考虑",
                "注意健康管理，保持身心平衡"
            ],
            "time_guidance": f"近期重要时间点：建议在{current_year}年{next_month.month}月{next_month.day}日至{next_three_months.month}月{next_three_months.day}日之间进行关键沟通或安排重要活动。{next_three_months.month}月后可评估进展并做出适当调整。"
        }
        
        # 根据问题类型调整内容
        if "机遇" in question or "把握" in question:
            analysis["gua_analysis"] = f"{gua_name}象征{symbol_meaning}，机遇往往隐藏在挑战之中。当前运势虽有困顿，但蕴含成长契机。"
            analysis["opportunity_identification"] = "识别机遇特征：关注新出现的小迹象，特别是人际关系和技能提升领域。机遇往往以微小变化的形式出现，需要敏锐观察。"
        
        if "改善" in question or "提升" in question:
            analysis["action_steps"] = [
                "分析当前困境的根本原因",
                "制定系统的改善计划",
                "逐步实施，每步都要验证效果"
            ]
    
    # 保存到session_state
    st.session_state.deep_analysis_content = analysis
    
    return analysis

def generate_deep_divination_result(gua_summary, question):
    """生成深化解卦结果（基于上次结果+新问题）- 调用AI生成分析内容"""
    # 清除之前保存的分析内容，准备生成新的
    if 'deep_analysis_content' in st.session_state:
        del st.session_state.deep_analysis_content
    
    # 获取卦象详细信息
    gua_name = gua_summary.get("gua_name", "当前卦象")
    current_gua = st.session_state.get("current_gua", None)
    gua_symbol = current_gua.get("symbol", "") if current_gua else ""
    
    # 获取详细解析
    detailed_analysis = get_gua_detailed_analysis(
        gua_name, 
        gua_symbol, 
        gua_summary.get("gua_text", ""), 
        gua_summary.get("gua_description", "")
    )
    
    # 调用generate_targeted_analysis生成AI分析内容
    # 这个函数会调用DeepSeek和Qwen API
    analysis_content = generate_targeted_analysis(gua_name, question, detailed_analysis)
    
    # 返回标记，实际内容已保存在session_state.deep_analysis_content中
    return "generated"

def show_default_divination_result(gua):
    """显示默认的占卜结果"""
    # 解释
    st.markdown(f'<div class="gua-interpretation"><strong>解释：</strong>{gua["interpretation"]}</div>', unsafe_allow_html=True)
    
    # 事件相关解释
    if st.session_state.divination_event:
        st.markdown(f'<div class="gua-interpretation"><strong>关于"{st.session_state.divination_event}"：</strong>根据此卦象，建议您保持耐心，顺应自然规律，不可急于求成。</div>', unsafe_allow_html=True)
    
    # 详细解释部分
    st.markdown("### 按朱熹《易经启蒙》解卦方法占卜结果")
    st.markdown(f"#### 周易第{gua['id']}卦详解")
    
    # 爻辞解释
    st.markdown("**爻辞：**")
    st.markdown(f"根据{gua['name']}的爻辞分析，此卦象体现了阴阳变化的规律。")
    
    # 白话文解释
    st.markdown("**白话文解释：**")
    st.markdown(f"从现代角度理解，{gua['name']}告诉我们：{gua['interpretation']}")
    
    # 邵雍河洛理数解释
    st.markdown("**邵雍河洛理数爻辞解释：**")
    st.markdown("**平：** 此卦象表示运势平稳，适合守成，不宜妄动。")
    
    # 傅佩荣解卦手册
    st.markdown("**傅佩荣解卦手册：**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**时运：** 守成尚可，不宜妄动")
        st.markdown("**财运：** 适宜稳健投资")
    with col2:
        st.markdown("**家宅：** 维护家声，和睦相处")
        st.markdown("**身体：** 注意调养，保持健康")
    
    # 卦辞参考
    st.markdown("### 卦辞参考")
    st.markdown("以下内容为卦辞参考，帮助理解本卦和变卦的含义：")
    
    st.markdown(f"**•本卦{gua['name']}卦辞：**")
    st.markdown(f"**第{gua['id']}卦：{gua['name']}**")
    st.markdown(f"**{gua['name']}。{gua['text']}**")
    st.markdown(f"**象曰：{gua['description']}**")
    
    st.markdown("**白话文解释：**")
    st.markdown(f"{gua['interpretation']}")
    
    # 结语 - 特殊展现（红色边框框体）
    st.markdown('<div class="conclusion-box">', unsafe_allow_html=True)
    st.markdown('<div class="conclusion-title">结语</div>', unsafe_allow_html=True)
    divination_event = st.session_state.get("divination_event", "")
    conclusion_text = generate_conclusion(
        gua["name"], 
        gua["text"], 
        gua["description"], 
        divination_event,
        None
    )
    st.markdown(f'<div class="conclusion-content">{conclusion_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_qa_analysis_state(current_question, analysis_content, original_question=""):
    """显示深度分析状态界面"""
    st.markdown("---")
    
    # 判断问题类型，只有解梦/占卜类问题才显示"原始梦境上下文"
    # 风水问题不显示"原始梦境上下文"
    is_dream_or_divination = any(keyword in current_question.lower() or keyword in (original_question.lower() if original_question else "") 
                                  for keyword in ["梦", "梦见", "周公", "解梦", "占卜", "卦", "卜", "算", "预测"])
    is_fengshui = any(keyword in current_question.lower() or keyword in (original_question.lower() if original_question else "")
                      for keyword in ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房", "财位", "绿植", "摆放"])
    
    # 显示分析焦点和原始梦境上下文（仅对解梦/占卜类问题）
    original_context_html = ""
    if original_question and is_dream_or_divination and not is_fengshui:
        original_context_html = f'<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(139, 0, 0, 0.2);"><strong style="color: #8B0000;">原始梦境上下文：</strong><br><span style="color: #654321; font-style: italic;">{original_question}</span></div>'
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 248, 220, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%);
                border: 2px solid #8B0000; border-radius: 10px; padding: 20px; margin: 20px 0;">
        <h3 style="color: #8B0000; margin-top: 0;">📌 当前分析焦点</h3>
        <p style="font-size: 18px; font-weight: bold; color: #654321; margin: 10px 0;">{current_question}</p>
        {original_context_html}
    </div>
    """, unsafe_allow_html=True)
    
    # 显示深度分析内容
    st.markdown("### 深度分析结果")
    st.markdown(analysis_content)
    
    # 显示其他相关问题（供切换）
    follow_up_questions_list = st.session_state.get("follow_up_questions_list", [])
    if follow_up_questions_list and len(follow_up_questions_list) > 1:
        st.markdown("---")
        st.markdown("### 其他相关问题")
        st.markdown("您还可以继续探讨以下方面：")
        for i, follow_q in enumerate(follow_up_questions_list, 1):
            if follow_q != current_question:  # 不显示当前问题
                if st.button(f"📌 {follow_q}", key=f"other_follow_up_{i}", use_container_width=False):
                    # 切换到新的相关问题
                    st.session_state["current_follow_up_question"] = follow_q
                    st.session_state["qa_question_input"] = follow_q
                    st.session_state["qa_analysis_content"] = None  # 清除旧内容
                    st.session_state["auto_trigger_qa"] = True
                    st.session_state["qa_input_key_suffix"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    st.rerun()
    
    # 添加持续对话功能
    st.markdown("---")
    st.markdown("### 继续提问")
    st.markdown("您可以继续提问，我会基于您的问题和之前的对话，持续为您提供深入的解答。")
    
    # 初始化对话历史（如果不存在）
    if "qa_conversation_history" not in st.session_state:
        st.session_state.qa_conversation_history = []
    
    # 显示对话历史
    if st.session_state.qa_conversation_history:
        st.markdown("#### 对话历史")
        for i, (msg_question, msg_answer) in enumerate(st.session_state.qa_conversation_history[-5:], 1):
            with st.expander(f"对话 {i}: {msg_question[:50]}..."):
                st.markdown(f"**问题：** {msg_question}")
                st.markdown(f"**回答：** {msg_answer}")
    
    # 输入框
    continue_question = st.text_area(
        "请输入您的问题：",
        key="qa_continue_question",
        height=100,
        placeholder="例如：这个问题还有哪些需要注意的细节？"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        # 检查是否正在生成答案
        is_generating_answer = st.session_state.get("qa_generating_answer", False)
        
        if st.button("发送", key="send_qa_question", use_container_width=True, disabled=is_generating_answer):
            if continue_question.strip():
                # 保存问题到session state
                st.session_state.qa_pending_question = continue_question
                # 设置生成状态
                st.session_state.qa_generating_answer = True
                st.session_state.qa_continue_question = ""
                st.rerun()
            else:
                st.warning("请输入您的问题")
    
    # 如果正在生成答案，显示加载动画
    if st.session_state.get("qa_generating_answer", False):
        st.markdown("""
        <div style="text-align: center; padding: 40px; margin: 30px 0;">
            <div style="display: inline-block; width: 60px; height: 60px; border: 6px solid rgba(139, 0, 0, 0.1); border-top-color: #8B0000; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;"></div>
            <div style="color: #8B0000; font-size: 20px; font-weight: bold;">正在生成占卜结果，请稍候...</div>
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            </style>
        </div>
        """, unsafe_allow_html=True)
        
        # 获取最后一个问题
        if st.session_state.qa_conversation_history:
            last_question = st.session_state.qa_conversation_history[-1][0]
        else:
            # 从输入框获取问题
            last_question = st.session_state.get("qa_last_question", "")
        
        if not last_question:
            # 如果对话历史为空，需要从session state获取问题
            # 这应该在按钮点击时保存
            last_question = st.session_state.get("qa_pending_question", "")
        
        if last_question:
            # 添加到对话历史（如果还没有）
            if not st.session_state.qa_conversation_history or (len(st.session_state.qa_conversation_history) > 0 and st.session_state.qa_conversation_history[-1][1] != ""):
                if st.session_state.qa_conversation_history:
                    st.session_state.qa_conversation_history.append((last_question, ""))
                else:
                    st.session_state.qa_conversation_history = [(last_question, "")]
            
            # 构建上下文（包含原始问题和对话历史）
            context = f"原始问题：{original_question if original_question else current_question}\n"
            context += f"当前分析问题：{current_question}\n\n"
            if st.session_state.qa_conversation_history:
                context += "对话历史：\n"
                for q, a in st.session_state.qa_conversation_history[:-1]:
                    context += f"Q: {q}\nA: {a}\n\n"
            
            # 调用问答系统（传入完整上下文）
            try:
                # 构建完整的问题上下文
                full_question = f"{context}\n当前问题：{last_question}"
                result = enhanced_qa.answer_question(full_question)
                answer = result.get("answer", "抱歉，暂时无法回答这个问题。")
                
                # 更新对话历史
                if st.session_state.qa_conversation_history:
                    st.session_state.qa_conversation_history[-1] = (last_question, answer)
                
                # 更新当前显示内容（显示最新回答）
                st.session_state["qa_analysis_content"] = answer
                st.session_state["current_follow_up_question"] = last_question
                
                # 清除生成状态和临时问题
                st.session_state.qa_generating_answer = False
                if "qa_pending_question" in st.session_state:
                    del st.session_state.qa_pending_question
                st.rerun()
            except Exception as e:
                st.error(f"处理问题时出错：{str(e)}")
                # 如果出错，从对话历史中移除未完成的问题
                if st.session_state.qa_conversation_history and st.session_state.qa_conversation_history[-1][1] == "":
                    st.session_state.qa_conversation_history.pop()
                # 清除生成状态
                st.session_state.qa_generating_answer = False
                if "qa_pending_question" in st.session_state:
                    del st.session_state.qa_pending_question
                st.rerun()
    
    # 返回按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← 返回相关问题列表", key="back_to_questions", use_container_width=True):
            st.session_state["qa_show_analysis"] = False
            st.session_state["current_follow_up_question"] = None
            st.session_state["qa_analysis_content"] = None
            # 恢复到相关问题列表状态（显示原始答案和相关问题列表）
            st.rerun()

def show_qa_page():
    """显示智能问答页面 - 增强版"""
    st.markdown('<div class="section-title">智能问答</div>', unsafe_allow_html=True)
    
    # 检查是否在深度分析状态（显示分析结果）
    if st.session_state.get("qa_show_analysis", False) and st.session_state.get("qa_analysis_content"):
        # 显示深度分析状态界面
        current_question = st.session_state.get("current_follow_up_question", "")
        original_question = st.session_state.get("original_question", "")
        analysis_content = st.session_state.get("qa_analysis_content", "")
        show_qa_analysis_state(current_question, analysis_content, original_question)
        return  # 直接返回，不显示输入表单
    
    # 如果返回后，显示原始答案和相关问题列表
    if not st.session_state.get("qa_show_analysis", False) and st.session_state.get("current_answer") and st.session_state.get("follow_up_questions_list"):
        # 显示原始答案
        st.markdown("### 回答：")
        st.markdown(st.session_state.get("current_answer", ""))
        
        # 显示相关问题列表
        follow_up_questions_list = st.session_state.get("follow_up_questions_list", [])
        if follow_up_questions_list:
            st.markdown("---")
            st.markdown("### 相关思考问题")
            st.markdown("基于您的问题，您可以继续深入探讨以下方面：")
            for i, follow_q in enumerate(follow_up_questions_list, 1):
                if st.button(f"📌 {follow_q}", key=f"follow_up_{i}", use_container_width=False):
                    # 切换到深度分析状态
                    st.session_state["qa_show_analysis"] = True
                    st.session_state["current_follow_up_question"] = follow_q
                    st.session_state["qa_question_input"] = follow_q
                    # 设置自动触发问答
                    st.session_state["auto_trigger_qa"] = True
                    st.session_state["qa_input_key_suffix"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    st.rerun()
        
        # 添加返回按钮，返回到输入界面
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← 返回输入界面", key="back_to_input", use_container_width=True):
                # 清除相关状态，返回到输入界面
                st.session_state["current_answer"] = None
                st.session_state["follow_up_questions_list"] = None
                st.session_state["original_question"] = None
                st.session_state["qa_question_input"] = ""
                st.session_state["qa_input_key_suffix"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
                st.rerun()
        return  # 显示相关问题列表后返回
    
    # 问题分类选择
    st.markdown("**问题类型：**")
    question_type = st.radio("问题类型", ["日常生活风水", "周公解梦", "日常提问", "综合问题"], horizontal=True, label_visibility="collapsed")
    
    # 检查是否需要自动触发问答（来自点击相关问题）
    auto_trigger = st.session_state.get("auto_trigger_qa", False)
    current_follow_up = st.session_state.get("current_follow_up_question", "")
    
    # 如果是在深度分析状态，隐藏输入框，直接使用相关问题
    if st.session_state.get("qa_show_analysis", False) and current_follow_up:
        question = current_follow_up
        # 不显示输入框，直接使用相关问题
    else:
        # 问题输入 - 正常显示输入框
        input_key = "qa_question_input"
        if "qa_input_key_suffix" in st.session_state:
            input_key = f"qa_question_input_{st.session_state['qa_input_key_suffix']}"
            del st.session_state["qa_input_key_suffix"]
        question = st.text_input("请输入您的问题：", value=st.session_state.get("qa_question_input", ""), placeholder=get_placeholder_by_type(question_type), key=input_key)
    
    # 如果是在深度分析状态且需要自动触发，直接执行问答，不显示输入表单
    if st.session_state.get("qa_show_analysis", False) and current_follow_up and auto_trigger:
        # 清除自动触发标志
        st.session_state.auto_trigger_qa = False
        # 直接执行问答逻辑，不显示输入表单
        if ENHANCED_QA_AVAILABLE:
            try:
                # 显示思考过程容器
                st.markdown("### 回答：")
                st.markdown("**智能思考过程：**")
                
                # 生成思考过程
                question_type_detected = "综合问题"
                if any(keyword in question for keyword in ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房"]):
                    question_type_detected = "日常生活风水"
                elif any(keyword in question for keyword in ["梦", "梦见", "周公", "解梦"]):
                    question_type_detected = "周公解梦"
                elif any(keyword in question for keyword in ["健康", "饮食", "运动", "工作", "学习", "情感", "家庭", "朋友", "爱情"]):
                    question_type_detected = "日常提问"
                
                thinking_process = enhanced_qa.generate_thinking_process(question, question_type_detected)
                thinking_steps = thinking_process.split("\n\n")
                
                # 逐步显示思考过程
                progress_bar = st.progress(0)
                thinking_placeholder = st.empty()
                
                for i, step in enumerate(thinking_steps):
                    thinking_placeholder.markdown(step)
                    progress_bar.progress((i + 1) / len(thinking_steps))
                    time.sleep(0.5)  # 每步间隔0.5秒，加快显示速度
                
                # 清除进度条
                progress_bar.empty()
                
                # 显示"正在生成答案..."并添加进度指示
                st.markdown("**正在生成答案...**")
                answer_placeholder = st.empty()
                
                # 添加加载动画
                loading_placeholder = st.empty()
                loading_placeholder.markdown("🔄 正在调用AI模型进行分析...")
                
                # 调用增强问答系统，传递原始问题作为上下文（如果是相关问题的深入分析）
                original_question = st.session_state.get("original_question", "")
                
                # 判断问题类型：只有解梦/占卜类问题才传递原始问题上下文
                is_dream_or_divination = any(keyword in question.lower() for keyword in ["梦", "梦见", "周公", "解梦", "占卜", "卦", "卜", "算", "预测"])
                is_fengshui = any(keyword in question.lower() for keyword in ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房", "财位", "绿植", "摆放"])
                
                if original_question and original_question != question and is_dream_or_divination and not is_fengshui:
                    # 如果是解梦/占卜类问题的深入分析，构建包含原始问题的上下文
                    context_question = f"原始问题：{original_question}\n\n当前分析问题：{question}\n\n请基于原始问题，针对当前分析问题进行深度专业化分析。"
                    result = enhanced_qa.answer_question(context_question)
                else:
                    # 风水问题或其他问题直接回答，不传递原始问题上下文
                    result = enhanced_qa.answer_question(question)
                
                # 清除加载提示
                loading_placeholder.empty()
                
                # 提取答案部分（去掉思考过程）
                answer_lines = result["answer"].split("\n\n")
                answer_start = 0
                for i, line in enumerate(answer_lines):
                    if "智能分析结果" in line:
                        answer_start = i
                        break
                
                if answer_start > 0:
                    answer_content = "\n\n".join(answer_lines[answer_start:])
                else:
                    answer_content = result["answer"]
                
                # 如果是相关问题的深入分析，优化答案显示格式
                if original_question and original_question != question:
                    # 识别原始问题的类型
                    question_type = detect_question_type(original_question)
                    
                    # 根据问题类型生成专业化的分析标题
                    if "吉凶" in question or "吉凶程度" in question:
                        title = "吉凶分析结果"
                        if question_type == "梦境":
                            context_text = f"基于您的梦境「{original_question}」"
                        elif question_type == "风水":
                            context_text = f"基于您的风水问题「{original_question}」"
                        elif question_type == "日常":
                            context_text = f"基于您的问题「{original_question}」"
                        else:
                            context_text = f"基于您的问题「{original_question}」"
                        answer_content = f"## **{title}**\n\n{context_text}，吉凶评估如下：\n\n{answer_content}"
                    elif "细节" in question or "含义" in question:
                        if question_type == "梦境":
                            title = "梦境细节深度解析"
                            context_text = f"基于您的梦境「{original_question}」"
                        elif question_type == "风水":
                            title = "风水布局深度解析"
                            context_text = f"基于您的风水问题「{original_question}」"
                        elif question_type == "日常":
                            title = "问题细节深度解析"
                            context_text = f"基于您的问题「{original_question}」"
                        else:
                            title = "细节深度解析"
                            context_text = f"基于您的问题「{original_question}」"
                        answer_content = f"## **{title}**\n\n{context_text}，关键元素分析如下：\n\n{answer_content}"
                    elif "应对" in question or "策略" in question or "如何" in question:
                        title = "针对性应对方案"
                        if question_type == "梦境":
                            context_text = f"基于您的梦境「{original_question}」"
                        elif question_type == "风水":
                            context_text = f"基于您的风水问题「{original_question}」"
                        elif question_type == "日常":
                            context_text = f"基于您的问题「{original_question}」"
                        else:
                            context_text = f"基于您的问题「{original_question}」"
                        answer_content = f"## **{title}**\n\n{context_text}，建议采取以下措施：\n\n{answer_content}"
                
                # 保存分析内容并切换到分析界面
                st.session_state["qa_analysis_content"] = answer_content
                st.rerun()
                
            except Exception as e:
                st.error(f"问答系统出错: {e}")
                # 回退到默认问答
                answer = rag_qa_answer(question)
                st.markdown("### 回答：")
                st.markdown(answer)
        return  # 直接返回，不显示输入表单
    
    # 正常显示输入表单
    # 显示原始问题（如果有相关问题的上下文）
    original_question = st.session_state.get("original_question", "")
    if original_question and auto_trigger and question != original_question:
        st.info(f"📌 **当前分析问题：** {question}\n\n**基于原始问题：** {original_question}")
    
    # 提问按钮或自动触发
    if auto_trigger or st.button("提问", key="ask_question"):
        if auto_trigger:
            st.session_state.auto_trigger_qa = False
        if question:
            if ENHANCED_QA_AVAILABLE:
                try:
                    # 显示思考过程容器
                    st.markdown("### 回答：")
                    st.markdown("**智能思考过程：**")
                    
                    # 生成思考过程
                    question_type_detected = "综合问题"
                    if any(keyword in question for keyword in ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房"]):
                        question_type_detected = "日常生活风水"
                    elif any(keyword in question for keyword in ["梦", "梦见", "周公", "解梦"]):
                        question_type_detected = "周公解梦"
                    elif any(keyword in question for keyword in ["健康", "饮食", "运动", "工作", "学习", "情感", "家庭", "朋友", "爱情"]):
                        question_type_detected = "日常提问"
                    
                    thinking_process = enhanced_qa.generate_thinking_process(question, question_type_detected)
                    thinking_steps = thinking_process.split("\n\n")
                    
                    # 逐步显示思考过程
                    progress_bar = st.progress(0)
                    thinking_placeholder = st.empty()
                    
                    for i, step in enumerate(thinking_steps):
                        thinking_placeholder.markdown(step)
                        progress_bar.progress((i + 1) / len(thinking_steps))
                        time.sleep(0.5)  # 每步间隔0.5秒，加快显示速度
                    
                    # 清除进度条
                    progress_bar.empty()
                    
                    # 显示"正在生成答案..."并添加进度指示
                    st.markdown("**正在生成答案...**")
                    answer_placeholder = st.empty()
                    
                    # 添加加载动画
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("🔄 正在调用AI模型进行分析...")
                    
                    # 调用增强问答系统，传递原始问题作为上下文（如果是相关问题的深入分析）
                    original_question = st.session_state.get("original_question", "")
                    if original_question and original_question != question:
                        # 如果是相关问题的深入分析，构建包含原始问题的上下文
                        context_question = f"原始问题：{original_question}\n\n当前分析问题：{question}\n\n请基于原始问题，针对当前分析问题进行深度专业化分析。"
                        result = enhanced_qa.answer_question(context_question)
                    else:
                        result = enhanced_qa.answer_question(question)
                    
                    # 清除加载提示
                    loading_placeholder.empty()
                    
                    # 提取答案部分（去掉思考过程）
                    answer_lines = result["answer"].split("\n\n")
                    answer_start = 0
                    for i, line in enumerate(answer_lines):
                        if "智能分析结果" in line:
                            answer_start = i
                            break
                    
                    if answer_start > 0:
                        answer_content = "\n\n".join(answer_lines[answer_start:])
                    else:
                        answer_content = result["answer"]
                    
                    # 如果是相关问题的深入分析，优化答案显示格式
                    if original_question and original_question != question:
                        # 识别原始问题的类型
                        question_type = detect_question_type(original_question)
                        
                        # 根据问题类型生成专业化的分析标题
                        if "吉凶" in question or "吉凶程度" in question:
                            title = "吉凶分析结果"
                            if question_type == "梦境":
                                context_text = f"基于您的梦境「{original_question}」"
                            elif question_type == "风水":
                                context_text = f"基于您的风水问题「{original_question}」"
                            elif question_type == "日常":
                                context_text = f"基于您的问题「{original_question}」"
                            else:
                                context_text = f"基于您的问题「{original_question}」"
                            answer_content = f"## **{title}**\n\n{context_text}，吉凶评估如下：\n\n{answer_content}"
                        elif "细节" in question or "含义" in question:
                            if question_type == "梦境":
                                title = "梦境细节深度解析"
                                context_text = f"基于您的梦境「{original_question}」"
                            elif question_type == "风水":
                                title = "风水布局深度解析"
                                context_text = f"基于您的风水问题「{original_question}」"
                            elif question_type == "日常":
                                title = "问题细节深度解析"
                                context_text = f"基于您的问题「{original_question}」"
                            else:
                                title = "细节深度解析"
                                context_text = f"基于您的问题「{original_question}」"
                            answer_content = f"## **{title}**\n\n{context_text}，关键元素分析如下：\n\n{answer_content}"
                        elif "应对" in question or "策略" in question or "如何" in question:
                            title = "针对性应对方案"
                            if question_type == "梦境":
                                context_text = f"基于您的梦境「{original_question}」"
                            elif question_type == "风水":
                                context_text = f"基于您的风水问题「{original_question}」"
                            elif question_type == "日常":
                                context_text = f"基于您的问题「{original_question}」"
                            else:
                                context_text = f"基于您的问题「{original_question}」"
                            answer_content = f"## **{title}**\n\n{context_text}，建议采取以下措施：\n\n{answer_content}"
                    
                    # 显示最终答案
                    answer_placeholder.markdown(answer_content)
                    
                    # 保存原始问题（如果是第一次提问，保存为原始问题）
                    if 'original_question' not in st.session_state or not st.session_state.get('original_question'):
                        st.session_state.original_question = question
                    
                    # 正常显示答案和相关问题
                    # 生成逻辑思维链 - 深入或衍生问题
                    follow_up_questions = generate_follow_up_questions(question, answer_content)
                    if follow_up_questions:
                        # 保存相关问题列表供后续使用
                        st.session_state["follow_up_questions_list"] = follow_up_questions
                        st.session_state["current_answer"] = answer_content
                        
                        st.markdown("---")
                        st.markdown("### 相关思考问题")
                        st.markdown("基于您的问题，您可以继续深入探讨以下方面：")
                        for i, follow_q in enumerate(follow_up_questions, 1):
                            if st.button(f"📌 {follow_q}", key=f"follow_up_{i}", use_container_width=False):
                                # 切换到深度分析状态
                                st.session_state["qa_show_analysis"] = True
                                st.session_state["current_follow_up_question"] = follow_q
                                st.session_state["qa_question_input"] = follow_q
                                # 设置自动触发问答
                                st.session_state["auto_trigger_qa"] = True
                                st.session_state["qa_input_key_suffix"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
                                st.rerun()
                    
                except Exception as e:
                    st.error(f"问答系统出错: {e}")
                    # 回退到默认问答
                    answer = rag_qa_answer(question)
                    st.markdown("### 回答：")
                    st.markdown(answer)
            else:
                # 使用默认问答
                answer = rag_qa_answer(question)
                st.markdown("### 回答：")
                st.markdown(answer)
        else:
            st.warning("请输入问题")
    
    # 示例问题
    st.markdown("### 示例问题：")
    examples = get_examples_by_type(question_type)
    for i, example in enumerate(examples):
        if st.button(f"示例{i+1}: {example}", key=f"example_{i}"):
            st.session_state.example_question = example
            st.rerun()
    
    # 如果点击了示例问题
    if hasattr(st.session_state, 'example_question'):
        question = st.session_state.example_question
        if ENHANCED_QA_AVAILABLE:
            try:
                # 显示思考过程容器
                st.markdown("### 回答：")
                st.markdown("**智能思考过程：**")
                
                # 生成思考过程
                question_type_detected = "综合问题"
                if any(keyword in question for keyword in ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房"]):
                    question_type_detected = "日常生活风水"
                elif any(keyword in question for keyword in ["梦", "梦见", "周公", "解梦"]):
                    question_type_detected = "周公解梦"
                elif any(keyword in question for keyword in ["健康", "饮食", "运动", "工作", "学习", "情感", "家庭", "朋友", "爱情"]):
                    question_type_detected = "日常提问"
                
                thinking_process = enhanced_qa.generate_thinking_process(question, question_type_detected)
                thinking_steps = thinking_process.split("\n\n")
                
                # 逐步显示思考过程
                progress_bar = st.progress(0)
                thinking_placeholder = st.empty()
                
                for i, step in enumerate(thinking_steps):
                    thinking_placeholder.markdown(step)
                    progress_bar.progress((i + 1) / len(thinking_steps))
                    time.sleep(0.5)  # 每步间隔0.5秒，加快显示速度
                
                # 清除进度条
                progress_bar.empty()
                
                # 显示"正在生成答案..."并添加进度指示
                st.markdown("**正在生成答案...**")
                answer_placeholder = st.empty()
                
                # 添加加载动画
                loading_placeholder = st.empty()
                loading_placeholder.markdown("🔄 正在调用AI模型进行分析...")
                
                # 调用增强问答系统
                result = enhanced_qa.answer_question(question)
                
                # 清除加载提示
                loading_placeholder.empty()
                
                # 提取答案部分（去掉思考过程）
                answer_lines = result["answer"].split("\n\n")
                answer_start = 0
                for i, line in enumerate(answer_lines):
                    if "智能分析结果" in line:
                        answer_start = i
                        break
                
                if answer_start > 0:
                    answer_content = "\n\n".join(answer_lines[answer_start:])
                else:
                    answer_content = result["answer"]
                
                # 显示最终答案
                answer_placeholder.markdown(answer_content)
                
            except Exception as e:
                st.error(f"问答系统出错: {e}")
        else:
            answer = rag_qa_answer(question)
            st.markdown("### 回答：")
            st.markdown(answer)
        
        # 清除示例问题
        del st.session_state.example_question
    
    # 返回首页按钮
    st.markdown("---")
    if st.button("返回首页", key="back_home_qa", use_container_width=True):
        st.session_state.current_page = "home"
        st.rerun()

def detect_question_type(question):
    """识别问题类型（风水、梦境、日常等）"""
    if not question:
        return "综合"
    
    question_lower = question.lower()
    
    # 风水问题识别
    fengshui_keywords = ["风水", "朝向", "楼层", "家具", "客厅", "卧室", "厨房", "财位", "五行", "方位", "属", "生肖", "买房", "装修", "布局"]
    if any(keyword in question_lower for keyword in fengshui_keywords):
        return "风水"
    
    # 梦境问题识别
    dream_keywords = ["梦", "梦见", "周公", "解梦", "梦境"]
    if any(keyword in question_lower for keyword in dream_keywords):
        return "梦境"
    
    # 日常问题识别
    daily_keywords = ["健康", "饮食", "运动", "工作", "学习", "情感", "家庭", "朋友", "爱情", "事业", "职业", "升职", "跳槽", "如何", "怎样", "怎么", "怎么办"]
    if any(keyword in question_lower for keyword in daily_keywords):
        return "日常"
    
    # 默认返回综合
    return "综合"

def get_placeholder_by_type(question_type):
    """根据问题类型获取占位符"""
    placeholders = {
        "日常生活风水": "例如：我家客厅的沙发应该怎么摆放？",
        "周公解梦": "例如：我梦见了一条龙，这是什么意思？",
        "日常提问": "例如：如何提高工作效率？",
        "综合问题": "例如：请帮我分析一下我的运势"
    }
    return placeholders.get(question_type, "请输入您的问题")

def get_examples_by_type(question_type):
    """根据问题类型获取示例问题"""
    examples = {
        "日常生活风水": [
            "客厅沙发应该怎么摆放？",
            "卧室床头朝向有什么讲究？",
            "厨房炉灶和水槽的位置关系？",
            "买房时楼层选择有什么建议？"
        ],
        "周公解梦": [
            "梦见龙是什么意思？",
            "梦见蛇有什么寓意？",
            "梦见水代表什么？",
            "梦见老人有什么含义？"
        ],
        "日常提问": [
            "如何提高工作效率？",
            "怎样保持身心健康？",
            "如何改善人际关系？",
            "怎样平衡工作和生活？"
        ],
        "综合问题": [
            "请分析一下我的运势",
            "如何选择合适的工作？",
            "怎样规划人生发展？",
            "如何提升个人魅力？"
        ]
    }
    return examples.get(question_type, ["请输入您的问题"])

if __name__ == "__main__":
    main()
