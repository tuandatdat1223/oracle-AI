import streamlit as st
import os
import json
import time
import db_helper
import ai_helper

st.set_page_config(page_title="Oracle VibeApex", page_icon="💻", layout="centered")

# Khởi tạo các giá trị cấu hình mặc định (đọc từ biến môi trường hoặc để trống)
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if "db_user" not in st.session_state:
    st.session_state.db_user = os.environ.get("DB_USER", "")
if "db_pass" not in st.session_state:
    st.session_state.db_pass = os.environ.get("DB_PASS", "")
if "db_host" not in st.session_state:
    st.session_state.db_host = os.environ.get("DB_HOST", "localhost")
if "db_port" not in st.session_state:
    st.session_state.db_port = os.environ.get("DB_PORT", "1521")
if "db_sid" not in st.session_state:
    st.session_state.db_sid = os.environ.get("DB_SID", "xepdb1")
if "db_conn" not in st.session_state:
    st.session_state.db_conn = None

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "👋 Xin chào! Tôi là **AI Architect** hỗ trợ hệ thống Oracle của bạn.\n\nBạn có thể yêu cầu tôi thiết kế bảng (`Tạo bảng nhân viên`), chỉnh sửa cấu trúc (`Thêm cột lương`), hoặc xuất dữ liệu (`Deploy bảng SACH4`). Bạn muốn tôi làm gì hôm nay?"})

if "db_history_context" not in st.session_state:
    st.session_state.db_history_context = []

if "schema_cache" not in st.session_state:
    st.session_state.schema_cache = {}

if "current_model_idx" not in st.session_state:
    st.session_state.current_model_idx = 0

FREE_MODELS = [
    "models/gemini-3.1-flash-lite",
    "models/gemini-2.5-flash"
]

# ==========================================
# 3. BẢNG ĐIỀU KHIỂN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("## 🔑 Cấu Hình API & Database")
    
    # 1. Nhập API Key Gemini
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Nhập API Key để kích hoạt AI"
    )
    
    # 2. Nhập thông tin kết nối database
    st.markdown("### 🔌 Oracle Database Connection")
    db_user = st.text_input("Username", value=st.session_state.db_user)
    db_pass = st.text_input("Password", type="password", value=st.session_state.db_pass)
    db_host = st.text_input("Host", value=st.session_state.db_host)
    db_port = st.text_input("Port", value=st.session_state.db_port)
    db_sid = st.text_input("SID / Service Name", value=st.session_state.db_sid)
    
    # Nút kết nối
    if st.button("🔌 Kết Nối Hệ Thống", use_container_width=True):
        st.session_state.gemini_api_key = api_key_input
        st.session_state.db_user = db_user
        st.session_state.db_pass = db_pass
        st.session_state.db_host = db_host
        st.session_state.db_port = db_port
        st.session_state.db_sid = db_sid
        
        if db_user and db_pass and db_host and db_port and db_sid:
            with st.spinner("Đang thử kết nối database..."):
                conn = db_helper.init_db(db_user, db_pass, db_host, db_port, db_sid)
                if conn:
                    st.session_state.db_conn = conn
                    st.success("🟢 Kết nối Database thành công!")
                    st.rerun()
                else:
                    st.session_state.db_conn = None
                    st.error("🔴 Không thể kết nối. Vui lòng kiểm tra lại thông tin.")
        else:
            st.warning("⚠️ Vui lòng nhập đầy đủ thông tin Database.")
            
    st.markdown("---")
    
    # Hiển thị trạng thái hiện tại
    db_ok = db_helper.check_connection(st.session_state)
    if db_ok:
        st.success("🟢 **Database Local:** Đã kết nối")
        st.caption(f"👤 User: `{st.session_state.db_user}` | 🌐 Host: `{st.session_state.db_host}`")
        
        st.markdown("---")
        st.markdown("### 🛠️ Tiện Ích Mở Rộng")
        
        # Tiện ích 2: Import Dữ liệu
        with st.expander("📥 Import Excel / CSV"):
            import_table = st.text_input("Tên bảng đích (Ví dụ: KHACHHANG)")
            uploaded_file = st.file_uploader("Chọn file CSV/Excel", type=["csv", "xlsx", "xls"])
            if st.button("🚀 Bắt đầu Import", use_container_width=True):
                if not uploaded_file or not import_table:
                    st.error("Vui lòng nhập tên bảng và tải file.")
                else:
                    try:
                        import pandas as pd
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                            
                        with st.spinner("Đang chèn dữ liệu..."):
                            success, msg = db_helper.import_dataframe_to_table(st.session_state.db_conn, import_table, df)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
                    except Exception as e:
                        st.error(f"Lỗi đọc file: {e}")
    else:
        st.error("🔴 **Database Local:** Chưa kết nối hoặc Mất kết nối")

    st.markdown("---")
    
    # Nút Reset Chat
    if st.button("🗑️ Xóa Lịch Sử Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "👋 Lịch sử chat đã được xóa. Tôi sẵn sàng hỗ trợ yêu cầu mới của bạn!"
        })
        st.session_state.db_history_context = []
        st.session_state.schema_cache = {}
        st.session_state.current_erd = None
        st.rerun()

    st.markdown("---")
    st.caption("Oracle VibeApex Chatbot v1.2")

