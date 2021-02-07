from burp import IBurpExtender#oncelikle yazdigimiz her uzanti icin bir gerelilik olan bu sinifi import edelim.
from burp import IIntruderPayloadGeneratorFactory # bu sinifleri incelemek icin o api kismindan bakarsin boylece neyi uygulayabiecegini anlarsin
#bunu ineledigimizde getnextpayload sinifi yakalamis oldugunuz http isteginden orijinal yuku alacaktir.veya fuzzer olarak sectigin yeribu fonksiyon bzie orijinal test senaryosunu bulmamizi ve ardindan onu geri dondurmemizi saglar.boylece burp yeni fuzzed degeri gonderirr
from burp import IIntruderPayloadGenerator
#bir intredur payload olusturmak icin gerekli olan sinifleri ice aktaralim.

from java.util import List, ArrayList

import random





class BHPFuzzer(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payloads = 10 #burp fuzzing islemelerini ne zaman bitecegini buradan anliyor
        self.num_iterations = 0
        return

    def hasMorePayloads(self):#maximum fuzzing islemine ulasip ulasmadiginin kontrolunu yapar
        if self.num_iterations == self.max_payloads:
            return False
        else:
            return True
    def getNextPayload(self,current_payload): # burada fuzzing islemi yapilir
    # convert into a string
        payload = "".join(chr(x) for x in current_payload)#stringe donusturme islemi yapar bayt olarak gelir
        # call our simple mutator to fuzz the POST
        payload = self.mutate_payload(payload)# fuzzing fonksiyonuna atar
        
        # increase the number of fuzzing attempts
        self.num_iterations += 1
        
        return payload
    def reset(self):
        self.num_iterations = 0
        return
    def mutate_payload(self,original_payload): #fuzzing islemi
        # pick a simple mutator or even call an external script
        picker = random.randint(1,3)
        
        # select a random offset in the payload to mutate
        offset = random.randint(0,len(original_payload)-1)
        payload = original_payload[:offset]
        
        # random offset insert a SQL injection attempt
        if picker == 1:
            payload += "'"
        
        # jam an XSS attempt in
        if picker == 2:
            payload += "<script>alert('BHP!');</script>"
        
        # repeat a chunk of the original payload a random number
        if picker == 3:
            
            chunk_length = random.randint(len(payload[offset:]),len(payload)-1)
            repeater = random.randint(1,10)
            
            for i in range(repeater):
                payload += original_payload[offset:offset+chunk_length]
                
        # add the remaining bits of the payload
        payload += original_payload[offset:]
        
        return payload        
    #payloadin belrili kismini ve ne yapacagini random belirliyor 
    
    
    
class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        return
    
    def getGeneratorName(self):#payload olusturucumuzun adini basitce dondrumek icin 
        return "BHP Payload Generator" 
    def createNewInstance(self, attack):
        return BHPFuzzer(self, attack) #son adim saldiri parametresini alan   