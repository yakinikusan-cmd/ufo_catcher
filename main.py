from servo import KondoServo
import keyboard
import speech_recognition as sr
from enum import Enum
from gui import Gui
import flet as ft
import time

class State(Enum):
    IDLE = 0
    RECOGNIZE = 1
    FAILED = 2
    PLAY = 3

X_AXIS_ID = 0
Y_AXIS_ID = 1
Z_AXIS_ID = 2
KEYWORD = "トリート"


state = State.IDLE
last_state = state

gui = None

r = sr.Recognizer()
mic = sr.Microphone()


Servo = KondoServo("COM16")

def space_callback(event):
    global state
    if event.event_type == "down" and (state == State.IDLE or state == State.FAILED):
        state = State.RECOGNIZE
        with mic as source:
            r.adjust_for_ambient_noise(source) #雑音対策
            audio = r.listen(source)

        print ("Now to recognize it...")

        try:
            text = r.recognize_google(audio,language="ja")
            print(text)
            if  KEYWORD in text :
                state = State.PLAY
            else:
                state = State.FAILED
                gui.set_content(gui.failed_content(text))

        # 以下は認識できなかったときに止まらないように。
        except sr.UnknownValueError:
            print("could not understand audio")
            state = State.IDLE

pressed_keys = set()

def on_key_event(event):
    global state
    print(f'イベントタイプ: {event.event_type}, キー名: {event.name}, スキャンコード: {event.scan_code}, 時間: {event.time}')


    if event.event_type == "down":
        if event.name in pressed_keys:
            return
        pressed_keys.add(event.name)
    elif event.event_type == "up":
        pressed_keys.discard(event.name)
    else:
        return


    if event.name == "space":
        space_callback(event)
    if event.name == "b":
        state = State.IDLE

    if state == State.PLAY:
        if event.event_type == "down":
            if event.name == "up":
                Servo.krs_setPos_CMD(X_AXIS_ID,11500)
            if event.name == "down":
                Servo.krs_setPos_CMD(X_AXIS_ID,4000)

            if event.name == "left":
                Servo.krs_setPos_CMD(Y_AXIS_ID,11500)
            if event.name == "right":
                Servo.krs_setPos_CMD(Y_AXIS_ID,4000)

            if event.name == "u":
                Servo.krs_setPos_CMD(Z_AXIS_ID,11500)
            if event.name == "n":
                Servo.krs_setPos_CMD(Z_AXIS_ID,4000)


        if event.event_type == "up":
            if event.name == "up":
                Servo.krs_setPos_CMD(X_AXIS_ID,7500)
            if event.name == "down":
                Servo.krs_setPos_CMD(X_AXIS_ID,7500)
            if event.name == "left":
                Servo.krs_setPos_CMD(Y_AXIS_ID,7500)
            if event.name == "right":
                Servo.krs_setPos_CMD(Y_AXIS_ID,7500)

            if event.name == "u":
                Servo.krs_setPos_CMD(Z_AXIS_ID,7500)
            if event.name == "n":
                Servo.krs_setPos_CMD(Z_AXIS_ID,7500)
       # time.sleep(0.1);



keyboard.hook(on_key_event)
# print("キーボードイベントの監視を開始しました。ESCキーで終了します。")


def main(page: ft.Page):
    global state,last_state,gui
    try: 
        gui = Gui(page)
        while(True):
            if not state == last_state:
                match(state):
                    case State.IDLE:
                        gui.set_content(gui.idle_content)
                    case State.RECOGNIZE:
                        gui.set_content(gui.recognize_content)
                    case State.PLAY:
                        gui.set_content(gui.play_content)
                last_state = state
                time.sleep(0.01)
                    

    except KeyboardInterrupt: 
        print("\nCtrl+Cにより終了します。")
    finally:
        keyboard.unhook_all()

if __name__ == '__main__':
    ft.app(target=main)
