CreateFormData(ByRef retData, ByRef retHeader, objParam) {
   New CreateFormData(retData, retHeader, objParam)
}

Class CreateFormData {
   __New(ByRef retData, ByRef retHeader, objParam) {
      Local CRLF := "`r`n", i, k, v, str, pvData
      ; Create a random Boundary
      Local Boundary := this.RandomBoundary()
      Local BoundaryLine := "------------------------------" . Boundary
    this.Len := 0 ; GMEM_ZEROINIT|GMEM_FIXED = 0x40
    this.Ptr := DllCall( "GlobalAlloc", "UInt",0x40, "UInt",1, "Ptr"  )          ; allocate global memory
      ; Loop input paramters
      For k, v in objParam
      {
         If IsObject(v) {
            For i, FileName in v
            {
               str := BoundaryLine . CRLF
                    . "Content-Disposition: form-data; name=""" . k . """; filename=""" . FileName . """" . CRLF
                    . "Content-Type: " . this.MimeType(FileName) . CRLF . CRLF
          this.StrPutUTF8( str )
          this.LoadFromFile( Filename )
          this.StrPutUTF8( CRLF )
            }
         } Else {
            str := BoundaryLine . CRLF
                 . "Content-Disposition: form-data; name=""" . k """" . CRLF . CRLF
                 . v . CRLF
        this.StrPutUTF8( str )
         }
      }
      this.StrPutUTF8( BoundaryLine . "--" . CRLF )
    ; Create a bytearray and copy data in to it.
    retData := ComObjArray( 0x11, this.Len ) ; Create SAFEARRAY = VT_ARRAY|VT_UI1
    pvData  := NumGet( ComObjValue( retData ) + 8 + A_PtrSize )
    DllCall( "RtlMoveMemory", "Ptr",pvData, "Ptr",this.Ptr, "Ptr",this.Len )
    this.Ptr := DllCall( "GlobalFree", "Ptr",this.Ptr, "Ptr" )                   ; free global memory 
    retHeader := "multipart/form-data; boundary=----------------------------" . Boundary
   }
  StrPutUTF8( str ) {
    Local ReqSz := StrPut( str, "utf-8" ) - 1
    this.Len += ReqSz                                  ; GMEM_ZEROINIT|GMEM_MOVEABLE = 0x42
    this.Ptr := DllCall( "GlobalReAlloc", "Ptr",this.Ptr, "UInt",this.len + 1, "UInt", 0x42 )   
    StrPut( str, this.Ptr + this.len - ReqSz, ReqSz, "utf-8" )
  }
  LoadFromFile( Filename ) {
    Local objFile := FileOpen( FileName, "r" )
    this.Len += objFile.Length                     ; GMEM_ZEROINIT|GMEM_MOVEABLE = 0x42 
    this.Ptr := DllCall( "GlobalReAlloc", "Ptr",this.Ptr, "UInt",this.len, "UInt", 0x42 )
    objFile.RawRead( this.Ptr + this.Len - objFile.length, objFile.length )
    objFile.Close()       
  }
   RandomBoundary() {
      str := "0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z"
      Sort, str, D| Random
      str := StrReplace(str, "|")
      Return SubStr(str, 1, 12)
   }
   MimeType(FileName) {
      n := FileOpen(FileName, "r").ReadUInt()
      Return (n        = 0x474E5089) ? "image/png"
           : (n        = 0x38464947) ? "image/gif"
           : (n&0xFFFF = 0x4D42    ) ? "image/bmp"
           : (n&0xFFFF = 0xD8FF    ) ? "image/jpeg"
           : (n&0xFFFF = 0x4949    ) ? "image/tiff"
           : (n&0xFFFF = 0x4D4D    ) ? "image/tiff"
           : "application/octet-stream"
   }
}
GetBitmapFromClipboard() {
    if !DllCall("IsClipboardFormatAvailable", "UInt", CF_BITMAP := 2)
       return false
    if !DllCall("OpenClipboard", "Ptr", 0)
       throw "OpenClipboard failed"
    hBitmap := DllCall("GetClipboardData", "UInt", CF_BITMAP)
    DllCall("CloseClipboard")
    if !hBitmap
       throw "GetClipboardData failed"
    Return hBitmap
 }
 
 HBitmapToPng(hBitmap, destPngFilePath) {
    static CLSID_WICImagingFactory  := "{CACAF262-9370-4615-A13B-9F5539DA4C0A}"
          , IID_IWICImagingFactory  := "{EC5EC8A9-C395-4314-9C77-54D7A935FF70}"
          , GUID_ContainerFormatPng := "{1B7CFAF4-713F-473C-BBCD-6137425FAEAF}"
          , WICBitmapUseAlpha := 0x00000000, GENERIC_WRITE := 0x40000000
          , WICBitmapEncoderNoCache := 0x00000002
          
    VarSetCapacity(GUID, 16, 0)
    DllCall("Ole32\CLSIDFromString", "WStr", GUID_ContainerFormatPng, "Ptr", &GUID)
    IWICImagingFactory := ComObjCreate(CLSID_WICImagingFactory, IID_IWICImagingFactory)
    Vtable( IWICImagingFactory    , CreateBitmapFromHBITMAP := 21 ).Call("Ptr", hBitmap, "Ptr", 0, "UInt", WICBitmapUseAlpha, "PtrP", IWICBitmap)
    Vtable( IWICImagingFactory    , CreateStream            := 14 ).Call("PtrP", IWICStream)
    Vtable( IWICStream            , InitializeFromFilename  := 15 ).Call("WStr", destPngFilePath, "UInt", GENERIC_WRITE)
    Vtable( IWICImagingFactory    , CreateEncoder           :=  8 ).Call("Ptr", &GUID, "Ptr", 0, "PtrP", IWICBitmapEncoder)
    Vtable( IWICBitmapEncoder     , Initialize              :=  3 ).Call("Ptr", IWICStream, "UInt", WICBitmapEncoderNoCache)
    Vtable( IWICBitmapEncoder     , CreateNewFrame          := 10 ).Call("PtrP", IWICBitmapFrameEncode, "Ptr", 0)
    Vtable( IWICBitmapFrameEncode , Initialize              :=  3 ).Call("Ptr", 0)
    Vtable( IWICBitmapFrameEncode , WriteSource             := 11 ).Call("Ptr", IWICBitmap, "Ptr", 0)
    Vtable( IWICBitmapFrameEncode , Commit                  := 12 ).Call()
    Vtable( IWICBitmapEncoder     , Commit                  := 11 ).Call()
    for k, v in [IWICBitmapFrameEncode, IWICBitmapEncoder, IWICStream, IWICBitmap, IWICImagingFactory]
       ObjRelease(v)
 }
 
 Vtable(ptr, n) {
    return Func("DllCall").Bind(NumGet(NumGet(ptr+0), A_PtrSize*n), "Ptr", ptr)
 }