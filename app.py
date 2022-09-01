import arrow  # Time library
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import random
import time
import argparse
import os
from country_list import countries_for_language
import json


# Useragents to change browser
desktop_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 Safari/537.36 Edg/92.0.874.0"
mobile_useragents = [
    "Mozilla/5.0 (Linux; Android 10; SM-G975U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36",
]

# Vars
logins = []
firstName = ''
lastName = ''
current_path = os.path.dirname(os.path.realpath(__file__))

# Argparse Specific - takes input on first and last name for use in logincheck function
parser = argparse.ArgumentParser()
parser.add_argument("first_name")
parser.add_argument("last_name")
parser.add_argument("-d", "--debug", help="turn off headless",
                    action="store_true")
parser.add_argument("-b", "--blind", help="disable point checks (use if pts check is buggy)",
                    action="store_true")
args = parser.parse_args()

# Imports first and last name from argparse
firstName = args.first_name
lastName = args.last_name

if args.debug:  # Checks if debug mode turned on
    headless_mode = False
else:
    headless_mode = True

blindmode = args.blind

# You Need a file called userpass.txt with the usernames and passwords on different lines
# !!!!!! Make sure you have a newline on the last line of your userpass.txt file
with open(f'{current_path}/userpass.txt') as passdoc:
    # Puts each set of logins and passwords in a list [[L1, P1], [L2, P2] ...]
    for line in passdoc:
        line = line[:-1]
        if str(line)[-3:] == "com":
            logins.append([line])
        else:
            logins[len(logins)-1].append(line)

# Imports element data from json file
with open(f'{current_path}/elements.json') as jfile:
    element_data = json.load(jfile)

# Imports url data from json file
with open(f'{current_path}/urls.json') as jfile:
    url_data = json.load(jfile)

# Random word list
r = str(requests.get(
    'https://raw.githubusercontent.com/lorenbrichter/Words/master/Words/en.txt').content).split(r'\n')
# Takes uses platform & headless status to create webdriver


def create_driver(mobile, headless):
    if mobile:
        print('Mobile Browser')
    else:
        print("Desktop Browser")

    # Selects the Correct User Agent
    if mobile:
        # Picks from many different useragents
        useragent = random.choice(mobile_useragents)
    else:
        useragent = desktop_useragent

    # Adds the Correct arguments
    opts = Options()
    # Tells chrome what the user agent is
    opts.add_argument(f"user-agent={useragent}")

    if headless:
        opts.add_argument('--headless')  # Turns on headless mode
        opts.add_experimental_option(
            'excludeSwitches', ['enable-logging'])  # Turns off verbose logging

    # Creates webdriver with options and returns it
    return webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=opts)


# Logs in the User using the microsoft dialog
def login(driver_login, acct):
    logged_in = False  # True when successfully logged in

    user, passwd = acct  # Sets Username and Password values from acct list

    login_attempts = 0

    while not logged_in and login_attempts < 5:
        login_attempts += 1
        print("Attempting Login...   ", user)
        driver_login.get('https://login.live.com/')
        time.sleep(3)  # Wait for page to load

        if (len(driver_login.find_elements(By.NAME, 'loginfmt')) > 0):
            driver_login.find_element(By.NAME, 'loginfmt').send_keys(user)
            time.sleep(1)  # Delay Between Send Keys and Click
            driver_login.find_element(By.XPATH,
                                      '//*[@id="idSIButton9"]').click()  # next button
            time.sleep(2)  # Delay for password screen
            driver_login.find_element(By.NAME, 'passwd').send_keys(passwd)
            time.sleep(1)  # Delay Between Send Keys and Click
            driver_login.find_element(By.XPATH,
                                      '//*[@id="idSIButton9"]').click()  # sign in button
            time.sleep(3)

        logged_in = login_check(driver_login)
        # print("Logged In: ", logged_in) ## Debug Code
        # print("User: ", user) ## Debug Code
        # print("Pass: ", passwd) ## Debug Code
    if logged_in:
        print("Login Successful: ", user)  # Prints Email to the Screen
    else:
        return Exception("Login Failed")


