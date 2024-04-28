import requests
import time
import os
import base64
import cv2
import numpy as np

def requestDetect() -> None:
    t = time.time()
    with open("Image.txt", "r") as f:
        data = {
            "base64Image": f.read(),
            "Tscore": "0.7"
        }

    a = requests.request("get", "http://127.0.0.1:8000/detect", json=data).text
    print(f"좌표: {a}, 소요시간: {time.time() - t}")

def setmodel() -> None:
    headers = {
        "model": "best.onnx"
    }
    a = requests.request("get", "http://127.0.0.1:8000/setmodel", headers=headers).text
    print(a)

def getProvider() -> None:
    a = requests.request("get", "http://127.0.0.1:8000/getProviders").text
    print(a)

def main() -> None:
    setmodel()
    # for v in range(10):
    requestDetect()
    # base64Image = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAJCAIAAACExCpEAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADDSURBVChTY2D4n49Ae4IYlnkw7AxgiNZgWOjGtNabgaHMhGGyA0OSNoMUN4MQB0ObFVyacTVQ+mkKw8VohncZDPuDGfyUQNJww1Z7MTDoiTAAQbgaw8MkhiXuIOkrMQyznBmOhjGAdDvKMDAzMqTpgAxY4IZsONMaoDTcKCDHTBxZmnmtDwOjrTRDhBqDkRgDGxMDJwtDgDJDngHIxjhNjjxDBu56S4bXaVgR8xwXBoUkfaZeW4ZuGxS00I3hVjzTGm8ALuJOICeIY4MAAAAASUVORK5CYII="
    # decodeImage = base64.b64decode(base64Image)
    # nparr = np.frombuffer(decodeImage, np.uint8)
    # image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # image = cv2.resize(image, (640, 640))
    # image_data = np.array(image) / 255.0
    # image_data = np.transpose(image_data, (2, 0, 1))
    # image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
    # cv2.imshow("a", image_data)
    # cv2.waitKey(0)

if (__name__ == "__main__"):
    main()