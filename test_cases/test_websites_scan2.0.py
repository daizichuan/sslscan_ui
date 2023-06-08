# import eventlet;eventlet.monkey_patch(all=True)
# import gevent.monkey;gevent.monkey.patch_all()

import os
import shutil
import sys
import time
from datetime import datetime

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

from SSLScan_UI.common.sqlite_utils import SqliteUtils
from SSLScan_UI.common.excel_utils import ExcelUtils
from SSLScan_UI.common.log import log
from SSLScan_UI.page_object.detection_page import GetDriver, Check, SignatureInfo, WebsiteAbstract
from funboost import boost, ConcurrentModeEnum
from funboost.concurrent_pool.custom_evenlet_pool_executor import CustomEventletPoolExecutor
from funboost.concurrent_pool.custom_gevent_pool_executor import GeventPoolExecutor
from funboost.concurrent_pool.custom_threadpool_executor import ThreadPoolExecutorShrinkAble

'''
1、判断站点扫描是否成功，成功记录耗时；不成功，耗时记录为0
2、成功的标志是 url变成含有index并且有CA信息
3、失败的标志是 1）url上有 errpath；2）或者当url有index，但是没有CA信息时
'''

# 设置 协程池大小
pool = ThreadPoolExecutorShrinkAble(100)


def _get_certificates_info(certificates_dict):
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


@boost('website_scan', specify_concurrent_pool=pool, qps=10, concurrent_mode=ConcurrentModeEnum.THREADING)
def websites_scan(url, website):
    driver_type = 'chrome'
    driver = GetDriver(url, driver_type).get_driver()
    Check(driver).website_check(website)

    lst_tmp = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    # 1、日期时间列和站点名称列
    lst_tmp.append(timestamp)
    lst_tmp.append(website)

    # 站点信息列
    while True:
        cur_url = driver.current_url
        if 'errpath' in cur_url:
            lst_tmp.append('该站点不支持SSL')
            lst_tmp.append(0)
            break

        if 'index' in cur_url:
            try:
                ca_infos_dict = SignatureInfo(driver).get_signature_certinfo()
                log.info(f'{website}_{timestamp}证书信息：{ca_infos_dict}')
                ca_infos = _get_certificates_info(ca_infos_dict)
                lst_tmp.append(ca_infos)
                try:
                    time_consuming = int(WebsiteAbstract(driver)()['abstract']['耗时信息'])
                    log.info(f'{website}_{timestamp}耗时：{time_consuming}')
                    lst_tmp.append(time_consuming)
                except Exception as e:
                    log.info(e)
                    lst_tmp.append(0)
                break
            except Exception as e:
                log.info(e)
                lst_tmp.append('证书链信息为空')
                lst_tmp.append(0)
                break

        time.sleep(0.5)
    driver.quit()

    log.info(f'{website}_{timestamp} lst_tmp_res：{lst_tmp}')
    SqliteUtils().set_time_consuming(lst_tmp)


if __name__ == '__main__':
    start = datetime.now()  # 运行的开始时间
    date_time = datetime.now().strftime('%Y%m%d%H%M%S')  # 结果文件名称中的日期时间
    SqliteUtils().clear_time_consuming()  # 运行前清理上次跑的sqlite里的记录
    # 复制站点扫描模板文件
    case_datas = '../test_datas/test_site.xlsx'
    case_datas_new = f'../test_datas/test_site{date_time}.xlsx'
    shutil.copy(case_datas, case_datas_new)

    excel_utils = ExcelUtils()
    websites_scan.clear()  # 运行前清理上次消息队列里的可能出现的异常未跑完的消息
    url = excel_utils.get_excel_website_url()
    log.info(f'=========={url}==========')
    websites_tmp = excel_utils.get_excel_websites()
    websites = [''.join(website) for website in websites_tmp]
    try:
        cycle_num = 1
        for _ in range(cycle_num):  # 这里决定总共跑多少次
            for i, website in enumerate(websites):
                websites_scan.push(url, website)  # 把 website放入消息队列中，生产消息
        websites_scan.consume()  # 消费消息
        websites_scan.wait_for_possible_has_finish_all_tasks(5)  # 当消息队列中没有消息时，等待5分钟，以防止有任务没跑完，然后停掉脚本
        ExcelUtils().gen_websites_scan_excel(case_datas_new, SqliteUtils().get_time_consuming_all())
        log.info(f'==========sqlite记录结果数：{len(SqliteUtils().get_time_consuming_all())}==========')

        end = datetime.now()
        log.info(f'==========运行时长：{end - start}==========')

        os._exit(444)  # 退出线程，停止脚本
    except Exception:
        end = datetime.now()
        log.info(f'==========运行时长：{end - start}==========')
