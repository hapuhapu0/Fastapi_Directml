model := "best.onnx"
capturePos := "[0, 0, 1000, 1000]"
Tscore := 0.8

Find := new Detect()

F1::
if Find.setModel(model) {
    a := A_TickCount
    result := Find.requestDetect(capturePos, Tscore)
    msgbox, % "결과값: " result "`n 소요시간: " A_TickCount - a
}
Else
    msgbox, % 모델 로드 실패

Return
    

F5::
ExitApp
Exit

class Detect {
    __New(Path := "main.exe", SleepTime := 5000) {
        run, % Path,,Hide,PID
        sleep, % SleepTime
        this.wh := ComObjCreate("WinHTTP.WinHTTPRequest.5.1")
    }

    setModel(modelPath) {
        this.wh.open("GET", "http://127.0.0.1:8000/setmodel")
        this.wh.SetRequestHeader("model", modelPath)
        this.wh.send()
        return this.wh.ResponseText()
    }

    getProvider() {
        this.wh.open("GET", "http://127.0.0.1:8000/GETProviders")
        this.wh.send()
        return this.wh.ResponseText()
    }

    requestDetect(capturePos, Tscore) {
        this.wh.open("POST", "http://127.0.0.1:8000/detect")
        this.wh.SetRequestHeader("capturePos", capturePos)
        this.wh.SetRequestHeader("Tscore", Tscore)
        this.wh.send()
        return this.wh.ResponseText()
    }
}