import configparser

from SSLScan_UI.common.log import log


class IniUtils:
    def __init__(self):
        self.file = '../conf/all_web_locators_results_cache.ini'
        self.conf = configparser.ConfigParser()

    # ini里分割符是 = 或 : ，URL里把:替换成_
    def get_cache_results(self, key: str):
        self.conf.read(self.file, encoding="gbk")
        res = ''
        try:
            # python读取ini文件，当数据里有%会有异常
            # res = eval(self.conf['cache'][key.replace(':', '_').replace('DZCDZC', '%')].replace('DZCDZC', '%'))
            res = eval(self.conf['cache'][key.replace(':', '_')])
        except KeyError:
            log.info(f'没有{key}对应的缓存数据')
        # print(self.conf.items('cache'))
        return res

    def set_cache_results(self, key: str, value):
        # python读取ini文件，当数据里有%会有异常
        # key = key.replace('%', 'DZCDZC')
        # value = value.replace('%', 'DZCDZC')

        self.conf.read(self.file)
        if "cache" not in self.conf.sections():
            print(self.conf.sections())
            self.conf.add_section("cache")

        self.conf.set('cache', key.replace(':', '_'), str(value))
        with open(self.file, "w+") as config_file:
            self.conf.write(config_file)

    def clear_cache_results(self):
        with open(self.file, "w") as config_file:
            config_file.truncate()

    def test(self):
        self.conf.read(self.file)
        print(self.conf.sections())


if __name__ == '__main__':
    # print(IniUtils().get_cache_results('192.168.10.130_443'))
    IniUtils().set_cache_results('192.168.10.111_444', "{'a':1}")
    IniUtils().test()
