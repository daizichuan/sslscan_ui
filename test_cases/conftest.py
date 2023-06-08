import shutil
from datetime import datetime

import pytest

from SSLScan_UI.common.log import log


@pytest.fixture(scope='session')
def setback_excel_file_name():
    # test_data_excel = r"../test_datas/SSL_Scan_data_all.xlsx"
    # file_name = f"../test_datas/SSL_Scan_data_all{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    # log.info(f'生成结果文件{file_name}')
    # shutil.copy(test_data_excel, file_name)
    # return file_name
    pass


