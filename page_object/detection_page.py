import time

from SSLScan_UI.common.dict_utils import check_key_dict_list_value
from SSLScan_UI.common.https_website_security_detection import *


class DetectionPage:
    def __init__(self, url, website, driver_type='chrome'):
        self.url = url
        self.driver_type = driver_type
        self.driver = GetDriver(self.url, self.driver_type).get_driver()
        Check(self.driver).website_check(website)

        # 各个模块结果
        self.website_abstract = {}
        self.algo_kind = {}
        self.signature_certinfo = {}
        self.signature_certinfo_details = {}
        self.protocol = {}
        self.signature_detail = {}
        self.encryption_suite = {}

        # 结果集合，统一放到一个字典里
        self.results_all_dict = {}

    # 简介
    def gen_website_abstract(self):
        res = WebsiteAbstract(self.driver).get_website_abstract()
        self.website_abstract = res
        self.results_all_dict.update(res)
        return self

    # 证书信息
    def gen_algo_kind(self):
        res = SignatureInfo(self.driver).get_algo_kind()
        self.algo_kind = res
        self.results_all_dict.update(res)
        return self

    # 证书链信息
    def gen_signature_certinfo(self):
        res = SignatureInfo(self.driver).get_signature_certinfo()
        self.signature_certinfo = res
        self.results_all_dict.update(res)
        return self

    # 证书信息 - 详细信息
    def gen_signature_certinfo_details(self):
        res = SignatureInfo(self.driver).get_signature_certinfo_details()
        self.signature_certinfo_details = res
        self.results_all_dict.update(res)
        return self

    # 协议与套件 - 协议
    def gen_protocol(self):
        res = ProtocolSuite(self.driver).get_protocol()
        self.protocol = res
        self.results_all_dict.update(res)
        return self

    # 协议与套件 - 加密套件
    def gen_encryption_suite(self, flag='1'):
        res = ProtocolSuite(self.driver).get_encryption_suite(flag)
        self.encryption_suite = res
        self.results_all_dict.update(res)
        return self

    # 协议详情
    def gen_signature_detail(self):
        res = SignatureDetail(self.driver).get_signature_detail()
        self.signature_detail = res
        self.results_all_dict.update(res)
        return self

    def __call__(self, *args, **kwargs):
        self.gen_website_abstract()
        self.gen_algo_kind()
        self.gen_signature_certinfo()
        # 新版本详细信息已经在页面显示，不用点击跳转
        # self.gen_signature_certinfo_details()
        self.gen_protocol()
        self.gen_encryption_suite()
        self.gen_signature_detail()

        log.info(self.results_all_dict)

        # quit掉driver
        TearDown(self.driver)
        return self


if __name__ == '__main__':
    pass

