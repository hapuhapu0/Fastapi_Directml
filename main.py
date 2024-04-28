from typing import Annotated
import multiprocessing
import uvicorn
from fastapi import FastAPI, Header, Body
from pydantic import BaseModel

import onnxruntime as ort
import numpy as np
import cv2
import base64

class DetectItem(BaseModel):
    base64Image: str
    Tscore: str | None = 0.8

class DetectImage:
    def __init__(self) -> None:
        self.trainModel = None
        self.Provider = None

        # Error message
        # Model not loaded
        self.Error_modelNotLoad = "Model not Loaded"

app = FastAPI()
Detect = DetectImage()

def preprocess(img: base64.b64encode) -> np.ndarray:
    # load image
    decodeImage = base64.b64decode(img)
    nparr = np.frombuffer(decodeImage, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    image = cv2.resize(image, dsize=(640, 640))
    image_data = np.array(image) / 255.0
    image_data = np.transpose(image_data, (2, 0, 1))
    image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
    return image_data
    

@app.get("/detect")
async def detectImage(item: DetectItem):
    try:
        base64Image = item.base64Image
        Tscore = item.Tscore
        print(Tscore)
        if (Detect.trainModel == None):
            return Detect.Error_modelNotLoad
        else:
            Tscore = float(Tscore)
            imageData = preprocess(base64Image)

            output = Detect.trainModel.run(None, {"images": imageData})
            obj = output[0][0]

            x1, y1, x2, y2, scores = obj
            if len(scores) > 0:
                max_score = np.max(scores)
            else:
                max_score = 0
            if max_score > Tscore:
                detected_objects = []
                for i in range(len(scores)):
                    if scores[i] > Tscore:
                        detected_objects.append([round(x1[i]), round(y1[i])])
                return detected_objects
    except Exception as e:
        return e

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