def login_check(check_driver):
    # Checks if name is on the webpage
    check_driver.get('https://account.microsoft.com/')
    time.sleep(2)
    account_pg = str(check_driver.page_source.encode(
        'utf-8'))  # Page source Code

    if not check_name_on_page(account_pg):
        return False

    # ---- Sign In Button ----

    # Make generic search
    check_driver.get(url_data['time_search'])
    # Source code of full webpage
    search_engine_fullpage = str(check_driver.page_source.encode('utf-8'))

    # Checks if using mobile or desktop useragent
    mobile = check_driver.execute_script(
        "return navigator.userAgent") in mobile_useragents

    signin_tries = 0
    while (signin_tries < 3) and (not check_name_on_page(search_engine_fullpage)):
        signin_tries += 1
        if not mobile:
            if len(check_driver.find_elements(By.XPATH, '//*[@id="id_a"]')) > 0:
                check_driver.find_element(By.XPATH, '//*[@id="id_a"]').click()

        else:
            try:
                time.sleep(1)
                check_driver.find_element(By.ID, 'mHamburger').click()
            except:
                try:
                    check_driver.find_element(By.ID, 'bnp_btn_accept').click()
                except:
                    pass
                try:
                    check_driver.find_element(By.ID, 'bnp_ttc_close').click()
                except:
                    pass
                time.sleep(1)
                try:
                    check_driver.find_element(By.ID, 'mHamburger').click()
                except:
                    pass
            try:
                time.sleep(1)
                check_driver.find_element(By.ID, 'HBSignIn').click()
            except:
                pass

        # Source code of full webpage
        search_engine_fullpage = str(check_driver.page_source.encode('utf-8'))
    return check_name_on_page(search_engine_fullpage)


def element_on_page(elements_key, element_check_driver):
    """
    Element On Page
    ----
    Returns whether the xpath is present on the page
    """
    if (len(element_check_driver.find_elements(By.XPATH, element_data[elements_key]))) > 0:
        return True
    return False


def check_name_on_page(sourceCode):
    """
    Check Name On Page
    --
    Checks if the name is present in the sourcecode of the page
    """

    if ((firstName in sourceCode) or (lastName in sourceCode)):
        return True
    return False


def check_num_pts(check_driver, blind):
    points = []

    check_driver.get(url_data["points_url"])

    time.sleep(3)  # Wait for the page to load

    rewards_fullpage = str(check_driver.page_source.encode('utf-8'))
    rewards_body = check_driver.find_element(
        By.TAG_NAME, "body").text  # All of the text on the webpage

    # In some instances, a join now button is displayed, it needs to be clicked
    if ("When you join Microsoft Rewards" in rewards_body):
        print("join btn detected")
        check_driver.find_element(By.XPATH,
                                  element_data['join_now_btn_xpath']).click()
        # ↓ Done since the join now button takes you to bing.com and not to points pg
        check_driver.get(url_data["points_url"])

    check_driver.get(url_data["points_url"])
    # input()
    # Checking level2/level1
    lvlcheck = check_driver.find_elements(
        By.XPATH, element_data["mobile_search_full_xpath"])
    lvl2 = len(lvlcheck) > 0

    if lvl2:
        print("level2")
        # Gets number of points remaining for each category
        pc_search_pts_remaining = check_driver.find_element(By.XPATH,
                                                            element_data['pc_search_pts_lvl2_xpath']).text
        slash_index = pc_search_pts_remaining.index("/")
        pc_search_pts_remaining = int(
            pc_search_pts_remaining[slash_index+1:]) - int(pc_search_pts_remaining[:slash_index])

        edge_search_pts_remaining = check_driver.find_element(By.XPATH,
                                                              element_data['edge_search_pts_lvl2_xpath']).text
        slash_index = edge_search_pts_remaining.index("/")
        edge_search_pts_remaining = int(
            edge_search_pts_remaining[slash_index+1:]) - int(edge_search_pts_remaining[:slash_index])

        mobile_search_pts_remaining = check_driver.find_element(By.XPATH,
                                                                element_data['mobile_search_pts_lvl2_xpath']).text
        slash_index = mobile_search_pts_remaining.index("/")
        mobile_search_pts_remaining = int(
            mobile_search_pts_remaining[slash_index+1:]) - int(mobile_search_pts_remaining[:slash_index])

        points.append(pc_search_pts_remaining)
        points.append(edge_search_pts_remaining)
        points.append(mobile_search_pts_remaining)
        
        if blind:
            points = [0, 0, 0]
    else:
        print("lvl1")
        # Gets number of points remaining for each category
        pc_search_pts_remaining = check_driver.find_element(By.XPATH,
                                                            element_data['pc_search_pts_lvl1_xpath']).text
        print(pc_search_pts_remaining)
        slash_index = pc_search_pts_remaining.index("/")
        pc_search_pts_remaining = int(
            pc_search_pts_remaining[slash_index+1:]) - int(pc_search_pts_remaining[11:slash_index])

        edge_search_pts_remaining = check_driver.find_element(By.XPATH,
                                                              element_data['edge_search_pts_lvl1_xpath']).text
        slash_index = edge_search_pts_remaining.index("/")
        edge_search_pts_remaining = int(
            edge_search_pts_remaining[slash_index+1:]) - int(edge_search_pts_remaining[11:slash_index])

        points.append(pc_search_pts_remaining)
        points.append(edge_search_pts_remaining)
        if blind:
            points = [0, 0]

    return points


