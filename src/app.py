"""
CORE AGENT APP - ĐỀ TÀI 5: TRỢ LÝ TRA CỨU ĐƠN HÀNG & ĐỔI TRẢ
(Dành cho Role 4: Core Agent Developer & Integrator)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from tools import AVAILABLE_TOOLS, get_order_details, check_return_eligibility, calculate_refund_amount, create_return_ticket
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_action(llm_output: str):
    """
    Phân tích cú pháp Action từ câu trả lời của LLM.
    Dạng kỳ vọng: Action: tên_công_cụ[tham_số_1, tham_số_2]
    """
    match = re.search(r"Action:\s*(\w+)\[(.*?)\]", llm_output, re.IGNORECASE)
    if match:
        tool_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        args = [arg.strip(" '\"") for arg in raw_args.split(",") if arg.strip()]
        return tool_name, args
    return None, []


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n[CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"Chatbot trả lời:\n{response}")
    return response


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n[REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    conversation_history = f"Câu hỏi của khách hàng: {user_query}\n"
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        prompt = conversation_history + "\nHãy đưa ra Thought tiếp theo và Action (hoặc Final Answer):"
        llm_response = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
        print(f"🤖 Agent phản hồi:\n{llm_response}")
        
        if "Final Answer:" in llm_response:
            print("\n[REACT AGENT] Hoàn thành xuất sắc nhiệm vụ.")
            return llm_response
            
        tool_name, args = parse_action(llm_response)
        
        if tool_name and tool_name in AVAILABLE_TOOLS:
            print(f"Thực thi Tool: {tool_name} với tham số {args}")
            tool_func = AVAILABLE_TOOLS[tool_name]
            try:
                if len(args) == 1:
                    obs = tool_func(args[0])
                elif len(args) == 2:
                    obs = tool_func(args[0], args[1])
                elif len(args) == 3:
                    obs = tool_func(args[0], args[1], args[2])
                else:
                    obs = tool_func()
            except Exception as e:
                obs = f"LỖI THỰC THI TOOL {tool_name}: {str(e)}"
                
            print(f"Observation: {obs}")
            conversation_history += f"\n{llm_response}\nObservation: {obs}"
        else:
            conversation_history += f"\n{llm_response}"

    if step >= MAX_ITERATIONS:
        print(f"\nGUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước lặp. Ngắt lặp an toàn để tránh treo hệ thống!")


if __name__ == "__main__":
    print("==========================================================================")
    print(" BÀI LAB 3: CHATBOT VS REACT AGENT - ĐỀ TÀI 5: TRỢ LÝ ĐƠN HÀNG & ĐỔI TRẢ")
    print("==========================================================================")
    
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    tc_list = tests
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        idx = int(sys.argv[1])
        if 1 <= idx <= len(tests):
            tc_list = [tests[idx - 1]]
        
    for tc in tc_list:
        print("\n==========================================================================")
        print(f"TEST CASE #{tc['id']}: [{tc['category']}]")
        print(f"Câu hỏi: {tc['question']}")
        print(f"Kỳ vọng: {tc['expected_behavior']}")
        print("==========================================================================")
        
        print("\n--- DEMO 1: CHẠY CÂU HỎI TRÊN CHATBOT BASELINE ---")
        run_baseline_chatbot(tc["question"], provider)
        
        print("\n--- DEMO 2: CHẠY CÂU HỎI TRÊN REACT AGENT ---")
        run_react_agent(tc["question"], provider)
