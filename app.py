from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time

desktop_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 Safari/537.36 Edg/92.0.874.0"
mobile_useragent = "Mozilla/5.0 (Linux; Android 11; SM-N986B) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/88.0.4324.152 Mobile Safari/537.36" # Galaxy Note 20 Ultra

with open('userpass.txt') as passdoc:
    username1 = passdoc.readline()[:-1]
    pass1 = passdoc.readline()[:-1]
    username2 = passdoc.readline()[:-1]
    pass2 = passdoc.readline()[:-1]
    username3 = passdoc.readline()[:-1]
    pass3 = passdoc.readline()[:-1]

print(username1, pass1)
print(username2, pass2)
print(username3, pass3)
