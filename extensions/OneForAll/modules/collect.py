import threading
import importlib

from extensions.OneForAll.config.log import logger
from extensions.OneForAll.config import settings


class Collect(object):
    def __init__(self, domain):
        self.domain = domain
        self.modules = []
        self.collect_funcs = []

    def get_mod(self):
        """
        Get modules
        """
        if settings.enable_all_module:
            # The crawl module has some problems
            modules = ['extensions.OneForAll.modules.certificates', 'extensions.OneForAll.modules.check', 'extensions.OneForAll.modules.datasets',
                       'extensions.OneForAll.modules.dnsquery', 'extensions.OneForAll.modules.intelligence', 'extensions.OneForAll.modules.search']
            for module in modules:
                module_path = settings.module_dir.joinpath(module)
                for path in module_path.rglob('*.py'):
                    import_module = f'modules.{module}.{path.stem}'
                    self.modules.append(import_module)
        else:
            self.modules = settings.enable_partial_module

    def import_func(self):
        """
        Import do function
        """
        for module in self.modules:
            name = module.split('.')[-1]
            import_object = importlib.import_module(module)
            func = getattr(import_object, 'run')
            self.collect_funcs.append([func, name])

    def run(self):
        """
        Class entrance
        """
        logger.log('INFOR', f'Start collecting subdomains of {self.domain}')
        self.get_mod()
        self.import_func()

        threads = []
        # Create subdomain collection threads
        for func_obj, func_name in self.collect_funcs:
            thread = threading.Thread(target=func_obj, name=func_name,
                                      args=(self.domain,), daemon=True)
            threads.append(thread)
        # Start all threads
        for thread in threads:
            thread.start()
        # Wait for all threads to finish
        for thread in threads:
            # ???????????????????????? ?????????????????????????????????=?????????*module_thread_timeout
            # ?????????????????????????????? ?????????????????????????????????????????? ??????????????????????????????????????????
            thread.join(settings.module_thread_timeout)

        for thread in threads:
            if thread.is_alive():
                logger.log('ALERT', f'{thread.name} module thread timed out')


if __name__ == '__main__':
    collect = Collect('example.com')
    collect.run()
