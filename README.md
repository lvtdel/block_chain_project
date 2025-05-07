# Hướng dẫn Chạy Blockchain Lite

## Yêu cầu hệ thống
- Python 3.x
- virtualenv (môi trường ảo Python), có thể setup nhanh với pycharm hoặc theo hướng dẫn

## Tạo môi trường ảo

```shell

python -m venv .venv
```

## Kích hoạt môi trường ảo

### Windows
```shell

.venv\Scripts\activate
```

## Cài đặt các gói phụ thuộc
```shell

pip install -r requirements.txt
```
## Cấu hình file .env
Tham khảo từ .env.example
- DIFFICULTY: Độ khó của blockchain trong Pow
- MAX_TRANSACTION_PER_BLOCK: Số giao dịch (transaction) tối đa của 1 block

## Chạy với pycharm
- Hiện đã lưu cấu hình run trong .run, pycharm sẽ tự nhận.  
- Chạy cấu hình [Block chain] sẽ chạy cả 2 node  
  
**Hoặc chạy thủ công dưới đây nếu không dùng pycharm**

## Chạy Chain 1 (Node đầu tiên)
Sử dụng các tham số sau:
- PYTHONUNBUFFERED=1
- HTTP_PORT=5000
- GRPC_PORT=5001
- MY_ADD=127.0.0.1:5001

### Có thể cấu hình file .env và chạy 
```shell

python app.py
```
### Hoặc sử dụng biến môi trường tạm thời
Powershell
```bash

$$env:PYTHONUNBUFFERED = "1";$env:HTTP_PORT = "5000";$env:GRPC_PORT = "5001";$env:MY_ADD = "127.0.0.1:5001";python app.py
```
CMD
```bash

set PYTHONUNBUFFERED=1 && set HTTP_PORT=5000 && set GRPC_PORT=5001 && set MY_ADD=127.0.0.1:5001 && python app.py
```

## Chạy Chain 2 (Node thứ hai)
Sử dụng các tham số sau:
- PYTHONUNBUFFERED=1
- HTTP_PORT=6000
- GRPC_PORT=6001
- MY_ADD=127.0.0.1:6001
- REGISTER_ADD=127.0.0.1:5001

Khi có biến môi trường REGISTER_ADD thì node sẽ tự đăng ký với node có địa chỉ register đó

### Có thể cấu hình file .env và chạy
```bash

python app.py
```
### Hoặc sử dụng biến môi trường tạm thời
Powershell
```shell

$$env:PYTHONUNBUFFERED = "1"; $env:HTTP_PORT = "6000"; $env:GRPC_PORT = "6001"; $env:MY_ADD = "127.0.0.1:6001"; $env:REGISTER_ADD = "127.0.0.1:5001"; python app.py
```
CMD
```bash

set PYTHONUNBUFFERED=1 && set HTTP_PORT=6000 && set GRPC_PORT=6001 && set MY_ADD=127.0.0.1:6001 && set REGISTER_ADD=127.0.0.1:5001 && python app.py
```
## Kiểm tra hoạt động
- Chain 1 sẽ chạy với HTTP endpoint tại `http://localhost:5000`
- Chain 2 sẽ chạy với HTTP endpoint tại `http://localhost:6000`

## Cấu trúc cổng
### Chain 1:
- HTTP Port: 5000
- gRPC Port: 5001

### Chain 2:
- HTTP Port: 6000
- gRPC Port: 6001
- Kết nối với Chain 1 thông qua địa chỉ REGISTER_ADD

## Thử nghiệm
### Với ứng dụng test api insomia
Import file insomia_test_api/Insomnia_2025-05-07.har để lấy các enpoint test viết sẵn.

### Tạo cặp private-public key
Chạy lệnh sau
```bash

python generate_key.py
```
Copy private key lưu vào file /private_key_1

### Tạo, ký giao dịch và export json
- Tham khảo file sign_transaction.py
- Sau khi chạy sẽ sinh ra dữ liệu json dùng cho api tạo giao dịch [POST] /transaction/new

## Lưu ý
- Đảm bảo không có ứng dụng nào khác đang sử dụng các cổng 5000, 5001, 6000 và 6001
- Chạy Chain 1 trước, sau đó mới chạy Chain 2
- Chain 2 sẽ tự động kết nối với Chain 1 thông qua địa chỉ REGISTER_ADD
