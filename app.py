# USE THIS FOR PTS: https://www.bing.com/rewardsapp/bepflyoutpage?style=chromeextension
# https://github.com/blackluv/Microsoft-Rewards-Bot/blob/master/ms_rewards.py
# ^ Implement line #670
# TODO - Add comments/add more to json
import datetime
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

# # WINDOWS ONLY - DISPLAY NOTIFICATION FOR TASK SCHEDULER
# from win10toast import ToastNotifier
# toast = ToastNotifier()
# toast.show_toast("Microsoft Rewards Bot", "Point Farming Started",
#                  duration=4, icon_path=r"C:\Users\prana\Documents\jupiter-asteroid-master\notification.ico")

# Options
headless_mode = True

# RandomWords Specific
# r = list(requests.get(
#     "https://random-word-api.herokuapp.com/word?number=50").json()) OLD
r = str(requests.get(
    'https://raw.githubusercontent.com/lorenbrichter/Words/master/Words/en.txt').content).split(r'\n')


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
args = parser.parse_args()

# Imports first and last name from argparse
firstName = args.first_name
lastName = args.last_name

if args.debug: # Checks if debug mode turned on
    headless_mode = False


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

# Takes in the platform and whether or not it will be headless to create a webdriver
def create_driver(mobile, headless):
    print('Mobile: ', mobile, 'headless: ', headless) ## Debug Code
    # Selects the Correct User Agent
    if mobile:
        # Picks from 2 different useragents
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
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=opts)


# Logs in the User using the microsoft dialog
def login(driver_login, acct):
    logged_in = False  # True when successfully logged in

    user, passwd = acct  # Sets Username and Password values from acct list

    while not logged_in:
        print("Attempting Login...")
        driver_login.get('https://login.live.com/')
        time.sleep(3)  # Wait for page to load

        if (len(driver_login.find_elements_by_name('loginfmt')) > 0):
            driver_login.find_element(By.NAME, 'loginfmt').send_keys(user)
            time.sleep(1)  # Delay Between Send Keys and Click
            driver_login.find_element(By.XPATH, 
                '//*[@id="idSIButton9"]').click()  # next button
            time.sleep(2)  # Delay for password screen
            driver_login.find_element_by_name('passwd').send_keys(passwd)
            time.sleep(1)  # Delay Between Send Keys and Click
            driver_login.find_element(By.XPATH, 
                '//*[@id="idSIButton9"]').click()  # sign in button
            time.sleep(3)

        logged_in = login_check_v2(driver_login)
        print("Logged In: ", logged_in)
        # print("User: ", user) ## Debug Code
        # print("Pass: ", passwd) ## Debug Code
    print("Login Successful: ", user)  # Prints Email to the Screen


def login_check(check_driver):
    msft_acct_check = False  # This is the check for the microsoft account page
    bg_acct_check = False  # This is the check for the bing account page

    # Checks if name is on the webpage
    check_driver.get('https://account.microsoft.com/')
    time.sleep(2)
    account_body = check_driver.find_element_by_tag_name(
        "body").text  # All of the text on the webpage

    check_driver.get(url_data['time_search'])
    search_engine_fullpage = check_driver.page_source.encode('utf-8')

    if (((firstName in account_body) or (lastName in account_body))):
        msft_acct_check = True

    signin_tries = 0
    
    while(bg_acct_check == False and signin_tries <= 3):
        if ((firstName in str(search_engine_fullpage)) or (lastName in str(search_engine_fullpage))):
            bg_acct_check = True
        else:
            signin_tries += 1
            if len(check_driver.find_elements(By.XPATH, '//*[@id="id_a"]')) > 0:
                check_driver.find_element(By.XPATH, '//*[@id="id_a"]').click()
            elif len(check_driver.find_elements(By.XPATH, element_data['mobile_bing_hamburger'])) > 0:
                check_driver.find_element(By.XPATH, element_data['mobile_bing_hamburger']).click()
                time.sleep(2)
                if (len(check_driver.find_elements(By.XPATH, element_data['mobile_post_ham_pfp_xpath']))) > 0:
                    check_driver.find_element(By.XPATH, 
                        element_data['mobile_post_ham_pfp_xpath']).click()
                    time.sleep(2)
                    # input()
                    bg_acct_check = True
                    print('hamburger checked')
            time.sleep(1)
            search_engine_fullpage = check_driver.page_source.encode('utf-8')

    return bg_acct_check and msft_acct_check


