"""
文档解析与翻译模块
支持PDF文本提取、文言文翻译、QA知识库生成
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings
import sys
warnings.filterwarnings('ignore')

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .api_config import APIConfig

# PDF处理
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import fitz  # PyMuPDF

# 图像处理
from PIL import Image
import pytesseract

# 中文处理
import jieba
import opencc

# 编码检测
import chardet

# 网络请求
import requests
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, output_dir: str = "knowledge_base"):
        """初始化文档处理器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化中文处理工具
        self.cc = opencc.OpenCC('t2s')  # 繁体转简体
        jieba.initialize()
        
        # 翻译器配置
        self.translator = None
        self._setup_translator()
        
        logger.info(f"文档处理器初始化完成，输出目录: {self.output_dir}")
    
    def _setup_translator(self):
        """设置翻译器"""
        # 使用统一的API配置
        APIConfig.setup_environment_variables()
        translation_config = APIConfig.get_translation_config()
        
        if translation_config["api_key"] and translation_config["api_url"]:
            self.translator = APITranslator(translation_config["api_url"], translation_config["api_key"])
            logger.info("使用API翻译器")
        else:
            self.translator = LocalTranslator()
            logger.info("使用本地翻译器（基础功能）")
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """提取PDF文本"""
        try:
            # 方法1: 使用pdfminer
            text = extract_text(pdf_path, laparams=LAParams())
            if text.strip():
                return text
            
            # 方法2: 使用PyMuPDF
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            return text
            
        except Exception as e:
            logger.error(f"PDF文本提取失败 {pdf_path}: {e}")
            return ""
    
    def extract_pdf_images(self, pdf_path: str) -> List[str]:
        """提取PDF中的图像并OCR识别"""
        try:
            doc = fitz.open(pdf_path)
            texts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # 不是CMYK
                        img_data = pix.tobytes("png")
                        img_path = self.output_dir / f"temp_img_{page_num}_{img_index}.png"
                        
                        with open(img_path, "wb") as f:
                            f.write(img_data)
                        
                        # OCR识别
                        ocr_text = pytesseract.image_to_string(Image.open(img_path), lang='chi_sim+chi_tra')
                        if ocr_text.strip():
                            texts.append(ocr_text)
                        
                        # 清理临时文件
                        img_path.unlink()
                    
                    pix = None
            
            doc.close()
            return texts
            
        except Exception as e:
            logger.error(f"PDF图像OCR失败 {pdf_path}: {e}")
            return []
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """处理PDF文件"""
        logger.info(f"开始处理PDF: {pdf_path}")
        
        # 提取文本
        text = self.extract_pdf_text(pdf_path)
        
        # 提取图像OCR文本
        image_texts = self.extract_pdf_images(pdf_path)
        
        # 合并所有文本
        all_text = text + "\n".join(image_texts)
        
        # 文本预处理
        processed_text = self._preprocess_text(all_text)
        
        result = {
            'file_path': pdf_path,
            'file_name': Path(pdf_path).name,
            'raw_text': all_text,
            'processed_text': processed_text,
            'text_length': len(processed_text),
            'image_count': len(image_texts)
        }
        
        logger.info(f"PDF处理完成: {pdf_path}, 文本长度: {len(processed_text)}")
        return result
    
    def process_txt(self, txt_path: str) -> Dict[str, Any]:
        """处理TXT文件"""
        logger.info(f"开始处理TXT: {txt_path}")
        
        try:
            # 检测编码
            with open(txt_path, 'rb') as f:
                raw_data = f.read()
            
            # 使用chardet检测编码
            encoding_result = chardet.detect(raw_data)
            detected_encoding = encoding_result.get('encoding', 'utf-8')
            confidence = encoding_result.get('confidence', 0)
            
            logger.info(f"检测到编码: {detected_encoding}, 置信度: {confidence:.2f}")
            
            # 尝试多种编码
            encodings_to_try = [detected_encoding, 'utf-8', 'gbk', 'gb2312', 'big5', 'latin1']
            
            text = ""
            for encoding in encodings_to_try:
                if encoding:
                    try:
                        text = raw_data.decode(encoding)
                        logger.info(f"成功使用编码 {encoding} 读取文件")
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
            
            if not text:
                # 如果所有编码都失败，使用错误处理
                text = raw_data.decode('utf-8', errors='replace')
                logger.warning("使用UTF-8错误处理模式读取文件")
            
            # 文本预处理
            processed_text = self._preprocess_text(text)
            
            result = {
                'file_path': txt_path,
                'file_name': Path(txt_path).name,
                'raw_text': text,
                'processed_text': processed_text,
                'text_length': len(processed_text),
                'detected_encoding': detected_encoding,
                'encoding_confidence': confidence
            }
            
            logger.info(f"TXT处理完成: {txt_path}, 文本长度: {len(processed_text)}")
            return result
            
        except Exception as e:
            logger.error(f"TXT文件处理失败 {txt_path}: {e}")
            return {}
    
    def process_doc(self, doc_path: str) -> Dict[str, Any]:
        """处理DOC文件"""
        logger.info(f"开始处理DOC: {doc_path}")
        
        try:
            # 简单的DOC文件处理（需要python-docx库）
            import docx
            
            doc = docx.Document(doc_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # 文本预处理
            processed_text = self._preprocess_text(text)
            
            result = {
                'file_path': doc_path,
                'file_name': Path(doc_path).name,
                'raw_text': text,
                'processed_text': processed_text,
                'text_length': len(processed_text)
            }
            
            logger.info(f"DOC处理完成: {doc_path}, 文本长度: {len(processed_text)}")
            return result
            
        except ImportError:
            logger.warning("python-docx库未安装，跳过DOC文件处理")
            return {}
        except Exception as e:
            logger.error(f"DOC文件处理失败 {doc_path}: {e}")
            return {}
    
    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理空白字符
        text = ' '.join(text.split())
        
        # 繁体转简体
        text = self.cc.convert(text)
        
        # 移除特殊字符
        import re
        text = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf\w\s，。！？；：""''（）【】《》]', '', text)
        
        return text
    
    def translate_text(self, text: str) -> str:
        """翻译文言文"""
        if not self.translator:
            return text
        
        try:
            return self.translator.translate(text)
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return text
    
    def segment_text(self, text: str, max_length: int = 500) -> List[str]:
        """文本分段"""
        # 使用jieba分词
        sentences = jieba.cut(text)
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if len(current_segment + sentence) > max_length:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def generate_qa_pairs(self, segments: List[str]) -> List[Dict[str, str]]:
        """生成问答对"""
        qa_pairs = []
        
        for i, segment in enumerate(segments):
            if len(segment.strip()) < 10:  # 跳过太短的段落
                continue
            
            # 生成问题
            question = self._generate_question(segment, i)
            
            # 生成答案
            answer = self._generate_answer(segment)
            
            qa_pairs.append({
                'id': f"qa_{i:04d}",
                'question': question,
                'answer': answer,
                'source_text': segment,
                'segment_index': i
            })
        
        return qa_pairs
    
    def _generate_question(self, text: str, index: int) -> str:
        """生成问题"""
        # 简单的问题生成策略
        if "卦" in text:
            return f"关于第{index+1}段中的卦象内容，请详细解释"
        elif "爻" in text:
            return f"第{index+1}段中提到的爻辞含义是什么？"
        elif "易" in text:
            return f"第{index+1}段中的易经理论如何理解？"
        else:
            return f"请解释第{index+1}段的内容要点"
    
    def _generate_answer(self, text: str) -> str:
        """生成答案"""
        # 简单的答案生成策略
        return f"根据原文内容：{text[:200]}..."
    
    def save_knowledge_base(self, qa_pairs: List[Dict[str, str]], filename: str = "knowledge_base.jsonl"):
        """保存知识库"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for qa in qa_pairs:
                f.write(json.dumps(qa, ensure_ascii=False) + '\n')
        
        logger.info(f"知识库已保存到: {output_path}")
        return output_path
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """处理单个文档"""
        logger.info(f"开始处理文档: {file_path}")
        
        # 根据文件扩展名选择处理方法
        if file_path.endswith('.pdf'):
            doc_data = self.process_pdf(file_path)
        elif file_path.endswith('.txt'):
            doc_data = self.process_txt(file_path)
        elif file_path.endswith('.doc') or file_path.endswith('.docx'):
            doc_data = self.process_doc(file_path)
        else:
            logger.warning(f"不支持的文件格式: {file_path}")
            return {}
        
        if not doc_data:
            logger.warning(f"文档处理失败: {file_path}")
            return {}
        
        # 翻译文本
        translated_text = self.translate_text(doc_data['processed_text'])
        doc_data['translated_text'] = translated_text
        
        # 分段
        segments = self.segment_text(translated_text)
        doc_data['segments'] = segments
        
        # 生成QA对
        qa_pairs = self.generate_qa_pairs(segments)
        doc_data['qa_pairs'] = qa_pairs
        
        # 保存结果
        output_file = self.output_dir / f"{Path(file_path).stem}_processed.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"文档处理完成: {file_path}, QA对数量: {len(qa_pairs)}")
        return doc_data

class APITranslator:
    """API翻译器"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
    
    def translate(self, text: str) -> str:
        """使用API翻译"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'text': text,
                'source_lang': 'zh',
                'target_lang': 'zh',
                'style': 'classical'
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('translated_text', text)
            
        except Exception as e:
            logger.error(f"API翻译失败: {e}")
            return text

class LocalTranslator:
    """本地翻译器（基础功能）"""
    
    def __init__(self):
        self.cc = opencc.OpenCC('t2s')
    
    def translate(self, text: str) -> str:
        """本地翻译（主要是繁简转换和基础处理）"""
        # 繁简转换
        text = self.cc.convert(text)
        
        # 基础文言文处理
        text = self._basic_classical_processing(text)
        
        return text
    
    def _basic_classical_processing(self, text: str) -> str:
        """基础文言文处理"""
        # 这里可以添加更复杂的文言文处理逻辑
        # 目前只是简单的繁简转换
        return text

def main():
    """主函数"""
    print("文档解析与翻译系统")
    print("=" * 60)
    
    # 初始化处理器
    processor = DocumentProcessor()
    
    # 处理目标文件
    target_files = [
        "《六爻古籍经典合集》(1).pdf",
        "京氏易精粹全5册/《京氏易傳》.pdf",
        "京氏易精粹全5册/《京氏易精粹 5 易隐·易冒》郑同点校.pdf",
        "京氏易精粹全5册/《六爻古籍经典合集》-火珠林.pdf",
        "京氏易精粹全5册/《黄金策》.doc",
        "京氏易精粹全5册/京氏易传-汉-京房.txt",
        "京氏易精粹全5册/京氏易传导读（3星）.pdf",
        "京氏易精粹全5册/京氏易精粹  1  京氏易传、火珠林、黄金策.pdf",
        "京氏易精粹全5册/京氏易精粹  2  易林补遗.pdf",
        "京氏易精粹全5册/京氏易精粹  3  增删卜易·海底眼.pdf",
        "京氏易精粹全5册/京氏易精粹  4  野鹤老人占卜全书.pdf"
    ]
    
    all_qa_pairs = []
    
    for file_path in target_files:
        if os.path.exists(file_path):
            print(f"\n处理文件: {file_path}")
            try:
                result = processor.process_document(file_path)
                if result:
                    all_qa_pairs.extend(result.get('qa_pairs', []))
                    print(f"  处理完成，生成 {len(result.get('qa_pairs', []))} 个QA对")
                else:
                    print(f"  处理失败")
            except Exception as e:
                print(f"  处理出错: {e}")
        else:
            print(f"文件不存在: {file_path}")
    
    # 保存完整知识库
    if all_qa_pairs:
        processor.save_knowledge_base(all_qa_pairs, "complete_knowledge_base.jsonl")
        print(f"\n知识库生成完成，总共 {len(all_qa_pairs)} 个QA对")
    else:
        print("\n没有生成任何QA对")

if __name__ == "__main__":
    main()
