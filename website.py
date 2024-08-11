from flask import Flask, render_template, request, jsonify
import pyautogui
import cv2
from flask_socketio import SocketIO
import base64
import threading
import time
import keyboard

app = Flask(__name__)
socketio = SocketIO(app)
cordinate_enabled = False
keypress = 0
camera = cv2.VideoCapture(4)  # Use 0 for default camera
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('video_frame', {'frame': frame})
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move_mouse', methods=['POST'])
def move_mouse():
    global data, cordinate_enabled
    if cordinate_enabled:
        data = request.json
        x = data['x']
        y = data['y']
        pyautogui.moveTo(x, y)
        pyautogui.click()
        return jsonify({"status": "success"})

@app.route('/type_text', methods=['POST'])
def type_text():
    global data, text, cordinate_enabled
    data = request.json
    text = data['text']
    if cordinate_enabled and not "enter" in text:
        pyautogui.write(text)
    elif cordinate_enabled and "enter" in text:
        print("Message received: " + text)
        text = text.replace("enter", "")
        pyautogui.write(text, interval=0.10)
        pyautogui.hotkey('enter')
    return jsonify({"status": "success"})

def on_f12_press(event):
        global keypress, cordinate_enabled
        keypress += 1
        if keypress == 1:
            cordinate_enabled = True
            print("Cordinates enabled")
        if keypress == 2:
            keypress = 0
            if cordinate_enabled:
                cordinate_enabled = False
                print("Cordinates disabled")

keyboard.on_press_key("f12", on_f12_press)
threading.Thread(target=keyboard.wait, daemon=True)

if __name__ == '__main__':
    threading.Thread(target=gen_frames, daemon=True).start()
    socketio.run(app, debug=True)