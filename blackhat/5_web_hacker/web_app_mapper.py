import Queue
import threading
import os
import urllib2

threads = 10

target = "http://www.blackhatpython.com"
directory = "/Users/justin/Downloads/joomla-3.1.1"
filters = [".jpg",".gif","png",".css"] #hangi dosyalari istiyorsak hangi uzantilar ise
#unlar web uygulamasina gore degisir


os.chdir(directory)

web_paths = Queue.Queue() #uzak sunucuda bulanay calistigimiz dosyalari saklar

for r,d,f in os.walk("."): # tum dosya ve dizinlerde gezinmek icin oswalki kullanir
    for files in f:
        remote_path = "%s/%s" % (r,files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)
    #Yerel olarak buldugumuz her gecerli dosya icin, onu web_paths Kuyrugumuza ekleriz.

def test_remote(): #queedan olusan bir dizi pathini alir ve onu dener var mi yok mu idye
    #Dosyayi almayi basarirsak, HTTP durum kodunu ve dosyanin tam yolunu (5) cikaririz. Dosya bulunamazsa veya bir .htaccess dosyasi tarafindan korunuyorsa, bu urllib2'nin bir hata atmasina neden olur, bu hatayi ele aliriz (6), boylece dongu calismaya devam edebilir.
    while not web_paths.empty():
        path = web_paths.get()
        url = "%s%s" % (target, path)
        request = urllib2.Request(url)    
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            
            print ("[%d] => %s" % (response.code,path))
            response.close()
            
        except urllib2.HTTPError as error:
            #print "Failed %s" % error.code
            pass

for i in range(threads):
    print("Spawning thread: %d" % i)
    t = threading.Thread(target=test_remote)
    t.start()
    