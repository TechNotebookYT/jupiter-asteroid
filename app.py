from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
import argparse

# Useragents to spoof browser
desktop_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 Safari/537.36 Edg/92.0.874.0"
mobile_useragent = "Mozilla/5.0 (Linux; Android 11; SM-N986B) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/88.0.4324.152 Mobile Safari/537.36" # Galaxy Note 20 Ultra

# File path for the chromedriver
chrome_path = r'/usr/local/bin/chromedriver'

# Vars
logins = []
firstName = ''
lastName = ''

# Argparse Specific - takes input on whether account is lvl 1 or 2
parser = argparse.ArgumentParser()
parser.add_argument("first_name")
parser.add_argument("last_name")
args = parser.parse_args()

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
    opts.add_argument(f"user-agent={useragent}")
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
    return (firstName in bodyTag.text) or (lastName in bodyTag.text)


# Checks the num of points earned on the present day
def check_num_pts(check_driver):
    pcsearch = False
    mobilesearch = False
    edgesearch = False

    rewards_btn = check_driver.find_element_by_xpath(
        r'//*[@id="navs"]/div/div/div/div/div[4]/a')
    rewards_btn.click()
    time.sleep(5)
    check_driver.get("https://rewards.microsoft.com/pointsbreakdown")
    check_driver.switch_to.window(check_driver.window_handles[0])
    time.sleep(5)   
    points = []
    
    lvl2Field = 'Mobile search' #This is only present if the account is at level 2

    bodyTag = check_driver.find_element_by_tag_name("body") # Returns everything in the body tag
    
    # Checks if the account is at level 2 status and sets the lvl2 boolean accordingly
    if lvl2Field in bodyTag.text:
        lvl2 = True
        print("LVL2")
    else:
        lvl2 = False
        print("LVL1")


    if lvl2:
        # PC Pts
        pc_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_pcsearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text
        
        max_pcsearch = (max_pcsearch[int(max_pcsearch.index('/'))+2:])
        pcsearch = (int(pc_search_pts) == int(max_pcsearch))
        
        # Edge Pts
        edge_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_edgesearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text
        
        max_edgesearch = (max_edgesearch[int(max_edgesearch.index('/'))+2:])
        edgesearch = (int(edge_search_pts) == int(max_edgesearch))

        # Mobile Pts
        mobile_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_mobilesearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text
        
        max_mobilesearch = (max_mobilesearch[int(max_mobilesearch.index('/'))+2:])
        mobilesearch = (int(mobile_search_pts) == int(max_mobilesearch))


        # Adds the point data to the list
        points.append([pcsearch, mobilesearch, edgesearch])
        points.append([int(pc_search_pts), int(mobile_search_pts), int(edge_search_pts)])
        points.append([int(max_pcsearch), int(
            max_mobilesearch), int(max_edgesearch)])
    else:
        # PC Pts
        pc_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_pcsearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text

        max_pcsearch = (max_pcsearch[int(max_pcsearch.index('/'))+2:])
        pcsearch = (pc_search_pts == max_pcsearch)

        # Edge Pts
        edge_search_pts = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]/b').text
        max_edgesearch = check_driver.find_element_by_xpath(
            '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[3]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text
        
        max_edgesearch = (max_edgesearch[int(max_edgesearch.index('/'))+2:])
        edgesearch = (edge_search_pts == max_edgesearch)

        # Adds the point data to the list
        points.append([pcsearch, edgesearch])
        points.append([int(pc_search_pts), int(edge_search_pts)])
        points.append([int(max_pcsearch), int(max_edgesearch)])
    
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
        num1 = random.randint(1, 5001030)
        num2 = random.randint(1, 500900)
        return f"{num1}{random.choice(['*', '-', '^'])}{num2}"

    for i in range(int(num)):
        stringtosearch = random.choice([coordinate_generator(), numbergen()])
        driver_search.get(f'https://www.bing.com/search?q={stringtosearch}')
        print(str(int((i+1)/num*100))+"%")
        time.sleep(2)

def main():
    firstName = args.first_name
    lastName = args.last_name
    for i in range(len(logins)):
        driver = create_driver(False, False)
        login(driver, logins[i])
        pts = check_num_pts(driver)
        print(pts)
        while not ((pts[0][0] or pts[0][1]) or (pts[0][2])):
            if not pts[0][0] and not pts[0][1]:
                random_searches(driver, (pts[1][0]+pts[1][1])/5)
            if not pts[0][2]:
                driver_mobile = create_driver(True, False)
                login(driver_mobile, logins[i])
                random_searches(driver_mobile, (pts[1][0]+pts[1][1])/5)
                driver_mobile.quit()
            pts = check_num_pts(driver)
        driver.quit()
        

main()
