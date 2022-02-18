# USE THIS FOR PTS: https://www.bing.com/rewardsapp/bepflyoutpage?style=chromeextension
# https://github.com/blackluv/Microsoft-Rewards-Bot/blob/master/ms_rewards.py
# ^ Implement line #670
# TODO - Add comments/add more to json
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
import argparse
import os
from random_word import RandomWords
import json

# Useragents to change browser
desktop_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 Safari/537.36 Edg/92.0.874.0"
mobile_useragents = [
    "Mozilla/5.0 (Linux; Android 10; SM-G975U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.93 Mobile Safari/537.36",
]

# File path for the chromedriver
chrome_path = r'/usr/local/bin/chromedriver'

# Vars
logins = []
firstName = ''
lastName = ''
current_path = os.path.dirname(os.path.realpath(__file__))

# Argparse Specific - takes input on first and last name for use in logincheck function
parser = argparse.ArgumentParser()
parser.add_argument("first_name")
parser.add_argument("last_name")
args = parser.parse_args()

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
    return webdriver.Chrome(chrome_path, options=opts)


# Logs in the User using the microsoft dialog
def login(driver_login, acct):
    logged_in = False  # True when successfully logged in

    user, passwd = acct  # Sets Username and Password values from acct list

    while not logged_in:
        print("Attempting Login...")
        driver_login.get('https://login.live.com/')
        time.sleep(3)  # Wait for page to load

        driver_login.find_element_by_name('loginfmt').send_keys(user)
        time.sleep(1)  # Delay Between Send Keys and Click
        driver_login.find_element_by_xpath(
            '//*[@id="idSIButton9"]').click()  # next button
        time.sleep(2)  # Delay for password screen
        driver_login.find_element_by_name('passwd').send_keys(passwd)
        time.sleep(1)  # Delay Between Send Keys and Click
        driver_login.find_element_by_xpath(
            '//*[@id="idSIButton9"]').click()  # sign in button
        time.sleep(3)

        logged_in = login_check(driver_login)
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

    check_driver.get(url_data['sunset_search'])
    search_engine_fullpage = check_driver.page_source.encode('utf-8')

    if (((firstName in account_body) or (lastName in account_body))):
        msft_acct_check = True

    signin_tries = 0
    
    while(bg_acct_check == False and signin_tries <= 3):
        if ((firstName in str(search_engine_fullpage)) or (lastName in str(search_engine_fullpage))):
            bg_acct_check = True
        else:
            signin_tries += 1
            check_driver.find_element_by_xpath('//*[@id="id_a"]').click()
            time.sleep(1)
            search_engine_fullpage = check_driver.page_source.encode('utf-8')

    return bg_acct_check and msft_acct_check


# Checks the num of points earned on the present day {OLD}
def check_num_pts(check_driver):
    pcsearch_complete = False
    mobilesearch_complete = False
    edgesearch_complete = False

    check_driver.get('https://account.microsoft.com/')
    time.sleep(3)
    rewards_btn = check_driver.find_element_by_xpath(
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
        pc_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_pcsearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_pcsearch = (max_pcsearch[int(max_pcsearch.index('/'))+2:])
        pcsearch_complete = (int(pc_search_pts) == int(max_pcsearch))

        # Edge Pts
        edge_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_edgesearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_edgesearch = (max_edgesearch[int(max_edgesearch.index('/'))+2:])
        edgesearch_complete = (int(edge_search_pts) == int(max_edgesearch))

        # Mobile Pts
        mobile_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_mobilesearch = check_driver.find_element_by_xpath(
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
        pc_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_pcsearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_pcsearch = (max_pcsearch[int(max_pcsearch.index('/'))+2:])
        pcsearch_complete = (pc_search_pts == max_pcsearch)

        # Edge Pts
        edge_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_edgesearch = check_driver.find_element_by_xpath(
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
        check_driver.find_element_by_xpath(
            element_data['join_now_btn_xpath']).click()
        # ↓ Done since the join now button takes you to bing.com and not to points pg
        check_driver.get(url_data["points_url"])

    # Checking level2/level1
    lvlcheck = check_driver.find_elements_by_xpath(element_data["mobile_search_full_xpath"])
    lvl2 = len(lvlcheck) > 0

    if lvl2:
        print("level2")
        # Gets number of points remaining for each category
        pc_search_pts_remaining = check_driver.find_element_by_xpath(
            element_data['pc_search_pts_lvl2_xpath']).text
        slash_index = pc_search_pts_remaining.index("/")
        pc_search_pts_remaining = int(
            pc_search_pts_remaining[slash_index+1:]) - int(pc_search_pts_remaining[:slash_index])

        edge_search_pts_remaining = check_driver.find_element_by_xpath(
            element_data['edge_search_pts_lvl2_xpath']).text
        slash_index = edge_search_pts_remaining.index("/")
        edge_search_pts_remaining = int(
            edge_search_pts_remaining[slash_index+1:]) - int(edge_search_pts_remaining[:slash_index])

        mobile_search_pts_remaining = check_driver.find_element_by_xpath(
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
        pc_search_pts_remaining = check_driver.find_element_by_xpath(
            element_data['pc_search_pts_lvl1_xpath']).text
        print(pc_search_pts_remaining)
        slash_index = pc_search_pts_remaining.index("/")
        pc_search_pts_remaining = int(
            pc_search_pts_remaining[slash_index+1:]) - int(pc_search_pts_remaining[11:slash_index])

        edge_search_pts_remaining = check_driver.find_element_by_xpath(
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

    r = RandomWords().get_random_words()  # Random word list
    while not r:
        r = RandomWords().get_random_words()
    
    def randomWordDefinition():
        # Example search: exemptions define5
        random_word_search = str(random.choice(r))
        random_word_search += random.choice([" def", " define", " definitio", "definition", "defin", "meaning"])
        random_word_search += str(random.randint(0, 9))

        return random_word_search

    for i in range(int(num)):
        stringtosearch = random.choice(
            [coordinate_generator(), numbergen(), randomWordDefinition()])
        driver_search.get(f'https://www.bing.com/search?q={stringtosearch}')
        print(str(int((i+1)/num*100))+"%")
        time.sleep(random.randint(2, 5))


def mobilePts(headless, ptsRemaining, userpass):
    driver_mobile = create_driver(True, headless)  # Creates mobile driver
    login(driver_mobile, userpass)  # Logs in on mobile driver
    random_searches(driver_mobile, ptsRemaining)  # Starts random searches
    driver_mobile.quit()  # Closes the mobile driver


def main():
    print(datetime.date.today().strftime("%B %d, %Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))

    # Imports first and last name from argparse
    firstName = args.first_name
    lastName = args.last_name

    # firstName = 'Pranav'
    # lastName = 'Bala'
    for i in range(2): #Runs 2 passes on accts
        for i in range(len(logins)):
            driver = create_driver(False, True)  # Creates the desktop driver
            login(driver, logins[i])  # Logs in on desktop driver
            # Checks the number of points and adds it to pts list
            pts = updated_check_num_pts(driver)
            print(pts)  # Prints out the pts list

            pc_complete = (pts[0] == 0)
            edge_complete = (pts[1] == 0)

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
                        mobilePts(True, (pts[2]/5)+1, logins[i])
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

