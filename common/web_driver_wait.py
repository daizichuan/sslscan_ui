from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from SSLScan_UI.common.yaml_utils import YamlUtils


def wait_util_locator(driver, key_super, key):
    return WebDriverWait(driver, 120, 0.5).until(
        EC.presence_of_all_elements_located((By.XPATH, YamlUtils().get_xpath_data(key_super, key))))


def wait_util_locator_n(driver, key_super, key, n):
    return WebDriverWait(driver, 120, 0.5).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, YamlUtils().get_xpath_data(key_super, key).replace('{n}', str(n)))))


def wait_util_locator_nm(driver, key_super, key, n, m):
    return WebDriverWait(driver, 120, 0.5).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, YamlUtils().get_xpath_data(key_super, key).replace('{n}', str(n)).replace('{m}', str(m)))))
