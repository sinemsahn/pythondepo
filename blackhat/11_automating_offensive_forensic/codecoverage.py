from immlib import *

class cc_hook(LogBpHook):
    
    def __init__(self):
        
        LogBpHook.__init__(self)
        self.imm = Debugger()
        
    def run(self,regs):
        
        self.imm.log("%08x" % regs['EIP'],regs['EIP'])
        self.imm.deleteBreakpoint(regs['EIP'])
        
        return
    def main(args):
        imm = Debugger()
        
        calc = imm.getModule("calc.exe")
        imm.analyseCode(calc.getCodebase())
        
        functions = imm.getAllFunctions(calc.getCodebase())
        
        hooker = cc_hook()
        
        for function in functions:
            hooker.add("%08x" % function, function)
        return "Tracking %d functions." % len(functions)    
    '''
    Bu, calc.exe'deki her işlevi bulan ve her biri için tek seferlik bir kesme noktası ayarlayan basit bir komut dosyasıdır. Bu, çalıştırılan her işlev için Bağışıklık Hata Ayıklayıcısının işlevin adresini çıkarması ve ardından aynı işlev adreslerini sürekli olarak günlüğe kaydetmememiz için kesme noktasını kaldırması anlamına gelir. Calc.exe'yi Bağışıklık Hata Ayıklayıcısı'na yükleyin, ancak henüz çalıştırmayın. Ardından, Bağışıklık Hata Ayıklayıcı ekranının altındaki komut çubuğuna şunu girin:
    !codecoverage
    
'''
    '''
    Şimdi işlemi F9 tuşuna basarak çalıştırabilirsiniz. Günlük Görünümüne (alt-L) geçerseniz, işlevlerin kaydırıldığını göreceksiniz. Şimdi = düğmesi dışında istediğiniz kadar düğmeyi tıklayın. Buradaki fikir, aradığınız tek işlev dışındaki her şeyi yürütmek istemenizdir. Yeterince etrafı tıkladıktan sonra, Günlük Görünümünü sağ tıklayın ve Pencereyi Temizle'yi seçin. Bu, daha önce vurduğunuz tüm işlevlerinizi kaldırır. Daha önce tıkladığınız bir düğmeyi tıklayarak bunu doğrulayabilirsiniz; günlük penceresinde hiçbir şey görmemelisiniz. Şimdi o pesky = düğmesini tıklayalım. Günlük ekranında yalnızca tek bir giriş görmelisiniz (3 + 3 gibi bir ifade girmeniz ve ardından = düğmesine basmanız gerekebilir). Windows XP SP2 sanal makinemde bu adres 0x01005D51'dir. Tamam! Bağışıklık Hata Ayıklayıcı kasırga turumuz ve bazı temel kod kapsama tekniklerimiz bitti ve kodu enjekte etmek istediğimiz adres bizde. Bu iğrenç işi yapmak için Volatilite kodumuzu yazmaya başlayalım.
Bu çok aşamalı bir süreçtir. Öncelikle calc.exe işlemini aramak için belleği taramamız ve ardından kabuk kodunu enjekte etmek için bellek alanını araştırmamız ve ayrıca RAM görüntüsünde daha önce bulduğumuz işlevi içeren fiziksel ofseti bulmamız gerekir. Daha sonra, kabuk kodumuza atlayan ve onu çalıştıran = düğmesinin işlev adresi üzerine küçük bir sıçrama eklememiz gerekir. Bu örnek için kullandığımız kabuk kodu, Countermeasure adlı fantastik bir Kanada güvenlik konferansında yaptığım bir gösteriden. Bu kabuk kodu, sabit kodlanmış ofsetler kullanıyor, bu nedenle kilometreniz değişebilir.
'''
    