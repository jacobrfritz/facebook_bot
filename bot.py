from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import time,re,json,os,logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 

month_lookup = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12
        }

current_month = datetime.now().month
current_day = datetime.now().day
current_hour = datetime.now().hour
current_minute = datetime.now().minute

#selenium options
option = Options()
option.add_argument('--disable-gpu')
option.add_argument("--disable-notifications")
option.add_argument("--headless=new")
service = Service()

driver = webdriver.Chrome(service = service,options=option)
        
#gives you a list of friends that don't have birthday data
def crawl():
    with open('friend_data.json', 'r') as f:
            friends = json.load(f)
    with open('friend_links.json','r') as f:
        links = json.load(f)
    links_with_data = [link['link'] for link in friends]
    no_data_links = [link for link in links if link not in links_with_data]
    links_to_crawl = no_data_links[0:50]
    return links_to_crawl

#text included in facebook post  
def birthday_message(friend):
    return f"""Happy Birthday!"""

#navigates to friends wall and opens post
def birthday_post(friends):
    for friend in friends:
        time.sleep(5)
        driver.get(friend['link'])
        time.sleep(5)
        els = driver.find_elements(By.CSS_SELECTOR,'.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6')
        for el in els:
            if re.search('Write something',el.text):
                el.click()
                time.sleep(5)
                pop_up = driver.find_element(By.CSS_SELECTOR,'.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate')
                message = ''
                message = birthday_message(friend)
                pop_up.send_keys(message)
                time.sleep(3)
                button = driver.find_elements(By.CSS_SELECTOR, '.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft')
                for b in button:
                    if (b.text == 'Post'):
                        driver.execute_script("arguments[0].click();", b)
                        print(f"Message Posted : {message}, name: {friend['name']},link:{friend['link']}")
                        time.sleep(5)
                        break
                break

#checks if friends birthday is in their profile 
def birthday_check():
    about_class_texts = driver.find_elements(By.CSS_SELECTOR, '.x193iq5w.xeuugli.x13faqbe.x1vvkbs.xlh3980.xvmahel.x1n0sxbx.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x4zkp8e.x3x7a5m.x6prxxf.xvq8zen.xo1l8bm.xzsf02u.x1yc453h')
    for about_class_text in about_class_texts:
        if(about_class_text.text.split(' ')[0] in month_lookup.keys()):
            return about_class_text.text
    return None
        
#checks which friends have birthdays today
def is_birthday():
    with open('friend_data.json') as f:
        friend_data = json.load(f)
    friend_data_is_birthday = []
    for friend in friend_data:
        if(friend['birth_month'] == current_month and friend['birth_day'] == current_day):
            friend['is_birthday'] = True
        else:
            friend['is_birthday'] = False
        friend_data_is_birthday.append(friend)
    json_object = json.dumps(friend_data_is_birthday, indent = 4)
    with open ('friend_data.json', 'w+') as f:
        f.write(json_object)
    return [friend for friend in friend_data_is_birthday if friend['is_birthday'] == True]

#goes to your friends profile, gets birthday data if available
#then saves to json
def get_friend_data(friend_links):
    friend_data_list = []
    for link in friend_links:
        with open('friend_data.json','r') as f:
            friend_data_list =  json.load(f)
        friend_data = {
        "name":str(),
        "birth_month":int(),
        "birth_day": int(),
        "link" :str()
        }
        if (re.search('profile',link)):
            contact_info = link + '&sk=about_contact_and_basic_info'
        else:
            contact_info = link + '/about_contact_and_basic_info'
        driver.get(contact_info)
        time.sleep(5)
        try:
            name_area = driver.find_element(By.CSS_SELECTOR,'.x78zum5.x15sbx0n.x5oxk1f.x1jxijyj.xym1h4x.xuy2c7u.x1ltux0g.xc9uqle')
            name = name_area.find_element(By.CSS_SELECTOR,'.x1heor9g.x1qlqyl8.x1pd3egz.x1a2a7pz').text
            friend_data['name'] = name.split(' ')[0]
        except:
            friend_data['name'] = None
        friend_data['link'] = link
        try:
            driver.find_element(By.XPATH, '//*[contains(text(), "Birth date")]')
            birthday = birthday_check()
            if birthday is not None:
                month, day = birthday.split(' ')
                friend_data['birth_month'] = month_lookup[month]
                friend_data['birth_day'] = int(day)
            else:
                friend_data['birth_month'] = None
                friend_data['birth_day'] = None
        except:
            friend_data['birth_month'] = None
            friend_data['birth_day'] = None
        time.sleep(5) 
        friend_data_list.append(friend_data)
        print(friend_data['name'],friend_data['birth_month'],friend_data['birth_day'])
        json_object = json.dumps(friend_data_list, indent = 4)
        with open ('friend_data.json', 'w') as f:
            f.write(json_object)
    return friend_data_list

#scrolls through friends page to reveal friends dynamically
def scroll():
    last_last_person = None
    this_last_person = None
    while True: 
        people = driver.find_elements(By.CSS_SELECTOR, '.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1lliihq')
        this_last_person= people[-1]
        scroll_origin = ScrollOrigin(this_last_person,0,0)
        ActionChains(driver)\
        .scroll_to_element(this_last_person)\
        .scroll_from_origin(scroll_origin, 0, 200)\
        .perform()
        if(last_last_person == this_last_person):
            return
        last_last_person = this_last_person
        time.sleep(3)
            
#gathers links to all friends profiles
def get_friend_links():
    
    driver.get('https://www.facebook.com/friends/list')
    scroll()
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    friend_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if re.search(r'https://www.facebook.com/.+',href):
            friend_links.append(href)
    json_object = json.dumps(friend_links, indent = 4)
    with open('friend_links.json','w+') as f:
        f.write(json_object)
    
#logs into facebook profile 
def login():
    driver.get('https://facebook.com')
    time.sleep(2)
    driver.find_element(by = 'name',value = 'email').send_keys(os.getenv('login'))
    driver.find_element(by = 'name',value = 'pass').send_keys(os.getenv('password'))
    driver.find_element(by = 'name',value = 'login').click()
    time.sleep(5)

#executes on first run
def new():
    if (os.path.exists('friend_links.json') == False):
        get_friend_links()
    if(os.path.exists('friend_data.json') == False):
        with open('friend_data.json','w+') as f:
           f.write(json.dumps(list())) 
        
        
def main():
    login()
    new()
    #Script runs Daily at 9 am check for birthdays and post, then crawl 
    #50 friend links that havent been crawled
    #needs to be minimized so ZUCK doesn't ban you
    logging.debug(f'daily {datetime.now()}')
    try:
        links_to_crawl = crawl()
        if links_to_crawl is not None:
            get_friend_data(links_to_crawl)
    except Exception as e:
        logging.debug(f'crawl falied {datetime.now()}')
        print(e)
    birthdays = is_birthday()
    birthday_post(birthdays)
    #script will be running daily but this will only execute
    #on mondays
    if(datetime.now().weekday() == 0):
        logging.debug(f'weekly {datetime.now()}')
        
        try:
            get_friend_links()
        except:
            logging.debug(f'get friend links failed {datetime.now()}')
try:
    main()
    print('done')
except Exception as e:
    print(e)




 










