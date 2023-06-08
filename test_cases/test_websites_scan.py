import os
import shutil
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

import pytest

from SSLScan_UI.common.excel_utils import ExcelUtils
from SSLScan_UI.common.log import log
from SSLScan_UI.page_object.detection_page import wait_util_locator, GetDriver, Check, SignatureInfo, WebsiteAbstract


def scroll_locator_into_view(driver):
    certificate_chain_informations = wait_util_locator(driver, 'signature_certinfo', 'infos')
    # selenium自带方法
    for i, _ in enumerate(certificate_chain_informations):
        # _.location_once_scrolled_into_view

        # 执行js脚本
        driver.execute_script('arguments[0].scrollIntoView({block: "center"})', _)

        # 元素背景高亮
        # driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", _,
        #                       "background: green; border: 2px solid red;")  # 元素的背景色和边框设置成绿色和红

        driver.save_screenshot(f'{i}.png')


class TestWebsites:
    def setup_class(self):
        # SqliteUtils().clear_time_consuming()
        self.actual_results = []
        self.ca_infos = []
        self.time_consumings = []
        self.set_back_list = []
        self.timestamp = []
        self.website = []
        self.all_res = []

    def setup_method(self):
        self.timestamp.append(int(round(time.time() * 1000)))

    def _get_certificates_info(self, certificates_dict):
        site_certificate = ''
        ca_certificate = ''
        root_certificate = ''

        try:
            if certificates_dict['site_certificate'] and len(list(certificates_dict['site_certificate'].keys())) > 1:
                site_certificate = certificates_dict['site_certificate']['颁发给']
                site_certificate = f'site_certificate：\n{site_certificate}'
        except Exception:
            pass

        try:
            if certificates_dict['ca_certificate'] and len(list(certificates_dict['ca_certificate'])) > 1:
                lst = []
                for _ in certificates_dict['ca_certificate']:
                    if 'ca_png_num' not in _:
                        lst.append(_['颁发给'])
                ca_certificate = ' | '.join(lst)
                ca_certificate = f'ca_certificate：\n{ca_certificate}'
        except Exception:
            pass

        try:
            if certificates_dict['root_certificate'] and len(list(certificates_dict['root_certificate'].keys())) > 1:
                root_certificate = certificates_dict['root_certificate']['颁发给']
                root_certificate = f'root_certificate：\n{root_certificate}'
        except Exception:
            pass

        return f'{site_certificate}\n{ca_certificate}\n{root_certificate}'

    @pytest.mark.parametrize('website', ExcelUtils().get_excel_websites())
    def test_websites_scan(self, website):
        driver_type = 'chrome'
        driver = GetDriver(ExcelUtils().get_excel_website_url(), driver_type).get_driver()
        Check(driver).website_check(website[0])
        self.website.append(website)

        lst_tmp = []
        lst_tmp.append(website[0])

        while True:
            cur_url = driver.current_url
            actual_result = 'Failed'
            ca_infos = 'Failed'
            time_consuming = 'Failed'
            if 'errpath' in cur_url:
                actual_result = '该站点不支持SSL'
                self.actual_results.append(actual_result)
                self.ca_infos.append('不显示')
                lst_tmp.append('不显示')
                self.time_consumings.append(0)
                lst_tmp.append(0)
                break
            if 'index' in cur_url:
                actual_result = '检测成功'
                self.actual_results.append(actual_result)

                flag = 0
                ca_infos_dict = {}
                try:
                    ca_infos_dict = SignatureInfo(driver).get_signature_certinfo()
                    log.info(ca_infos_dict)
                except Exception:
                    self.actual_results.append('该站点不支持SSL')
                    self.ca_infos.append('不显示')
                    lst_tmp.append('不显示')
                    self.time_consumings.append(0)
                    flag += 1
                    lst_tmp.append(0)

                ca_infos = self._get_certificates_info(ca_infos_dict)
                self.ca_infos.append(ca_infos)
                lst_tmp.append(ca_infos)
                if flag == 0:
                    try:
                        time_consuming = int(WebsiteAbstract(driver)()['abstract']['耗时信息'])
                        log.info(time_consuming)
                        self.time_consumings.append(time_consuming)
                        lst_tmp.append(time_consuming)
                    except Exception:
                        lst_tmp.append(0)

                break

            time.sleep(0.5)
        driver.quit()

        self.all_res.append(lst_tmp)
        log.info(f'res：{lst_tmp}')

        # log.info(f"case_result: {expected_result}, actual_result: {actual_result}")
        # assert expected_result == actual_result

    def teardown_method(self):
        pass

    def teardown_class(self):
        # 迭代1，写入原始用例文件
        # ExcelUtils().setback_excel_websites_results(
        #     [[self.actual_results, 2], [self.ca_infos, 4], [self.time_consumings, 6]])

        # 迭代2，每个站点单独一个sheet页
        # test_datas = []
        # for i in range(len(self.website)):
        #     test_datas.append([self.website[i], self.time_consumings[i], self.timestamp[i]])
        #     log.info([self.website[i], self.time_consumings[i], self.timestamp[i]])
        # SqliteUtils().set_time_consuming(test_datas)

        # 迭代3，写入单独的一个sheet里面
        ExcelUtils().gen_websites_scan_excel(self.all_res)


if __name__ == '__main__':
    start = datetime.now()
    # SqliteUtils().clear_time_consuming()
    date_time = datetime.now().strftime('%Y%m%d%H%M%S')
    # template_file = '../test_datas/SSL Scan站点扫描耗时统计.xlsx'
    # res_file = f'../test_datas/SSL Scan站点扫描耗时统计{date_time}.xlsx'
    # shutil.copy(template_file, res_file)

    # while True:
    # 每个站点扫描次数
    for _ in range(100):
        pytest.main(['-svvv', '-n 8', 'test_websites_scan.py'])

    # --count重复跑的次数 -n 进程数
    # pytest.main(['-svvv', '-n 4', '--count=2', 'test_websites_scan.py', '--clean-alluredir',
    #              '--alluredir=../report/allure_result'])
    case_datas = '../test_datas/test_site.xlsx'
    case_datas_copy = '../test_datas/test_site2.xlsx'
    case_datas_new = f'../test_datas/test_site{date_time}.xlsx'
    shutil.move(case_datas, case_datas_new)
    shutil.copy(case_datas_copy, case_datas)

    # os.system(r"allure generate ../report/allure_result -o ../report/allure_report --clean")

    # 迭代2，每个站点单独一个sheet页
    # sqlite_res = SqliteUtils().get_time_consuming_all()
    # website_lst = []
    # for _ in sqlite_res:
    #     if _[0] not in website_lst:
    #         website_lst.append(_[0])
    # for i, v in enumerate(website_lst):
    #     time_comsuming_lineChart(v, v, res_file)

    end = datetime.now()
    log.info(f'==========运行时长：{end - start}==========')
