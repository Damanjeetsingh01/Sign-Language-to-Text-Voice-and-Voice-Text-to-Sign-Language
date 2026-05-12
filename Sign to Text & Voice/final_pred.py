
import numpy as np
import math
import cv2
import os
import traceback
import pyttsx3
import threading
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk

try:
    import enchant
    ddd = enchant.Dict("en_US")
    ENCHANT_AVAILABLE = True
except Exception:
    ENCHANT_AVAILABLE = False
    print("[WARN] pyenchant not found — word suggestions disabled.")
BG        = "#0f172a"
PANEL     = "#1e293b"
CARD      = "#263348"
ACCENT    = "#38bdf8"
ACCENT2   = "#22d3ee"
GREEN     = "#22c55e"
RED       = "#ef4444"
YELLOW    = "#facc15"
MUTED     = "#94a3b8"
WHITE     = "#f1f5f9"
BORDER    = "#334155"


class SignLanguageApp:

    def __init__(self):

        self.model = load_model("cnn8grps_rad1_model.h5")
        self.hd    = HandDetector(maxHands=1)
        self.hd2   = HandDetector(maxHands=1)

        self.cap    = cv2.VideoCapture(0)
        self.offset = 29

        self.speaker = pyttsx3.init()
        self.speaker.setProperty("rate", 120)
        voices = self.speaker.getProperty("voices")
        self.speaker.setProperty("voice", voices[0].id)


        self.pts          = [(0, 0)] * 21   # hand landmarks
        self.prev_char    = ""
        self.count        = -1
        self.ten_prev     = [" "] * 10
        self.sentence     = " "
        self.word         = " "
        self.current_sym  = ""
        self.suggestions  = ["", "", "", ""]


        self._build_window()
        self.root.after(10, self.video_loop)
        self.root.mainloop()

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("🤟  Sign Language → Text Converter")
        self.root.geometry("1550x900")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.destructor)


        title_bar = tk.Frame(self.root, bg=PANEL, pady=12)
        title_bar.pack(fill="x")

        tk.Label(
            title_bar,
            text="🤟  Sign Language → Text Converter",
            font=("Segoe UI", 22, "bold"),
            bg=PANEL, fg=ACCENT
        ).pack(side="left", padx=24)

        tk.Label(
            title_bar,
            text="SIGN LANGUAGE TO TEXT AND VOICE CONVERTER || DELTA 4",
            font=("Segoe UI", 11),
            bg=PANEL, fg=MUTED
        ).pack(side="right", padx=24)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=12)

        self._build_left(main)
        self._build_right(main)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=PANEL, bd=0, relief="flat",
                        highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(left, text="📷  Live Camera",
                 font=("Segoe UI", 14, "bold"),
                 bg=PANEL, fg=WHITE).pack(pady=(12, 4))


        self.cam_panel = tk.Label(left, bg="black",
                                  highlightbackground=ACCENT,
                                  highlightthickness=2)
        self.cam_panel.pack(padx=12, pady=6)


        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=12, pady=6)

        tk.Label(left, text="✋  Hand Skeleton",
                 font=("Segoe UI", 14, "bold"),
                 bg=PANEL, fg=WHITE).pack(pady=(4, 4))

        self.hand_panel = tk.Label(left, bg="#111827",
                                   highlightbackground=ACCENT2,
                                   highlightthickness=2)
        self.hand_panel.pack(padx=12, pady=6)

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        # row 1 — letter + word cards side by side
        row1 = tk.Frame(right, bg=BG)
        row1.pack(fill="x", pady=(0, 10))

        self._letter_card(row1)
        self._word_card(row1)

        # row 2 — sentence (full width)
        self._sentence_card(right)

        # row 3 — suggestions
        self._suggestion_row(right)

        # row 4 — action buttons
        self._button_row(right)

        # row 5 — status bar
        self.status_var = tk.StringVar(value="Ready — show your hand to the camera")
        status = tk.Label(right, textvariable=self.status_var,
                          font=("Segoe UI", 10), bg=BG, fg=MUTED, anchor="w")
        status.pack(fill="x", padx=4, pady=(8, 0))

    def _letter_card(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", expand=True, fill="both", padx=(0, 8))

        tk.Label(card, text="CURRENT LETTER",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", padx=18, pady=(14, 0))

        self.letter_var = tk.StringVar(value="—")
        tk.Label(card, textvariable=self.letter_var,
                 font=("Segoe UI", 80, "bold"),
                 bg=CARD, fg=ACCENT).pack(padx=18, pady=(4, 18))

    def _word_card(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="right", expand=True, fill="both")

        tk.Label(card, text="CURRENT WORD",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", padx=18, pady=(14, 0))

        self.word_var = tk.StringVar(value="—")
        tk.Label(card, textvariable=self.word_var,
                 font=("Segoe UI", 36, "bold"),
                 bg=CARD, fg=GREEN,
                 wraplength=350, justify="left").pack(
                     anchor="w", padx=18, pady=(4, 18))

    def _sentence_card(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="SENTENCE",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", padx=18, pady=(12, 0))

        self.sentence_var = tk.StringVar(value="")
        tk.Label(card, textvariable=self.sentence_var,
                 font=("Segoe UI", 22),
                 bg=CARD, fg=WHITE,
                 wraplength=900, justify="left",
                 anchor="w").pack(fill="x", padx=18, pady=(4, 16))

    def _suggestion_row(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="SUGGESTIONS  →",
                 font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=MUTED).pack(side="left", padx=(4, 12))

        self.sug_btns = []
        for i in range(4):
            btn = tk.Button(
                frame,
                text="",
                font=("Segoe UI", 13, "bold"),
                bg=PANEL, fg=ACCENT2,
                activebackground=ACCENT,
                activeforeground=WHITE,
                bd=0, relief="flat",
                padx=18, pady=8,
                cursor="hand2",
                command=lambda idx=i: self._apply_suggestion(idx)
            )
            btn.pack(side="left", padx=6)
            self.sug_btns.append(btn)

    def _button_row(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", pady=4)

        btns = [
            ("🔊  Speak",    GREEN,  self.speak_text),
            ("🗑  Clear",    RED,    self.clear_text),
            ("⌫  Backspace", YELLOW, self.backspace_text),
        ]
        for txt, colour, cmd in btns:
            tk.Button(
                frame,
                text=txt,
                font=("Segoe UI", 14, "bold"),
                bg=colour, fg=WHITE if colour != YELLOW else "#0f172a",
                activebackground=colour,
                activeforeground=WHITE,
                bd=0, relief="flat",
                padx=28, pady=12,
                cursor="hand2",
                command=cmd
            ).pack(side="left", padx=8)

    def video_loop(self):
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.root.after(10, self.video_loop)
                return

            frame = cv2.flip(frame, 1)
            hands = self.hd.findHands(frame, draw=False, flipType=True)

            white = np.ones((400, 400, 3), np.uint8) * 255
            hand_found = False

            if hands and hands[0]:
                hand   = hands[0][0]
                x, y, w, h = hand["bbox"]

                x1 = max(0, x - self.offset)
                y1 = max(0, y - self.offset)
                x2 = min(frame.shape[1], x + w + self.offset)
                y2 = min(frame.shape[0], y + h + self.offset)
                crop = frame[y1:y2, x1:x2]

                if crop.size > 0:
                    handz = self.hd2.findHands(crop, draw=False, flipType=True)
                    if handz and handz[0]:
                        hmap = handz[0][0]
                        self.pts = hmap["lmList"]

                        os_x = ((400 - w) // 2) - 15
                        os_y = ((400 - h) // 2) - 15

                        self._draw_skeleton(white, os_x, os_y)
                        self._run_prediction(white)
                        self._update_suggestions()
                        hand_found = True
                        self.status_var.set(f"Hand detected  |  Letter: {self.current_sym}")

            if not hand_found:
                self.status_var.set("No hand detected — show your hand to the camera")

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb).resize((560, 420))
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_panel.imgtk = imgtk
            self.cam_panel.config(image=imgtk)

            hand_img = Image.fromarray(white).resize((280, 280))
            hand_imgtk = ImageTk.PhotoImage(image=hand_img)
            self.hand_panel.imgtk = hand_imgtk
            self.hand_panel.config(image=hand_imgtk)

        except Exception:
            print(traceback.format_exc())

        self.root.after(10, self.video_loop)

    def _draw_skeleton(self, white, os_x, os_y):
        pts = self.pts

        def p(i):
            return (pts[i][0] + os_x, pts[i][1] + os_y)

        connections = (
            list(range(0, 4)),   # thumb
            list(range(5, 8)),   # index
            list(range(9, 12)),  # middle
            list(range(13, 16)), # ring
            list(range(17, 20)), # pinky
        )
        extras = [(5, 9), (9, 13), (13, 17), (0, 5), (0, 17)]

        for seg in connections:
            for t in range(len(seg) - 1):
                cv2.line(white, p(seg[t]), p(seg[t + 1]), (0, 200, 50), 3)
        for a, b in extras:
            cv2.line(white, p(a), p(b), (0, 200, 50), 3)
        for i in range(21):
            cv2.circle(white, p(i), 5, (0, 0, 255), -1)

    def _run_prediction(self, img):
        img_input = img.reshape(1, 400, 400, 3)
        prob = np.array(self.model.predict(img_input, verbose=0)[0], dtype="float32")
        ch1 = int(np.argmax(prob)); prob[ch1] = 0
        ch2 = int(np.argmax(prob)); prob[ch2] = 0

        pts = self.pts
        pl  = [ch1, ch2]

        def dist(a, b):
            return math.sqrt((pts[a][0]-pts[b][0])**2 + (pts[a][1]-pts[b][1])**2)

        # ── all disambiguation rules from original ──
        if pl in [[5,2],[5,3],[3,5],[3,6],[3,0],[3,2],[6,4],[6,1],[6,2],
                   [6,6],[6,7],[6,0],[6,5],[4,1],[1,0],[1,1],[6,3],[1,6],
                   [5,6],[5,1],[4,5],[1,4],[1,5],[2,0],[2,6],[4,6],[1,0],
                   [5,7],[1,6],[6,1],[7,6],[2,5],[7,1],[5,4],[7,0],[7,5],[7,2]]:
            if (pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]):
                ch1 = 0

        if [ch1,ch2] in [[2,2],[2,1]]:
            if pts[5][0] < pts[4][0]: ch1 = 0

        pl = [ch1, ch2]
        if pl in [[0,0],[0,6],[0,2],[0,5],[0,1],[0,7],[5,2],[7,6],[7,1]]:
            if (pts[0][0]>pts[8][0] and pts[0][0]>pts[4][0] and
                    pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and
                    pts[0][0]>pts[20][0] and pts[5][0]>pts[4][0]):
                ch1 = 2

        pl = [ch1, ch2]
        if pl in [[6,0],[6,6],[6,2]]:
            if dist(8,16) < 52: ch1 = 2

        pl = [ch1, ch2]
        if pl in [[1,4],[1,5],[1,6],[1,3],[1,0]]:
            if (pts[6][1]>pts[8][1] and pts[14][1]<pts[16][1] and
                    pts[18][1]<pts[20][1] and pts[0][0]<pts[8][0] and
                    pts[0][0]<pts[12][0] and pts[0][0]<pts[16][0] and
                    pts[0][0]<pts[20][0]):
                ch1 = 3

        pl = [ch1, ch2]
        if pl in [[4,6],[4,1],[4,5],[4,3],[4,7]]:
            if pts[4][0] > pts[0][0]: ch1 = 3

        pl = [ch1, ch2]
        if pl in [[5,3],[5,0],[5,7],[5,4],[5,2],[5,1],[5,5]]:
            if pts[2][1]+15 < pts[16][1]: ch1 = 3

        pl = [ch1, ch2]
        if pl in [[6,4],[6,1],[6,2]]:
            if dist(4,11) > 55: ch1 = 4

        pl = [ch1, ch2]
        if pl in [[1,4],[1,6],[1,1]]:
            if (dist(4,11)>50 and pts[6][1]>pts[8][1] and
                    pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and
                    pts[18][1]<pts[20][1]):
                ch1 = 4

        pl = [ch1, ch2]
        if pl in [[3,6],[3,4]]:
            if pts[4][0] < pts[0][0]: ch1 = 4

        pl = [ch1, ch2]
        if pl in [[2,2],[2,5],[2,4]]:
            if pts[1][0] < pts[12][0]: ch1 = 4

        pl = [ch1, ch2]
        if pl in [[3,6],[3,5],[3,4]]:
            if (pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and
                    pts[4][1]>pts[10][1]):
                ch1 = 5

        pl = [ch1, ch2]
        if pl in [[3,2],[3,1],[3,6]]:
            if (pts[4][1]+17>pts[8][1] and pts[4][1]+17>pts[12][1] and
                    pts[4][1]+17>pts[16][1] and pts[4][1]+17>pts[20][1]):
                ch1 = 5

        pl = [ch1, ch2]
        if pl in [[4,4],[4,5],[4,2],[7,5],[7,6],[7,0]]:
            if pts[4][0] > pts[0][0]: ch1 = 5

        pl = [ch1, ch2]
        if pl in [[0,2],[0,6],[0,1],[0,5],[0,0],[0,7],[0,4],[0,3],[2,7]]:
            if (pts[0][0]<pts[8][0] and pts[0][0]<pts[12][0] and
                    pts[0][0]<pts[16][0] and pts[0][0]<pts[20][0]):
                ch1 = 5

        pl = [ch1, ch2]
        if pl in [[5,7],[5,2],[5,6]]:
            if pts[3][0] < pts[0][0]: ch1 = 7

        pl = [ch1, ch2]
        if pl in [[4,6],[4,2],[4,4],[4,1],[4,5],[4,7]]:
            if pts[6][1] < pts[8][1]: ch1 = 7

        pl = [ch1, ch2]
        if pl in [[6,7],[0,7],[0,1],[0,0],[6,4],[6,6],[6,5],[6,1]]:
            if pts[18][1] > pts[20][1]: ch1 = 7

        pl = [ch1, ch2]
        if pl in [[0,4],[0,2],[0,3],[0,1],[0,6]]:
            if pts[5][0] > pts[16][0]: ch1 = 6

        pl = [ch1, ch2]
        if pl == [7,2]:
            if pts[18][1]<pts[20][1] and pts[8][1]<pts[10][1]: ch1 = 6

        pl = [ch1, ch2]
        if pl in [[2,1],[2,2],[2,6],[2,7],[2,0]]:
            if dist(8,16) > 50: ch1 = 6

        pl = [ch1, ch2]
        if pl in [[4,6],[4,2],[4,1],[4,4]]:
            if dist(4,11) < 60: ch1 = 6

        pl = [ch1, ch2]
        if pl in [[1,4],[1,6],[1,0],[1,2]]:
            if pts[5][0]-pts[4][0]-15 > 0: ch1 = 6


        pl = [ch1, ch2]
        for cond_list in [
            [[5,0],[5,1],[5,4],[5,5],[5,6],[6,1],[7,6],[0,2],[7,1],[7,4],[6,6],[7,2],[5,0],[6,3],[6,4],[7,5],[7,2]],
            [[6,1],[6,0],[0,3],[6,4],[2,2],[0,6],[6,2],[7,6],[4,6],[4,1],[4,2],[0,2],[7,1],[7,4],[6,6],[7,2],[7,5],[7,2]],
        ]:
            if pl in cond_list:
                if (pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                        pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]):
                    ch1 = 1
                    break

        pl = [ch1, ch2]
        if pl in [[6,1],[6,0],[4,2],[4,1],[4,6],[4,4]]:
            if (pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and
                    pts[18][1]>pts[20][1]):
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[5,0],[3,4],[3,0],[3,1],[3,5],[5,5],[5,4],[5,1],[7,6]]:
            if (pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and
                    pts[2][0]<pts[0][0] and pts[4][1]>pts[14][1]):
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[4,1],[4,2],[4,4]]:
            if (dist(4,11)<50 and pts[6][1]>pts[8][1] and
                    pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and
                    pts[18][1]<pts[20][1]):
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[3,4],[3,0],[3,1],[3,5],[3,6]]:
            if (pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and
                    pts[2][0]<pts[0][0] and pts[14][1]<pts[4][1]):
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[6,6],[6,4],[6,1],[6,2]]:
            if pts[5][0]-pts[4][0]-15 < 0: ch1 = 1

        pl = [ch1, ch2]
        if pl in [[5,4],[5,5],[5,1],[0,3],[0,7],[5,0],[0,2],[6,2],[7,5],[7,1],[7,6],[7,7]]:
            if (pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]):
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[1,5],[1,7],[1,1],[1,6],[1,3],[1,0]]:
            if (pts[4][0]<pts[5][0]+15 and pts[6][1]<pts[8][1] and
                    pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and
                    pts[18][1]>pts[20][1]):
                ch1 = 7

        pl = [ch1, ch2]
        if pl in [[5,5],[5,0],[5,4],[5,1],[4,6],[4,1],[7,6],[3,0],[3,5]]:
            if (pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and
                    pts[4][1]>pts[14][1]):
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[3,5],[3,0],[3,6],[5,1],[4,1],[2,0],[5,0],[5,5]]:
            fg = 13
            if not (pts[0][0]+fg<pts[8][0] and pts[0][0]+fg<pts[12][0] and
                    pts[0][0]+fg<pts[16][0] and pts[0][0]+fg<pts[20][0]) and \
               not (pts[0][0]>pts[8][0] and pts[0][0]>pts[12][0] and
                    pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0]) and \
               dist(4,11) < 50:
                ch1 = 1

        pl = [ch1, ch2]
        if pl in [[5,0],[5,5],[0,1]]:
            if (pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]>pts[16][1]):
                ch1 = 1

        # ── map group codes → letters ──────────
        if ch1 == 0:
            ch1 = "S"
            if (pts[4][0]<pts[6][0] and pts[4][0]<pts[10][0] and
                    pts[4][0]<pts[14][0] and pts[4][0]<pts[18][0]):
                ch1 = "A"
            if (pts[4][0]>pts[6][0] and pts[4][0]<pts[10][0] and
                    pts[4][0]<pts[14][0] and pts[4][0]<pts[18][0] and
                    pts[4][1]<pts[14][1] and pts[4][1]<pts[18][1]):
                ch1 = "T"
            if (pts[4][1]>pts[8][1] and pts[4][1]>pts[12][1] and
                    pts[4][1]>pts[16][1] and pts[4][1]>pts[20][1]):
                ch1 = "E"
            if (pts[4][0]>pts[6][0] and pts[4][0]>pts[10][0] and
                    pts[4][0]>pts[14][0] and pts[4][1]<pts[18][1]):
                ch1 = "M"
            if (pts[4][0]>pts[6][0] and pts[4][0]>pts[10][0] and
                    pts[4][1]<pts[18][1] and pts[4][1]<pts[14][1]):
                ch1 = "N"

        if ch1 == 2:
            ch1 = "C" if dist(12,4) > 42 else "O"

        if ch1 == 3:
            ch1 = "G" if dist(8,12) > 72 else "H"

        if ch1 == 7:
            ch1 = "Y" if dist(8,4) > 42 else "J"

        if ch1 == 4: ch1 = "L"
        if ch1 == 6: ch1 = "X"

        if ch1 == 5:
            if (pts[4][0]>pts[12][0] and pts[4][0]>pts[16][0] and
                    pts[4][0]>pts[20][0]):
                ch1 = "Z" if pts[8][1] < pts[5][1] else "Q"
            else:
                ch1 = "P"

        if ch1 == 1:
            if (pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]):
                ch1 = "B"
            elif (pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]):
                ch1 = "D"
            elif (pts[6][1]<pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]):
                ch1 = "F"
            elif (pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]):
                ch1 = "I"
            elif (pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]>pts[16][1] and pts[18][1]<pts[20][1]):
                ch1 = "W"
            elif (pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and
                    pts[4][1]<pts[9][1]):
                ch1 = "K"
            elif ((dist(8,12)-dist(6,10)) < 8 and
                    pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]):
                ch1 = "U"
            elif ((dist(8,12)-dist(6,10)) >= 8 and
                    pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and
                    pts[4][1]>pts[9][1]):
                ch1 = "V"
            elif (pts[8][0]>pts[12][0] and
                    pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]):
                ch1 = "R"

        if ch1 in [1,"E","S","X","Y","B"]:
            if (pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and
                    pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]):
                ch1 = " "

        if ch1 in ["E","Y","B"]:
            if (pts[4][0]<pts[5][0] and pts[6][1]>pts[8][1] and
                    pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and
                    pts[18][1]>pts[20][1]):
                ch1 = "next"

        if (pts[0][0]>pts[8][0] and pts[0][0]>pts[12][0] and
                pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0] and
                pts[4][1]<pts[8][1] and pts[4][1]<pts[12][1] and
                pts[4][1]<pts[16][1] and pts[4][1]<pts[20][1] and
                pts[4][1]<pts[6][1] and pts[4][1]<pts[10][1] and
                pts[4][1]<pts[14][1] and pts[4][1]<pts[18][1]):
            ch1 = "Backspace"

        if ch1 == "next" and self.prev_char != "next":
            prev2 = self.ten_prev[(self.count - 2) % 10]
            prev0 = self.ten_prev[(self.count) % 10]
            if prev2 != "next":
                if prev2 == "Backspace":
                    self.sentence = self.sentence[:-1]
                elif prev2 != "Backspace":
                    self.sentence += prev2
            else:
                if prev0 != "Backspace":
                    self.sentence += prev0

        if ch1 == "  " and self.prev_char != "  ":
            self.sentence += "  "

        self.prev_char = ch1
        self.current_sym = ch1
        self.count += 1
        self.ten_prev[self.count % 10] = ch1

        if self.sentence.strip():
            sp = self.sentence.rfind(" ")
            self.word = self.sentence[sp+1:]

        display = ch1 if isinstance(ch1, str) else str(ch1)
        self.letter_var.set(display if display not in ("next","Backspace"," ") else
                            ("⎵" if display==" " else ("↵" if display=="next" else "⌫")))
        self.word_var.set(self.word.strip() or "—")
        self.sentence_var.set(self.sentence.strip())

    def _update_suggestions(self):
        if not ENCHANT_AVAILABLE or not self.word.strip():
            for btn in self.sug_btns:
                btn.config(text="", state="disabled")
            return

        try:
            sugs = ddd.suggest(self.word.strip())[:4]
            for i, btn in enumerate(self.sug_btns):
                if i < len(sugs):
                    btn.config(text=sugs[i], state="normal")
                    self.suggestions[i] = sugs[i]
                else:
                    btn.config(text="", state="disabled")
                    self.suggestions[i] = ""
        except Exception:
            pass

    def _apply_suggestion(self, idx):
        sug = self.suggestions[idx]
        if not sug:
            return
        sp = self.sentence.rfind(" ")
        self.sentence = self.sentence[:sp+1] + sug.upper() + " "
        self.word = ""
        self.sentence_var.set(self.sentence.strip())
        self.word_var.set("")


    def speak_text(self):
        text = self.sentence.strip() or str(self.current_sym)
        if not text:
            return

        def _speak():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 120)
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[0].id)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception:
                import traceback
                print(traceback.format_exc())

        t = threading.Thread(target=_speak, daemon=True)
        t.start()

    def clear_text(self):
        self.sentence = " "
        self.word     = " "
        self.current_sym = ""
        self.letter_var.set("—")
        self.word_var.set("—")
        self.sentence_var.set("")
        for btn in self.sug_btns:
            btn.config(text="", state="disabled")

    def backspace_text(self):
        self.sentence = self.sentence.rstrip()
        if self.sentence:
            self.sentence = self.sentence[:-1]
        self.sentence_var.set(self.sentence.strip())
        sp = self.sentence.rfind(" ")
        self.word = self.sentence[sp+1:]
        self.word_var.set(self.word.strip() or "—")

    def destructor(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()


if __name__ == "__main__":
    print("Starting Sign Language to Text Converter...")
    SignLanguageApp()