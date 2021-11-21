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
        else:
            logins[len(logins)-1].append(line)

# Takes in the platform and whether or not it will be headless to create a webdriver
def create_driver(mobile, headless):
    # Selects the Correct User Agent
    if mobile:
        useragent = mobile_useragent
    else:
        useragent = desktop_useragent

    # Adds the Correct arguments
    opts = Options()
    opts.add_argument(useragent)
    if headless:
        opts.add_argument('--headless')
        opts.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(chrome_path, options=opts)

# Logs in the User using the microsoft dialog
def login(driver_login, acct):
    logged_in = False  # True when successfully logged in

    user, passwd = acct  # Sets Username and Password values

    while (logged_in == False):
        print("Attempting Login...")
        driver_login.get('https://login.live.com/')
        time.sleep(5)  # Wait for page to load

        driver_login.find_element_by_name('loginfmt').send_keys(user)
        time.sleep(1)  # Delay Between Send Keys and Click
        driver_login.find_element_by_xpath(
            '//*[@id="idSIButton9"]').click()  # next button
        time.sleep(3)  # Delay for password screen
        driver_login.find_element_by_name('passwd').send_keys(passwd)
        time.sleep(1)  # Delay Between Send Keys and Click
        driver_login.find_element_by_xpath(
            '//*[@id="idSIButton9"]').click()  # sign in button
        time.sleep(5)

        logged_in = login_check(driver_login)

    print("Login Successful: ", user)  # Prints Email to the Screen


def login_check(check_driver):
    check_driver.get('https://account.microsoft.com/')
    time.sleep(3)
    bodyTag = check_driver.find_element_by_tag_name("body")
    return ("Pranav" in bodyTag.text) or ("Bala" in bodyTag.text)


# Checks the num of points earned on the present day
def check_num_pts(check_driver):
   rewards_btn = check_driver.find_element_by_xpath(r'//*[@id="navs"]/div/div/div/div/div[4]/a')
   rewards_btn.click()
   time.sleep(3)
   check_driver.get("https://rewards.microsoft.com/pointsbreakdown")
   time.sleep(5000)

def main():
    driver = create_driver(False, False)
    login(driver, logins[0])
    check_num_pts(driver)

main()
