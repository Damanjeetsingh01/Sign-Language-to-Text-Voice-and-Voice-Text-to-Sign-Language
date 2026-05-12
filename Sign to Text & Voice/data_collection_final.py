import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import os as oss
import traceback

# Initialize webcam
capture = cv2.VideoCapture(0)

# Initialize Hand Detectors
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)

# Set up directories and counters
count = len(oss.listdir(
    "C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\AtoZ_3.1\\A\\"))
c_dir = 'A'

offset = 15
step = 1
flag = False
suv = 0

# Create and save a blank white image
white = np.ones((400, 400), np.uint8) * 255
cv2.imwrite("C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\white.jpg", white)

while True:
    try:
        success, frame = capture.read()
        if not success:
            print("Failed to read from webcam.")
            break

        frame = cv2.flip(frame, 1)


        hands, frame = hd.findHands(frame, draw=False, flipType=True)

        white = cv2.imread(
            "C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\white.jpg")

        if hands:
            hand = hands[0]  # this is a dict now
            x, y, w, h = hand['bbox']

            # prevent out-of-bounds cropping
            y1 = max(0, y - offset)
            y2 = min(frame.shape[0], y + h + offset)
            x1 = max(0, x - offset)
            x2 = min(frame.shape[1], x + w + offset)

            image = np.array(frame[y1:y2, x1:x2])


            handz, imz = hd2.findHands(image, draw=True, flipType=True)

            if handz:
                hand = handz[0]
                pts = hand['lmList']

                os_x = ((400 - w) // 2) - 15
                os_y = ((400 - h) // 2) - 15

                # Draw the hand skeleton lines
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

                # Connecting lines between fingers
                cv2.line(white, (pts[5][0] + os_x, pts[5][1] + os_y), (pts[9][0] + os_x, pts[9][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[9][0] + os_x, pts[9][1] + os_y), (pts[13][0] + os_x, pts[13][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[13][0] + os_x, pts[13][1] + os_y), (pts[17][0] + os_x, pts[17][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[0][0] + os_x, pts[0][1] + os_y), (pts[5][0] + os_x, pts[5][1] + os_y), (0, 255, 0), 3)
                cv2.line(white, (pts[0][0] + os_x, pts[0][1] + os_y), (pts[17][0] + os_x, pts[17][1] + os_y), (0, 255, 0), 3)

                # Draw landmark points
                for i in range(21):
                    cv2.circle(white, (pts[i][0] + os_x, pts[i][1] + os_y), 2, (0, 0, 255), 1)

                skeleton1 = np.array(white)
                cv2.imshow("Skeleton", skeleton1)

        # Display info text on frame
        frame = cv2.putText(frame, f"dir={c_dir}  count={count}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.imshow("Frame", frame)

        # Keyboard controls
        interrupt = cv2.waitKey(1)
        if interrupt & 0xFF == 27:  # ESC key
            break

        # Change letter
        if interrupt & 0xFF == ord('n'):
            c_dir = chr(ord(c_dir) + 1)
            if ord(c_dir) == ord('Z') + 1:
                c_dir = 'A'
            flag = False
            count = len(oss.listdir(
                f"C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\AtoZ_3.1\\{c_dir}\\"))

        # Toggle auto-save
        if interrupt & 0xFF == ord('a'):
            flag = not flag
            suv = 0 if flag else suv

        print("Flag:", flag)
        if flag:
            if suv == 180:
                flag = False
            if step % 3 == 0:
                save_path = (f"C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\AtoZ_3.1\\{c_dir}\\{count}.jpg")
                cv2.imwrite(save_path, skeleton1)
                print(f"Saved: {save_path}")
                count += 1
                suv += 1
            step += 1

    except Exception:
        print("==", traceback.format_exc())

capture.release()
cv2.destroyAllWindows()
