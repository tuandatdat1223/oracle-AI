import google.generativeai as genai
import time
import json
import streamlit as st

def call_gemini_agent(api_key, sys_prompt, current_model_idx, free_models):
    """
    Gọi Gemini API sử dụng cấu hình API Key và danh sách model dự phòng.
    Có cơ chế tự động chuyển model khi gặp lỗi Rate Limit (RPM).
    """
    if not api_key:
        return None, "Chưa cấu hình API Key cho Google Gemini."
        
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return None, f"Lỗi cấu hình API Key: {e}"
        
    total_models = len(free_models)
    raw_text = ""
    
    for attempt in range(total_models):
        model_idx = (current_model_idx + attempt) % total_models
        model_name = free_models[model_idx]
        short_name = model_name.split("/")[-1]
        
        try:
            st.write(f"🌐 Đang gọi Model: `{short_name}`...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                sys_prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
            raw_text = response.text
            st.session_state.current_model_idx = model_idx
            break
        except Exception as e:
            st.write(f"⚠️ Model `{short_name}` gặp sự cố hoặc quá tải giới hạn RPM... Đang thử model tiếp theo...")
            time.sleep(1)
            
    if not raw_text:
        return None, "Không thể kết nối đến các model AI lúc này. Vui lòng kiểm tra lại API Key."
        
    try:
        ai_data = json.loads(raw_text)
        return ai_data, None
    except json.JSONDecodeError:
        return None, "Model trả về dữ liệu không đúng cấu trúc JSON mong muốn."
