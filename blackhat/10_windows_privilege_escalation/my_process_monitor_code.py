import win32con
import win32api
import win32security

import wmi
import sys
import os


#---------------------------------------------------------------------
def log_to_file(message):
    fd = open(LOG_FILE, "ab")
    fd.write("%s\r\n" % message)
    fd.close()

    return

# create a log file header
if not os.path.isfile(LOG_FILE):
    log_to_file("Time,User,Executable,CommandLine,PID,ParentPID,Privileges")

# instantiate the WMI interface WMI sinifini ornekleyerek 
c = wmi.WMI()

# create our process monitor surec olusturma olayini izelemsini soyleyerek basliyoruz PythonWMI belgeleirni okuyarak, surec olusturma veya silme olaylarini izleyebileceginizi ogreniyoruz.
process_watcher = c.Win32_Process.watch_for("creation")

#surec olaylarini yakindan izlemek istediginize karar verirseniz islemi kullanabilirisiniz ve bu islem bir surecin gectigi her olay hakkinda sizi bilgilendirir.

while True:
    try:
        new_process = process_watcher()# yeni bir islem olayi dondurene kadar dongu bloklanir 
    # yeni islem olayi, pesinde oldugumuz tum ilgili bilgileri iceren win32_process2 adli bir WMI sinifidir. 

        proc_owner  = new_process.GetOwner()# sinif islevleirndne biri, sureci kimin baslattigini beirlemek icin GetOWnerdir. buradan aradigimiz tum islem bilgilerini toplar ekrana cikarir ve bir dosyaya kaydederiz.
        proc_owner  = "%s\\%s" % (proc_owner[0],proc_owner[2])
        create_date = new_process.CreationDate
        executable  = new_process.ExecutablePath
        cmdline     = new_process.CommandLine
        pid         = new_process.ProcessId
        parent_pid  = new_process.ParentProcessId

        privileges  = get_process_privileges(pid)

        process_log_message = "%s,%s,%s,%s,%s,%s,%s" % (create_date, proc_owner, executable, cmdline, pid, parent_pid,privileges)

        print "%s\r\n" % process_log_message

        log_to_file(process_log_message)

    except:
        pass
#-------------------------------------------------------------------
