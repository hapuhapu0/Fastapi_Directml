from typing import Annotated
import multiprocessing
import uvicorn

from fastapi import FastAPI, Header

import onnxruntime as ort
import numpy as np

class DetectImage:
    def __init__(self) -> None:
        self.trainModel = None
        self.Provider = None

        # Error Message
        # Model not loaded
        self.Error_modelNotLoad = "Model not Loaded"

    def preprocess():
        pass

    def proprocess():
        pass

app = FastAPI()
Detect = DetectImage()

@app.get("/detect")
async def detectImage(base64Image: Annotated[str | None, Header()] = None):
    if (Detect.trainModel == None):
        return Detect.Error_modelNotLoad
    return base64Image

@app.get("/setmodel")
async def setmodel(model: Annotated[str | None, Header()] = None, Provider: Annotated[str | None, Header()] = None):
    Detect.trainModel = model
    Detect.Provider = Provider
    return model

@app.get("/getProviders")
async def getProviders():
    return ort.get_available_providers()

def main() -> None:
    multiprocessing.freeze_support()
    uvicorn.run(app)

if (__name__ == "__main__"):
    main()