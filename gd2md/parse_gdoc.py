from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import subprocess
import time
import requests
import json
import re
import lxml
import bs4
import glob, os, os.path
import sys

text_cache = None
vp = False

download_dir = os.path.expanduser('~') + "/Downloads"

def verbose_print(text, dedupe=True):
    global vp, text_cache

    if vp and (text_cache != text or dedupe == False):
        text_cache = text
        print(text)
        return True

    return False

def clean_downloads():
    return True
    global download_dir
    
    verbose_print("Cleaning up old png files in download dir: %s" % download_dir)
    filelist = glob.glob(os.path.join(download_dir, "*.png"))
    for f in filelist:
        os.remove(f)

def scrollDown(browser, numberOfScrollDowns):
 body = browser.find_element_by_css_selector('body')
 body.click()
 while numberOfScrollDowns >=0:
    body.send_keys(Keys.PAGE_DOWN)
    numberOfScrollDowns -= 1
 return browser

def get_url(site, text):
    root = bs4.BeautifulSoup(site.page_source, features="lxml")
    for link in root.findAll('image', attrs={'xlink:href': re.compile("^https://")}):
        url = link.get('xlink:href')
        if text in url:
            return url
    return None

def populateids(site):
    global download_dir
    url_map = {}
    file_map ={}
    scripts = site.find_elements_by_xpath("//script[contains(text(), 'kix.')]")

    for script in scripts:
        script_source = script.get_attribute('innerHTML')
        script_source = clean_modelChunk(script_source)
        modelChunk = json.loads(script_source)

        for a in modelChunk:
            if 'ty' in a:
                if 'et' in a:
                    if 'id' in a:
                        if 'epm' in a:
                            if 'ee_eo' in a['epm']:
                                if 'd_id' in a['epm']['ee_eo']:
                                    if a['ty'] == 'ae' and a['et'] == 'inline':
                                        id = a['id']
                                        key = a['epm']['ee_eo']['d_id']
                                        url_map[id] = get_url(site, key)
                                        file_map[id] = download_dir + "/" + key + ".png"

    return url_map, file_map 

def get_pwd(pwdfile):
    with open(pwdfile) as f:
        s = " ".join([x.strip() for x in f])
    return s

def clean_modelChunk(text):
    text = text[text.find('['):]
    head, sep, tail = text.partition('];')
    return head + ']'

def parseDocument(url, username, pwdfile, download_path, headless, v_p):
    global vp
    vp = v_p

    #Initialize Selenium
    verbose_print("Initializing Selenium Driver...")

    chrome_options = Options()
    #hrome_options.add_argument("download.default_directory=/tmp")
    chrome_options.add_argument("--verbose")
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")



    site = webdriver.Chrome(options=chrome_options)


    command_result = site.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
    command_result = site.execute("send_command", params)

    verbose_print("Initialization done.")

    verbose_print("Browsing to URL: %s" % url)


    site.get(url)
    time.sleep(5)

    verbose_print("Got to site...")

    #Username/Email
    if headless:
        verbose_print("Working in HEADLESS mode...")
    else:
        verbose_print("Working in HEADFUL mode...")

    fld1=site.find_elements_by_xpath("//input[@type='email' and @id='Email']")
    fld2=site.find_elements_by_xpath("//input[@type='email' and @id='identifierId']")
    if len(fld1) > 0:
        fld = fld1[0]
    elif len(fld2) > 0:
        fld = fld2[0]
    else:
        print("Error: Could not locate username field, exiting...", file=sys.stderr)

    subm1=site.find_elements_by_xpath("//input[@type='submit' and @id='next' and @name='signIn' ]")
    subm2=site.find_elements_by_xpath("//div[@role='button' and @id='identifierNext']")
    if len(subm1) > 0:
        subm = subm1[0]
    elif len(subm2) > 0:
        subm = subm2[0]
    else:
        print("Error: Could not locate username submit button, exiting...", file=sys.stderr)

    fld.send_keys(username)

    verbose_print("Attempting to Login...")

    if headless and vp:
        verbose_print("Taking screenshot of Login page...")
        site.save_screenshot(download_path + "/Username_Prompt.png")

    time.sleep(2)
    subm.click()
    time.sleep(5)

    html_return = site.page_source
    site.save_screenshot(download_path + "/Password_Prompt.png")

    #Password
    fld1=site.find_elements_by_xpath("//input[@type='password' and @id='password']")
    fld2=site.find_elements_by_xpath("//input[@type='password' and @name='password']")
    if len(fld1) > 0:
        fld = fld1[0]
    elif len(fld2) > 0:
        fld = fld2[0]
    else:
        print("Error: Could not locate password field, exiting...", file=sys.stderr)

    subm1=site.find_elements_by_xpath("//input[@type='submit' and @id='submit']")
    subm2=site.find_elements_by_xpath("//div[@role='button' and @id='passwordNext']")
    if len(subm1) > 0:
        subm = subm1[0]
    elif len(subm2) > 0:
        subm = subm2[0]
    else:
        print("Error: Could not locate password submit button, exiting...", file=sys.stderr)

    pwd = get_pwd(pwdfile)
    fld.send_keys(pwd)
    if headless and vp:
        verbose_print("Taking screenshot of Password page...")
        site.save_screenshot(download_path + "/Password_Prompt.png")


    time.sleep(2)
    subm.click()
    time.sleep(20)

    #Check for Wrong Password
    password_request = site.find_elements_by_xpath("//span[@jsslot and contains(text(), 'Wrong password.')]")
    if password_request:
        print("Wrong password for user: %s  exiting..." % username, file=sys.stderr)
        if headless and vp:
            site.save_screenshot(download_path + "/Wrong_Password_Page.png")
        sys.exit(1)

    #Check for Access Request
    request = site.find_elements_by_xpath("//button[@id='request-access-button']")
    if request:
        print("Looks like user: %s do not have access to this doc, exiting..." % username, file=sys.stderr)
        if headless and vp:
            site.save_screenshot(download_path + "/Reqest_Access_Page.png")
        sys.exit(1)

    verbose_print("Succesful login...")


    if headless and vp:
        verbose_print("Taking screenshot of document page...")
        site.save_screenshot(download_path + "/Document_Loaded.png")

    verbose_print("Scrolling down the doc and wait 20 sec...")
    #Make sure we get to end of doc...
    site = scrollDown(site, 500)
    time.sleep(20)

     #Get a dic with key(Tag) value pair (URL)
    verbose_print("Scanning document for drawing images...")
    urls_map, files_map = populateids(site)
    verbose_print("Scanning Done...")


    #Clean ~/Download dir
    clean_downloads()

    #Download the files
    verbose_print("Downloading files...")
    for key, value in urls_map.items():
        site.get(value)
        time.sleep(1)
    verbose_print("Downloading done...")

    verbose_print("Closing selenium driver...")
    site.quit()

    return files_map, urls_map
