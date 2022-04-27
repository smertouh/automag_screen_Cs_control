import win32ui, win32gui, win32con, win32api

def grab_screen(s):
    hwnd = win32gui.GetDesktopWindow()
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (x, y), win32con.SRCCOPY)

    # Можно сохранить полученный битмап в BPM огромных размеров
    # saveBitMap.SaveBitmapFile(saveDC, 'screenshot.bmp')

    # --------------------------------------------------------------
    # Либо воспользоваться PIL для сохранения в любом другом формате
    import PIL.Image

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    image = PIL.Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)


    image.save(s, format='png')
    # --------------------------------------------------------------

    saveDC.DeleteDC()
    win32gui.DeleteObject(saveBitMap.GetHandle())

if __name__ == '__main__':
    s0= "d:\\data\\screenshot\\"
    s = s0 + "screen_" + "sfas" + ".png"
    if os.path.exists(s0):
        pass
    else:
        os.mkdir(s0)
    grab_screen(s)