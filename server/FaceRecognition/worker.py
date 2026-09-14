import sys
import struct
import os
import cv2
from recognition import FaceRecognitionCamera


class Worker:
    def __init__(self, known_people):
        self.face_recognition = FaceRecognitionCamera(known_people)

    def get_frame(self):
        return self.face_recognition.get_frame()

    def release(self):
        self.face_recognition.release()


if __name__ == "__main__":

    # Folder containing worker.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # People known by the face recognition system
    known_people = {
        "Velizar": os.path.join(BASE_DIR, "velizar.jpg")
    }

    print("Starting face recognition...", file=sys.stderr)
    print("Known people:", known_people, file=sys.stderr)

    worker = Worker(known_people)

    try:
        while True:
            frame_data = worker.get_frame()

            if frame_data is None:
                continue

            frame = frame_data["image"]

            success, encoded = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 80]
            )

            if not success:
                continue

            data = encoded.tobytes()

            # Send frame size first
            sys.stdout.buffer.write(struct.pack(">I", len(data)))

            # Send JPEG
            sys.stdout.buffer.write(data)

            sys.stdout.buffer.flush()

    except KeyboardInterrupt:
        pass

    finally:
        worker.release()