from selenium.webdriver.common.by import By

from SSLScan_UI.common.yaml_utils import YamlUtils


def find_element(driver, key_super, key):
    return driver.find_element(by=By.XPATH, value=YamlUtils().get_xpath_data(key_super, key))


def find_element_n(driver, key_super, key, n):
    return driver.find_element(by=By.XPATH, value=YamlUtils().get_xpath_data(key_super, key).replace('{n}', str(n)))


def find_element_nm(driver, key_super, key, n, m):
    return driver.find_element(by=By.XPATH,
                               value=YamlUtils().get_xpath_data(key_super, key).replace('{n}', str(n)).replace('{m}',
                                                                                                               str(m)))
