import time
import configparser
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


class QuotexAutomate:
    bet_failed = False
    QA = []

    def __init__(self):
        self.QA.append(self)
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.logins = configparser.ConfigParser()
        self.logins.read("logins.ini", encoding="utf-8")
        self.login(self.logins["account_1"]["login"], self.logins["account_1"]["password"])
        self.choose_training_cash()

    def exit(self):
        print("Выхожу из приложения")
        # self.driver.quit()

    def login(self, email, password):
        self.driver.get("https://market-quotex.net/ru/sign-up/modal")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[1]/nav/a[1]"))
            )
        except:
            print("Не могу найти кнопку выбора входа")
            self.exit()
        else:
            element.click()
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
        except:
            print("Не могу найти поле для ввода логина ")
            self.exit()
        else:
            element.send_keys(email)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
        except:
            print("Не могу найти поле для ввода пароля ")
            self.exit()
        else:
            element.send_keys(password)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/form/div[4]/button"))
            )
        except:
            print("Не могу найти кнопку входа")
            self.exit()
        else:
            element.click()

    def choose_training_cash(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "usermenu__info"))
            )
        except:
            print("Не могу найти кнопку выбора счета")
            self.exit()
        else:
            element.click()
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Демо счет"))
            )
        except:
            print("Не могу найти кнопку демо счета")
            self.exit()
        else:
            element.click()

    def choose_real_cash(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "usermenu__info"))
            )
        except:
            print("Не могу найти кнопку выбора счета")
            self.exit()
        else:
            element.click()
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Реальный счет"))
            )
        except:
            print("Не могу найти кнопку реального счета")
            self.exit()
        else:
            element.click()

    def choose_bet_time(self, bet_time):
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[1]/main/div[2]/div[1]/div/div[5]/div[1]/label/input")))
        for i in range(8):
            elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(0)
        elem.send_keys(0)
        elem.send_keys(0)
        elem.send_keys(bet_time)

    def choose_currency(self, currency_to_select):
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/div[1]/main/div[1]/div/div[2]/div[1]/div[1]/button')))
        elem.click()
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/div[1]/main/div[1]/div/div[2]/div[1]/div[1]/div/div/div/div[1]/input')))
        elem.send_keys(currency_to_select)
        try:
            elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/div[1]/main/div[1]/div/div[2]/div[1]/div[1]/div/div/div/div[2]/div/div/div[2]/div[1]')))
            elem.click()
            # print(f"    Выбрана валютная пара {currency_to_select}")
        except:
            print("Не могу найти валютную пару, ставка не сделана ", currency_to_select)
            self.bet_failed = True

    def make_bet(self, direction, bet_time, currency):
        self.choose_bet_time(bet_time)
        self.choose_currency(currency)
        if self.bet_failed:
            self.bet_failed = False
            return
        if direction == 'вверх':
            elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[6]/div[1]/button')))
            elem.click()

        if direction == 'вниз':
            elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[6]/div[5]/button')))
            elem.click()
        print("        Ставка сделана")

    def get_currency_open_close(self):
        time.sleep(3)
        elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/div[1]/main/div[2]/div[2]/div[2]/div[2]')))
        elem.click()
        time.sleep(1)
        open_currency = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/div[1]/main/div[2]/div[2]/div[2]/div[2]/ul/li[3]/div[2]')))
        time.sleep(1)
        close_currency = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/div[1]/main/div[2]/div[2]/div[2]/div[2]/ul/li[4]/div[2]')))
        print(f"Начальная котировка - {open_currency.text}, конечная - {close_currency.text}")

        return open_currency.text, close_currency.text
        # elem = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/main/div[2]/div[2]/div[2]')
        # elem.click()

