# Tanin (他人) - Anonymous Real-time Chat

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/your-username/tanin-app/main.yml?branch=main)](https://github.com/your-username/tanin-app/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Tanin (他人)**, trong tiếng Nhật có nghĩa là "người lạ", là một ứng dụng web hiệu năng cao cho phép người dùng kết nối và trò chuyện ẩn danh (văn bản & video) với những người xa lạ một cách ngẫu nhiên.

Dự án này không chỉ là một ứng dụng chat, mà còn là một minh chứng cho việc thiết kế và xây dựng một hệ thống backend phức tạp, có khả năng mở rộng, sử dụng các công nghệ hiện đại và tuân thủ các phương pháp DevOps tốt nhất.

---

## 🏛️ Sơ Đồ Kiến Trúc

Sơ đồ dưới đây mô tả kiến trúc tổng quan và luồng dữ liệu của hệ thống.

![Tanin Architecture Diagram](https://your-image-hosting-url/tanin_architecture.png)
*(Lưu ý: Bạn nên tự vẽ một sơ đồ kiến trúc bằng công cụ như [draw.io](https://draw.io) hoặc [Excalidraw](https://excalidraw.com/) và tải lên để lấy link)*

---

## ✨ Tính Năng Nổi Bật

-   **Ghép cặp thời gian thực**: Sử dụng Redis để quản lý hàng đợi và ghép cặp người dùng một cách hiệu quả.
-   **Chat Text & Video**:
    -   **Text**: Giao tiếp tức thời với độ trễ thấp thông qua **WebSockets**.
    -   **Video**: Gọi video P2P chất lượng cao, bảo mật và tiết kiệm băng thông server nhờ **WebRTC**.
-   **Kiến trúc hướng dịch vụ**: Tách biệt rõ ràng giữa các tác vụ RESTful (quản lý) và các tác vụ Real-time (tương tác).
-   **Tài liệu hóa API tự động**: Giao diện Swagger UI và ReDoc tương tác được sinh ra tự động từ code nhờ FastAPI.
-   **Containerized & Reproducible**: Toàn bộ ứng dụng và các dịch vụ phụ thuộc được đóng gói bằng Docker, đảm bảo môi trường phát triển và triển khai nhất quán.
-   **CI/CD Pipeline**: Tích hợp GitHub Actions để tự động chạy kiểm thử (tests) và phân tích code (linting) mỗi khi có thay đổi.

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

| Lĩnh vực              | Công nghệ                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| **Backend**           | Python 3.11+, FastAPI, Uvicorn                                                                          |
| **Giao tiếp Real-time** | WebSockets (cho Signaling & Text), WebRTC (cho Media)                                                   |
| **Cơ sở dữ liệu**     | Redis (Quản lý trạng thái real-time), PostgreSQL (Lưu trữ dữ liệu bền vững)                               |
| **Tương tác DB**      | SQLAlchemy 2.0 (ORM bất đồng bộ), Pydantic (Validation)                                                 |
| **Bảo mật**            | Passlib (Hashing), python-jose (JWT)                                                                    |
| **Quản lý dự án**     | Poetry                                                                                                  |
| **DevOps**            | Docker, Docker Compose, Nginx, GitHub Actions                                                           |
| **Testing**           | Pytest, pytest-asyncio, HTTPX                                                                           |

---

## 🚀 Bắt đầu (Getting Started)

### Yêu cầu tiên quyết
-   Python 3.11+
-   Poetry (>=1.2)
-   Docker và Docker Compose

### Cài đặt và Chạy cục bộ

1.  **Clone repository:**
    ```bash
    git clone https://github.com/huyvnnb/tanin.git
    cd tanin
    ```

2.  **Tạo file biến môi trường:**
    Dự án sử dụng file `.env` để quản lý các biến môi trường. Hãy tạo file của bạn từ file mẫu.
    ```bash
    cp .env.example .env
    ```
    *(Bạn có thể chỉnh sửa các giá trị trong file `.env` nếu muốn, nhưng các giá trị mặc định đã được cấu hình để chạy với Docker Compose.)*

3.  **Cài đặt các dependency:**
    Poetry sẽ đọc file `pyproject.toml`, giải quyết các dependency, và cài đặt chúng vào một môi trường ảo riêng biệt.
    ```bash
    poetry install
    ```

4.  **Khởi chạy hệ thống với Docker Compose:**
    Lệnh này sẽ dựng và khởi chạy tất cả các container cần thiết (app, db, redis) ở chế độ nền.
    ```bash
    docker-compose up -d --build
    ```

5.  **Xong! Hệ thống đã sẵn sàng:**
    -   **Backend Server**: `http://localhost:8000`
    -   **API Docs (Swagger)**: `http://localhost:8000/docs`
    -   **API Docs (ReDoc)**: `http://localhost:8000/redoc`

### Chạy Kiểm thử (Tests)
Để đảm bảo chất lượng code, hãy chạy bộ test bằng `pytest`:
```bash
poetry run pytest