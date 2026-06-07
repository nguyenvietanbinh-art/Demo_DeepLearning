# SmartCounterAI Final Project

SmartCounterAI là đồ án nhận dạng, theo dõi và đếm người/phương tiện trong video hoặc camera.

## Công nghệ
- YOLOv8: phát hiện đối tượng.
- ByteTrack/BoxMOT: theo dõi đối tượng và gán ID.
- OpenCV: xử lý video, vẽ bounding box, xuất video.
- Flask: giao diện web upload video/chọn camera.
- CSV: lưu thống kê kết quả.

## Chức năng
- Upload video trên web.
- Chọn camera input.
- Nhận diện Person, Car, Motorcycle, Bus, Truck.
- Tracking ID bằng ByteTrack.
- Đếm theo class.
- Đếm theo hướng đi qua line.
- Chọn line ngang, line dọc hoặc auto.
- Giữ nguyên tỉ lệ/kích thước video gốc để bounding box dễ quan sát.
- Xuất video output chuẩn web MP4.
- Xuất file CSV thống kê.
- Cấu trúc project chuẩn cho báo cáo đồ án.

## Cài đặt
```bash
conda activate smartcounter
pip install -r requirements.txt
```

## Chạy Web
```bash
python app.py
```

Mở trình duyệt:
```text
http://127.0.0.1:5000
```

## Chạy CLI với video
```bash
python main.py --source data/videos/test.mp4 --line-mode auto --line-pos 0.5
```

## Chạy CLI với camera
```bash
python main.py --source 0 --line-mode auto --line-pos 0.5
```

## Chọn line để đếm chính xác hơn
- Xe chạy ngang trái/phải: chọn `vertical`.
- Xe chạy trên/xuống: chọn `horizontal`.
- Không chắc hướng: chọn `auto`.

`line_pos = 0.5` nghĩa là vạch nằm giữa video. Có thể nhập pixel như `300`.

## Lưu ý về độ chính xác
Hệ thống đếm dựa trên việc tâm đối tượng vượt qua vạch. Nếu video có nhiều làn hoặc xe đi không qua vạch, hãy chỉnh line mode/line position để vạch cắt qua luồng xe chính.
