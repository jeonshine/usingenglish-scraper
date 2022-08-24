
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from oauth2client.service_account import ServiceAccountCredentials
import gspread, time

def connect_gspread(file_name):

    scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = 'lxper.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)
    sheets = gc.open(file_name)

    return sheets

def write_gspread(worksheet, index, result):

    last_alphabet = chr(65 + len(result))

    try:
        worksheet.update(f"A{index}:{last_alphabet}{index}", [result])
    except:
        # over 50000 string in one cell ==> error
        # allow one data writing per a sec
        print(f"{index} index got error while gspread writing")

def init_browser(url, version):

    # option for browser
    browser = uc.Chrome(version_main=version, suppress_welcome=True)
    browser.maximize_window()
    browser.implicitly_wait(10)

    # init browser
    browser.get(url)
    time.sleep(2)

    return browser

def get_worksheet(title, rows, cols):

    try:
        return SHEETS.worksheet(title)
    except:
        return SHEETS.add_worksheet(title=title, rows=rows, cols=cols)

if  __name__  ==  "__main__" :
    # chorme version
    CHROME_VERSION = 103

    # google sperad 
    GSPREAD = "usingenglish"

    # spreadsheet header
    HEADER = ["phrasal verb" , "phrasal verb", "meaning", "example", "seperable"]
    SHEETS = connect_gspread(GSPREAD)

    # a ~ z loop 
    for seq in range(1, 26):

        # 0 >>> a, 26 >>> z 
        starting_letter = chr(65 + seq).lower()

        url = f"https://www.usingenglish.com/reference/phrasal-verbs/{starting_letter}.html"

        worksheet = get_worksheet(starting_letter, 1000, 10)

        write_gspread(worksheet, 1, HEADER)

        browser = init_browser(url, CHROME_VERSION)

        phrasal_verbs = browser.find_elements(By.XPATH, '//div[@id="main_content_body"]//ul[@class="list-inline"]//a')
        phrasal_verb_links = [phrasal_verb.get_attribute("href") for phrasal_verb in phrasal_verbs]
        phrasal_verb_texts = [phrasal_verb.text for phrasal_verb in phrasal_verbs]

        time.sleep(1)

        # phrasal verb links loop
        count = 1
        for phrasal_verb_link, phrasal_verb_text in zip(phrasal_verb_links, phrasal_verb_texts):

            browser.get(phrasal_verb_link)

            time.sleep(1)

            try:
                page_not_found = browser.find_element(By.XPATH, '//h1[contains(text(), "Page Not Found")]')
                
                if page_not_found: write_gspread(worksheet,  count + 1, [phrasal_verb_text])

                count += 1

            except:

                phrasal_verb_cards = browser.find_elements(By.XPATH, '//dl//div[@class="card mb-3"]')

                # phrasal verb cards loop
                for index_b, phrasal_verb_card in enumerate(phrasal_verb_cards):

                    result = []
                    
                    try:
                        phrasal_verb = phrasal_verb_card.find_element(By.XPATH, '//dt').text
                    except:
                        phrasal_verb = ""

                    try:
                        meaning = phrasal_verb_card.find_elements(By.XPATH, './dd//p[@class="ms-5"]')[0].text
                    except:
                        meaning = ""

                    try:    
                        example = phrasal_verb_card.find_elements(By.XPATH, './dd//p[@class="ms-5"]')[1].text
                    except:
                        example = ""

                    try:
                        seperable = phrasal_verb_card.find_element(By.XPATH, './dd//ul//li').text
                    except:
                        seperable = ""

                    result.extend([phrasal_verb_text, phrasal_verb, meaning, example, seperable])
                    
                    write_gspread(worksheet,  count + index_b + 1, result)

                    time.sleep(1)

                count += len(phrasal_verb_cards)

        browser.quit()

    print("debug")