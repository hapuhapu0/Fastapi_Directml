#include CreateFormData.ahk

FileRead, Read, Image.txt
JsonData := ({"base64Image": Read, "Tscore": "0.8"})
CreateFormData(PostData, ContentType, oForm)

wh := ComObjCreate("WinHTTP.WinHTTPRequest.5.1")
wh.open("post", "http://127.0.0.1:8000/detect")
wh.SetRequestHeader("Content-Type", "application/json")
wh.send(PostData)
msgbox, % wh.ResponseText()

; FileRead, Read, Image.txt

; oForm := { id: myid1
;           , index: 0
;           , file: ["ClipboardImage.png"] }
; CreateFormData(PostData, ContentType, oForm)

; Find := new Detect()
; if Find.setModel("best.onnx")
;     Find.requestDetect(Read, 0.7)
; Else
;     msgbox, % 모델 로드 실패
exitapp
exit

class Detect {
    __New() {
        this.wh := ComObjCreate("WinHTTP.WinHTTPRequest.5.1")
    }

    setModel(modelPath) {
        this.wh.open("get", "http://127.0.0.1:8000/setmodel")
        this.wh.SetRequestHeader("model", modelPath)
        this.wh.send()
        return this.wh.ResponseText()
    }

    getProvider() {
        this.wh.open("get", "http://127.0.0.1:8000/getProviders")
        this.wh.send()
        return this.wh.ResponseText()
    }

    requestDetect(base64Image, Score) {
        this.wh.open("get", "http://127.0.0.1:8000/detect")
        this.wh.SetRequestHeader("base64Image", base64Image)
        this.wh.SetRequestHeader("Tscore", Score)
        this.wh.send()
        return this.wh.ResponseText()
    }
}