import sys
import struct
import volatility.conf as conf
import volatility.registry as registry

memory_file = "WindowsXPSP2.vmem" # ilk olarak analiz edecegimiz bellei ayarladik
sys.path.append("/Users/justin/Downloads/volatility-2.3.1") # votality kitapliklarini eklemesi icin votality indirme yolunu ekledi bunu duzenle!!!

registry.PluginImporter()
config = conf.ConfObject()

import volatility.commands as commands
import volatility.addrspace as addrspace

config.parse_options() # geri kalanlar votalitie kodun geri kalani sadece votalitie ornegimiz profil ve konfigurasyon seceneklerini ayarlmak 
config.PROFILE = "WinXPSP2x86"
config.LOCATION = "file://%s" % memory_file

registry.register_global_options(config, commands.Command)
registry.register_global_options(config, addrspace.BaseAddressSpace)

#simdi gerecek hash dokum kodu 
from volatility.plugins.registry.registryapi import RegistryApi
from volatility.plugins.registry.lsadump import HashDump

registry = RegistryApi(config)# yaygin olarak kullanilan kayit defteri islevlerine sahip bir yardimci sinif olan yeni bir registryapi prnegi olusturuyoruz. parametre olarak sadce mevcut yapilandirmayi alir
registry.populate_offsets()# bu cagri daha once ele aldigimiz hivelist komutunu calistirmanin esdegerini gerceklestirir.

sam_offset = None
sys_offset = None

for offset in registry.all_offsets:
    if registry.all_offsets[offset].endswith("\\SAM"): # daha sonra sam ve sytem yerlerini arayan kesfedilen kovanlarin her birinde yurumeye baslariz.
        sam_offset = offset
        print "[*] SAM: 0x%08x" % offset
        
    if registry.all_offsets[offset].endswith("\\system"):
        sys_offset = offset
        print "[*] System: 0x%08x" % offset
        
    if sam_offset is not None and sys_offset is not None:    
        config.sys_offset = sys_offset # kesfedildiklerinde mevcut konfigurasyon  nesnesini ilgili ofsetleriyle guncelleriz.
        config.sam_offset = sam_offset
        
        hashdump = HashDump(config) # ardindan bir hashdump nesnesi olustuurp mevcut yapilandirma nesnesine geciyoruz. 
        
        for hash in hashdump.calculate(): # gerek kullanici adlarini ve bunlarla iliskili hashlerini ureten hesapaam islevi cagrisindan elde edilen sonuclari yinelemektir.
            print hash
        break
if sam_offset is None or sys_offset is None:
    print "[*] Failed to find the system or SAM offsets."        