# StellarAcademy - AI Astronomy Educator & NASA 3D Simulator

StellarAcademy là một ứng dụng web giáo dục thiên văn học và khoa học vũ trụ tương tác cao. Hệ thống kết hợp giữa mô hình đa tác nhân (Multi-Agent Workflow) xây dựng trên Google ADK 2.0, hệ thống công cụ thời gian thực qua giao thức MCP (Model Context Protocol) kết nối với NASA API, và trình giả lập không gian 3D tương tác trực tiếp (NASA's Eyes Simulation).

---

## Hướng dẫn chạy ứng dụng trên máy cục bộ (Local)

Bạn có hai cách để khởi chạy ứng dụng này trên máy cá nhân: **Chạy trực tiếp bằng Terminal** (Khuyên dùng khi phát triển/chỉnh sửa code) hoặc **Chạy bằng Docker Compose** (Khuyên dùng để kiểm thử nhanh).

---

### Cách 1: Khởi chạy trực tiếp bằng Terminal (Khuyên dùng)

Yêu cầu máy bạn đã cài đặt sẵn:
* **Python** (Phiên bản 3.10 trở lên)
* **Node.js** (Phiên bản 18 trở lên)

#### Bước 1: Khởi chạy Backend (FastAPI Server)
1. Mở terminal mới và di chuyển vào thư mục `backend`:
   ```bash
   cd backend
   ```
2. Tạo môi trường ảo Python (nếu chưa tạo):
   ```bash
   python -m venv .venv
   ```
3. Kích hoạt môi trường ảo:
   * **Trên Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\activate
     ```
   * **Trên macOS / Linux:**
     ```bash
     source .venv/bin/activate
     ```
4. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
5. Đảm bảo file `.env` đã có trong thư mục `backend` với nội dung chứa khóa API của bạn:
   ```env
   AI_STUDIO_API = "YOUR_GEMINI_API_KEY"
   NASA_API = "YOUR_NASA_API_KEY"
   ```
6. Khởi chạy máy chủ Backend:
   ```bash
   python main.py
   ```
   *Máy chủ backend sẽ khởi chạy tại địa chỉ: `http://localhost:8000`*

---

#### Bước 2: Khởi chạy Frontend (React + Vite)
1. Mở một terminal mới song song và di chuyển vào thư mục `frontend`:
   ```bash
   cd frontend
   ```
2. Cài đặt các gói thư viện Node.js:
   ```bash
   npm install
   ```
3. Khởi chạy ứng dụng Frontend ở chế độ phát triển:
   ```bash
   npm run dev
   ```
4. Mở trình duyệt và truy cập vào đường dẫn hiển thị trên terminal (thường là `http://localhost:5173`).

---

### Cách 2: Khởi chạy nhanh bằng Docker Compose

Cách này yêu cầu máy bạn đã cài đặt và đang bật **Docker Desktop**.

1. Đảm bảo file `.env` đã có ở thư mục gốc của dự án (cùng cấp với file `docker-compose.yml`).
2. Mở terminal tại thư mục gốc của dự án và chạy lệnh:
   ```bash
   docker-compose up --build
   ```
3. Docker sẽ tự động xây dựng container cho cả Backend và Frontend, cấu hình mạng nội bộ và khởi chạy.
4. Sau khi hoàn tất, mở trình duyệt và truy cập vào địa chỉ:
   ```
   http://localhost:3000
   ```
5. Để dừng ứng dụng, nhấn `Ctrl + C` trên terminal hoặc chạy lệnh `docker-compose down`.

---

## Cấu trúc thư mục chính

```text
├── backend/
│   ├── agent_workflow.py    # Định nghĩa luồng xử lý đa tác nhân (ADK 2.0 Graph)
│   ├── nasa_mcp_server.py   # Máy chủ MCP kết nối và lấy dữ liệu trực tiếp từ NASA API
│   ├── main.py              # FastAPI Web Server kết nối API với giao diện
│   ├── requirements.txt     # Các thư viện Python cần thiết
│   └── Dockerfile           # Dockerfile đóng gói backend
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Giao diện chính (Retro Arcade Chat & 3D Simulation)
│   │   └── index.css        # Hệ thống CSS tùy biến giao diện Retro 8-bit/16-bit
│   ├── package.json         # Danh sách thư viện và script của Frontend
│   └── Dockerfile           # Dockerfile đóng gói frontend sử dụng Nginx
├── docker-compose.yml       # Cấu hình khởi chạy nhanh toàn bộ hệ thống bằng Docker
└── sync_and_push.bat        # Kịch bản tự động đồng bộ code và đẩy lên GitHub
```

---

## Tính năng nổi bật của dự án

1. **Giao diện Retro Arcade Độc đáo:** Thiết kế theo phong cách trò chơi điện tử 8-bit/16-bit với hiệu ứng CRT scanline, bảng màu chính thức của NASA, font chữ pixel đặc trưng mang lại trải nghiệm trẻ trung và lôi cuốn.
2. **Giả lập 3D NASA's Eyes Đồng bộ:** Khi bạn hỏi về một hành tinh (ví dụ: Sao Hỏa) hoặc tàu vũ trụ (ví dụ: Voyager 1), hệ thống AI không chỉ trả lời bằng văn bản mà còn tự động điều khiển, đồng bộ hóa khung cảnh giả lập 3D bên phải tập trung vào đối tượng đó.
3. **Dữ liệu thời gian thực từ NASA:** Tích hợp trực tiếp với các API chính thức của NASA thông qua MCP Server để lấy Ảnh Thiên văn trong ngày (APOD), thông tin tiểu hành tinh bay gần Trái Đất (NeoWs), và các cảnh báo thời tiết vũ trụ (DONKI).
4. **Cơ chế tự phục hồi lỗi API:** Backend tích hợp sẵn vòng lặp tự động thử lại với độ trễ tăng dần (Exponential Backoff) giúp ứng dụng hoạt động bền bỉ, giảm thiểu lỗi quá tải (503/500) từ API miễn phí.
