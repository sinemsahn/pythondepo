import win32gui
import win32ui
import win32con
import win32api

# grab a handle to the main desktop window tum ekrani kapsayan br handler olusturur
hdesktop = win32gui.GetDesktopWindow()

# determine the size of all monitors in pixels tum pencerenin pixellerine karar verir ekranalrin boyutu belirlenir boylece ekran goruntusu icin gerekli olan boyutlari biliriz
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

# create a device context aracin iceirgini olusturu  bir ichaz baglami context olusturur ve masaustuna bir handle geciririz.
desktop_dc = win32gui.GetWindowDC(hdesktop)
img_dc = win32ui.CreateDCFromHandle(desktop_dc)

# create a memory based device context hafiza tabanli context olusturur bitmap baytlarini bir dosyaya depolayan kadar goruntu yakalamamizi saklayacagimiz bir yer olusturu
mem_dc = img_dc.CreateCompatibleDC()

# create a bitmap object bitmap nesnesi olusturur
screenshot = win32ui.CreateBitmap() 
screenshot.CreateCompatibleBitmap(img_dc, width, height)
mem_dc.SelectObject(screenshot)

# copy the screen into our memory device context ekrai kopyalar ve biizm memory conetxt icine atar
mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
#bitblt fonksiyonu ekran goruntusunun bit kopyasini  alir ve contextde saklar  
# save the bitmap to a file bitmap dosyasini kaydeder
screenshot.SaveBitmapFile(mem_dc, 'c:\\WINDOWS\\Temp\\screenshot.bmp')#gorunutuyu diske doker 

# free our objects nesneyi birakir
mem_dc.DeleteDC()
win32gui.DeleteObject(screenshot.GetHandle())