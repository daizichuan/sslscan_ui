import time

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class DriverManager:
    def __init__(self):
        self.options = Options()
        # 不加载图片
        # self.options.add_argument('blink-settings=imagesEnabled=false')
        # 无头某事，不显示浏览器
        self.options.add_argument('--headless')
        # 最大化窗口
        self.options.add_argument('--start-maximized')
        # 解决linux环境报错
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        # 加载策略
        '''
        normal：等待整个页面加载完毕再开始执行操作
        eager：等待整个dom树加载完成，即DOMContentLoaded这个事件完成，也就是只要 HTML 完全加载和解析完毕就开始执行操作。放弃等待图片、样式、子帧的加载。
        none：等待html下载完成，哪怕还没开始解析就开始执行操作。
        '''
        self.options.page_load_strategy = 'none'

    def chrome_driver(self):
        # 加快加载设置
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        return driver

    def driver_manager(self, driver, url):
        driver.get(url)
        # 隐式等待，窗口最大化和两个加载超时配置
        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.set_page_load_timeout(5)
        driver.set_script_timeout(5)
        return driver


if __name__ == '__main__':
    pass
