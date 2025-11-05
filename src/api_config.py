"""
API密钥配置管理
统一管理项目中所有API密钥
"""

import os

class APIConfig:
    """API配置管理类"""
    
    # Qwen API配置
    QWEN_API_KEY = "sk-db8a829806aa49a980f4d2992aef56df"
    QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY = "sk-05d426cc8cdf4f84bc347eddc5ecdc28"
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # 翻译API配置（使用Qwen作为默认翻译服务）
    TRANSLATION_API_KEY = QWEN_API_KEY
    TRANSLATION_API_URL = QWEN_API_URL
    
    @classmethod
    def get_qwen_config(cls):
        """获取Qwen API配置"""
        return {
            "api_key": cls.QWEN_API_KEY,
            "api_url": cls.QWEN_API_URL
        }
    
    @classmethod
    def get_deepseek_config(cls):
        """获取DeepSeek API配置"""
        return {
            "api_key": cls.DEEPSEEK_API_KEY,
            "api_url": cls.DEEPSEEK_API_URL
        }
    
    @classmethod
    def get_translation_config(cls):
        """获取翻译API配置"""
        return {
            "api_key": cls.TRANSLATION_API_KEY,
            "api_url": cls.TRANSLATION_API_URL
        }
    
    @classmethod
    def setup_environment_variables(cls):
        """设置环境变量"""
        os.environ['QWEN_API_KEY'] = cls.QWEN_API_KEY
        os.environ['DEEPSEEK_API_KEY'] = cls.DEEPSEEK_API_KEY
        os.environ['TRANSLATION_API_KEY'] = cls.TRANSLATION_API_KEY
        os.environ['TRANSLATION_API_URL'] = cls.TRANSLATION_API_URL
