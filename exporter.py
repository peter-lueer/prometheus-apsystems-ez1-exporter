import argparse
from configparser import ConfigParser
import datetime
import json
import logging
import os
import prometheus_client
import socket
import sys
import time
from APsystemsEZ1 import APsystemsEZ1M # import the APsystemsEZ1 library

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s :: %(levelname)8s :: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

class Exporter(object):
    """
    Prometheus Exporter for APSystems EZ1
    """
    def __init__(self, args):
        """
        initializes the exporter

        :param args: the argparse.Args
        """
        
        self.__metric_port = int(args.metric_port)
        self.__collect_interval_seconds = args.collect_interval_seconds
        self.__log_level = int(args.log_level)
        self.__log_level = int(os.getenv('LOG_LEVEL',30))
        
        if self.__log_level == 10:
            logger.debug("Set Logging to DEBUG")
            logger.setLevel(logging.DEBUG)
        elif self.__log_level == 20:
            logger.info("Set Logging to INFO")
            logger.setLevel(logging.INFO)
        elif self.__log_level == 30:
            logger.warning("Set Logging to WARNING")
            logger.setLevel(logging.WARNING)
        elif self.__log_level == 40:
            logger.error("Set Logging to ERROR")
            logger.setLevel(logging.ERROR)
        elif self.__log_level == 50:
            logger.critical("Set Logging to CRITICAL")
            logger.setLevel(logging.CRITICAL)
        
        logger.info(
            "exposing metrics on port '{}'".format(self.__metric_port)
        )

        self.__init_client(args.config_file, args.inverter_ip, args.inverter_port)
        self.__init_metrics()
        try:
            prometheus_client.start_http_server(self.__metric_port)
        except Exception as e:
            logger.critical(
                "starting the http server on port '{}' failed with: {}".format(self.__metric_port, str(e))
            )
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='APSystems EZ1 Prometheus Exporter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--metric-port',
                        default=9120,
                        help='port to expose the metrics on')
    parser.add_argument('--collect-interval-seconds',
                        default=30,
                        help='collection interval in seconds')
    parser.add_argument('--inverter-ip',
                        default=None,
                        help='IP of inverter device')
    parser.add_argument('--inverter-port',
                        default=8050,
                        help='Port of inverter device (default is 8050)')
    parser.add_argument('--log-level',
                        default=30,
                        help='10-Debug 20-Info 30-Warning 40-Error 50-Critical')

    # Start up the server to expose the metrics.
    e = Exporter(parser.parse_args())
    # Generate some requests.
    while True:
        e.collect()
