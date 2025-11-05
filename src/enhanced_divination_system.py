"""
增强解卦系统 - 结合本地知识库提供丰富的解卦内容
"""
import json
import os
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

class EnhancedDivinationSystem:
    """增强解卦系统"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """加载本地知识库"""
        try:
            # 获取项目根目录（向上两级：src -> yingzaiyice -> 项目根目录）
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 尝试多个可能的知识库路径
            knowledge_base_paths = [
                os.path.join(base_dir, "knowledge_base"),
                os.path.join(os.path.dirname(base_dir), "knowledge_base"),
                "knowledge_base"
            ]
            
            knowledge_base_dir = None
            for path in knowledge_base_paths:
                if os.path.exists(path):
                    knowledge_base_dir = path
                    break
            
            if not knowledge_base_dir:
                print("警告: 未找到知识库目录")
                return
            
            # 加载QA格式的知识库
            qa_file = os.path.join(knowledge_base_dir, "《六爻古籍经典合集》_qa.json")
            if os.path.exists(qa_file):
                with open(qa_file, 'r', encoding='utf-8') as f:
                    qa_data = json.load(f)
                    self.knowledge_base['qa'] = qa_data
            
            # 加载其他知识库文件
            knowledge_files = [
                "《京氏易傳》_processed.json",
                "京氏易精粹  1  京氏易传、火珠林、黄金策_processed.json",
                "京氏易精粹  2  易林补遗_processed.json",
                "京氏易精粹  3  增删卜易·海底眼_processed.json",
                "京氏易精粹  4  野鹤老人占卜全书_processed.json"
            ]
            
            for filename in knowledge_files:
                file_path = os.path.join(knowledge_base_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.knowledge_base[filename] = data
                        
        except Exception as e:
            print(f"加载知识库时出错: {e}")
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict]:
        """在知识库中搜索相关内容"""
        results = []
        
        # 在QA知识库中搜索
        if 'qa' in self.knowledge_base:
            qa_data = self.knowledge_base['qa']
            if 'qa_pairs' in qa_data:
                for qa_pair in qa_data['qa_pairs']:
                    if query in qa_pair.get('question', '') or query in qa_pair.get('answer', ''):
                        results.append({
                            'type': 'qa',
                            'question': qa_pair.get('question', ''),
                            'answer': qa_pair.get('answer', ''),
                            'source': qa_pair.get('source', '')
                        })
                        if len(results) >= max_results:
                            break
        
        # 在其他知识库中搜索
        for filename, data in self.knowledge_base.items():
            if filename == 'qa':
                continue
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        text = item.get('processed_text', '') or item.get('raw_text', '')
                        if query in text:
                            results.append({
                                'type': 'text',
                                'content': text[:500] + '...' if len(text) > 500 else text,
                                'source': filename
                            })
                            if len(results) >= max_results:
                                break
        
        return results
    
    def get_enhanced_divination_result(self, gua_name: str, gua_symbol: str, event: str = "") -> Dict[str, Any]:
        """获取增强的解卦结果"""
        
        # 基础解卦信息
        base_result = {
            "gua_name": gua_name,
            "gua_symbol": gua_symbol,
            "event": event,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 1. 白话文解释
        base_result["plain_explanation"] = self.get_plain_explanation(gua_name, gua_symbol)
        
        # 2. 象辞解释
        base_result["xiang_ci"] = self.get_xiang_ci(gua_name, gua_symbol)
        
        # 3. 邵雍河洛理数爻辞解释
        base_result["shao_yong_explanation"] = self.get_shao_yong_explanation(gua_name, gua_symbol)
        
        # 4. 傅佩荣解卦手册
        base_result["fu_peirong_handbook"] = self.get_fu_peirong_handbook(gua_name, gua_symbol)
        
        # 5. 卦辞参考
        base_result["gua_ci_reference"] = self.get_gua_ci_reference(gua_name, gua_symbol)
        
        # 6. 变卦分析
        base_result["changing_gua"] = self.get_changing_gua_analysis(gua_name, gua_symbol)
        
        # 7. 解卦步骤
        base_result["divination_steps"] = self.get_divination_steps()
        
        return base_result
    
    def get_plain_explanation(self, gua_name: str, gua_symbol: str) -> str:
        """获取白话文解释"""
        # 搜索相关知识
        search_results = self.search_knowledge(f"{gua_name} 白话文 解释", 3)
        
        if search_results:
            explanations = []
            for result in search_results:
                if result['type'] == 'qa':
                    explanations.append(result['answer'])
                else:
                    explanations.append(result['content'])
            
            return " ".join(explanations[:2])  # 取前两个结果
        
        # 默认解释
        default_explanations = {
            "乾卦": "乾卦象征天，表示刚健有力，积极向上。此卦象表明当前形势有利，适合积极行动，但需要保持谦逊和谨慎。",
            "坤卦": "坤卦象征地，表示柔顺包容，厚德载物。此卦象表明需要以柔克刚，以德服人，保持耐心和包容。",
            "屯卦": "屯卦象征初生艰难，表示事物刚开始发展时遇到的困难。此卦象表明需要克服困难，坚持不懈。",
            "蒙卦": "蒙卦象征启蒙教育，表示需要学习和成长。此卦象表明应该虚心学习，寻求指导，不可自满。",
            "需卦": "需卦象征等待时机，表示需要耐心等待合适的时机。此卦象表明不可急躁，要等待时机成熟。",
            "讼卦": "讼卦象征争讼，表示可能遇到争议或冲突。此卦象表明需要谨慎处理人际关系，避免不必要的争执。"
        }
        
        return default_explanations.get(gua_name, f"根据{gua_name}的卦象，建议保持中庸之道，顺应自然规律。")
    
    def get_xiang_ci(self, gua_name: str, gua_symbol: str) -> str:
        """获取象辞解释"""
        search_results = self.search_knowledge(f"{gua_name} 象辞", 2)
        
        if search_results:
            for result in search_results:
                if "象曰" in result.get('content', '') or "象曰" in result.get('answer', ''):
                    return result.get('answer', result.get('content', ''))
        
        # 默认象辞
        default_xiang_ci = {
            "乾卦": "象曰：天行健，君子以自强不息。",
            "坤卦": "象曰：地势坤，君子以厚德载物。",
            "屯卦": "象曰：云雷屯，君子以经纶。",
            "蒙卦": "象曰：山下出泉，蒙。君子以果行育德。",
            "需卦": "象曰：云上于天，需。君子以饮食宴乐。",
            "讼卦": "象曰：天与水违行，讼。君子以作事谋始。"
        }
        
        return default_xiang_ci.get(gua_name, f"象曰：{gua_name}象征天地运行之道，君子应当顺应自然规律。")
    
    def get_shao_yong_explanation(self, gua_name: str, gua_symbol: str) -> str:
        """获取邵雍河洛理数爻辞解释"""
        search_results = self.search_knowledge(f"{gua_name} 邵雍 河洛理数", 2)
        
        if search_results:
            explanations = []
            for result in search_results:
                content = result.get('answer', result.get('content', ''))
                if "邵雍" in content or "河洛" in content:
                    explanations.append(content)
            
            if explanations:
                return explanations[0]
        
        # 默认邵雍解释
        return f"平：得此爻者，{gua_name}表示运势平稳，适合守成，不宜妄动。或遇贵人好友提携而发财进人，女人有生育之喜。不良者，防疾诉忧患，或女人有不贞之事，做官的有被贬职之忧。"
    
    def get_fu_peirong_handbook(self, gua_name: str, gua_symbol: str) -> Dict[str, str]:
        """获取傅佩荣解卦手册"""
        search_results = self.search_knowledge(f"{gua_name} 傅佩荣", 3)
        
        handbook = {
            "时运": "守成尚可，不宜妄动。",
            "财运": "适宜稳健投资，不宜冒险。",
            "家宅": "维护家声，和睦相处。",
            "身体": "注意调养，保持健康。",
            "事业": "稳步发展，不可急躁。",
            "感情": "以诚相待，顺其自然。"
        }
        
        if search_results:
            for result in search_results:
                content = result.get('answer', result.get('content', ''))
                if "傅佩荣" in content:
                    # 尝试从内容中提取具体建议
                    if "时运" in content:
                        handbook["时运"] = self.extract_advice(content, "时运")
                    if "财运" in content:
                        handbook["财运"] = self.extract_advice(content, "财运")
                    if "家宅" in content:
                        handbook["家宅"] = self.extract_advice(content, "家宅")
                    if "身体" in content:
                        handbook["身体"] = self.extract_advice(content, "身体")
        
        return handbook
    
    def extract_advice(self, content: str, keyword: str) -> str:
        """从内容中提取特定关键词的建议"""
        lines = content.split('\n')
        for line in lines:
            if keyword in line:
                # 提取冒号后的内容
                if '：' in line:
                    return line.split('：')[1].strip()
                elif ':' in line:
                    return line.split(':')[1].strip()
        return f"关于{keyword}的建议：保持中庸之道。"
    
    def get_gua_ci_reference(self, gua_name: str, gua_symbol: str) -> Dict[str, str]:
        """获取卦辞参考"""
        search_results = self.search_knowledge(f"{gua_name} 卦辞", 3)
        
        reference = {
            "main_gua": {
                "name": gua_name,
                "ci": f"{gua_name}的卦辞内容",
                "xiang": f"{gua_name}的象辞内容"
            },
            "changing_gua": {
                "name": f"{gua_name}变卦",
                "ci": f"{gua_name}变卦的卦辞内容",
                "xiang": f"{gua_name}变卦的象辞内容"
            }
        }
        
        if search_results:
            for result in search_results:
                content = result.get('answer', result.get('content', ''))
                if "卦辞" in content or "象曰" in content:
                    # 尝试提取卦辞和象辞
                    lines = content.split('\n')
                    for line in lines:
                        if "卦辞" in line or "象曰" in line:
                            if "卦辞" in line:
                                reference["main_gua"]["ci"] = line.strip()
                            if "象曰" in line:
                                reference["main_gua"]["xiang"] = line.strip()
        
        return reference
    
    def get_changing_gua_analysis(self, gua_name: str, gua_symbol: str) -> Dict[str, str]:
        """获取变卦分析"""
        # 生成变卦
        changing_symbol = self.generate_changing_symbol(gua_symbol)
        changing_gua_name = self.get_gua_name_by_symbol(changing_symbol)
        
        return {
            "changing_gua_name": changing_gua_name,
            "changing_symbol": changing_symbol,
            "analysis": f"本卦{gua_name}变卦为{changing_gua_name}，表示事物的发展变化趋势。本卦代表当前状况，变卦代表未来趋势。"
        }
    
    def generate_changing_symbol(self, symbol: str) -> str:
        """生成变卦符号"""
        symbol_list = list(symbol)
        # 随机改变一爻
        change_pos = random.randint(0, len(symbol_list) - 1)
        symbol_list[change_pos] = '0' if symbol_list[change_pos] == '1' else '1'
        return ''.join(symbol_list)
    
    def get_gua_name_by_symbol(self, symbol: str) -> str:
        """根据符号获取卦名"""
        # 这里应该有一个完整的64卦映射表
        gua_mapping = {
            "111111": "乾卦",
            "000000": "坤卦",
            "100010": "屯卦",
            "010001": "蒙卦",
            "111010": "需卦",
            "010111": "讼卦",
            "010000": "师卦",
            "000010": "比卦",
            "110111": "小畜卦",
            "111011": "履卦",
            "111000": "泰卦",
            "000111": "否卦"
        }
        
        return gua_mapping.get(symbol, f"未知卦象({symbol})")
    
    def get_divination_steps(self) -> List[str]:
        """获取解卦步骤"""
        return [
            "① 无变爻：看本卦卦辞",
            "② 一个变爻：看本卦变爻爻辞",
            "③ 两个变爻：看本卦两个变爻爻辞，以上爻为主",
            "④ 三个变爻：看本卦和之卦卦辞，以本卦为主",
            "⑤ 四个变爻：看之卦两个不变爻爻辞，以下爻为主",
            "⑥ 五个变爻：看之卦不变爻爻辞",
            "⑦ 六个变爻：看之卦卦辞",
            "⑧ 六个都是变爻：乾坤两卦看用九、用六"
        ]

# 创建全局实例
enhanced_divination = EnhancedDivinationSystem()
