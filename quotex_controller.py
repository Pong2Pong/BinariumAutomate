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
    ready_for_work = False

    def __init__(self):
        self.service = Service(executable_path=ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=self.service)

        self.driver.maximize_window()

        self.logins = configparser.ConfigParser()
        self.logins.read("logins.ini", encoding="utf-8")

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
                EC.presence_of_element_located((By.CLASS_NAME, "usermenu"))
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
                EC.presence_of_element_located((By.CLASS_NAME, "usermenu"))
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

    def choose_bet_time(self, time):
        # time.sleep(10)
        # self.driver.find_element(By.CLASS_NAME, "input-control__label__switch")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "input-control__label__switch"))
            )
        except:
            print("Не могу найти кнопку выбора времени ставки")
            self.exit()
        else:
            element.click()

        # if time > 0 and time <=5:
        #     try:
        #         element = WebDriverWait(self.driver, 10).until(
        #             EC.presence_of_element_located(
        #                 (By.XPATH, f'//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[5]/div[1]/label/div/div[{time}]'))
        #         )
        #     except:
        #         print("Не могу выбрать время ставки")
        #         self.exit()
        #     else:
        #         element.click()

    def choose_bet_type(self):
        time.sleep(5)
        elem = self.driver.find_element(By.XPATH, "/html/body/div/div/div[1]/main/div[2]/div[1]/div/div[5]/div[1]/label/input")
        elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys('0')
        elem.send_keys('2')



    def select_bet_time(self, bet_time):
        time.sleep(5)
        elem = self.driver.find_element(By.XPATH,
                                        "/html/body/div/div/div[1]/main/div[2]/div[1]/div/div[5]/div[1]/label/input")
        for i in range(10):
            elem.send_keys(Keys.ARROW_LEFT)
        elem.send_keys(0)
        elem.send_keys(bet_time)

    def make_bet(self, direction, time):
        print(f"Я делаю ставку {direction} на {time} мин")
