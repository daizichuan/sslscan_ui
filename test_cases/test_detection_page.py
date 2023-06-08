import os
import re
import shutil
import sys
import time
from datetime import datetime

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

import allure
import pytest

from SSLScan_UI.common.case_level_allure_map import get_allure_level
from SSLScan_UI.common.dict_utils import check_key_dict_list_value
from SSLScan_UI.common.diskcache_utils import DiskcacheUtils
from SSLScan_UI.common.excel_utils import ExcelUtils
from SSLScan_UI.common.log import log
from SSLScan_UI.page_object.detection_page import DetectionPage, wait_util_locator, find_element, GetDriver, Check, \
    SignatureInfo
from SSLScan_UI.conf.web_module_map import map_dict
from SSLScan_UI.common.datatime_utils import expiryDays_sec


class TestSSlScan:
    def setup_class(self):
        self.test_data_excel = r"../test_datas/SSL_Scan_data_all.xlsx"
        self.file_name = f"../test_datas/SSL_Scan_data_all{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        log.info(f'生成结果文件{self.file_name}')
        shutil.copy(self.test_data_excel, self.file_name)
        # 清除缓存
        DiskcacheUtils().clear_diskcache_results()
        self.global_list = []
        self.actual_results = []
        self.ca_infos = []
        log.info(f'==========运行环境：{ExcelUtils().get_excel_service_url()}==========')

    def setup_method(self):
        pass

    @allure.step('测试步骤')
    @pytest.mark.parametrize('args', ExcelUtils().get_excel_data())
    def test_detection_page(self, args):
        # 模块名
        allure.dynamic.feature(args['test_module'])
        # 用例名
        allure.dynamic.title(f"{args['NO']}_{args['case_name']}")
        # 用例等级
        allure.dynamic.severity(get_allure_level(args['case_level']))
        # 用例中的数据去空格，页面空格也做过处理
        # args = remove_space(args)

        # 第七种情况，多次刷新，加密套件结果是否重复
        if '加密套件' in args['test_module'] and args['expected_result'] == '不重复':
            detection_page_instance = DetectionPage(ExcelUtils().get_excel_service_url(), args['test_website'])
            detection_page_driver = detection_page_instance.__dict__['driver']
            set_tmp = set()
            lst = []
            for i in range(30):
                if i == 0:
                    encryption_suite_results = detection_page_instance.gen_encryption_suite().encryption_suite
                    set_tmp.add('-'.join(
                        check_key_dict_list_value(encryption_suite_results, map_dict()[args['web_module']])[
                            args['test_item']]))
                else:
                    ele = find_element(detection_page_driver, 'website_detail', 'flush')
                    detection_page_driver.execute_script("arguments[0].click();", ele)
                    encryption_suite_results = detection_page_instance.gen_encryption_suite(
                        flag='True').encryption_suite
                    set_tmp.add('-'.join(
                        check_key_dict_list_value(encryption_suite_results, map_dict()[args['web_module']])[
                            args['test_item']]))
            detection_page_driver.quit()

            log.info(f'结果集合{set_tmp}')

            if len(set_tmp) == 1:
                self.global_list.append('不重复')
                DiskcacheUtils().set_diskcache_results(args['NO'], '不重复')
                log.info(f"case_result: {str(args['expected_result'])}, actual_result: '不重复'")
            else:
                self.global_list.append('重复')
                DiskcacheUtils().set_diskcache_results(args['NO'], '重复')
                log.info(f"case_result: {str(args['expected_result'])}, actual_result: '重复'")
                assert len(set_tmp) == 1
            return

        # 所有结果放进一个字典里
        try:
            cache = DiskcacheUtils().get_diskcache_results(args['test_website'])
        except Exception:
            cache = None

        # 判断有无cache，有就不用获取，没有再获取
        all_web_locators_results = {}
        flag = 0
        try:
            if not cache or args['test_item'] == 'check_datetime':
                # 打开页面，获取页面元素对应的值
                flag = 1
                all_web_locators_results = DetectionPage(ExcelUtils().get_excel_service_url(),
                                                         args['test_website'])().results_all_dict
                DiskcacheUtils().set_diskcache_results(args['test_website'], all_web_locators_results)
            elif cache:
                flag = 2
                # 从缓存里读，ini文件
                log.info(f"读取{args['test_website']}缓存数据")
                all_web_locators_results = DiskcacheUtils().get_diskcache_results(args['test_website'])
                log.info(f"缓存数据{all_web_locators_results}")
        except Exception as e:
            log.info(e)
            res = 'Case Failed'
            if flag == 1:
                res = 'Locator TimeOut'
            elif flag == 2:
                res = 'Key Error'

            self.global_list.append(res)
            DiskcacheUtils().set_diskcache_results(args['NO'], res)
            # 获取不到数据，这里为了Allure报告为失败
            assert 1 == 0

        ###########################################################################
        # 用例中的期望结果
        case_result = str(args['expected_result'])

        # 第五种情况，简介检测时间，与现在的日期时间误差不超过10分钟，即为通过
        if args['web_module'] == '简介' and args['test_item'] == 'check_datetime':
            web_module_result = check_key_dict_list_value(all_web_locators_results, map_dict()[args['web_module']])
            actual_datetime = datetime.strptime(web_module_result['检测时间'], '%Y-%m-%d %H:%M:%S')
            now_datetime = datetime.now()
            res_5 = abs(
                (actual_datetime - now_datetime).total_seconds() / 60)
            if res_5 < 10:
                actual_result = 'TRUE'
                log.info(f"case_result: {actual_datetime}, actual_result: {now_datetime}")
                assert True
            else:
                actual_result = 'FALSE'
                log.info(f"case_result: {actual_datetime}, actual_result: {now_datetime}")
                DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                self.global_list.append(actual_result)
                assert False
            DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
            self.global_list.append(actual_result)
            return

        # 第三种情况，处理证书链特殊情况，包括是否有信息
        if args['test_item'] in ['site_certificate_info', 'ca_certificate_info', 'root_certificate_info']:
            actual_result = 'ERROR'
            # site和root字典里有计数num字典，所以>1，ca是列表，可能多个子字典，子字典里不记录计数，有单独计数子字典
            if args['test_item'] in ['site_certificate_info', 'root_certificate_info']:
                if len(check_key_dict_list_value(all_web_locators_results,
                                                 args['test_item'].split('_info')[0])) > 1:
                    actual_result = 'TRUE'
                else:
                    actual_result = 'FALSE'
            elif args['test_item'] == 'ca_certificate_info':
                if len(check_key_dict_list_value(all_web_locators_results,
                                                 args['test_item'].split('_info')[0])) > 0:
                    actual_result = 'TRUE'
                else:
                    actual_result = 'FALSE'
            DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
            self.global_list.append(actual_result)
            log.info(f"case_result: {case_result}, actual_result: {actual_result}")
            assert case_result == actual_result
            return

        # 页面元素的实际结果
        # 第一种情况，根据kv，直接获取页面数据
        web_module_result = check_key_dict_list_value(all_web_locators_results, map_dict()[args['web_module']])

        # 从key 获取 value
        actual_result = check_key_dict_list_value(web_module_result, args['test_item'])

        # 第八种情况，加密套件个数获取
        if '加密套件' in args['test_module'] and args['web_module'] == '加密套件':
            # 加密套件，具体加密协议类型的个数，一般个数是个位，这里3代表百位
            if len(args['expected_result']) < 3:
                actual_result = len(actual_result)
            elif args['expected_result'] in ''.join(actual_result):
                actual_result = args['expected_result']
            else:
                actual_result = '没有'

        # 第六种情况，针对key不存在不显示情况 部分信息不存在，就不在页面显示
        if case_result == '不显示' and not actual_result:
            actual_result = '不显示'
            DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
            self.global_list.append(actual_result)
            log.info(f"case_result: {case_result}, actual_result: {actual_result}")
            return

        if isinstance(actual_result, int):
            actual_result = str(actual_result)
        log.info(f"test_item：{args['test_item']}")

        # 第四种情况，证书详情有效期是否过期
        if args['web_module'] == '证书信息' and args['test_item'] == '有效期':
            start_datetime = web_module_result['开始时间']
            end_datetime = web_module_result['结束时间']
            expiry_days = web_module_result['有效期']
            expiry_secs = expiryDays_sec(expiry_days)

            start_datetime_sp = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            end_datetime_sp = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
            now_datetime = datetime.now()
            # 没过期，结束时间和现在时间做对比
            expire_flag = 0
            if now_datetime < end_datetime_sp:
                actual_secs = (end_datetime_sp - now_datetime).total_seconds()
                log.info(f"case_result: {expiry_secs}, actual_result: {actual_secs}")

            # 过期
            if now_datetime > end_datetime_sp:
                expire_flag = 1
                actual_secs = (end_datetime_sp - now_datetime).total_seconds()
                log.info(f"case_result: {expiry_secs}, actual_result: {actual_secs}")
            # 两天数只差不超过一天，也就是86400秒，就算通过
            try:
                assert abs(actual_secs - expiry_secs) <= 864000
                # 防止 -37天-23小时-26分钟-31秒 这种格式错误，正确 -37天23小时26分钟31秒
                if expire_flag == 1:
                    assert str(actual_result).count('-') == 1
                # 实际不清楚具体过期几天，这里计算，然后对比，成功就返回True
                actual_result = 'TRUE'
                DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                self.global_list.append(actual_result)
            except Exception:
                actual_result = 'FALSE'
                DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                self.global_list.append(actual_result)
                assert False
            return

        # 第二种情况，证书链有效期 保护日期时间和剩余天数时，处理
        try:
            if re.match(r'(.*?)（剩余 (.*?)秒.*?', actual_result, re.M | re.I):
                match_obj = re.match(r'(.*?)（剩余 (.*?)秒.*?', actual_result, re.M | re.I)
                datatime_ = match_obj.group(1)
                days = match_obj.group(2) + '秒'

                end_datetime = datatime_.split('~')[1]
                end_datetime_sp = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
                now_datetime = datetime.now()

                # 两天数只差不超过一天，也就是86400秒，就算通过
                if args['expected_result'] == 'TRUE':
                    actual_result = days
                    actual_secs = (end_datetime_sp - now_datetime).total_seconds()
                    expiry_secs = expiryDays_sec(actual_result)
                    assert abs(actual_secs - expiry_secs) <= 864000
                    actual_result = 'TRUE'
                    DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                    self.global_list.append(actual_result)
                    log.info(f"case_result: {expiry_secs}, actual_result: {actual_secs}")
                    return
                elif re.match(r'.*?~.*?', args['expected_result'], re.M | re.I):
                    actual_result = datatime_
                    assert case_result == actual_result
                    DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                    self.global_list.append(actual_result)
                    log.info(f"case_result: {case_result}, actual_result: {actual_result}")
                    return

        except TypeError:
            pass

        # 去掉crlUrl里的字段
        if args['test_item'] == 'crlUrl':
            actual_result = actual_result.replace(' URIName: ', '')

        # 处理 actual_result 为列表时，转换成字符串
        if isinstance(actual_result, list):
            actual_result = '-'.join(actual_result)

        # 回写excel表里实际结果
        DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
        self.global_list.append(actual_result)
        log.info(f"case_result: {case_result}, actual_result: {actual_result}")

        # 处理excel表格里预期条件为空的情况
        if case_result == 'nan':
            if actual_result == '' or actual_result is None or actual_result == 'None':
                actual_result = 'nan'

        assert case_result == actual_result

    @allure.step('测试步骤')
    @pytest.mark.parametrize('args', ExcelUtils().get_excel_data('Sheet2'))
    def test_websites_scan(self, args):
        # 模块名
        allure.dynamic.feature(args['test_module'])
        # 用例名
        allure.dynamic.title(f"{args['case_id']}_{args['case_name']}")
        # 用例等级
        allure.dynamic.severity(get_allure_level(args['case_level']))

        driver = GetDriver(ExcelUtils().get_excel_service_url()).get_driver()

        # 第一种情况，不输入直接点击，提示404
        if str(args['test_website']).lower() == 'nan':
            Check(driver).website_check(args['test_website'])
            infos = wait_util_locator(driver, 'check', 'tips_code')
            for _ in infos:
                find_element(driver, 'check', 'tips_code')
                log.info("返回404错误")
                DiskcacheUtils().set_diskcache_results(args['NO'], '返回404错误')
                self.actual_results.append('返回404错误')
            return

        Check(driver).website_check(args['test_website'])

        # 第三种情况，成功或失败之后还可以点击返回，并成功返回首页
        if args['test_item'] == '返回首页':
            infos = wait_util_locator(driver, 'check', 'back_homepage')
            for _ in infos:
                ele = find_element(driver, 'check', 'back_homepage')
                driver.execute_script("arguments[0].click();", ele)
                # ActionChains(driver).move_to_element(ele).click(ele).perform()

            wait_util_locator(driver, 'check', 'scan_btn')
            log.info("返回首页成功")
            DiskcacheUtils().set_diskcache_results(args['NO'], '返回首页成功')
            self.actual_results.append('返回首页成功')
            return

        # 第二种情况，只对扫描成功与否进行处理
        while True:
            cur_url = driver.current_url
            if 'errpath' in cur_url:
                actual_result = '该站点不支持SSL'
                DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                self.actual_results.append(actual_result)
                break
            if 'index' in cur_url:
                actual_result = '检测成功'
                DiskcacheUtils().set_diskcache_results(args['NO'], actual_result)
                self.actual_results.append(actual_result)

                try:
                    SignatureInfo(driver).get_signature_certinfo()
                except Exception:
                    DiskcacheUtils().set_diskcache_results(args['NO'], '该站点不支持SSL')
                    self.actual_results.append('该站点不支持SSL')
                break
            time.sleep(0.5)

        driver.quit()

        log.info(f"case_result: {args['expected_result']}, actual_result: {actual_result}")
        assert args['expected_result'] == actual_result

    def teardown_method(self):
        pass

    def teardown_class(self):
        # 回写excel表里实际结果
        # ExcelUtils().setback_excel_actual_results(self.global_list, 'Sheet1', self.file_name)
        # log.info(self.global_list)
        # ExcelUtils().setback_excel_actual_results(self.actual_results, 'Sheet2', self.file_name)
        # log.info(self.actual_results)
        s_name = ['Sheet1', 'Sheet2']
        ExcelUtils().setback_excel_accordingto_NO(f_name=self.file_name, s_name=s_name)


if __name__ == '__main__':
    date_time = datetime.now().strftime('%Y%m%d%H%M%S')
    pytest.main(
        ['-svvv', '-n 4', 'test_detection_page.py', '--clean-alluredir',
         f'--alluredir=../report/{date_time}/allure_result'])
    os.system(f"allure generate ../report/{date_time}/allure_result -o ../report/{date_time}/allure_report --clean")
