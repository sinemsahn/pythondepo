from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64
bing_api_key = "YOURKEY" #ayda 2500 ucretsiz 
class BurpExtender(IBurpExtender, IContextMenuFactory):#icontext olan kullanici burpta bir istege sag tikladiginda bir baglam menusu saglamamiza izin veren  icontext i tanimlayarak basliyoruz.
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
        
        # we set up our extension
        callbacks.setExtensionName("BHP Bing")#menu isleyicimizi kullanicinin hangi sityee tikladigini belirleyebilmemiz ve daha sonra bing sorgularimizi saglayacak sekilde kaydederiz.
        callbacks.registerContextMenuFactory(self)
        
        return
    
    def bing_query(self,bing_query_string):
        
        print "Performing Bing search: %s" % bing_query_string
        
        # encode our query
        quoted_query = urllib.quote(bing_query_string)
        
        http_request = "GET https://api.datamarket.azure.com/Bing/Search/Web?$ format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request += "Host: api.datamarket.azure.com\r\n"
        http_request += "Connection: close\r\n"
        http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request += "User-Agent: Blackhat Python\r\n\r\n"
        json_body = self._callbacks.makeHttpRequest("api.datamarket.azure.com",443,True,http_request).tostring()
        
        json_body = json_body.split("\r\n\r\n",1)[1]
        try:
            r = json.loads(json_body) #json ayristiricisina iletiyor
            
            if len(r["d"]["results"]):
                for site in r["d"]["results"]:
                    
                print "*" * 100
                print site['Title']
                print site['Url']
                print site['Description']
                print "*" * 100
                
                j_url = URL(site['Url'])
                
            if not self._callbacks.isInScope(j_url):
                print "Adding to Burp scope"
                self._callbacks.includeInScope(j_url)
        except:
            print "No results from Bing"
            pass
        return

    
    
    
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        #hangi http isteginin secildigini belirlemek icin kullacagimiz bir IContextMenu.. nesnesini alacak olan createMenultem islevimizi kurmaktir. menu ogesi olusturur ve bing_menu islevinin click olayini islemesini saglamaktir
        return menu_list
    #bing sorgusu ve sonuc cikarmak icin 
    def bing_menu(self,event):#bu islev kullanici tanimladigimiz contexte tikladiginde tetiklenir
    # grab the details of what the user clicke
        http_traffic = self.context.getSelectedMessages()
        print "%d requests highlighted" % len(http_traffic)
        for traffic in http_traffic:
        http_service = traffic.getHttpService()
        host = http_service.getHost()
        print "User selected host: %s" % host #trafigi alir bing_searche yollar
        self.bing_search(host)
        return
    def bing_search(self,host):
        # check if we have an IP or hostname
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
        
        if is_ip: #ip mi host mu karari icin
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True
        bing_query_string = "'ip:%s'" % ip_address        
        self.bing_query(bing_query_string)
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)
            #simdi istegi binge gondermek ve sonuclari ayristirmak icin burpun http apisini kullanacak yapiyi yazalim
        