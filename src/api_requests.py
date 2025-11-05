"""
API请求处理模块
实现类似图片中的schema分支处理功能
支持kind="string"的RAG问答请求
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .rag_qa_system import AnswerWithRAGContextStringPrompt, IChingRAGSystem
from typing import Dict, Any, Tuple, Optional
import json
from datetime import datetime


class APIRequestHandler:
    """API请求处理器"""
    
    def __init__(self):
        self.rag_system = IChingRAGSystem()
    
    def _build_rag_context_prompts(self, schema: str, use_schema_prompt: bool = True) -> Tuple[str, Any, str]:
        """
        构建RAG上下文提示
        类似图片中的_build_rag_context_prompts方法
        """
        if schema == "number":
            # 数字类型处理（示例）
            system_prompt = "你是一个专业的数字分析专家..."
            response_format = {"type": "number"}
            user_prompt = "请分析以下数字: {context}"
            
        elif schema == "boolean":
            # 布尔类型处理（示例）
            system_prompt = "你是一个专业的判断专家..."
            response_format = {"type": "boolean"}
            user_prompt = "请判断以下内容: {context}"
            
        elif schema == "names":
            # 名称列表处理（示例）
            system_prompt = "你是一个专业的名称提取专家..."
            response_format = {"type": "array", "items": {"type": "string"}}
            user_prompt = "请提取以下内容中的名称: {context}"
            
        elif schema == "string":
            # 新增: 支持开放性文本问题
            prompt_instance = AnswerWithRAGContextStringPrompt()
            system_prompt = (
                prompt_instance.system_prompt_with_schema 
                if use_schema_prompt 
                else prompt_instance.system_prompt
            )
            response_format = AnswerWithRAGContextStringPrompt.AnswerSchema
            user_prompt = AnswerWithRAGContextStringPrompt.user_prompt
            
        else:
            raise ValueError(f"不支持的schema类型: {schema}")
        
        return system_prompt, response_format, user_prompt
    
    def process_rag_request(self, 
                           question: str, 
                           context: str, 
                           schema: str = "string",
                           use_schema_prompt: bool = True) -> Dict[str, Any]:
        """
        处理RAG请求
        类似图片中的API请求处理流程
        """
        try:
            # 1. 构建提示
            system_prompt, response_format, user_prompt_template = self._build_rag_context_prompts(
                schema, use_schema_prompt
            )
            
            # 2. 格式化用户提示
            user_prompt = user_prompt_template.format(
                question=question,
                context=context
            )
            
            # 3. 处理请求
            if schema == "string":
                # 使用RAG系统处理字符串类型问题
                answer = self.rag_system.answer_question(question)
                
                # 转换为标准格式
                result = {
                    "step_by_step_analysis": answer["step_by_step_analysis"],
                    "reasoning_summary": answer["reasoning_summary"],
                    "relevant_pages": answer["relevant_pages"],
                    "final_answer": answer["final_answer"],
                    "schema": "string",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 其他类型的处理（示例）
                result = {
                    "answer": f"处理{schema}类型问题: {question}",
                    "schema": schema,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": True,
                "data": result,
                "system_prompt": system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt,
                "user_prompt": user_prompt[:100] + "..." if len(user_prompt) > 100 else user_prompt
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "schema": schema,
                "timestamp": datetime.now().isoformat()
            }


def demo_api_requests():
    """演示API请求处理功能"""
    print("API请求处理演示")
    print("=" * 50)
    
    # 初始化处理器
    handler = APIRequestHandler()
    
    # 测试不同schema类型
    test_cases = [
        {
            "question": "请简要总结'乾卦'的主要特征和含义",
            "context": "乾卦是八卦之首，代表纯阳用事...",
            "schema": "string",
            "description": "字符串类型 - 开放性文本问题"
        },
        {
            "question": "分析以下数字",
            "context": "1, 2, 3, 4, 5",
            "schema": "number",
            "description": "数字类型"
        },
        {
            "question": "判断以下内容是否正确",
            "context": "乾卦代表纯阳",
            "schema": "boolean",
            "description": "布尔类型"
        },
        {
            "question": "提取以下内容中的名称",
            "context": "京氏易传、火珠林、黄金策",
            "schema": "names",
            "description": "名称列表类型"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['description']}")
        print(f"Schema: {case['schema']}")
        print(f"问题: {case['question']}")
        print("-" * 40)
        
        # 处理请求
        result = handler.process_rag_request(
            question=case['question'],
            context=case['context'],
            schema=case['schema']
        )
        
        # 显示结果
        if result['success']:
            print("处理成功!")
            print(f"系统提示: {result['system_prompt']}")
            print(f"用户提示: {result['user_prompt']}")
            
            if case['schema'] == 'string':
                data = result['data']
                print(f"分步分析: {data['step_by_step_analysis'][:100]}...")
                print(f"推理总结: {data['reasoning_summary']}")
                print(f"相关页面: {data['relevant_pages']}")
                print(f"最终答案: {data['final_answer'][:100]}...")
            else:
                print(f"答案: {result['data']['answer']}")
        else:
            print(f"处理失败: {result['error']}")
        
        print("\n" + "="*50)


def test_schema_branching():
    """测试schema分支功能"""
    print("\n测试Schema分支功能:")
    print("-" * 30)
    
    handler = APIRequestHandler()
    
    # 测试不同的schema类型
    schemas = ["string", "number", "boolean", "names", "invalid"]
    
    for schema in schemas:
        try:
            system_prompt, response_format, user_prompt = handler._build_rag_context_prompts(schema)
            print(f"Schema '{schema}': 成功")
            print(f"  系统提示长度: {len(system_prompt)}")
            print(f"  响应格式: {type(response_format).__name__}")
            print(f"  用户提示模板: {user_prompt[:50]}...")
        except ValueError as e:
            print(f"Schema '{schema}': 失败 - {e}")
        print()


def show_implementation_details():
    """展示实现细节"""
    print("\n实现细节:")
    print("-" * 20)
    
    print("1. _build_rag_context_prompts 方法:")
    print("   - 支持 schema == 'string' 分支")
    print("   - 自动调用 AnswerWithRAGContextStringPrompt")
    print("   - 实现方式与 number/boolean/names 完全一致")
    
    print("\n2. 新增功能:")
    print("   - 支持开放性文本问题的RAG问答")
    print("   - kind 或 schema 为 string 时自动启用")
    print("   - 完整的结构化输出")
    
    print("\n3. 系统提示构建:")
    print("   - system_prompt_with_schema (带Schema)")
    print("   - system_prompt (基础版本)")
    print("   - 根据 use_schema_prompt 参数选择")
    
    print("\n4. 响应格式:")
    print("   - AnswerSchema 完整定义")
    print("   - step_by_step_analysis")
    print("   - reasoning_summary")
    print("   - relevant_pages")
    print("   - final_answer")


def main():
    """主函数"""
    print("API请求处理模块演示")
    print("实现类似图片中的schema分支处理功能")
    print("=" * 60)
    
    # 1. 演示API请求处理
    demo_api_requests()
    
    # 2. 测试schema分支
    test_schema_branching()
    
    # 3. 展示实现细节
    show_implementation_details()
    
    print("\n" + "="*60)
    print("演示完成！")
    print("系统已支持 kind='string' 的RAG问答请求处理。")


if __name__ == "__main__":
    main()
