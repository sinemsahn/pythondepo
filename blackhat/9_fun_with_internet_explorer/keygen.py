from Crypto.PublicKey import RSA

new_key = RSA.generate(2048, e=65537)
public_key = new_key.publickey().exportKey("PEM")
private_key = new_key.exportKey("PEM")

print public_key
print private_key

# rsalari cozmek icin metin haline getirmek icin , 2 anahtar cifti verir genel anahtari ie_exfil.py betigine kopyala , ardindan ozel anahtari private key degiskenine ekleyecegin decryptor.py ye gecelim.