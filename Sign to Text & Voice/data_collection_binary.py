import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import os
import traceback


capture = cv2.VideoCapture(0)

# Hand detectors
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)

# Count images in test directory
count = len(os.listdir(
    "C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\test_data_2.0\\Gray_imgs\\A"
))

p_dir = "A"
c_dir = "a"

offset = 30
step = 1
flag = False
suv = 0

# Create and save blank white image
white = np.ones((400, 400), np.uint8) * 255
cv2.imwrite("C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\white.jpg", white)

while True:
    try:
        success, frame = capture.read()
        if not success:
            print("❌ Failed to read from camera")
            break

        frame = cv2.flip(frame, 1)
        img_final = img_final1 = img_final2 = None

        # ✅ FIXED: Unpack hands and frame
        hands, frame = hd.findHands(frame, draw=False, flipType=True)

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            # Safe crop
            y1 = max(0, y - offset)
            y2 = min(frame.shape[0], y + h + offset)
            x1 = max(0, x - offset)
            x2 = min(frame.shape[1], x + w + offset)

            image = frame[y1:y2, x1:x2]
            roi = image

            # Create grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (1, 1), 2)

            # Create binary image
            gray2 = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur2 = cv2.GaussianBlur(gray2, (5, 5), 2)
            th3 = cv2.adaptiveThreshold(
                blur2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            _, test_image = cv2.threshold(th3, 27, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Prepare gray image (no draw)
            test_image1 = blur
            img_final1 = np.ones((400, 400), np.uint8) * 148
            h1, w1 = test_image1.shape
            img_final1[(400 - h1) // 2:(400 - h1) // 2 + h1,
                       (400 - w1) // 2:(400 - w1) // 2 + w1] = test_image1

            # Prepare binary image
            img_final = np.ones((400, 400), np.uint8) * 255
            h2, w2 = test_image.shape
            img_final[(400 - h2) // 2:(400 - h2) // 2 + h2,
                      (400 - w2) // 2:(400 - w2) // 2 + w2] = test_image

        hands, frame = hd.findHands(frame, draw=False, flipType=True)

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            y1 = max(0, y - offset)
            y2 = min(frame.shape[0], y + h + offset)
            x1 = max(0, x - offset)
            x2 = min(frame.shape[1], x + w + offset)

            image = frame[y1:y2, x1:x2]
            white = cv2.imread(
                "C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\white.jpg"
            )

            handz, imz = hd2.findHands(image, draw=False, flipType=True)

            if handz:
                hand = handz[0]
                pts = hand['lmList']

                os_x = ((400 - w) // 2) - 15
                os_y = ((400 - h) // 2) - 15

                # Draw skeleton lines
                for t in range(0, 4):
                    cv2.line(white, (pts[t][0] + os_x, pts[t][1] + os_y),
                             (pts[t + 1][0] + os_x, pts[t + 1][1] + os_y), (0, 255, 0), 3)
                for t in range(5, 8):
                    cv2.line(white, (pts[t][0] + os_x, pts[t][1] + os_y),
                             (pts[t + 1][0] + os_x, pts[t + 1][1] + os_y), (0, 255, 0), 3)
                for t in range(9, 12):
                    cv2.line(white, (pts[t][0] + os_x, pts[t][1] + os_y),
                             (pts[t + 1][0] + os_x, pts[t + 1][1] + os_y), (0, 255, 0), 3)
                for t in range(13, 16):
                    cv2.line(white, (pts[t][0] + os_x, pts[t][1] + os_y),
                             (pts[t + 1][0] + os_x, pts[t + 1][1] + os_y), (0, 255, 0), 3)
                for t in range(17, 20):
                    cv2.line(white, (pts[t][0] + os_x, pts[t][1] + os_y),
                             (pts[t + 1][0] + os_x, pts[t + 1][1] + os_y), (0, 255, 0), 3)

                # Connect base joints
                cv2.line(white, (pts[5][0] + os_x, pts[5][1] + os_y), (pts[9][0] + os_x, pts[9][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[9][0] + os_x, pts[9][1] + os_y), (pts[13][0] + os_x, pts[13][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[13][0] + os_x, pts[13][1] + os_y), (pts[17][0] + os_x, pts[17][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[0][0] + os_x, pts[0][1] + os_y), (pts[5][0] + os_x, pts[5][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[0][0] + os_x, pts[0][1] + os_y), (pts[17][0] + os_x, pts[17][1] + os_y), (0, 255, 0), 3)

                # Draw landmarks
                for i in range(21):
                    cv2.circle(white, (pts[i][0] + os_x, pts[i][1] + os_y), 2, (0, 0, 255), 1)

                cv2.imshow("Skeleton", white)

            # Grayscale image with drawings
            roi1 = frame[y1:y2, x1:x2]
            gray1 = cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY)
            blur1 = cv2.GaussianBlur(gray1, (1, 1), 2)
            test_image2 = blur1
            img_final2 = np.ones((400, 400), np.uint8) * 148
            h3, w3 = test_image2.shape
            img_final2[(400 - h3) // 2:(400 - h3) // 2 + h3,
                       (400 - w3) // 2:(400 - w3) // 2 + w3] = test_image2

            cv2.imshow("Binary", img_final)

        # Show main frame
        cv2.imshow("Frame", frame)

        # Keyboard actions
        interrupt = cv2.waitKey(1)
        if interrupt & 0xFF == 27:  # ESC
            break

        if interrupt & 0xFF == ord('n'):
            p_dir = chr(ord(p_dir) + 1)
            c_dir = chr(ord(c_dir) + 1)
            if ord(p_dir) == ord('Z') + 1:
                p_dir, c_dir = "A", "a"
            flag = False
            count = len(os.listdir(
                f"C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\test_data_2.0\\Gray_imgs\\{p_dir}\\"
            ))

        if interrupt & 0xFF == ord('a'):
            flag = not flag
            suv = 0 if flag else suv

        print("Flag =", flag)

        if flag:
            if suv == 50:
                flag = False
            if step % 2 == 0:
                # Save gray and gray-with-drawing
                gray_path = f"C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\test_data_2.0\\Gray_imgs\\{p_dir}\\{c_dir}{count}.jpg"
                gray_draw_path = f"C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\test_data_2.0\\Gray_imgs_with_drawing\\{p_dir}\\{c_dir}{count}.jpg"
                cv2.imwrite(gray_path, img_final1)
                cv2.imwrite(gray_draw_path, img_final2)
                print(f" Saved: {gray_path}")
                count += 1
                suv += 1
            step += 1

    except Exception:
        print("==", traceback.format_exc())

capture.release()
cv2.destroyAllWindows()
