wh := ComObjCreate("WinHTTP.WinHTTPRequest.5.1") 

ttt := 0
loop, 40 {
    a := A_TickCount
    wh.open("GET", "http://127.0.0.1:8000/detect")
    wh.SetRequestHeader("base64Image", "aaa")
    wh.send()
    ; msgbox, % wh.ResponseText() "`, 소요시간: " A_TickCount - a
    ttt := ttt + (A_TickCount - a )
}
msgbox, % ttt
exitapp
exit