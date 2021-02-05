import re
import zlib
import cv2
from scapy.all import *

pictures_directory = "/home/wild/Desktop/pythondepo/blackhat/4owningthenetwork_with_scappy/pictures"
faces_directory = "/home/wild/Desktop/pythondepo/blackhat/4owningthenetwork_with_scappy/faces"
pcap_file = "home/wild/Desktop/pythondepo/blackhat/4owningthenetwork_with_scappy/arper.pcap"

#bu iki fonk pcap dosyamizdan aldigimiz http verilerine daha yakindan bakmamiza yardimci olur

def get_http_headers(http_payload):#bu fonk ham http trafigini alir ve normal bir ifade kullanarak basliklari bler
    try:
        # split the headers off if it is HTTP traffic
        headers_raw = http_payload[:http_payload.index("\r\n\r\n")+2]
        # break out the headers
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers_raw))
    except:
        return None
    if "Content-Type" not in headers:
        return None
    return headers

def extract_image(headers,http_payload):#http ustbilgilerini alir ve http yanitinda bir goruntu alip almadigni belirler . content-type basliginin gercekten goruntu mime turunu icerdigii tespit edersek, goruntu turunu ayiririz ve gecis halindeki goruntu turunu ayiririz ve gecis halindeki goruntude skstrma varsa goruntu turunu ve ham goruntu arabellegini dondurmeden once skstrmayi acamay calisiriz.
    image = None
    image_type = None
    try:
        if "image" in headers['Content-Type']:
            # grab the image type and image body
            image_type = headers['Content-Type'].split("/")[1]
            image = http_payload[http_payload.index("\r\n\r\n")+4:]
            # if we detect compression decompress the image
            try:
                if "Content-Encoding" in headers.keys():
                    if headers['Content-Encoding'] == "gzip":
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == "deflate":
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None,None
    return image,image_type

def face_detect(path,file_name):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("./haarcascade_frontalface_alt.xml")#onceden egitilmis bir sistem
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
    
    if len(rects) == 0:
        return False
    
    rects[:, 2:] += rects[:, :2]
    # highlight the faces in the image    
    for x1,y1,x2,y2 in rects:
        cv2.rectangle(img,(x1,y1),(x2,y2),(127,255,0),2)
        
    cv2.imwrite("%s/%s-%s" % (faces_directory,pcap_file,file_name),img)
    return True
    
def http_assembler(pcap_file):
        
    carved_images = 0
    faces_detected = 0
    
    a = rdpcap(pcap_file) #pcap dosyasi acilir
    
    sessions = a.sessions() #her tcp sessioni ayirmak icin 
    for session in sessions:
        http_payload = ""  #sadece http trafigini filtrelyoruz
        for packet in sessions[session]:
            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    # reassemble the stream
                    http_payload += str(packet[TCP].payload) # ardindan tumhttp trafigini yukunu tek bir tamponda birlestiriyoruz bu wirsharkta tcp stream follow demek giib
            except:
                pass
        headers = get_http_headers(http_payload) # tum bilgileri topladiktan sonra http ust bilgilerini incelemek icin ustbilgi ayristirma functiona aktariyoruz
        if headers is None:
            continue
        image,image_type = extract_image(headers,http_payload)#bir goruntu aldigimizi dogruladiktan sonra ham goruntuyu cikarir goruntu turunu ve goruntunun kendisinin ikili govdesini dondururuz.
        if image is not None and image_type is not None:
    # store the image
            file_name = "%s-pic_carver_%d.%s" % (pcap_file,carved_images,image_type)
            fd = open("%s/%s" % (pictures_directory,file_name),"wb")
            fd.write(image)
            fd.close()
            carved_images += 1
            # now attempt face detection
            try:#cikarilan goruntuyu depolar ve ardindan dosya yolunu yuz algilama rutinimize geciririz
                result = face_detect("%s/%s" % (pictures_directory,file_name),file_name)
                if result is True:
                    faces_detected += 1
            except:
                pass
    return carved_images, faces_detected
carved_images, faces_detected = http_assembler(pcap_file)
print( "Extracted: %d images" % carved_images)
print ("Detected: %d faces" % faces_detected)
    