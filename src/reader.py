import cv2
import numpy as np
from pyzbar.pyzbar import decode


def process_frame(frame):
    # Chuyển đổi hình ảnh sang thang độ xám
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Giải mã các mã QR trong khung hình
    decoded_objects = decode(gray_frame)

    for obj in decoded_objects:
        # Lấy tọa độ của hộp bao quanh mã QR
        points = obj.polygon
        if len(points) == 4:
            pts = [tuple(point) for point in points]
            pts = [pts]
            pts = np.array(pts, dtype=np.int32)  # Convert pts to a numpy array
            cv2.polylines(
                frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2
            )  # Pass [pts] as a list of numpy arrays

        # Đọc dữ liệu từ mã QR
        qr_data = obj.data.decode("utf-8")
        print(f"QR Code Data: {qr_data}")

        # Hiển thị dữ liệu trên khung hình
        cv2.putText(
            frame,
            qr_data,
            (points[0].x, points[0].y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )

    return frame


def read_qr_from_video_binary(video_data):
    cap = cv2.VideoCapture()
    cap.open(video_data)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Xử lý khung hình
        frame = process_frame(frame)

        # Hiển thị khung hình
        cv2.imshow("QR Code Reader", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
