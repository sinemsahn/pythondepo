import ctypes
import random
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
#bunlar toplam fare tiklamalari, cift tiklamalar ve tus vuruslarinin sayisini izleyecegimiz ana degiskenlerdir. daha sonra fare olaylarinin zamanlamasina da bakacagiz.
keystrokes = 0
mouse_clicks = 0
double_clicks = 0

#asagidakiler sistemin ne kadar suredir calistigini ve son kullanici girisinden bu yana ne kadar sure calistigini tespit etmek icindir
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), #cagriyi yapmadan once cbSize degiskenini yapinin boyutuna gore baslatmali
    ("dwTime", ctypes.c_ulong)
    ]
def get_last_input():
    
    struct_lastinputinfo = LASTINPUTINFO() # son gris olayinini sistemde tespit edildigi zamani milisaniye cinsinden tutar
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    
    # get last input registered
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))
    
    # now determine how long the machine has been running sistemin ne kadar suredir calistigi belirlenir
    run_time = kernel32.GetTickCount()
    
    elapsed = run_time - struct_lastinputinfo.dwTime
    
    print "[*] It's been %d milliseconds since the last input event." % elapsed
    
    return elapsed

# TEST CODE REMOVE AFTER THIS PARAGRAPH! komut dosyasini calistirp ardindan fareyi hareket ettirebileceginiz veya kklavyedeki bir tus basip bu yeni kodparcasnii calisirken gorebileceginiz basit bir test kodudur.asagidaki bu 3 kodu silip tus vuruslarini ve fare tiklamalrina bakmak icin bazi ek kodlar ekelyelim . PyHook yerine bu sefer pure ctypes kullanacagiz pyhookda olur ama , sandboxlar yinede bizim bu yontemlerimizi tespit edebilirler dikkat etmek lazim
#while True:
 #   get_last_input()
  #  time.sleep(1)
    

def get_key_press(): # bu fonksiyon bize fare tiklamalrinin sayisini, fare tikalmalarinin zamanini ve hedefin kac tus vurus verdigni soyler.
    global mouse_clicks
    global keystrokes
    
    for i in range(0,0xff): # bu gecerli giris anahtarlari araligni yineleyerek calisir
        if user32.GetAsyncKeyState(i) == -32767: # her bir anahtar icin getas.. foksyionu ile tusa basilip basilmadigini kontrol eder. 
            
            # 0x1 is the code for a left mouse-click tusa basildigi anlasilirsa sol fare dugmesi tiklamasi icin sanal anahtar kodu olan 0x1 olup olmadgini kontrol ederiz. toplam fare tiklama sayisi artiriyoruz ve daha sonra zamanlama hesaplamalari yapabilmemiz icin gecerli zaman damgasini donduruyoruz
            if i == 0x1:
                mouse_clicks += 1
                return time.time()
            elif i > 32 and i < 127: # klavyede ascii tus basimlarinin olup olmadigni da kontrol ediyoruz ve eger oyleyse tespit edilen toplam tus vurus sayisini artiriyoruz simdi bu islmeleri toplam korumali alan algilama dongusunda birlestirelim
                keystrokes += 1
    return None

def detect_sandbox():
    
    global mouse_clicks
    global keystrokes
    
    max_keystrokes = random.randint(10,25) # ne kadar tolerans gecebiliriz onlari belirliyoruz
    max_mouse_clicks = random.randint(5,25)
    
    double_clicks = 0
    max_double_clicks = 10
    double_click_threshold = 0.250 # in seconds
    first_double_click = None
    
    average_mousetime = 0
    max_input_threshold = 30000 # in milliseconds
    
    previous_timestamp = None
    detection_complete = False
    
    last_input = get_last_input()# daha sonra sistmee bir tur kullanici girisi kaydedildigi icin gecen sureyi aliriz ve girisi gordugumuzden bu yana cok uzun zamna gectgigini hissedersek truva ati died olur burada olak yerine rasthele zararsiz hareketlerde yaptirtabilirsin
    
    # if we hit our threshold let's bail out ilk giirs gecildikten sonra birincil tus vurusumuzu ve fare tiklamasi algilama dongumuze geciyoruz.
    if last_input >= max_input_threshold:
        sys.exit(0)
        
    while not detection_complete:
        
        keypress_time = get_key_press()
        
        if keypress_time is not None and previous_timestamp is not None:
            
            # calculate the time between double clicks once tuslara basmalari veya fare tiklamalrini kontrol ederiz ve islevin bir deger dondurmesi durumunda fare tiklamasinin gerceklestigi zaman damgasi oldugunu biliriz.
            elapsed = keypress_time - previous_timestamp# fare tiklamalari arasindaki zamna hesaplanir
            
            # the user double clicked
            if elapsed <= double_click_threshold: #cift tiklama var mi diye esikle karsilastirilir
                double_clicks += 1
                
                if first_double_click is None:
                    # grab the timestamp of the first double click
                    first_double_click = time.time()
                else:
                    if double_clicks == max_double_clicks: #max cift tiklama belirle onuda asarsa tespit ettruvayi oldur
                        if keypress_time - first_double_click <= (max_double_clicks * double_click_threshold):
                            sys.exit(0)
            # we are happy there's enough user input max kontrolleri yapilip cikilir
            if keystrokes >= max_keystrokes and double_clicks >= max_double_clicks and mouse_clicks >= max_mouse_clicks:
                
                return
            
            previous_timestamp = keypress_time
            
        elif keypress_time is not None:
            previous_timestamp = keypress_time

detect_sandbox()
print "We are ok!"
