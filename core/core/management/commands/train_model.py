from django.core.management.base import BaseCommand

import pickle
import face_recognition
import os
import cv2

from student.models import Student, StudentFace


class Command(BaseCommand):

    help = 'Train Face Recognition Model'

    def handle(self, *args, **kwargs):

        known_encodings = []
        known_names = []

        students = Student.objects.all()

        print("\n============================")
        print("TRAINING AI FACE MODEL")
        print("============================\n")

        total_encoded = 0
        total_skipped = 0

        # =====================
        # LOOP STUDENTS
        # =====================

        for student in students:

            print(f"\nProcessing: {student.user.first_name}")

            # =====================
            # USE ONLY LATEST 5 IMAGES
            # =====================

            faces = StudentFace.objects.filter(

                student=student

            ).order_by('-id')[:5]

            # NO DATASET

            if not faces.exists():

                print("⚠ No dataset found")

                continue

            # =====================
            # LOOP IMAGES
            # =====================

            for face in faces:

                try:

                    # =====================
                    # IMAGE PATH
                    # =====================

                    image_path = face.image.path

                    # =====================
                    # FILE EXISTS
                    # =====================

                    if not os.path.exists(image_path):

                        print(

                            f"❌ Missing file skipped: "
                            f"{image_path}"

                        )

                        total_skipped += 1

                        continue

                    # =====================
                    # LOAD IMAGE
                    # =====================

                    image = face_recognition.load_image_file(
                        image_path
                    )

                    # =====================
                    # RESIZE FOR SPEED
                    # =====================

                    small_image = cv2.resize(

                        image,

                        (320, 240)

                    )

                    # =====================
                    # FACE DETECTION
                    # =====================

                    face_locations = face_recognition.face_locations(

                        small_image,

                        model="hog"

                    )

                    # =====================
                    # NO FACE
                    # =====================

                    if len(face_locations) == 0:

                        print(

                            f"⚠ No face found: "
                            f"{image_path}"

                        )

                        total_skipped += 1

                        continue

                    # =====================
                    # MULTIPLE FACE
                    # =====================

                    if len(face_locations) > 1:

                        print(

                            f"⚠ Multiple faces skipped: "
                            f"{image_path}"

                        )

                        total_skipped += 1

                        continue

                    # =====================
                    # FACE ENCODING
                    # =====================

                    encodings = face_recognition.face_encodings(

                        small_image,

                        face_locations,

                        num_jitters=1

                    )

                    # =====================
                    # SAVE ENCODINGS
                    # =====================

                    if len(encodings) > 0:

                        known_encodings.append(
                            encodings[0]
                        )

                        known_names.append(
                            student.id
                        )

                        total_encoded += 1

                        print(

                            f"✅ Encoded: "
                            f"{student.user.first_name}"

                        )

                    else:

                        print(

                            f"⚠ Encoding failed: "
                            f"{image_path}"

                        )

                        total_skipped += 1

                except Exception as e:

                    print(

                        f"\n❌ Error processing: "
                        f"{image_path}"

                    )

                    print(e)

                    total_skipped += 1

        # =====================
        # SAVE MODEL
        # =====================

        with open('encodings.pkl', 'wb') as f:

            pickle.dump({

                'encodings': known_encodings,

                'names': known_names

            }, f)

        # =====================
        # FINAL OUTPUT
        # =====================

        print("\n============================")
        print("AI MODEL TRAINED SUCCESSFULLY")
        print("============================\n")

        print(f"✅ Total Encoded Faces : {total_encoded}")
        print(f"⚠ Total Skipped Faces : {total_skipped}")

        print("\nencodings.pkl created successfully\n")