import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

private_key = "###PASTE PRIVATE KEY HERE###"

rsakey = RSA.importKey(private_key)# rsa isniifmizi ozel anahtarlarla basitce somutlastiriyoruz
rsakey = PKCS1_OAEP.new(rsakey)

chunk_size= 256
offset = 0
decrypted = ""
encrypted = base64.b64decode(encrypted) # kodlanmis blogumuzu tumlr'dan base64decode oalrak kodluyoruz.

while offset < len(encrypted):# 256 bytlik parcalari alip sifresini cozerek yavasca orijinal duz metin dizimizi olusturuyouz
    decrypted += rsakey.decrypt(encrypted[offset:offset+chunk_size])
    offset += chunk_size
    
# now we decompress to original yuku diger tarafta skstrdigimiz icin bu tarafta acariz
plaintext = zlib.decompress(decrypted)

print plaintext
