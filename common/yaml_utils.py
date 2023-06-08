import yaml


class YamlUtils:
    def __init__(self):
        self.env_dir = '../conf/common.yaml'
        self.xpath_dir = '../conf/xpath.yaml'
        self.cache_dir = '../conf/all_web_locators_results_cache.yaml'

    def get_env_data(self, key):
        with open(self.env_dir, 'r', encoding='utf8') as f:
            data = yaml.safe_load(f)
        return data['env'][key]

    def get_xpath_data(self, key_super, key):
        with open(self.xpath_dir, 'r', encoding='utf8') as f:
            data = yaml.safe_load(f)
        return data[key_super][key]

    def get_test_data(self, file, key):
        with open(file, 'r', encoding='utf8') as f:
            data = yaml.safe_load(f)
        return data[key]

    def clear_cache_results(self):
        with open(self.cache_dir, encoding="utf-8", mode="w") as f:
            f.truncate()

    def get_cache_results(self, key):
        with open(self.cache_dir, 'r', encoding='utf8') as f:
            data = yaml.safe_load(f)
        return data[key]

    def set_cache_results(self, data):
        with open(self.cache_dir, encoding="utf-8", mode="a") as f:
            yaml.dump(data, stream=f, allow_unicode=True)


if __name__ == '__main__':
    y = YamlUtils()
    y.clear_cache_results()
    print(y.get_cache_results('192.168.10.130:443'))
