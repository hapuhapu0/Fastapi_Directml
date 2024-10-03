from typing import Annotated, Union
from fastapi import FastAPI, Header, Body
from pydantic import BaseModel

from tendo import singleton

import multiprocessing
import uvicorn
import onnxruntime as ort
import numpy as np
import cv2
import base64

import win32gui
import win32ui
import win32con

singleton.SingleInstance()

class DetectItem(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    Tscore: int | None = 0.8

class DetectImage:
    def __init__(self) -> None:
        self.trainModel = None
        self.Provider = None

        # Error message
        # Model not loaded
        self.error_ModelNotLoad = "Model not Loaded"

async def captureScreen(Pos: tuple, GrayScale: bool = True) -> np.ndarray:
    try:
        width = Pos[2] - Pos[0]
        height = Pos[3] - Pos[1]

        hdesktop = win32gui.GetDesktopWindow()
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        dcObj = win32ui.CreateDCFromHandle(desktop_dc)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()

        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (width, height), dcObj, (Pos[0], Pos[1]), win32con.SRCCOPY)

        bmpinfo = dataBitMap.GetInfo()
        bmpstr = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (height, width, 4)

        if (GrayScale == True):
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return img
    
    except Exception as e:
        return False
    
    finally:
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.DeleteObject(dataBitMap.GetHandle())

async def addPadding(Image: np.ndarray) -> np.ndarray:
    height, width = Image.shape[:2]

    margin = [np.abs(height - width) // 2, np.abs(height - width) // 2]

    if (np.abs(height - width) % 2 != 0):
        margin[0] += 1

    if (height < width):
        margin_list = [margin, [0, 0]]
    else:
        margin_list = [[0, 0], margin]

    if len(Image.shape) == 3:
        margin_list.append([0,0])

    output = np.pad(Image, margin_list, mode='constant')
    return output
    
async def preProcess(image: base64.b64encode) -> np.ndarray:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = await addPadding(image)
    image = cv2.resize(image, dsize=(640, 640))
    image_data = np.array(image) / 255.0
    image_data = np.transpose(image_data, (2, 0, 1))
    image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
    return image_data

async def postProcess(result: list, Tscore: float, shape: list) -> np.ndarray:
    obj = result[0][0]
    x1, y1, x2, y2, scores = obj
    
    if len(scores) > 0:
        max_score = np.max(scores)
    else:
        max_score = 0
    
    if max_score > Tscore:
        detected_objects = []
        
        scale_x = shape[1] / 640
        scale_y = shape[0] / 640
        
        for i in range(len(scores)):
            if scores[i] > Tscore:
                scaled_x = round(x1[i] * scale_x)
                scaled_y = round(y1[i] * scale_y)
                
                detected_objects.append([scaled_x, scaled_y])
        
        return detected_objects
    
    return []

app = FastAPI()
Detect = DetectImage()

@app.post("/detect")
async def detectImage(
    capturePos: Annotated[list | None, Header()],
    Tscore: Annotated[str | None, Header()] = 0.8
):
    try:
        capturePos = eval(capturePos[0])
        if (Detect.trainModel == None):
            return Detect.error_ModelNotLoad
        else:
            Tscore = float(Tscore)
            ScreenImage = await captureScreen(capturePos, False)
            w, h, _ = ScreenImage.shape

            ScreenImage = await preProcess(ScreenImage)

            output = Detect.trainModel.run(None, {"images": ScreenImage})
            result = await postProcess(output, Tscore, [w, h])
            
            return result
    except Exception as e:
        print(f"Unknown Error error: {e}")
        return f"Unknown Error error: {e}"

@app.get("/setmodel")
async def setmodel(model: Annotated[str | None, Header()], Provider: Annotated[str | None, Header()] = None):
    try:
        if (Provider == None):
            Detect.trainModel = ort.InferenceSession(model, providers=ort.get_available_providers())
        else:
            Detect.trainModel = ort.InferenceSession(model, providers=Provider)
        return True
    
    except Exception as e:
        return e

@app.get("/getProviders")
async def getProviders():
    try:
        return ort.get_available_providers()
    
    except Exception as e:
        return e

def main() -> None:
    multiprocessing.freeze_support()
    uvicorn.run(app)

if (__name__ == "__main__"):
    main()