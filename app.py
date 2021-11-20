from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time

desktop_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 Safari/537.36 Edg/92.0.874.0"
mobile_useragent = "Mozilla/5.0 (Linux; Android 11; SM-N986B) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/88.0.4324.152 Mobile Safari/537.36" # Galaxy Note 20 Ultra

# File path for the chromedriver
chrome_path = r'/usr/local/bin/chromedriver'

# Vars
logins = []

# You Need a file called userpass.txt with the usernames and passwords on different lines
with open('userpass.txt') as passdoc:
    # Puts each set of logins and passwords in a list [[L1, P1], [L2, P2] ...]
    for line in passdoc:
        line = line[:-1]
        if str(line)[-3:] == "com":
            logins.append([line])
            print(logins)
        else:
            logins[len(logins)-1].append(line)
            print(logins)



