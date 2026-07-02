# Oracle VibeApex AI Agent

Đây là một ứng dụng quản lý và tương tác với Oracle Database sử dụng trí tuệ nhân tạo (Gemini AI) và giao diện Streamlit.

## Các Tính Năng Nổi Bật

1. **AI DBA Trợ Lý Mệnh Lệnh:** Dịch yêu cầu ngôn ngữ tự nhiên thành câu lệnh SQL hoặc PL/SQL và tự động thực thi (Nếu được người dùng cho phép).
2. **Quản Lý Database Local:** Kết nối trực tiếp với Oracle Database nội bộ, truy vấn và trả về kết quả dưới dạng bảng.
3. **Smart Data Importer:** Upload file Excel (.xlsx) hoặc CSV và tự động Import toàn bộ dữ liệu vào bảng Oracle.
4. **Phân Tích AI:** Gửi cấu trúc và dữ liệu lỗi cho AI để tự động sửa lỗi và đưa ra lời khuyên.

## Cách Cài Đặt

1. **Clone repository này về máy:**
   ```bash
   git clone <địa_chỉ_repo_của_bạn>
   cd Oracle_VibeApex
   ```

2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Thiết lập Môi Trường:**
   Tạo một file `.env` ở cùng thư mục và điền thông tin sau (Hoặc bạn có thể nhập trực tiếp trên giao diện web):
   ```env
   GEMINI_API_KEY=your_api_key_here
   DB_USER=your_db_username
   DB_PASS=your_db_password
   DB_HOST=localhost
   DB_PORT=1521
   DB_SID=your_sid_or_service_name
   ```

4. **Chạy Ứng Dụng:**
   ```bash
   streamlit run app.py
   ```
   Sau đó truy cập vào `http://localhost:8501` trên trình duyệt.

## Công Nghệ Sử Dụng
- [Streamlit](https://streamlit.io/) (Giao diện Web)
- [OracleDB](https://python-oracledb.readthedocs.io/) (Kết nối Database)
- [Google Generative AI](https://ai.google.dev/) (Tích hợp Gemini 1.5/2.0)
- Pandas & OpenPyXL (Xử lý dữ liệu Excel/CSV)
