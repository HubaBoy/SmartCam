import cv2
import face_recognition


class FaceRecognitionCamera:

    def __init__(self, known_people):
        self.known_faces_encoding = []
        self.known_faces_names = []

        # Load known people
        for name, image_path in known_people.items():

            print(f"Loading face: {name} from {image_path}")

            image = face_recognition.load_image_file(image_path)

            encodings = face_recognition.face_encodings(image)

            if not encodings:
                print(f"No face found in {image_path}")
                continue

            # Use the first detected face
            self.known_faces_encoding.append(encodings[0])
            self.known_faces_names.append(name)

            print(f"Loaded face for: {name}")

        # Open camera
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")

        print("Camera opened successfully")

    def get_frame(self):

        success, frame = self.camera.read()

        if not success:
            print("Could not read camera frame")
            return None

        # OpenCV uses BGR.
        # face_recognition expects RGB.
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Find faces
        face_locations = face_recognition.face_locations(
            rgb_frame
        )

        # Get face encodings
        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations
        )

        faces = []

        for (top, right, bottom, left), face_encoding in zip(
            face_locations,
            face_encodings
        ):

            name = "Unknown"

            # Compare against known faces
            if self.known_faces_encoding:

                matches = face_recognition.compare_faces(
                    self.known_faces_encoding,
                    face_encoding,
                    tolerance=0.6
                )

                if True in matches:

                    first_match_index = matches.index(True)

                    name = self.known_faces_names[
                        first_match_index
                    ]

            # Draw rectangle
            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 0, 255),
                2
            )

            # Draw name
            cv2.putText(
                frame,
                name,
                (left, max(top - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

            faces.append({
                "name": name,
                "location": {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                }
            })

        return {
            "image": frame,
            "faces": faces
        }

    def release(self):
        if self.camera:
            self.camera.release()