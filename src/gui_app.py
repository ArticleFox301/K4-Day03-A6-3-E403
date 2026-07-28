"""
STREAMLIT WEB UI APP - DE TAI 5: TRO LY TRA CUU DON HANG & DOI TRA
Giao dien web truc quan ho tro nhap API Key va chay truc tiep voi model gemini-flash-latest hoat dong 100%.
"""

import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import (
    GeminiProvider,
    OpenAIProvider,
    OllamaProvider,
    MockProvider,
    normalize_gemini_model,
    list_ollama_models,
)
from app import load_test_cases, parse_action

st.set_page_config(
    page_title="Lab 3 - Chatbot vs ReAct Agent (De tai 5)",
    layout="wide"
)

st.title("LAB 3: CHATBOT VS REACT AGENT - DE TAI 5: TRO LY DON HANG & DOI TRA")
st.caption("Nhom thuc hien: Tran Luong Hoang Anh (Role 1, 2) | Nguyen Thi Thu Trang (Role 3, 5) | Nguyen Trung Duc (Role 4)")
st.markdown("---")

st.sidebar.header("CAU HINH SYSTEM & API KEY")

provider_choice = st.sidebar.selectbox(
    "Chon LLM Provider:",
    ["Ollama (Local)", "Gemini (Google AI)", "Offline Mock Mode", "OpenAI"]
)

api_key_input = ""
gemini_model_input = "gemini-flash-latest"
available_gemini_models = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

if provider_choice == "Ollama (Local)":
    ollama_base_url = st.sidebar.text_input("Ollama Base URL:", value="http://localhost:11434")
    local_models = list_ollama_models(ollama_base_url)
    if local_models:
        ollama_model_input = st.sidebar.selectbox("Chon Model Ollama (da pull san):", local_models)
    else:
        st.sidebar.warning("Khong ket noi duoc Ollama. Kiem tra 'ollama serve' da chay chua.")
        ollama_model_input = st.sidebar.text_input("Nhap ten model Ollama thu cong:", value="qwen3:4b")

elif provider_choice == "Gemini (Google AI)":
    api_key_input = st.sidebar.text_input(
        "Nhap Gemini API Key:",
        value="",
        type="password",
        help="Nhap API Key cua Google Gemini AI Studio"
    )
    
    if api_key_input:
        if st.sidebar.button("KIEM TRA DANH SACH MODEL HO TRO CHO API KEY NAY"):
            try:
                from google import genai
                client = genai.Client(api_key=api_key_input)
                fetched_models = []
                for m in client.models.list():
                    name = getattr(m, 'name', '')
                    if name.startswith('models/'):
                        name = name[7:]
                    if 'gemini' in name:
                        fetched_models.append(name)
                if fetched_models:
                    st.session_state['fetched_models'] = fetched_models
                    st.sidebar.success(f"Tim thay {len(fetched_models)} models ho tro cho API Key cua ban!")
                else:
                    st.sidebar.warning("Khong tim thay model phu hop.")
            except Exception as e:
                st.sidebar.error(f"Loi kiem tra API Key: {str(e)}")

    if 'fetched_models' in st.session_state and st.session_state['fetched_models']:
        available_gemini_models = st.session_state['fetched_models']
        
    gemini_model_choice = st.sidebar.selectbox(
        "Chon Gemini Model tu danh sach:",
        available_gemini_models + ["Custom Model Name"]
    )
    
    if gemini_model_choice == "Custom Model Name":
        custom_raw = st.sidebar.text_input("Nhap ten model Gemini tuy chinh:", value="gemini-flash-latest")
        gemini_model_input = normalize_gemini_model(custom_raw)
    else:
        gemini_model_input = gemini_model_choice

elif provider_choice == "OpenAI":
    api_key_input = st.sidebar.text_input("Nhap OpenAI API Key:", type="password")
    gemini_model_input = st.sidebar.selectbox("Chon Model OpenAI:", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])

if provider_choice == "Ollama (Local)":
    current_provider = OllamaProvider(model=ollama_model_input, base_url=ollama_base_url)
    st.sidebar.success(f"Dang dung Ollama Local! Model: {ollama_model_input}")
elif provider_choice == "Gemini (Google AI)" and api_key_input:
    current_provider = GeminiProvider(api_key=api_key_input, model=gemini_model_input)
    st.sidebar.success(f"Da ket noi Gemini API! Active Model: {current_provider.model_name}")
elif provider_choice == "OpenAI" and api_key_input:
    current_provider = OpenAIProvider(api_key=api_key_input, model=gemini_model_input)
    st.sidebar.success(f"Da ket noi OpenAI API! Model: {gemini_model_input}")
else:
    current_provider = MockProvider()
    if provider_choice != "Offline Mock Mode":
        st.sidebar.warning("Chua nhap API Key. Dang chay o che do Offline Mock Mode de dam bao an toan.")
    else:
        st.sidebar.info("Che do Offline Mock Mode dang hoat dong.")

test_cases = load_test_cases()

tab1, tab2, tab3 = st.tabs(["CHAY TEST CASES MAU", "TRO CHUYEN TRUC TIEP", "KIEN TRUC & SCORING MATRIX"])

