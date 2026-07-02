# 💻 Oracle VibeApex: Trợ Lý Ảo AI DBA & Quản Trị Oracle Database Thông Minh & deploy Apex Table

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![OracleDB](https://img.shields.io/badge/Database-Oracle%2011g/12c/19c/21c-orange.svg)](https://python-oracledb.readthedocs.io/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20Flash/Pro-brightgreen.svg)](https://ai.google.dev/)

**Oracle VibeApex** là giải pháp trợ lý AI DBA và quản trị cơ sở dữ liệu chuyên nghiệp được xây dựng trên nền tảng **Python**, **Streamlit** và tích hợp sức mạnh từ mô hình ngôn ngữ lớn **Google Gemini (LLM)**. Ứng dụng giúp đơn giản hóa quá trình vận hành, viết script, gỡ lỗi PL/SQL và nạp dữ liệu vào cơ sở dữ liệu Oracle thông qua giao diện hội thoại trực quan (Conversational UI) và các công cụ mở rộng mạnh mẽ.

---

## 🚀 Các Tính Năng Nổi Bật (Key Features)

### 🤖 1. Trợ Lý AI DBA & Viết Code Tự Động (AI-Powered SQL Generator)
* **Dịch ngôn ngữ tự nhiên thành SQL/PL/SQL:** Chỉ cần gõ yêu cầu của bạn bằng tiếng Việt (Ví dụ: *"Tạo cho tôi một bảng lưu thông tin hóa đơn và các ràng buộc liên quan"*), AI sẽ tự động tạo cấu trúc bảng hoàn chỉnh.
* **Đề xuất tối ưu hóa truy vấn:** Phân tích, giải thích mã lỗi và tối ưu hóa các câu lệnh SQL dài hoặc truy vấn chậm.
* **Thực thi trực tiếp an toàn (Interactive Execution):** Người dùng có thể kiểm tra đoạn mã SQL do AI sinh ra và nhấn thực thi trực tiếp trên giao diện để áp dụng vào DB chỉ bằng 1 click.

### 🐛 2. Bộ Gỡ Lỗi PL/SQL Nâng Cao (Advanced PL/SQL Debugger)
* Khi biên dịch (Compile) các khối lệnh PL/SQL phức tạp như **Procedure, Function, Trigger, Package** gặp lỗi:
* Hệ thống sẽ tự động bắt lỗi và truy vấn ngược lại bảng hệ thống ẩn của Oracle là `USER_ERRORS`.
* Phân tích và hiển thị chi tiết: **Tên đối tượng bị lỗi, Số dòng (Line), Số cột (Position), và Nội dung lỗi cụ thể**.
* Không còn tình trạng đoán mò lỗi biên dịch khi viết mã PL/SQL.

###  3. Trình Nhập Liệu Thông Minh (Smart Data Importer)
* Hỗ trợ tải lên (upload) các file dữ liệu dạng **Excel (.xlsx, .xls)** hoặc **CSV**.
* Người dùng chỉ cần nhập tên bảng đích, hệ thống sẽ tự động quét và map cấu trúc cột trong file với các cột thực tế trong bảng cơ sở dữ liệu Oracle (hỗ trợ so khớp không phân biệt hoa thường).
* Sử dụng cơ chế chèn dữ liệu hàng loạt **`executemany()`** của thư viện `oracledb` giúp tốc độ ghi đè/chèn dữ liệu cực nhanh và hạn chế tối đa tài nguyên mạng.
* Hiển thị thông báo kết quả chi tiết: Số bản ghi chèn thành công, và chi tiết nguyên nhân nếu có lỗi dòng nào.

### ⚙️ 4. Kiến Trúc Module & Bảo Mật Chuẩn Doanh Nghiệp (Secure & Modular Architecture)
* **Tách biệt mã nguồn (Decoupled Design):** Mã nguồn được tổ chức sạch sẽ theo kiến trúc chia nhỏ lớp nghiệp vụ:
  * `app.py`: Đảm nhiệm việc dựng UI bằng Streamlit và quản lý trạng thái phiên làm việc (Session State).
  * `db_helper.py`: Đảm nhiệm tất cả các kết nối Driver đến Oracle DB, truy vấn metadata, nhập liệu và xử lý lỗi hệ thống.
  * `ai_helper.py`: Xử lý giao thức API gọi đến mô hình Google Gemini và cơ chế chuyển đổi mô hình dự phòng tự động (failover).
* **Bảo mật tuyệt đối (Zero Credentials Leak):** Toàn bộ thông tin cấu hình nhạy cảm (Username, Password, API Key) được đưa ra ngoài thông qua file môi trường `.env` hoặc nhập trực tiếp từ Sidebar bảo mật. Không lưu cứng bất cứ thông tin nhạy cảm nào vào mã nguồn.

---

##  Hướng Dẫn Cài Đặt Chi Tiết (Installation Guide)

###  Yêu Cầu Hệ Thống (Prerequisites)
* Hệ điều hành: Windows, macOS, hoặc Linux.
* Python phiên bản **3.10** hoặc cao hơn.
* Oracle Database Client hoặc quyền kết nối tới cơ sở dữ liệu Oracle bất kỳ (Local hoặc Cloud).

### 1. Tải Mã Nguồn
```bash
git clone <url-repository-cua-ban>
cd Oracle_VibeApex
```

### 2. Thiết Lập Môi Trường Ảo & Cài Đặt Thư Viện
Khuyến nghị tạo môi trường ảo độc lập để tránh xung đột thư viện:
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 3. Cấu Hình Biến Môi Trường
Tạo một file `.env` ở thư mục gốc của dự án (bạn có thể copy cấu trúc từ file `.env.example` có sẵn):
```env
GEMINI_API_KEY=Nhập_API_Key_Gemini_Tại_Đây
DB_USER=tên_đăng_nhập_database
DB_PASS=mật_khẩu_database
DB_HOST=localhost
DB_PORT=1521
DB_SID=xepdb1 (hoặc Tên Service Name của bạn)
```
*Lưu ý: Nếu không khai báo file `.env`, ứng dụng sẽ hiển thị các ô nhập trống ở Sidebar để bạn tự cấu hình trên giao diện.*

---

## Cách Vận Hành Ứng Dụng (Running the App)

Chạy câu lệnh dưới đây để khởi động ứng dụng Web:
```bash
streamlit run app.py
```
Sau khi chạy thành công, một trang web sẽ tự động mở ra tại địa chỉ mặc định: [http://localhost:8501](http://localhost:8501).

---

## Cấu Trúc Thư Mục Dự Án (Project Directory Tree)

```text
Oracle_VibeApex/
│
├── app.py                # Điểm khởi chạy ứng dụng & Quản lý giao diện Streamlit
├── db_helper.py          # Lớp tương tác Oracle DB (Connect, Execute, Debug, Import)
├── ai_helper.py          # Lớp tương tác với Gemini LLM (Failover & API connection)
│
├── requirements.txt      # Danh sách các thư viện cần cài đặt
├── .env.example          # File cấu hình mẫu môi trường
├── .gitignore            # Khai báo chặn đẩy file bảo mật (.env) lên GitHub
└── README.md             # Hướng dẫn chi tiết dự án (Bạn đang đọc file này)
```

---

##  Giấy Phép & Bảo Mật (License & Security)
* Dự án này được mở nguồn theo giấy phép **MIT License**.
* **Cảnh báo quan trọng:** Không bao giờ cam kết (commit) file `.env` chứa mật khẩu thực lên các nền tảng public như GitHub. Hãy luôn giữ file `.env` trong danh mục `.gitignore`.
