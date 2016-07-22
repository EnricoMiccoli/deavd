import logging
import modules.config as config

levels = {'debug': logging.DEBUG,
          'warning': logging.WARNING,
          'info': logging.INFO,
          'error': logging.ERROR,
          'critical': logging.CRITICAL,
         }
logging.basicConfig(
        filename=config.conf['logfile'],
        level=levels[config.conf['loglevel']],
        format='%(asctime)s::%(levelname)s:%(name)s:%(message)s',
        )
