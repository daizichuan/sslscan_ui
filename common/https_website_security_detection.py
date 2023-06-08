import re
import time

from selenium.common import NoSuchElementException

from SSLScan_UI.common.find_element import find_element, find_element_n, find_element_nm
from SSLScan_UI.common.generate_driver import DriverManager
from SSLScan_UI.common.web_driver_wait import wait_util_locator, wait_util_locator_n
from SSLScan_UI.common.yaml_utils import YamlUtils
from SSLScan_UI.common.log import log


class GetDriver:
    '''
    生成driver
    '''

    def __init__(self, url, driver_type='chrome'):
        self.url = url
        self.driver_type = driver_type
        self.driver = self.get_driver()

    # 默认chrome浏览器，其他浏览器后续添加
    def get_driver(self):
        driver = DriverManager().chrome_driver()
        if 'chrome' == self.driver_type.lower():
            pass
        elif 'ie' == self.driver_type.lower():
            pass
        return DriverManager().driver_manager(driver, self.url)


class Check:
    '''
    首页，输入需要ssl scan的website
    '''

    def __init__(self, driver):
        self.driver = driver

    def website_check(self, website):
        infos = wait_util_locator(self.driver, 'check', 'url_input')
        for _ in infos:
            url_input = find_element(self.driver, 'check', 'url_input')

        # url_input = find_element(self.driver, 'check', 'url_input')
        scan_btn = find_element(self.driver, 'check', 'scan_btn')
        log.info(website)
        if str(website).lower() != 'nan':
            url_input.send_keys(website)
        scan_btn.click()


class WebsiteAbstract:
    '''
    结果 简介部分
    '''

    def __init__(self, driver):
        self.website_abstract_detail_dict = {}
        self.driver = driver

    def get_website_abstract_o(self):
        dict_tmp = {}

        dict_tmp['website_main'] = find_element(self.driver, 'website_detail',
                                                'website_main').text

        for key in ['website_title', 'ip_port', 'server', 'check_datetime', 'time_consuming']:
            self._get_kv(key, dict_tmp)
        # log.info(self.website_abstract_detail_dict)

        self.website_abstract_detail_dict['abstract'] = dict_tmp
        return self.website_abstract_detail_dict

    def _get_kv(self, key, dict_tmp):
        kv = find_element(self.driver, 'website_detail', key).text
        k, v = re.split("[: ：]", kv, 1)
        # 这里取出的数据，多了 “服务器”，所以这里去掉
        dict_tmp[k.strip()] = v.strip().split('服务器：')[0].split('耗时信息')[0].split('(毫秒)')[0]

    def get_website_abstract(self):
        dict_tmp = {}
        # 默认20s加载完成
        for i in range(101):
            print("\r{:3}%".format(i), end=' ')
            time.sleep(0.5)
        infos = wait_util_locator(self.driver, 'website_detail', 'time_consuming')
        for i, v in enumerate(infos):
            kv = find_element(self.driver, 'website_detail', 'time_consuming').text
        k, v = re.split("[: ：]", kv, 1)
        dict_tmp[k.strip()] = v.strip().split('耗时信息')[0].split('(毫秒)')[0]
        ip_port = find_element(self.driver, 'website_detail', 'ip_port').text
        dict_tmp.update({'ip_port': ip_port, 'ip': ip_port.split(':')[0], 'port': ip_port.split(':')[1]})
        dict_tmp['检测时间'] = \
            find_element(self.driver, 'website_detail', 'check_datetime').text.split('检测时间：')[1].split(' 耗时信息')[
                0]
        self.website_abstract_detail_dict['abstract'] = dict_tmp
        return self.website_abstract_detail_dict

    # 把其他方法拼接装载，直接WebsiteAbstract(driver).()调用
    def __call__(self, *args, **kwargs):
        return self.get_website_abstract()


