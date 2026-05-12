import math
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from keras.models import load_model
import traceback

# Load pre-trained model
model = load_model(
    'C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\cnn8grps_rad1_model.h5')

# Create and save a white image
white = np.ones((400, 400), np.uint8) * 255
cv2.imwrite("C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\white.jpg", white)

# Initialize webcam
capture = cv2.VideoCapture(0)

# Initialize Hand Detectors
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)

offset = 29
flag = False
dicttt = dict()
kok = []


# Helper functions
def distance(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))


def distance_3d(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2) + ((x[2] - y[2]) ** 2))


# ================= MAIN LOOP ==================
while True:
    try:
        success, frame = capture.read()
        if not success:
            print("Failed to read from webcam.")
            break

        frame = cv2.flip(frame, 1)


        hands, frame = hd.findHands(frame, draw=False, flipType=True)
        print(frame.shape)

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            # Prevent invalid slicing if bbox goes out of bounds
            y1 = max(0, y - offset)
            y2 = min(frame.shape[0], y + h + offset)
            x1 = max(0, x - offset)
            x2 = min(frame.shape[1], x + w + offset)
            image = frame[y1:y2, x1:x2]

            white = cv2.imread(
                "C:\\Users\\PC\\Desktop\\final_project\\Sign-Language-To-Text\\white.jpg")
            # ✅ FIXED: Unpack tuple returned by second detector
            handz, image = hd2.findHands(image, draw=False, flipType=True)

            if handz:
                hand = handz[0]
                pts = hand['lmList']

                # Draw hand skeleton
                os = ((400 - w) // 2) - 15
                os1 = ((400 - h) // 2) - 15

                # Draw finger connections
                for t in range(0, 4):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1),
                             (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                for t in range(5, 8):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1),
                             (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                for t in range(9, 12):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1),
                             (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                for t in range(13, 16):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1),
                             (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                for t in range(17, 20):
                    cv2.line(white, (pts[t][0] + os, pts[t][1] + os1),
                             (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)

                # Draw connecting lines
                cv2.line(white, (pts[5][0] + os, pts[5][1] + os1), (pts[9][0] + os, pts[9][1] + os1), (0, 255, 0), 3)
                cv2.line(white, (pts[9][0] + os, pts[9][1] + os1), (pts[13][0] + os, pts[13][1] + os1), (0, 255, 0), 3)
                cv2.line(white, (pts[13][0] + os, pts[13][1] + os1), (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0),
                         3)
                cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), (pts[5][0] + os, pts[5][1] + os1), (0, 255, 0), 3)
                cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0), 3)

                # Draw key points
                for i in range(21):
                    cv2.circle(white, (pts[i][0] + os, pts[i][1] + os1), 2, (0, 0, 255), 1)

                cv2.imshow("Skeleton", white)

                # Predict letter
                white_resized = white.reshape(1, 400, 400, 3)
                prob = np.array(model.predict(white_resized)[0], dtype='float32')

                ch1 = np.argmax(prob, axis=0)
                prob[ch1] = 0
                ch2 = np.argmax(prob, axis=0)
                prob[ch2] = 0
                ch3 = np.argmax(prob, axis=0)
                prob[ch3] = 0

                # (Your large condition logic continues here unchanged)
                # You can paste your full block of conditions here —
                # those are not modified, just keep them after this point.

                # Example debug output
                print("ch1=", ch1, " ch2=", ch2, " ch3=", ch3)

                frame = cv2.putText(frame, "Predicted " + str(ch1), (30, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow("Frame", frame)
        interrupt = cv2.waitKey(1)
        if interrupt & 0xFF == 27:
            # ESC key to exit
            break

    except Exception:
        print("==", traceback.format_exc())

# Cleanup
dicttt = {key: val for key, val in sorted(dicttt.items(), key=lambda ele: ele[1], reverse=True)}
print(dicttt)
print(set(kok))
capture.release()
cv2.destroyAllWindows()
1
