import cv2
import mediapipe as mp
import math
import os
import time


# =========================
# STUDENT DETAILS
# =========================

register_number = "22MCA001"

student_name = "Ankith_S_Shaji"


# =========================
# CREATE FOLDER
# =========================

folder_name = (

    f"{register_number}_"
    f"{student_name}"

)

path = os.path.join(

    'media',
    'student_faces',
    folder_name

)

os.makedirs(

    path,

    exist_ok=True

)


# =========================
# CAMERA
# =========================

cap = cv2.VideoCapture(0)


# =========================
# MEDIAPIPE
# =========================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(

    max_num_faces=1,

    refine_landmarks=True,

    min_detection_confidence=0.5,

    min_tracking_confidence=0.5

)

mp_draw = mp.solutions.drawing_utils


# =========================
# BLINK VARIABLES
# =========================

blink_count = 0

blink_detected = False


# =========================
# IMAGE COUNTER
# =========================

image_count = 0

max_images = 30

last_capture_time = time.time()


# =========================
# DISTANCE FUNCTION
# =========================

def distance(point1, point2):

    return math.sqrt(

        (point1.x - point2.x) ** 2 +

        (point1.y - point2.y) ** 2

    )


# =========================
# MAIN LOOP
# =========================

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2RGB

    )

    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            # EYE LANDMARKS

            top = face_landmarks.landmark[159]

            bottom = face_landmarks.landmark[145]

            left = face_landmarks.landmark[33]

            right = face_landmarks.landmark[133]

            # EYE RATIO

            vertical = distance(top, bottom)

            horizontal = distance(left, right)

            ratio = vertical / horizontal

            # DRAW EYE POINTS

            h, w, _ = frame.shape

            for point in [159,145,33,133]:

                x = int(

                    face_landmarks.landmark[point].x * w

                )

                y = int(

                    face_landmarks.landmark[point].y * h

                )

                cv2.circle(

                    frame,

                    (x,y),

                    3,

                    (0,255,0),

                    -1

                )

            # BLINK DETECTION

            if ratio < 0.20:

                blink_detected = True

            if ratio > 0.25 and blink_detected:

                blink_count += 1

                blink_detected = False

            # SHOW BLINKS

            cv2.putText(

                frame,

                f'Blinks: {blink_count}',

                (20,50),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0,255,0),

                2

            )

            # LIVE VERIFIED

            if blink_count >= 1:

                cv2.putText(

                    frame,

                    'LIVE VERIFIED',

                    (20,100),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    1,

                    (255,0,0),

                    3

                )

                # CAPTURE IMAGES

                current_time = time.time()

                if (

                    current_time - last_capture_time > 1

                    and image_count < max_images

                ):

                    image_count += 1

                    image_path = os.path.join(

                        path,

                        f"{image_count}.jpg"

                    )

                    cv2.imwrite(

                        image_path,

                        frame

                    )

                    print(

                        f"Saved: {image_path}"

                    )

                    last_capture_time = current_time

            # IMAGE COUNT

            cv2.putText(

                frame,

                f'Images: {image_count}/30',

                (20,150),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0,255,255),

                2

            )

    else:

        cv2.putText(

            frame,

            'NO FACE',

            (20,50),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (0,0,255),

            2

        )

    # SHOW WINDOW

    cv2.imshow(

        "Dataset Capture System",

        frame

    )

    # STOP WHEN 30 IMAGES SAVED

    if image_count >= max_images:

        print(

            "Dataset Collection Completed"

        )

        break

    # EXIT

    if cv2.waitKey(1) & 0xFF == ord('q'):

        break


# =========================
# RELEASE
# =========================

cap.release()

cv2.destroyAllWindows()