def random_searches(driver_search, num):
    """
    Random Searches
    ----------------------
    Random selection between a coordinate generator and a number generator
    driver_search -> selenium webdriver
    num -> number of searches remaining
    """

    # Generates random coordinates and enters in the search query
    def coordinate_generator():
        pos_neg = ["", "-"]
        num1 = random.randint(1, 75)
        num2 = random.randint(1, 75)
        num1_dec = random.randint(1, 9999)
        num2_dec = random.randint(1, 9999)
        num1_posneg = random.choice(pos_neg)
        num2_posneg = random.choice(pos_neg)

        return (f'{num1_posneg}{num1}.{num1_dec}, {num2_posneg}{num2}.{num2_dec}' +
                f" {random.choice(['coord', 'coordinate', 'map', 'zip code', 'zip', 'location'])}")

    # Creates random equations
    def numbergen():
        num1 = random.randint(1, 999)
        num1_dec = num1 = random.randint(1, 999)
        num2 = random.randint(1, 9999)
        num2_dec = random.randint(1, 99)
        return f"{num1}.{num1_dec}{random.choice(['*', '-', '^'])}{num2}.{num2_dec}"

    def randomWordDefinition():
        # Example search: exemptions define5
        random_word_search = str(random.choice(r))
        random_word_search += random.choice(
            [" def", " defin", " defition", " definition", " drfine", " meanin"])

        return random_word_search

    def randomCountryStats():
        country_attributes = ['metric or imperial', 'in NATO', 'gdp', 'capital', 'population', 'average income', 'language', 'map',
                              'continent', 'largest city', 'COVID', 'coronavirus', 'population density', 'news', 'president', 'internet', 'size']

        countries = list(countries_for_language('en'))
        country = countries[random.randint(0, 248)][1]
        return (country + " " + random.choice(country_attributes))

    def randomStockStats():
        stocks = requests.get(url_data['companies_list']).text.split("\n")

        stock_attributes = ['market cap', 'index', 'headquarters', 'stock price', 'share price', 'shares', 'description', 'name', 's&p', 's&p 500',
                            'china', 'russia', 'ukraine', 'US', 'privacy', 'data collection', 'products', 'jobs', 'software', 'hardware', 'pe ratio', 'dividentds']

        stock = stocks[random.randint(0, 500)]
        return (stock + " " + random.choice(stock_attributes))

    for i in range(int(num)):
        stringtosearch = random.choice(
            [coordinate_generator(), numbergen(), randomWordDefinition(), randomCountryStats(), randomStockStats()])  # Each function returns a unique search that
        driver_search.get(
            f'https://www.bing.com/search?q={stringtosearch}')  # Loads search
        # Prints percentage of searches completed on attempt
        print(str(int((i+1)/num*100))+"%")
        time.sleep(random.randint(1, 7))  # Time between searches


