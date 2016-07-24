#!/usr/bin/python3.5
# author == 'caibangyu'

import os
import logging
import logging.handlers
import argparse

import yaml
import tornado.ioloop
import tornado.web
import tornado.gen

from lib import users


class MainHandler(tornado.web.RequestHandler):

    def initialize(self):
        self._logger = logging.getLogger(__name__)

    @tornado.gen.coroutine
    def get(self):
        self._logger.info(self.request.arguments)
        self._logger.info(self.request.query_arguments)
        self._logger.info(self.request.body_arguments)

    @tornado.gen.coroutine
    def post(self):
        self._logger.info(self.request.arguments)
        self._logger.info(self.request.query_arguments)
        self._logger.info(self.request.body_arguments)


def get_argparser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-c', '--config', default='../conf/demo.yaml',
        help='config file path')
    parser.add_argument(
        '-p', '--port', default=7070,
        help='start at the specified port')
    args = parser.parse_args()
    return args


def log_config(config, multiprocessing=False):
    log_file = config.get("logfile", "api.log")
    log_level = config["logging"].get("log_level", "INFO")
    log_dir = config["logging"].get("log_dir", "./var/log/api")
    os.makedirs(log_dir, exist_ok=True)

    log_format = '[%(levelname)s]'
    if multiprocessing:
        log_format += '<p%(process)d - %(processName)s>'
    log_format += '<%(module)s>-%(funcName)s: %(message)s --- %(asctime)s'
    log_formatter = logging.Formatter(log_format)

    # add rotate log
    log_file = os.path.join(log_dir, log_file)
    loghandler_file = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7)
    loghandler_file.setFormatter(log_formatter)
    loghandler_file.setLevel(getattr(logging, log_level.upper(), None))

    # add stream log
    loghandler_stream = logging.StreamHandler()
    loghandler_stream.setFormatter(log_formatter)
    loghandler_stream.setLevel(logging.DEBUG)

    logger = logging.getLogger()
    logger.addHandler(loghandler_file)
    logger.addHandler(loghandler_stream)
    logger.setLevel(log_level)


def main():
    args = get_argparser()
    with open(args.config, 'r') as f:
        conf = yaml.load(f)
    log_config(conf['api'], multiprocessing=True)
    users.mysql_config = conf["api"]["mysql_config"]
    logger = logging.getLogger()
    logger.info(users.mysql_config)
    application = tornado.web.Application([
        ('/', MainHandler),
        ('/users', users.UserHandler),
        ('/users/([\w:\.]+)', users.UserHandler),
    ])
    application.listen(args.port, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
