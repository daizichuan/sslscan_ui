from diskcache import Index

from SSLScan_UI.common.log import log


class DiskcacheUtils:
    def __init__(self):
        self.index = Index('../conf')

    def get_diskcache_results(self, key: str):
        for k, v in self.index.items():
            if k == key:
                return v
        log.info(f'没有{key}对应的缓存数据')

    def set_diskcache_results(self, key: str, value):
        self.index[key] = value
        log.info(f'缓存插入key：{key}')
        log.info(f'缓存插入value：{value}')

    def clear_diskcache_results(self):
        self.index.clear()
        for _ in self.index.items():
            if not _:
                log.info(f'脏数据{_}')
        log.info(f'清除缓存')

    def print_diskcache_results(self):
        for _ in self.index.items():
            print(_)
