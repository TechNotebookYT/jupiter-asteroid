# USE THIS FOR PTS: https://www.bing.com/rewardsapp/bepflyoutpage?style=chromeextension
# https://github.com/blackluv/Microsoft-Rewards-Bot/blob/master/ms_rewards.py
# ^ Implement line #670
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
import argparse
import os
from random_word import RandomWords

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


# Takes in the platform and whether or not it will be headless to create a webdriver
def create_driver(mobile, headless):
    # print('Mobile: ', mobile, 'headless: ', headless) ## Debug Code
    # Selects the Correct User Agent
    if mobile:
        useragent = random.choice(mobile_useragents) # Picks from 2 different useragents
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
    return webdriver.Chrome(chrome_path, options=opts) # Creates webdriver with options and returns it


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
    msft_acct_check = False # This is the check for the microsoft account page
    bg_acct_check = False # This is the check for the bing account page

    # Checks if name is on the webpage
    check_driver.get('https://account.microsoft.com/')
    time.sleep(2)
    account_body = check_driver.find_element_by_tag_name("body").text # All of the text on the webpage
    
    check_driver.get('https://www.bing.com/search?q=when+is+the+sunset')
    search_engine_fullpage = check_driver.page_source.encode('utf-8')

    if (((firstName in account_body) or (lastName in account_body))):
        msft_acct_check = True
    
    signin_tries = 0
    while(bg_acct_check==False and signin_tries <= 3):
        if ((firstName in str(search_engine_fullpage)) or (lastName in str(search_engine_fullpage))):
            bg_acct_check = True
        else:
            signin_tries += 1
            check_driver.find_element_by_xpath('//*[@id="id_a"]').click()
            time.sleep(1)
            search_engine_fullpage = check_driver.page_source.encode('utf-8')

    return bg_acct_check and msft_acct_check


# Checks the num of points earned on the present day
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
    check_driver.switch_to.window(check_driver.window_handles[0]) # Switches to first tab
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
        mobilesearch_complete = (int(mobile_search_pts) == int(max_mobilesearch))

        # Adds the point data to the list
        points.append([pcsearch_complete, mobilesearch_complete, edgesearch_complete])
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

    check_driver.get(
        "https://www.bing.com/rewardsapp/bepflyoutpage?style=chromeextension")

    # Gets number of points remaining for each category
    pc_search_pts_remaining = check_driver.find_element_by_xpath(
        '//*[@id="modern-flyout"]/div/div[5]/div/div/div[1]/div/div/text()').text
    pc_search_pts_remaining = int(pc_search_pts_remaining[4:]) - int(pc_search_pts_remaining[:3])

    edge_search_pts_remaining = check_driver.find_element_by_xpath(
        '//*[@id="modern-flyout"]/div/div[5]/div/div/div[2]/div/div/text()').text
    edge_search_pts_remaining = int(edge_search_pts_remaining[4:]) - int(edge_search_pts_remaining[:3])

    mobile_search_pts_remaining = check_driver.find_element_by_xpath(
        '//*[@id="modern-flyout"]/div/div[5]/div/div/div[3]/div/div/text()').text
    mobile_search_pts_remaining = int(mobile_search_pts_remaining[4:]) - int(mobile_search_pts_remaining[:3])

    points.append(pc_search_pts_remaining, mobile_search_pts_remaining, edge_search_pts_remaining)

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
        cardinallr = ['E', 'W']
        cardinaltd = ['N', 'S']
        num1 = random.randint(1, 75)
        num2 = random.randint(1, 75)

        direction1 = random.choice(cardinallr)
        direction2 = random.choice(cardinaltd)
        return (f'{num1}° {direction1}, {num2}° {direction2}' +
                f" {random.choice(['coord', 'coordinate', 'map', 'zip code'])}")

    # Creates random equations
    def numbergen():
        num1 = random.randint(1, 99999)
        num2 = random.randint(1, 9999)
        return f"{num1}{random.choice(['*', '-', '^'])}{num2}"

    r = RandomWords().get_random_words() # Random word list
    def randomWordDefinition():
        # Example search: exemptions define5
        return(random.choice(r) + random.choice([" def", " define", " definition"] + random.randint(0, 9)))

    for i in range(int(num)):
        stringtosearch = random.choice([coordinate_generator(), numbergen(), randomWordDefinition()])
        driver_search.get(f'https://www.bing.com/search?q={stringtosearch}')
        print(str(int((i+1)/num*100))+"%")
        time.sleep(random.randint(1, 4))


def mobilePts(headless, ptsRemaining, userpass):
    driver_mobile = create_driver(True, headless) # Creates mobile driver
    login(driver_mobile, userpass) # Logs in on mobile driver
    random_searches(driver_mobile, ptsRemaining) # Starts random searches
    driver_mobile.quit() # Closes the mobile driver


def main():
    # Imports first and last name from argparse
    firstName = args.first_name
    lastName = args.last_name

    # firstName = 'Pranav'
    # lastName = 'Bala'

    for i in range(len(logins)):
        driver = create_driver(False, False) # Creates the desktop driver
        login(driver, logins[i]) # Logs in on desktop driver
        pts = check_num_pts(driver) # Checks the number of points and adds it to pts list
        print(pts) # Prints out the pts list

        if len(pts[0]) == 3:
            tries = 0
            while not (pts[0][0] and pts[0][1] and pts[0][2]):
                if not (pts[0][0] and pts[0][2]):
                    random_searches(
                        driver, ((pts[2][0]+pts[2][2]) - (pts[1][0]+pts[1][2]))/5+1)

                if not pts[0][1]:
                    mobilePts(False, (pts[2][1] - pts[1][1])/5, logins[i])
                
                pts = check_num_pts(driver)
                print(pts)

                tries += 1
                if tries >= 5:
                    print("Try limit reached... Proceeding to next account")
                    break
                elif tries >= 3:
                    print("Waiting 5 Mins...")
                    time.sleep(300) 

        else:
            tries = 0
            while not (pts[0][0] and pts[0][1]):
                random_searches(
                    driver, ((pts[2][0]+pts[2][1]) - (pts[1][0]+pts[1][1]))/5+1)

                pts = check_num_pts(driver)
                print(pts)
                
                tries += 1
                if tries >= 5:
                    print("Try limit reached... Proceeding to next account")
                    break
                elif tries >= 3:
                    print("Waiting 5 Mins...")
                    time.sleep(300)

        driver.quit()


main()