def login_check_v2(check_driver):
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
    mobile = check_driver.execute_script("return navigator.userAgent") in mobile_useragents

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


# Checks the num of points earned on the present day !**{OLD}**!
def DEPRECATED_check_num_pts(check_driver):
    pcsearch_complete = False
    mobilesearch_complete = False
    edgesearch_complete = False

    check_driver.get('https://account.microsoft.com/')
    time.sleep(3)
    rewards_btn = check_driver.find_element(By.XPATH, 
        r'//*[@id="navs"]/div/div/div/div/div[4]/a')
    rewards_btn.click()
    time.sleep(3)
    check_driver.get("https://rewards.microsoft.com/pointsbreakdown")
    check_driver.switch_to.window(
        check_driver.window_handles[0])  # Switches to first tab
    time.sleep(3)
    points = []

    lvl2Field = 'Mobile search'  # This is only present if the account is at level 2

    bodyTag = check_driver.find_element_by_tag_name(
        "body")  # Returns everything in the body tag

    # Checks if the account is at level 2 status and sets the lvl2 boolean accordingly
    if lvl2Field in bodyTag.text:
        lvl2 = True
        # print("LVL2") ## Debug Code
    else:
        lvl2 = False
        # print("LVL1") ## Debug Code

    if lvl2:
        # PC Pts
        pc_search_pts = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_pcsearch = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_pcsearch = (max_pcsearch[int(max_pcsearch.index('/'))+2:])
        pcsearch_complete = (int(pc_search_pts) == int(max_pcsearch))

        # Edge Pts
        edge_search_pts = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_edgesearch = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_edgesearch = (max_edgesearch[int(max_edgesearch.index('/'))+2:])
        edgesearch_complete = (int(edge_search_pts) == int(max_edgesearch))

        # Mobile Pts
        mobile_search_pts = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_mobilesearch = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_mobilesearch = (
            max_mobilesearch[int(max_mobilesearch.index('/'))+2:])
        mobilesearch_complete = (
            int(mobile_search_pts) == int(max_mobilesearch))

        # Adds the point data to the list
        points.append(
            [pcsearch_complete, mobilesearch_complete, edgesearch_complete])
        points.append([int(pc_search_pts), int(
            mobile_search_pts), int(edge_search_pts)])
        points.append([int(max_pcsearch), int(
            max_mobilesearch), int(max_edgesearch)])
    else:
        # PC Pts
        pc_search_pts = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_pcsearch = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_pcsearch = (max_pcsearch[int(max_pcsearch.index('/'))+2:])
        pcsearch_complete = (pc_search_pts == max_pcsearch)

        # Edge Pts
        edge_search_pts = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_edgesearch = check_driver.find_element(By.XPATH, 
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_edgesearch = (max_edgesearch[int(max_edgesearch.index('/'))+2:])
        edgesearch_complete = (edge_search_pts == max_edgesearch)

        # Adds the point data to the list
        points.append([pcsearch_complete, edgesearch_complete])
        points.append([int(pc_search_pts), int(edge_search_pts)])
        points.append([int(max_pcsearch), int(max_edgesearch)])

    return points


def updated_check_num_pts(check_driver):
    points = []

    check_driver.get(url_data["points_url"])

    time.sleep(3)  # Wait for the page to load

    rewards_fullpage = str(check_driver.page_source.encode('utf-8'))
    rewards_body = check_driver.find_element_by_tag_name(
        "body").text  # All of the text on the webpage

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
    lvlcheck = check_driver.find_elements(By.XPATH, element_data["mobile_search_full_xpath"])
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
        random_word_search += random.choice([" def", " defin", " defition", " definition", " drfine", " meanin"])

        return random_word_search

    def randomCountryStats():
        country_attributes = ['metric or imperial', 'in NATO', 'gdp', 'capital', 'population', 'average income', 'language', 'map', 'continent', 'largest city', 'COVID', 'coronavirus', 'population density', 'news', 'president', 'internet', 'size']

        countries = list(countries_for_language('en'))
        country = countries[random.randint(0, 248)][1]
        return (country + " " + random.choice(country_attributes))

    def randomStockStats():
        stocks = requests.get(url_data['companies_list']).text.split("\n")

        stock_attributes = ['market cap', 'index', 'headquarters', 'stock price', 'share price', 'shares', 'description', 'name', 's&p', 's&p 500', 'china', 'russia', 'ukraine', 'US', 'privacy', 'data collection', 'products', 'jobs', 'software', 'hardware', 'pe ratio', 'dividentds']

        
        stock = stocks[random.randint(0, 500)]
        return (stock + " " + random.choice(stock_attributes))

    for i in range(int(num)):
        stringtosearch = random.choice(
            [coordinate_generator(), numbergen(), randomWordDefinition(), randomCountryStats(), randomStockStats()]) # Each function returns a unique search that
        driver_search.get(f'https://www.bing.com/search?q={stringtosearch}') # Loads search
        print(str(int((i+1)/num*100))+"%") # Prints percentage of searches completed on attempt
        time.sleep(random.randint(1, 7)) # Time between searches

def complete_challenge_1(driver_challenge):
    # Completes the 1st challenge (10 pts)
    driver_challenge.get(url_data['points_url'])
    time.sleep(2.35)
    # CHecks if challenge element is there, if so, it clicks the challenge
    if len(driver_challenge.find_elements(By.XPATH, element_data['daily_challenge_1'])) > 0:
        driver_challenge.find_element(By.XPATH, element_data['daily_challenge_1']).click()


def mobilePts(headless, ptsRemaining, userpass):
    driver_mobile = create_driver(True, headless)  # Creates mobile driver
    login(driver_mobile, userpass)  # Logs in on mobile driver
    random_searches(driver_mobile, ptsRemaining)  # Starts random searches
    driver_mobile.quit()  # Closes the mobile driver


def main():
    # Datetime outputs for program logs
    print(datetime.date.today().strftime("%B %d, %Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))

    for i in range(2): #Runs 2 passes on accts
        for i in range(len(logins)):
            driver = create_driver(False, headless_mode)  # Creates the desktop driver
            login(driver, logins[i])  # Logs in on desktop driver
            # Checks the number of points and adds it to pts list
            pts = updated_check_num_pts(driver)
            print(pts)  # Prints out the pts list

            pc_complete = (pts[0] == 0)
            edge_complete = (pts[1] == 0)
            
            # Complete Daily Challenge
            complete_challenge_1(driver)

            if len(pts) == 3:
                mobile_complete = (pts[2] == 0)
                tries = 0
                while (not(pc_complete and edge_complete and mobile_complete)) and (tries < 3):
                    pc_complete = (pts[0] == 0)
                    edge_complete = (pts[1] == 0)
                    mobile_complete = (pts[2] == 0)
                    if not(pc_complete and edge_complete):
                        random_searches(driver, ((pts[0]+pts[1])/5)+1)
                    if not mobile_complete:
                        mobilePts(headless_mode, (pts[2]/5)+1, logins[i])
                    pts= updated_check_num_pts(driver)
                    print(pts)
                    tries+=1
                driver.quit()
            else:
                tries = 0
                while (not(pc_complete and edge_complete)) and (tries < 3):
                    pc_complete = (pts[0] == 0)
                    edge_complete = (pts[1] == 0)
                    random_searches(driver, ((pts[0]+pts[1])/5)+1)
                    pts = updated_check_num_pts(driver)
                    print(pts)
                    tries += 1
                driver.quit()

main()
