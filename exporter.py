import argparse
from configparser import ConfigParser
import datetime
import json
import logging
import os
import prometheus_client
import sys
import time
import requests
import signal

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

    
    def __init_client(self, config_file, inverter_ip, inverter_port):

        try:
            if inverter_ip != None and inverter_port != 0:
                logger.info("use commandline parameters")
                self.inverter_ip = inverter_ip
                self.inverter_port = int(inverter_port)
            elif os.getenv('Inverter_IP',None) != None or int(os.getenv('Inverter_Port',0)) != 0:
                logger.info("use environment variables")
                self.inverter_ip = os.getenv('Inverter_IP',None)
                self.inverter_port = int(os.getenv('Inverter_Port',0))
            else:
                logger.info("use config file '{}'".format(config_file))
                configur = ConfigParser()
                configur.read(config_file)

                self.inverter_ip = configur.get('inverter_config','IP')
                self.inverter_port = configur.getint('inverter_config','Port')

            
            if self.inverter_ip == None or self.inverter_port == 0:
                logger.error("No IP '{}' and Port '{}' Config found".format(self.inverter_ip,self.inverter_port))
                sys.exit(1)

        except Exception as e:
            logger.critical(
                "Initializing failed with: {}".format(str(e))
            )
            sys.exit(1)

    def __init_metrics(self):
        namespace = 'apsystems_ez1'

        self.version_info = prometheus_client.Gauge(
            name = 'version_info',
            documentation = 'Project version info',
            labelnames = ['project_version'],
            namespace = namespace
        )

        self.metrics = {}
        
        file_path = os.path.dirname(__file__) + '/'

        objectFile = open(file_path + 'objectlist.json')
        self.objectList = json.load(objectFile)

        for data in self.objectList:
            try:
                for metrics_data in self.objectList[data]['data']:
                    name = metrics_data["name"]

                    try:
                        documentation = metrics_data["documentation"]
                    except:
                        documentation = metrics_data["name"]
                    #index = self.addPrefix(data)
                    try:
                        dataType = metrics_data["type"]
                    except:
                        dataType = ""

                    if dataType == "TEMPERATURE":
                        self.metrics[name] = prometheus_client.Gauge(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                    elif dataType == "POWER":
                        self.metrics[name] = prometheus_client.Gauge(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                    elif dataType == "IO":
                        self.metrics[name] = prometheus_client.Gauge(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                    elif dataType == "SECONDS":
                        self.metrics[name] = prometheus_client.Gauge(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                    elif dataType == "TIMESTAMP":
                        self.metrics[name] = prometheus_client.Gauge(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                    elif dataType == "COUNTER":
                        self.metrics[name] = prometheus_client.Gauge(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                    elif dataType == "IP":
                        #do not save IP Information
                        self.metrics[name] = prometheus_client.Info(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )
                        nothing="empty"

                    elif dataType == "ENUM":
                        self.metrics[name] = prometheus_client.Enum(
                            name = name,
                            documentation = documentation,
                            namespace = namespace,
                            states = metrics_data['enum']
                        )
                    
                    else:
                        self.metrics[name] = prometheus_client.Info(
                            name = name,
                            documentation = documentation,
                            namespace = namespace
                        )

                #print(data + "- " + self.objectList[data]["name"] + ": ")
            except Exception as ex:
                #no Name found
                name=""

    def __collect_device_info_metrics(self):
        logger.debug(
            "collect info metrics"
        )
        # general device info metric
        self.version_info.labels(
            project_version="0.1"
        ).set(1)

    def typeExists(self, listelement):
        try:
            dataType = listelement['type']
            return True
        except:
            return False
        #'type' in objectList[index]


    def isset(self, listelement):
        try:
            if listelement == {}:
                return False
            else:
                return True
        except:
            return False

    # def int2ip(self, v):
    #     part1 = v & 255
    #     part2 = ((v >> 8) & 255)
    #     part3 = ((v >> 16) & 255)
    #     part4 = ((v >> 24) & 255)
    #     return str(part4) + "." + str(part3) + "." + str(part2) + "." + str(part1)

    def addPrefix(self, index):
        result = str(index)
        while len(result) < 3 :
            result = "0" + result
        return result

    def findType(self, calledFunction, valueToFind):
        result = ""
        for data in self.objectList[calledFunction]['data']:
            if data['name'] == valueToFind:
                try:
                    result = data['type']
                    return result
                except:
                    return ""
        return result

    def getEnumDefinition(self, calledFunction, objectName, enumToFind):
        result = ""
        for data in self.objectList[calledFunction]['data']:
                if data['name'] == objectName:
                    try:
                        result = data['enum'][int(enumToFind)]
                        return result
                    except:
                        return ""

        return result
    
    def setMetricsValue(self, calledFunction, resultJsonData):

        logger.debug("Read Values for {0}", calledFunction)
        try:
            for dataObject in resultJsonData['data']:
                name = dataObject
                value = resultJsonData['data'][dataObject]

                dataType = self.findType(calledFunction, name)
                if dataType == "TEMPERATURE" or dataType == "ANALOG":
                    state = int(value)/10
                elif dataType == "IO":
                    state = value > 0
                elif dataType == "IP":
                    #state = self.int2ip(value)
                    self.metrics[name].info({ name : value})
                    continue
                elif dataType == "ENUM":
                    state = self.getEnumDefinition(calledFunction,name,value)
                    self.metrics[name].state(state)
                    continue
                elif dataType == "":
                    self.metrics[name].info({ name : value})
                    continue
                
                self.metrics[name].set(value)
            
        except Exception as ex:
            logger.warning("Date not saved. ID:" + calledFunction + " Values:" + resultJsonData)
            error="Set Value Error"


    def __collect_data_from_Inverter(self):
        try:

            for calledFunction in self.objectList:
                response = requests.get('http://' + str(self.inverter_ip) + ':' + str(self.inverter_port) + '/' + calledFunction)
                result = response.json()
                response.close()

                self.setMetricsValue(calledFunction, result)
            
            # inverter = APsystemsEZ1M(self.inverter_ip, self.inverter_port)
            # # Get device information
            # device_info = inverter.get_device_info()
            # print("Device Information:", device_info)

            # # Get alarm information
            # alarm_info = inverter.get_alarm_info()
            # print("Alarm Information:", alarm_info)

            # # Get output data
            # output_data = inverter.get_output_data()
            # print("Output Data:", output_data)

            # # Get current power status
            # power_status = inverter.get_device_power_status()
            # print("Power Status:", power_status)            
            
        except Exception as ex:
            logger.error('Fail while Reading from Inverter')

    def collect(self):
        """
        collect discovers all devices and generates metrics
        """
        try:
            logger.info('Start collect method')

            #Collect Data from Inverter
            self.__collect_device_info_metrics()

            self.__collect_data_from_Inverter()
        
        except Exception as e:
            logger.warning(
                "collecting data from inverter failed with: {1}".format(str(e))
            )
        finally:
            logger.info('waiting {}s before next collection cycle'.format(self.__collect_interval_seconds))
            time.sleep(self.__collect_interval_seconds)

def handler(signum, frame):
    logger.warning("Signal handler called with signal: {1}".format(signum))
    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='APSystems EZ1 Prometheus Exporter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--metric-port',
                        default=9120,
                        help='port to expose the metrics on')
    parser.add_argument('--config-file',
                        default='/etc/apsystemsez1/config.ini',
                        help='path to the configuration file')
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
    signal.signal(signal.SIGABRT, handler)
    e = Exporter(parser.parse_args())
    # Generate some requests.
    while True:
        e.collect()