with tab1:
    st.subheader("Chay thu nghiem 5 Test Cases (So sanh Baseline Chatbot vs ReAct Agent)")
    
    selected_tc_id = st.selectbox(
        "Chon Test Case de chay kiem thu:",
        options=[tc["id"] for tc in test_cases],
        format_func=lambda x: f"Test Case #{x}: {test_cases[x-1]['question']} [{test_cases[x-1]['category']}]"
    )
    
    tc_data = test_cases[selected_tc_id - 1]
    
    st.info(f"Cau hoi: {tc_data['question']}\nKy vong: {tc_data['expected_behavior']}")
    
    if st.button("BAT DAU CHAY EXPERIMENT", type="primary"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CHATBOT BASELINE (Cap 2 - LLM Tinh)")
            with st.spinner("Chatbot dang sinh cau tra loi..."):
                baseline_res = current_provider.generate(tc_data["question"], system_prompt=CHATBOT_BASELINE_PROMPT)
                st.write(baseline_res)
                st.caption("Nhan xet: Chatbot thong thuong khong truy cap duoc CSDL nen tu choi hoac tra loi chung chung.")
                
        with col2:
            st.markdown("### REACT AGENT (Cap 3 - Thought -> Action -> Observation)")
            
            step = 0
            conv_history = f"Cau hoi cua khach hang: {tc_data['question']}\n"
            
            trace_container = st.container()
            
            while step < MAX_ITERATIONS:
                step += 1
                with trace_container:
                    st.markdown(f"**Step {step}/{MAX_ITERATIONS}**")
                    prompt = conv_history + "\nHay dua ra Thought tiep theo va Action (hoac Final Answer):"
                    llm_res = current_provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
                    
                    st.code(llm_res, language="yaml")
                    
                    if "Final Answer:" in llm_res:
                        st.success("ReAct Agent hoan thanh xuat sac nhiem vu!")
                        break
                        
                    tool_name, args = parse_action(llm_res)
                    if tool_name and tool_name in AVAILABLE_TOOLS:
                        st.markdown(f"*Thuc thi Tool:* `{tool_name}` voi tham so `{args}`")
                        tool_func = AVAILABLE_TOOLS[tool_name]
                        try:
                            if len(args) == 1:
                                obs = tool_func(args[0])
                            elif len(args) == 2:
                                obs = tool_func(args[0], args[1])
                            else:
                                obs = tool_func()
                        except Exception as e:
                            obs = f"LOI THUC THI TOOL: {str(e)}"
                            
                        st.info(f"Observation: {obs}")
                        conv_history += f"\n{llm_res}\nObservation: {obs}"
                    else:
                        conv_history += f"\n{llm_res}"

with tab2:
    st.subheader("Tuong tac dong voi ReAct Agent Tro ly Don hang & Doi tra")
    
    custom_query = st.text_input(
        "Nhap cau hoi tuy chinh (Vi du: Kiem tra don hang ORD-88219 hoac Toi muon doi tra ao bi rach khuy trong don ORD-88219):",
        value="Kiem tra don hang ORD-88219 giup toi."
    )
    
    if st.button("GUI CAU HOI CHO REACT AGENT"):
        st.markdown(f"**Cau hoi nguoi dung:** {custom_query}")
        
        step = 0
        conv_history = f"Cau hoi cua khach hang: {custom_query}\n"
        
        while step < MAX_ITERATIONS:
            step += 1
            st.markdown(f"--- **Vong lap Step {step}/{MAX_ITERATIONS}** ---")
            prompt = conv_history + "\nHay dua ra Thought tiep theo va Action (hoac Final Answer):"
            llm_res = current_provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
            
            st.code(llm_res, language="text")
            
            if "Final Answer:" in llm_res:
                st.success("ReAct Agent da hoan thanh va tra loi khach hang.")
                break
                
            tool_name, args = parse_action(llm_res)
            if tool_name and tool_name in AVAILABLE_TOOLS:
                st.markdown(f"**Goi Tool:** `{tool_name}` -> Tham so: `{args}`")
                tool_func = AVAILABLE_TOOLS[tool_name]
                try:
                    if len(args) == 1:
                        obs = tool_func(args[0])
                    elif len(args) == 2:
                        obs = tool_func(args[0], args[1])
                    else:
                        obs = tool_func()
                except Exception as e:
                    obs = f"LOI: {str(e)}"
                    
                st.warning(f"Observation tu CSDL: {obs}")
                conv_history += f"\n{llm_res}\nObservation: {obs}"
            else:
                conv_history += f"\n{llm_res}"

with tab3:
    st.subheader("Scoring Matrix & Trace Logs Observability")
    
    st.markdown("""
    #### BANG CHAM DIEM AGENTIC FIT (SCORING MATRIX) - DE TAI 5
    
    | Tieu chi | Diem (1-5) | Ly do phan tich chi tiet cho De tai 5 |
    | :--- | :---: | :--- |
    | Multi-step Reasoning | 5/5 | Can suy luan qua nhieu buoc: Nhan ma don -> Tra cuu CSDL -> Kiem tra chinh sach 7 ngay -> Tinh tien hoan -> Tao ve. |
    | Tool Interaction | 5/5 | Bat buoc tuong tac voi CSDL thuc te qua tools: lookup_order, check_return_eligibility, initiate_return. |
    | Dynamic Decision | 5/5 | Quyet dinh buoc tiep theo phu thuoc ket qua buoc truoc (Don qua 7 ngay -> Tu choi; Du dieu kien -> Tinh tien). |
    | Long Horizon | 4/5 | Quy trinh gom 3-4 buoc tac nghiep lien chuoi voi du lieu dong. |
    | **TONG DIEM FIT** | **19/20** | **KET LUAN: DE TAI 5 CUC KY PHU HOP VOI REACT AGENT!** |
    """)
    
    st.markdown("""
    #### DANH SACH TOOLS DANG KY SAN (TOOL REGISTRY)
    - `lookup_order[order_id]`: Tra cuu CSDL chi tiet don hang, ngay mua, trang thai giao hang.
    - `check_return_eligibility[order_id, reason]`: Kiem tra thoi han 7 ngay va ly do doi tra.
    - `initiate_return[order_id, reason]`: Tao ve doi tra va tinh so tien hoan tra.
    """)
