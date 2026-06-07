# SmartCounterAI

SmartCounterAI là đồ án nhận dạng, theo dõi và đếm người/phương tiện trong video hoặc camera.

## Công nghệ

* YOLOv8: phát hiện đối tượng.
* ByteTrack/BoxMOT: theo dõi đối tượng và gán ID.
* OpenCV: xử lý video, vẽ bounding box, xuất video.
* Flask: giao diện web upload video/chọn camera.
* CSV: lưu thống kê kết quả.

## Chức năng

* Upload video trên web.
* Chọn camera input.
* Nhận diện Person, Car, Motorcycle, Bus, Truck.
* Tracking ID bằng ByteTrack.
* Đếm theo class.
* Đếm theo hướng đi qua line.
* Chọn line ngang, line dọc hoặc auto.
* Giữ nguyên tỉ lệ/kích thước video gốc để bounding box dễ quan sát.
* Xuất video output chuẩn web MP4.
* Xuất file CSV thống kê.
* Cấu trúc project chuẩn cho báo cáo đồ án.

## Các cải tiến đã thực hiện

* Tích hợp YOLOv8 để phát hiện đối tượng trong video và camera.
* Tích hợp ByteTrack/BoxMOT để theo dõi đối tượng bằng ID.
* Giảm tình trạng đếm trùng bằng cách chỉ đếm khi ID đi qua vạch.
* Bổ sung chức năng đếm theo từng loại đối tượng.
* Bổ sung lựa chọn line ngang, line dọc và auto.
* Hỗ trợ xử lý cả ảnh, video và camera.
* Xây dựng giao diện Flask để upload video và xem kết quả.
* Xuất video kết quả có bounding box, class name, tracking ID và số lượng đếm.
* Xuất file CSV để lưu thống kê.
* Tổ chức lại source code theo cấu trúc project rõ ràng.
* Giữ nguyên kích thước video gốc để bounding box dễ quan sát hơn.

## Dataset sử dụng và mở rộng

Ngoài mô hình YOLOv8 pretrained, đồ án có bổ sung hướng mở rộng dữ liệu bằng các dataset mới trên Roboflow nhằm cải thiện khả năng nhận diện trong các trường hợp thực tế.

### 1. Sitting and Standing Dataset

Dataset dùng để phân biệt trạng thái người đứng và người ngồi.

Link dataset:

```text
https://universe.roboflow.com/apollo-solutions-dev/sitting-and-standing/dataset/3
```

Mục đích sử dụng:

* Train thêm class `standing`.
* Train thêm class `sitting`.
* Cải thiện khả năng phân loại trạng thái của người.

### 2. Tricycle Dataset

Dataset dùng để bổ sung khả năng nhận diện phương tiện dạng xe ba bánh/tricycle.

Link dataset:

```text
https://universe.roboflow.com/emerson-muli-df8nm/tricycle-9zhkf/dataset/1
```

Mục đích sử dụng:

* Bổ sung class `tricycle`.
* Mở rộng khả năng nhận diện phương tiện.
* Hỗ trợ các tình huống giao thông thực tế đa dạng hơn.

### 3. Person Dataset

Dataset dùng để cải thiện khả năng nhận diện người.

Link dataset:

```text
https://universe.roboflow.com/asmaa-qqgs0/person-oyts0/dataset/2
```

Mục đích sử dụng:

* Tăng dữ liệu cho class `person`.
* Cải thiện nhận diện người trong các góc nhìn khác nhau.
* Hỗ trợ tốt hơn cho bài toán đếm người.

## Train thêm mô hình `.pt`

Ban đầu hệ thống sử dụng model YOLOv8 pretrained như:

```text
yolov8n.pt
```

Sau khi bổ sung dataset mới, có thể train thêm để tạo model riêng cho đồ án, ví dụ:

```text
best.pt
```

Model sau khi train có thể nhận diện tốt hơn các class mở rộng như:

* person
* standing
* sitting
* tricycle
* car
* motorcycle
* bus
* truck

Lệnh train tham khảo:

```bash
yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640 batch=8
```

Sau khi train xong, file model thường nằm tại:

```text
runs/detect/train/weights/best.pt
```

Có thể copy file `best.pt` vào thư mục `models/`:

```text
models/best.pt
```

Sau đó chỉnh chương trình để sử dụng model mới thay cho `yolov8n.pt`.

Ví dụ:

```python
model = YOLO("models/best.pt")
```

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

* Xe chạy ngang trái/phải: chọn `vertical`.
* Xe chạy trên/xuống: chọn `horizontal`.
* Không chắc hướng: chọn `auto`.

`line_pos = 0.5` nghĩa là vạch nằm giữa video. Có thể nhập pixel như `300`.

## Lưu ý về độ chính xác

Hệ thống đếm dựa trên việc tâm đối tượng vượt qua vạch. Nếu video có nhiều làn hoặc xe đi không qua vạch, hãy chỉnh line mode/line position để vạch cắt qua luồng xe chính.

## Hướng phát triển

* Train thêm model YOLOv8 bằng các dataset mới.
* Phân biệt người đứng và người ngồi.
* Nhận diện thêm tricycle và các phương tiện đặc thù.
* Cải thiện nhận diện người bị che khuất.
* Xây dựng dashboard thống kê.
* Lưu lịch sử đếm vào database.
* Tối ưu tốc độ xử lý để chạy thời gian thực tốt hơn.
