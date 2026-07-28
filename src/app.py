"""
CORE AGENT APP - DE TAI 5: TRO LY TRA CUU DON HANG & DOI TRA
(Role 4: Core Agent Developer & Integrator - Nguyen Trung Duc)
File chinh ghep noi tat ca cac thanh phan: Tools + Prompts + Test Cases + Multi-Provider.
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

from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Doc bo test cases tu config/test_cases.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_action(llm_output: str):
    """
    Phan tich cu phap Action tu cau tra loi cua LLM.
    Dang ky vong: Action: ten_cong_cu[tham_so_1, tham_so_2]
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
    Chay Chatbot goc (Baseline) khong co Tool.
    """
    print(f"\n[CHATBOT BASELINE] Cau hoi: {user_query}")
    print(f"System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"Chatbot tra loi:\n{response}")
    return response


def run_react_agent(user_query: str, provider):
    """
    Chay ReAct Agent Loop (Thought -> Action -> Observation) co Guardrails.
    """
    print(f"\n[REACT AGENT] Cau hoi: {user_query}")
    step = 0
    conversation_history = f"Cau hoi cua khach hang: {user_query}\n"
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- Vong lap ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        prompt = conversation_history + "\nHay dua ra Thought tiep theo va Action (hoac Final Answer):"
        llm_response = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
        print(f"Agent phan hoi:\n{llm_response}")
        
        if "Final Answer:" in llm_response:
            print("\n[REACT AGENT] Hoan thanh xuat sac nhiem vu.")
            return llm_response
            
        tool_name, args = parse_action(llm_response)
        
        if tool_name and tool_name in AVAILABLE_TOOLS:
            print(f"Thuc thi Tool: {tool_name} voi tham so {args}")
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
                obs = f"LOI THUC THI TOOL {tool_name}: {str(e)}"
                
            print(f"Observation: {obs}")
            conversation_history += f"\n{llm_response}\nObservation: {obs}"
        else:
            conversation_history += f"\n{llm_response}"

    if step >= MAX_ITERATIONS:
        print(f"\nGUARDRAIL TRIGGERED: Da dat gioi han toi da {MAX_ITERATIONS} buoc lap. Ngat lap an toan!")


if __name__ == "__main__":
    print("==========================================================================")
    print("BAI LAB 3: CHATBOT VS REACT AGENT - DE TAI 5: TRO LY DON HANG & DOI TRA")
    print("Nhom thuc hien: Tran Luong Hoang Anh, Nguyen Thi Thu Trang, Nguyen Trung Duc")
    print("==========================================================================")
    
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"LLM Provider dang hoat dong: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"Da tai thanh cong {len(tests)} Test Cases tu config/test_cases.json\n")
    
    tc_list = tests
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        idx = int(sys.argv[1])
        if 1 <= idx <= len(tests):
            tc_list = [tests[idx - 1]]
        
    for tc in tc_list:
        print("\n==========================================================================")
        print(f"TEST CASE #{tc['id']}: [{tc['category']}]")
        print(f"Cau hoi: {tc['question']}")
        print(f"Ky vong: {tc['expected_behavior']}")
        print("==========================================================================")
        
        print("\n--- DEMO 1: CHAY CAU HOI TREN CHATBOT BASELINE ---")
        run_baseline_chatbot(tc["question"], provider)
        
        print("\n--- DEMO 2: CHAY CAU HOI TREN REACT AGENT ---")
        run_react_agent(tc["question"], provider)