# ==========================================
# 6. GIAO DIỆN CHÍNH
# ==========================================
st.title("💻 Oracle VibeApex - Chatbot")

# Kiểm tra cấu hình API và Kết nối Database
api_configured = bool(st.session_state.gemini_api_key)
db_ok = db_helper.check_connection(st.session_state)

if not api_configured or not db_ok:
    if not api_configured:
        st.info("⚠️ Vui lòng cấu hình **Google Gemini API Key** ở thanh bên (Sidebar) để kích hoạt AI.")
    if not db_ok:
        st.info("⚠️ Vui lòng kết nối **Oracle Database** ở thanh bên (Sidebar) để sử dụng chatbot điều khiển DB.")
    st.stop()

# Hiển thị lịch sử chat
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        if "download_data" in msg and msg["download_data"]:
            st.download_button(
                label=f"📥 Tải File {msg.get('download_file_name', 'script.sql')}",
                data=msg["download_data"],
                file_name=msg.get("download_file_name", "script.sql"),
                mime="text/x-sql",
                key=f"dl_hist_{idx}"
            )

# Nhận input từ người dùng
if prompt := st.chat_input("Nhập yêu cầu của bạn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        final_download_data = None
        final_download_filename = None
        
        with st.status("🤖 AI đang suy nghĩ và làm việc...", expanded=True) as status:
            agent_history = ""
            step_count = 0
            max_steps = 3
            final_ui_message = ""
            
            while step_count < max_steps:
                step_count += 1
                if step_count > 1:
                    st.write("🔍 Đang đánh giá lại cấu trúc dữ liệu...")
 
                # Lấy Schema hiện tại
                current_schema = db_helper.get_db_schema(st.session_state.db_conn)
                
                # Cắt tỉa lịch sử hội thoại
                chat_context = []
                recent_messages = [m for m in st.session_state.messages[:-1] if m["role"] in ["user", "assistant"]][-4:]
                for m in recent_messages:
                    role_name = "Người dùng" if m["role"] == "user" else "AI"
                    msg_content = m["content"]
                    if len(msg_content) > 300:
                        msg_content = msg_content[:300] + " ...[Đã rút gọn]"
                    chat_context.append(f"{role_name}: {msg_content}")
                
                chat_history_str = chr(10).join(chat_context) if chat_context else "Không có."
 
                # Tạo Prompt
                sys_prompt = f"""
                Bạn là một trợ lý AI thông minh tích hợp vào hệ thống Oracle.
                Lần này, bạn hoạt động như một AI Architect có khả năng ĐỌC/GHI ở Local và DEPLOY.
 
                [Cấu trúc Database hiện tại (Quan trọng để viết đúng tên cột)]
                {current_schema}
 
                [Ngữ cảnh 4 vòng chat gần đây (Trí nhớ của bạn)]
                {chat_history_str}
 
                [Lịch sử thay đổi DB trong phiên này]
                {chr(10).join(st.session_state.db_history_context)}
 
                [Yêu cầu từ người dùng]
                "{prompt}"
 
                [Quá trình khảo sát (nếu có)]
                {agent_history}
 
                BẮT BUỘC TRẢ VỀ ĐỊNH DẠNG JSON với các key sau:
                - "action": "READ", "EXECUTE", "DEPLOY" hoặc "CHAT"
                - "message": "Lời phản hồi hoặc giải thích kịch bản cho người dùng"
                - "sql": "Câu lệnh SQL nếu có"
                - "table_name": "Tên bảng (CHỈ BẮT BUỘC KHI action là DEPLOY)"
 
                Quy tắc cho từng Action:
                1. READ: Chạy lệnh SELECT để xem dữ liệu hoặc khảo sát cấu trúc ở LOCAL DB.
                2. EXECUTE: Chạy các lệnh DDL/DML (CREATE, ALTER...) ở LOCAL DB.
                3. DEPLOY: Dùng DUY NHẤT khi người dùng yêu cầu PUSH/DEPLOY/ĐẨY một bảng ĐÃ CÓ SẴN ở Local. Bắt buộc trả về "table_name". Không cần tạo thêm code sql.
                4. CHAT: Dùng để trả lời người dùng, không chứa code SQL.
                """
 
                # Gọi Helper AI
                ai_data, err_msg = ai_helper.call_gemini_agent(
                    st.session_state.gemini_api_key,
                    sys_prompt,
                    st.session_state.current_model_idx,
                    FREE_MODELS
                )
                
                if err_msg:
                    final_ui_message = f"❌ {err_msg}"
                    status.update(label="Lỗi kết nối AI", state="error", expanded=False)
                    break
 
                action = (ai_data.get("action") or "CHAT").upper()
                ai_msg = ai_data.get("message") or ""
                sql_code = (ai_data.get("sql") or "").strip()
                
                st.write(f"**Action:** `{action}`")

                if action == "CHAT":
                    final_ui_message = ai_msg
                    status.update(label="Hoàn tất!", state="complete", expanded=False)
                    break
                    
                elif action == "READ":
                    if sql_code in st.session_state.schema_cache:
                        output = st.session_state.schema_cache[sql_code]
                        agent_history += f"\n-- Lệnh READ (Cached):\n{sql_code}\n-- Kết quả DB:\n{output}\n"
                    else:
                        st.write(f"📖 Đang đọc Database Local...")
                        success, output = db_helper.run_sql_native(st.session_state.db_conn, sql_code, is_read=True)
                        if success:
                            if len(output) > 1000:
                                output = output[:1000] + "\n...[Dữ liệu dài đã bị cắt ngắn để tiết kiệm Token]..."
                            st.session_state.schema_cache[sql_code] = output
                            agent_history += f"\n-- Lệnh READ:\n{sql_code}\n-- Kết quả DB:\n{output}\n"
                        else:
                            agent_history += f"\n-- Lệnh READ bị lỗi:\n{output}\n"

                elif action == "EXECUTE":
                    if sql_code:
                        st.write("⚙️ Đang thực thi mã SQL vào Database Local...")
                        st.session_state.db_history_context.append(f"-- Lệnh đã chạy:\n{sql_code}")
                        if len(st.session_state.db_history_context) > 5:
                            st.session_state.db_history_context.pop(0)
                        success, output_msg = db_helper.run_sql_native(st.session_state.db_conn, sql_code, is_read=False)
                        if success:
                            st.success("✅ Đã thực thi thành công SQL Local!")
                            st.code(sql_code, language="sql")
                            final_ui_message = ai_msg
                            status.update(label="Hoàn tất Thực thi (Thành công)", state="complete", expanded=False)
                        else:
                            st.error(f"❌ Lỗi SQL Local: {output_msg}")
                            st.code(sql_code, language="sql")
                            final_ui_message = f"{ai_msg}\n\n⚠️ *Lưu ý: Có lỗi xảy ra khi chạy SQL. Xem chi tiết bên dưới.*"
                            status.update(label="Thực thi thất bại", state="error", expanded=True)
                    else:
                        final_ui_message = ai_msg
                        status.update(label="Hoàn tất Thực thi", state="complete", expanded=False)
                    break

                elif action == "DEPLOY":
                    table_name = (ai_data.get("table_name") or "").strip().upper()
                    if not table_name:
                        final_ui_message = "❌ AI không xác định được tên bảng để Deploy!"
                        break
                    
                    st.write(f"🚀 Bắt đầu xuất bảng **{table_name}**...")
                    success, result = db_helper.export_table_to_sql(st.session_state.db_conn, table_name)
                    if success:
                        final_ui_message = f"**{ai_msg}**\n\n✨ **[HOÀN TẤT]** Đã xuất ra file `.sql` thành công!\n\n📂 **Vị trí file:** `{result['file_path']}`\n\n💡 **Việc của bạn:** Vào APEX Web -> SQL Workshop -> SQL Scripts -> Upload file này lên và Run!"
                        final_download_data = result['full_script']
                        final_download_filename = result['filename']
                        status.update(label="Đã xuất file thành công", state="complete", expanded=False)
                    else:
                        final_ui_message = f"❌ Lỗi khi Deploy: {result}"
                        status.update(label="Lỗi hệ thống", state="error", expanded=False)
                    break
        
        # In kết quả cuối cùng ra UI
        message_placeholder.markdown(final_ui_message, unsafe_allow_html=True)
        
        # Lưu vào lịch sử chat
        msg_payload = {"role": "assistant", "content": final_ui_message}
        if final_download_data is not None:
            msg_payload["download_data"] = final_download_data
            msg_payload["download_file_name"] = final_download_filename
        st.session_state.messages.append(msg_payload)
        
        # Hiển thị nút tải file ngay lập tức dưới câu trả lời
        if final_download_data is not None:
            st.download_button(
                label=f"📥 Tải File {final_download_filename}",
                data=final_download_data,
                file_name=final_download_filename,
                mime="text/x-sql",
                key=f"dl_now_{int(time.time())}"
            )
