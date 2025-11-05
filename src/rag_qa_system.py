"""
RAG问答系统 - 基于周易理论的智能问答
实现类似AnswerWithRAGContextStringPrompt的功能
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerWithRAGContextStringPrompt:
    """
    基于RAG上下文的字符串答案提示类
    用于处理开放性的周易理论问题
    """
    
    instruction = """
    你是一个专业的周易理论专家，请基于提供的上下文信息回答用户的问题。
    请提供详细、准确、有深度的回答，结合传统易经理论和现代应用。
    """
    
    user_prompt = """
    问题：{question}
    
    相关上下文：
    {context}
    
    请基于以上上下文信息，提供详细的回答。
    """
    
    class AnswerSchema(BaseModel):
        """答案模式定义"""
        step_by_step_analysis: str = Field(
            description="详细分步推理过程，至少5步，150字以上。请结合上下文信息，逐步分析并归纳答案。"
        )
        reasoning_summary: str = Field(
            description="简要总结分步推理过程，约50字"
        )
        final_answer: str = Field(
            description="最终答案，基于周易理论的完整回答，200字以上"
        )
        relevant_sources: List[str] = Field(
            description="引用的相关来源，包括文档名称和关键段落"
        )
        confidence_score: float = Field(
            description="答案置信度，0-1之间",
            ge=0.0,
            le=1.0
        )


class RAGKnowledgeBase:
    """RAG知识库管理器"""
    
    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_data = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """加载知识库数据"""
        try:
            # 加载清理后的知识库
            cleaned_file = os.path.join(self.knowledge_base_path, "complete_knowledge_base_cleaned.jsonl")
            if os.path.exists(cleaned_file):
                with open(cleaned_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            self.knowledge_data.append(json.loads(line))
                logger.info(f"成功加载知识库，共{len(self.knowledge_data)}条记录")
            else:
                logger.warning("未找到清理后的知识库文件")
        except Exception as e:
            logger.error(f"加载知识库失败: {e}")
    
    def search_relevant_context(self, question: str, top_k: int = 5) -> List[Dict]:
        """搜索相关问题上下文"""
        relevant_contexts = []
        
        # 简单的关键词匹配搜索
        question_keywords = self.extract_keywords(question)
        
        for item in self.knowledge_data:
            score = self.calculate_relevance_score(question_keywords, item)
            if score > 0.1:  # 相关性阈值
                relevant_contexts.append({
                    'content': item.get('answer', ''),
                    'source': item.get('source_text', ''),
                    'score': score,
                    'segment_index': item.get('segment_index', 0)
                })
        
        # 按相关性排序并返回top_k
        relevant_contexts.sort(key=lambda x: x['score'], reverse=True)
        return relevant_contexts[:top_k]
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 周易相关关键词
        iching_keywords = [
            '乾', '坤', '震', '巽', '坎', '离', '艮', '兑',
            '卦', '爻', '变爻', '世爻', '应爻', '飞神', '伏神',
            '五行', '阴阳', '八卦', '六十四卦', '京氏易传',
            '预测', '占卜', '吉凶', '旺衰', '生克'
        ]
        
        keywords = []
        for keyword in iching_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    def calculate_relevance_score(self, question_keywords: List[str], item: Dict) -> float:
        """计算相关性得分"""
        score = 0.0
        content = item.get('answer', '') + ' ' + item.get('source_text', '')
        
        for keyword in question_keywords:
            if keyword in content:
                score += 1.0
        
        # 根据关键词密度调整得分
        if score > 0:
            score = score / len(question_keywords)
        
        return score


class IChingRAGSystem:
    """周易RAG问答系统"""
    
    def __init__(self):
        self.knowledge_base = RAGKnowledgeBase()
        self.prompt_template = AnswerWithRAGContextStringPrompt()
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """回答用户问题"""
        try:
            # 1. 搜索相关上下文
            relevant_contexts = self.knowledge_base.search_relevant_context(question)
            
            if not relevant_contexts:
                return self._generate_no_context_answer(question)
            
            # 2. 构建上下文
            context_text = self._build_context_text(relevant_contexts)
            
            # 3. 生成答案
            answer = self._generate_answer(question, context_text, relevant_contexts)
            
            return answer
            
        except Exception as e:
            logger.error(f"回答问题失败: {e}")
            return self._generate_error_answer(str(e))
    
    def _build_context_text(self, contexts: List[Dict]) -> str:
        """构建上下文文本"""
        context_parts = []
        for i, ctx in enumerate(contexts, 1):
            context_parts.append(f"上下文{i}:\n{ctx['content']}\n")
        
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str, sources: List[Dict]) -> Dict[str, Any]:
        """生成答案"""
        # 模拟AI回答生成（实际应用中会调用LLM）
        step_by_step_analysis = self._generate_step_analysis(question, context)
        reasoning_summary = self._generate_reasoning_summary(step_by_step_analysis)
        final_answer = self._generate_final_answer(question, context)
        relevant_sources = [f"来源{i+1}: {src['source'][:100]}..." for i, src in enumerate(sources)]
        confidence_score = min(0.9, 0.5 + len(sources) * 0.1)
        
        return {
            "step_by_step_analysis": step_by_step_analysis,
            "reasoning_summary": reasoning_summary,
            "final_answer": final_answer,
            "relevant_sources": relevant_sources,
            "confidence_score": confidence_score,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_step_analysis(self, question: str, context: str) -> str:
        """生成分步分析"""
        return f"""
        步骤1：分析问题关键词 - 识别问题中的周易理论要素
        步骤2：检索相关上下文 - 从知识库中找到相关的卦象、爻辞等内容
        步骤3：理解传统理论 - 结合京氏易传等经典理论进行解读
        步骤4：现代应用分析 - 将传统理论与现代预测应用相结合
        步骤5：综合归纳总结 - 基于以上分析得出完整答案
        """
    
    def _generate_reasoning_summary(self, analysis: str) -> str:
        """生成推理总结"""
        return "通过关键词分析、上下文检索、理论解读、现代应用和综合归纳五个步骤，基于传统周易理论提供专业回答。"
    
    def _generate_final_answer(self, question: str, context: str) -> str:
        """生成最终答案"""
        return f"""
        基于提供的周易理论上下文，我来回答您的问题：{question}
        
        根据传统易经理论，特别是京氏易传的体系，这个问题涉及到八卦、五行、阴阳等核心概念。
        在传统预测中，需要综合考虑卦象的变化、爻位的旺衰、以及世应关系等因素。
        
        现代应用中，我们可以将这些传统理论与数据分析和机器学习相结合，
        形成更加科学和准确的预测方法。这既保持了传统文化的精髓，
        又融入了现代技术的优势。
        
        建议在实际应用中，既要尊重传统理论的深度，也要结合现代方法的精度，
        以达到最佳的预测效果。
        """
    
    def _generate_no_context_answer(self, question: str) -> Dict[str, Any]:
        """生成无上下文答案"""
        return {
            "step_by_step_analysis": "未找到相关上下文，基于通用周易理论进行分析",
            "reasoning_summary": "基于通用理论进行推理",
            "final_answer": f"抱歉，在知识库中未找到与'{question}'直接相关的内容。建议您提供更具体的问题，或参考传统周易理论进行理解。",
            "relevant_sources": [],
            "confidence_score": 0.3,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_error_answer(self, error: str) -> Dict[str, Any]:
        """生成错误答案"""
        return {
            "step_by_step_analysis": "系统出现错误",
            "reasoning_summary": "无法正常处理问题",
            "final_answer": f"系统出现错误：{error}。请稍后重试或联系技术支持。",
            "relevant_sources": [],
            "confidence_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数 - 演示RAG问答系统"""
    print("周易RAG问答系统演示")
    print("=" * 50)
    
    # 初始化系统
    rag_system = IChingRAGSystem()
    
    # 示例问题
    test_questions = [
        "什么是乾卦？",
        "如何理解京氏易传中的世应关系？",
        "五行在预测中如何应用？",
        "什么是变爻？",
        "如何结合传统周易和现代预测？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 30)
        
        answer = rag_system.answer_question(question)
        
        print(f"分步分析: {answer['step_by_step_analysis']}")
        print(f"推理总结: {answer['reasoning_summary']}")
        print(f"最终答案: {answer['final_answer']}")
        print(f"相关来源: {', '.join(answer['relevant_sources'])}")
        print(f"置信度: {answer['confidence_score']:.2f}")
        print(f"时间戳: {answer['timestamp']}")


if __name__ == "__main__":
    main()
