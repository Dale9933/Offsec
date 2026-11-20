import threading
from ftplib import FTP, error_perm

import nmap
from pythonping import ping

target = "192.168.1.1"

def ping_host():
    response = ping(
       target=target,
       count=5,
       timeout=5,
       verbose=False
    )

    if response.success():
         print(f"Host {target} is reachable.")
         tcp_ports = scan_TCP_Ports()
         scan_UDP_ports()
         check_findings(tcp_ports)

    else:
            print(f"Host {target} is not reachable.")

def scan_TCP_Ports():
   scanner = nmap.PortScanner()
   scanner.scan(
        hosts=target,
        arguments='-sV -sC',
        ports= '1-1024'
   )
   print(scanner.csv())
   open_ports = []
   for host in scanner.all_hosts():
       for proto in scanner[host].all_protocols():
           for port in scanner[host][proto]:
               if scanner[host][proto][port]['state'] == 'open':
                   open_ports.append(port)
   return open_ports

def scan_UDP_ports():
   scanner = nmap.PortScanner()
   scanner.scan(
       hosts=target,
       arguments='-sU',
       ports= '1-1024',
 )
   print(scanner.csv())

def check_FTP_anonymous():
    try:
        ftp = FTP()
        ftp.connect(target, 21, timeout=5)
        ftp.login("anonymous", "anonymous@test.com")
        print(f"Anonymous FTP login on {target} worked.")
        try:
             print(ftp.nlst())
        except error_perm:
             print("Login ok but no listing allowed.")
        ftp.quit()
    except error_perm:
        print("Anonymous FTP login refused.")
    except Exception as e:
        print(f"FTP error: {e}")

def check_findings(open_ports):
    if 21 in open_ports:
         print("Port 21 open, trying anonymous FTP.")
         check_FTP_anonymous()

    if 80 in open_ports or 443 in open_ports:
         print("Webserver found, starting subenum.")
         # funktion muss eingebaut werden

def threads():
    tcp_threader=threading.Thread(target=scan_TCP_Ports)
    udp_threader=threading.Thread(target=scan_UDP_ports)
    tcp_threader.start()
    udp_threader.start()

if __name__ == "__main__":
    ping_host()