class SignatureInfo:
    '''
    证书信息
    '''

    def __init__(self, driver):
        self.algo_kind_dict = {}
        self.signature_certinfo_dict = {}
        self.signature_certinfo_details_dict = {}
        self.driver = driver

    def get_algo_kind(self):
        '''
        证书信息页面
        '''
        dict_tmp = {}

        dict_tmp['algo_name'] = find_element(self.driver, 'algo_kind', 'algo_name').text

        # 查看备用名称是否没有显示全，存”查看全部“链接
        try:
            check_all = find_element(self.driver, 'algo_kind', 'algo_kind_all')
            if check_all:
                check_all.click()
        except Exception:
            pass

        # 多对kv
        infos = wait_util_locator(self.driver, 'algo_kind', 'infos')
        for i, v in enumerate(infos):
            n = i + 1
            key = find_element_n(self.driver, 'algo_kind', 'info_key', n).text
            value = find_element_n(self.driver, 'algo_kind', 'info_value', n).text

            dict_tmp[key] = value.replace('\n', ', ')

        # 信任状态颜色
        try:
            if find_element(self.driver, 'algo_kind', 'trust_color'):
                dict_tmp['信任状态颜色'] = '红色'
        except Exception:
            dict_tmp['信任状态颜色'] = '不是吊销状态，字体颜色不是红色'

        self.algo_kind_dict['algo_kind'] = dict_tmp

        # log.info(self.algo_kind_dict)
        return self.algo_kind_dict

    def get_signature_certinfo(self):
        '''
        证书链信息
        '''
        infos = wait_util_locator(self.driver, 'signature_certinfo', 'infos')
        site_certificate_dict = {'site_png_num': 0}
        ca_certificate_lst = [{'ca_png_num': 0}]
        root_certificate_dict = {'root_png_num': 0}

        for i, _ in enumerate(infos):
            n = i + 1
            dict_tmp = {}
            infos_detail = wait_util_locator_n(self.driver, 'signature_certinfo', 'infos_detail', n)
            for j, _ in enumerate(infos_detail):
                m = j + 1
                key = find_element_nm(self.driver, 'signature_certinfo', 'info_key', n, m).text
                value = find_element_nm(self.driver, 'signature_certinfo', 'info_value', n, m).text
                dict_tmp[key] = value

            # 判断得到的是证书链里面的什么证书
            # 排一个是站点证书
            if i == 0:
                site_certificate_dict.update(dict_tmp)
                if find_element(self.driver, 'signature_certinfo', 'site_png'):
                    site_certificate_dict['site_png_num'] += 1
            elif i >= 1 and dict_tmp['颁发给'] != dict_tmp['颁发者']:
                ca_certificate_lst.append(dict_tmp)
                if find_element(self.driver, 'signature_certinfo', 'ca_png'):
                    for _ in ca_certificate_lst:
                        if 'ca_png_num' in _:
                            _['ca_png_num'] += 1
            elif i >= 1 and dict_tmp['颁发给'] == dict_tmp['颁发者']:
                root_certificate_dict.update(dict_tmp)
                if find_element(self.driver, 'signature_certinfo', 'root_png'):
                    root_certificate_dict['root_png_num'] += 1

        self.signature_certinfo_dict['site_certificate'] = site_certificate_dict
        self.signature_certinfo_dict['ca_certificate'] = ca_certificate_lst
        self.signature_certinfo_dict['root_certificate'] = root_certificate_dict

        # log.info(self.signature_certinfo_dict)
        return self.signature_certinfo_dict

    def get_signature_certinfo_details(self):
        '''
        证书信息 - 详细信息
        '''
        find_element(self.driver, 'signature_certinfo_details', 'click_locator').click()

        # 需要切换窗口到新生成的窗口
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

        dict_tmp = {}
        # 主题信息、签发者信息和证书信息
        for xpath_info in ['theme_infos', 'issuer_infos', 'certificate_infos']:
            infos = wait_util_locator(self.driver, 'signature_certinfo_details', xpath_info)
            dict_tmp[xpath_info] = self._get_kv(infos, xpath_info)

        self.signature_certinfo_details_dict.update(dict_tmp)

        # 切换回初始窗口，这里窗口只有两个，所以下标直接写0，且两个title名称一样
        self.driver.switch_to.window(windows[0])

        # log.info(self.signature_certinfo_details_dict)
        return self.signature_certinfo_details_dict

    def _get_kv(self, locators, xpath_info):
        '''
        详细信息获取kv子方法
        '''
        dict_tmp = {}
        for i, _ in enumerate(locators):
            n = i + 1
            key = find_element_nm(self.driver, 'signature_certinfo_details', f'{xpath_info}_kv', n, 1).text.replace(" ",
                                                                                                                    "")
            value = find_element_nm(self.driver, 'signature_certinfo_details', f'{xpath_info}_kv', n, 2).text.replace(
                " ", "")
            dict_tmp[key] = value
        return dict_tmp

    def __call__(self, *args, **kwargs):
        dict = {}
        lst = []
        lst.append(self.get_algo_kind())
        lst.append(self.get_signature_certinfo())
        # lst.append(self.get_signature_certinfo_details())
        dict['signature-info'] = lst
        return dict