def complete_challenge_1(driver_challenge):
    # Completes the 1st challenge (10 pts)
    driver_challenge.get(url_data['points_url'])
    time.sleep(2.35)
    # CHecks if challenge element is there, if so, it clicks the challenge
    if len(driver_challenge.find_elements(By.XPATH, element_data['daily_challenge_1'])) > 0:
        driver_challenge.find_element(
            By.XPATH, element_data['daily_challenge_1']).click()


def mobilePts(headless, ptsRemaining, userpass):
    driver_mobile = create_driver(True, headless)  # Creates mobile driver
    login(driver_mobile, userpass)  # Logs in on mobile driver
    random_searches(driver_mobile, ptsRemaining)  # Starts random searches
    driver_mobile.quit()  # Closes the mobile driver


def main():
    # Gets time & prints using arrow time library
    time = arrow.now(
        'US/Central').format("(MMM D, YYYY) (h:mm:ssA)")
    print(time)

    # used to determine whether to run again or terminate
    all_acct_pts = [[False, False, False] for i in range(len(logins))]

    for i in range(2):  # Runs MAX 2 passes on accts
        for i in range(len(logins)):
            # Creates the desktop driver
            driver = create_driver(False, headless_mode)
            login(driver, logins[i])  # Logs in on desktop driver
            # Checks the number of points and adds it to pts list
            pts = check_num_pts(driver, blindmode)
            # Prints out the pts list
            print("Remaining Pts: [desktop, edge, mobile]: ", pts)

            pc_complete = (pts[0] == 0)
            edge_complete = (pts[1] == 0)

            # Complete Daily Challenge
            complete_challenge_1(driver)

            if len(pts) == 3:
                # Lvl 2 Account Code
                mobile_complete = (pts[2] == 0)
                tries = 0
                while (not (pc_complete and edge_complete and mobile_complete)) and (tries < 3):
                    pc_complete = (pts[0] == 0)
                    edge_complete = (pts[1] == 0)
                    mobile_complete = (pts[2] == 0)
                    if not (pc_complete and edge_complete):
                        random_searches(driver, ((pts[0]+pts[1])/5)+1)
                    if not mobile_complete:
                        mobilePts(headless_mode, (pts[2]/5)+1, logins[i])
                    pts = check_num_pts(driver, blindmode)
                    print("Remaining Pts: [desktop, edge, mobile]: ", pts)
                    tries += 1
                driver.quit()
            else:
                # Lvl 1 Acct code
                tries = 0
                while (not (pc_complete and edge_complete)) and (tries < 3):
                    pc_complete = (pts[0] == 0)
                    edge_complete = (pts[1] == 0)
                    random_searches(driver, ((pts[0]+pts[1])/5)+1)
                    pts = check_num_pts(driver, blindmode)
                    print("Remaining Pts: [desktop, edge, mobile]: ", pts)
                    tries += 1
                driver.quit()

            if len(pts) == 3:
                all_acct_pts[i] = [pc_complete, edge_complete, mobile_complete]
            else:
                all_acct_pts[i] = [pc_complete, edge_complete, True]

            exitstatus = True  # Will terminate if true
            for ptsacct in all_acct_pts:
                for attr in ptsacct:
                    if not attr:
                        exitstatus = False

            if exitstatus:
                print("All targets reached... Exiting")
                exit()


try:
    main()
except Exception as e:
    print(e)
    from plyer import notification
    notification.notify(title="ERROR", message="Jupiter-Asteroid: Check Logs",
                        app_icon=os.path.join(current_path, "notification.ico"))
    time.sleep(3)
    notification.notify(title="ERROR", message=str(e[0:254]),
                        app_icon=os.path.join(current_path, "notification.ico"))
    # WARNING: LOGS NOT IMPLEMENTED YET
