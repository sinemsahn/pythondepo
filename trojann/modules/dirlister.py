import os

def run(**args):
    print "[*] In dirlister module."
    files = os.listdir(".")
    return str(files)
#gecerli dizindeki tum dosyalari listeleyen ve bu listeyi bir string olarak dondurur.