class ProtocolSuite:
    '''
    协议与套件
    '''

    def __init__(self, driver):
        self.protocol_dict = {}
        self.encryption_suite_dict = {}
        self.elliptic_curve_dict = {}
        self.link_signature_algorithm_dict = {}
        self.driver = driver

    def get_protocol(self):
        '''
        协议
        '''
        dict_tmp = {'SSL3_color': ''}
        infos = wait_util_locator(self.driver, 'protocol', 'infos')
        for i, _ in enumerate(infos):
            n = i + 1
            key = find_element_n(self.driver, 'protocol', 'protocol_name', n).text
            value = find_element_n(self.driver, 'protocol', 'support_or_not', n).text

            # 数据中有换行，替换\n
            dict_tmp[key] = value.replace('\n', ', ')

            # 获取SSL3 为支持时的文字颜色
            if 'SSL 3' in key and find_element_n(self.driver, 'protocol', 'protocol_name', n):
                dict_tmp['SSL3_color'] = '红色'

        self.protocol_dict['protocol'] = dict_tmp
        # log.info(self.protocol_dict)
        return self.protocol_dict

    def get_encryption_suite(self, flag='1'):
        '''
        加密套件
        '''
        infos = wait_util_locator(self.driver, 'encryption_suite', 'infos')
        dict_tmp = {'RC4_red_num': 0}
        try:
            for i in range(100):
                n = i + 1
                if n == 1 and flag == '1':
                    continue
                bar = find_element_n(self.driver, 'encryption_suite', 'protocol_names', n).text
                # key = 'test'
                # dict_tmp[key] = []
                if bar:
                    key = bar
                    dict_tmp[key] = []
                value = find_element_n(self.driver, 'encryption_suite', 'encryption_names', n).text
                dict_tmp[key].append(value)
                # 统计RC4标红个数
                if 'RC4' in value and find_element_n(self.driver, 'encryption_suite', 'RC4_red_color', n):
                    dict_tmp['RC4_red_num'] += 1
        except NoSuchElementException:
            self.encryption_suite_dict['encryption_suite'] = dict_tmp
        return self.encryption_suite_dict

    def __call__(self, *args, **kwargs):
        dict = {}
        lst = []
        lst.append(self.get_protocol())
        lst.append(self.get_encryption_suite())
        dict['protocol_suite'] = lst
        return dict


class SignatureDetail:
    '''
    协议详情
    '''

    def __init__(self, driver):
        self.signature_detail_dict = {}
        self.driver = driver

    def get_signature_detail(self):
        '''
        协议详情
        '''
        dict_tmp = {'RC4_color': ''}

        infos = wait_util_locator(self.driver, 'signature_detail', 'infos')
        for i, _ in enumerate(infos):
            n = i + 1
            key = find_element_n(self.driver, 'signature_detail', 'protocol_name', n).text
            value = find_element_n(self.driver, 'signature_detail', 'support_or_not', n).text

            dict_tmp[key] = value.replace('\n', ', ')
            # 获取RC4支持时文字的颜色
            try:
                if 'RC4' in key and find_element_n(self.driver, 'signature_detail', 'RC4_color', n):
                    dict_tmp['RC4_color'] = '红色'
            except Exception:
                pass
        self.signature_detail_dict['signature_detail'] = dict_tmp
        # log.info(self.signature_detail_dict)
        return self.signature_detail_dict

    def __call__(self, *args, **kwargs):
        return self.get_signature_detail()


class TearDown:
    '''
    关掉driver
    '''

    def __init__(self, driver):
        self.driver = driver
        self._tear_down()

    def _tear_down(self):
        self.driver.quit()


if __name__ == '__main__':
    # url = YamlUtils().get_env_data('80.30')
    url = 'http://192.168.80.72:8018/sslscan/#/'
    driver_type = 'chrome'
    driver = GetDriver(url, driver_type).get_driver()
    website = r'www.baidu.com'
    Check(driver).website_check(website)
    # print(WebsiteAbstract(driver)())
    # print(SignatureInfo(driver).get_signature_certinfo())
    # print(SignatureDetail(driver)())

    TearDown(driver)
