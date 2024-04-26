import requests
import time

def requestDetect() -> None:
    t = time.time()
    headers = {
        "base64Image": "detecttest"
    }
    a = requests.request("get", "http://127.0.0.1:8000/detect", headers=headers).text
    print(f"{a}, {time.time() - t}")

def setmodel() -> None:
    headers = {
        "model": "modeltest"
    }
    a = requests.request("get", "http://127.0.0.1:8000/setmodel", headers=headers).text
    print(a)

def getProvider() -> None:
    a = requests.request("get", "http://127.0.0.1:8000/getProviders").text
    print(a)

def main() -> None:
    getProvider()

if (__name__ == "__main__"):
    main()