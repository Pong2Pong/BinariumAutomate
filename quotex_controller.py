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
    def __init__(self):
        self.service = Service(executable_path=ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=self.service)

        self.driver.maximize_window()

        self.logins = configparser.ConfigParser()
        self.logins.read("logins.ini", encoding="utf-8")
        self.login(self.logins["account_1"]["login"], self.logins["account_1"]["password"])
        self.choose_training_cash()

    def exit(self):
        print("Выхожу из приложения")
        self.driver.quit()

    def login(self, email, password):
        self.driver.get("https://broker-qx.com/ru/sign-in/modal/")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/form/div[1]/label/input"))
            )
        except:
            print("Не могу найти поле для ввода логина ")
            self.exit()
        else:
            element.send_keys(email)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/form/div[2]/label/input"))
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
