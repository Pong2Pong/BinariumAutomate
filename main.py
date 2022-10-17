import time
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# import telegram_controller
import quotex_controller


class BinariumAutomate:
    ready_for_work = False

    def __init__(self):
        self.service = Service(executable_path=ChromeDriverManager().install())

        self.browser = webdriver.Chrome(service=self.service)

        self.config = configparser.ConfigParser()
        self.config.read("logins.ini", encoding="utf-8")

    def login(self, email, password):
        self.browser.get("https://binarium.direct/ru")
        time.sleep(2)
        self.browser.find_element(By.XPATH, "/html/body/app-client/div/ng-component/"
                                            "mat-sidenav-container/mat-sidenav-content/"
                                            "div[5]/app-start-sidebar/div/div[1]/div[2]/"
                                            "div/div/div/div/a[1]").click()
        self.browser.find_element(By.ID, "mat-input-3").send_keys(email)
        self.browser.find_element(By.ID, "mat-input-4").send_keys(password)
        self.browser.find_element(By.XPATH, "/html/body/app-client/div/ng-component/mat-sidenav-container/mat-sidenav"
                                            "-content/div[5]/app-start-sidebar/div/div["
                                            "2]/app-auth-form/div/div/form/button").click()

    def make_bet(self, direction, time):
        print(f"Я делаю ставку {direction} на {time} мин")


if __name__ == '__main__':
    # binarium = BinariumAutomate()
    # binarium.login('sergei.khatiushin@yandex.ru', 'S291001s')
    # ready_for_work = True
    # print(f"Готов к работе")
    # telegram_controller.client.run_until_disconnected()
    quotex = quotex_controller.QuotexAutomate()
    quotex.login(quotex.logins["account_1"]["login"], quotex.logins["account_1"]["password"])
    time.sleep(5)
    quotex.select_bet_time(3)
    quotex.select_bet_time(5)


