# coding: utf8

import sys
import logging
import json
import re
import pickle
import os
import argparse
import ConfigParser
import requests
import sched
import time
from datetime import datetime, date
from lxml import html
from baidupcsapi import PCS
from cloudsight import recognize_img


_CONF_FILE = 'config.ini'
_LOG_FILE = 'history.log'

_pcs = None
_history = {}

logging.basicConfig()
logger = logging.getLogger('drama_downloader')
logger.setLevel(logging.INFO)


def _parse_conf(conf_file):
    try:
        conf = ConfigParser.SafeConfigParser()
        conf.read(conf_file)
        return conf
    except:
        logger.error('Failed to open conf file(%s).', _CONF_FILE)
        sys.exit(-1)


def _get_pcs(conf):
    def _captcha_callback(img):
        logger.info('Try to recognize captcha...')
        result = recognize_img(img)
        if not result:
            return ''

        m = re.search(r'\d+', result)
        if m:
            return m.group()

        return ''

    global _pcs
    if _pcs:
        return _pcs

    try:
        username = conf.get('baidupan', 'username')
        password = conf.get('baidupan', 'password')
        if not username or not password:
            logger.error('No username or password found.')
            return

        _pcs = PCS(username,
                  password,
                  captcha_callback=_captcha_callback)

        logger.info('Baidupan login successfully.')

        return _pcs
    except:
        import traceback
        traceback.print_exc()
        logger.error('Failed to login in baidupan.')
        sys.exit(-1)


def download_drama(args):
    conf = _parse_conf(args.config)
    _LOG_FILE = args.log

    _load_history()

    today = date.today()

    for key, value in conf.items('drama'):
        url, day, rule = map(lambda x: x.strip(), value.split(';'))
        if not url or not rule:
            logger.error('Url or rule not found. (key=%s)', key)
            continue

        day = int(day)
        if day <= 0 or day - 1 != datetime.today().weekday():
            continue

        last_download = _get_history(key)
        if last_download is not None and last_download >= today:
            continue

        try:
            r = requests.get(url)
            if not r.ok:
                logger.error('Failed to fetch %s', url)
                continue

            tree = html.fromstring(r.text)
            resource_url = tree.xpath(rule)
            if not resource_url:
                logger.error('No resource found. (key=%s)', key)
                continue


            pcs = _get_pcs(conf)
            pcs.add_download_task(resource_url,
                                  '%s/%s/' % (conf.get('baidupan', 'dest_dir'),
                                              key))
            if not r.ok:
                logger.error('Failed to add download task. (key=%s, url=%s)',
                             key, resource_url)
                continue

            _set_history(key)

            logger.info('Add download task successfully. (key=%s, url=%s)',
                        key, resource_url)

        except Exception as e:
            logger.error('Error: %s', e.message)

    if args.daemon:
        _schedule.enter(24 * 3600, 0, download_drama, (args, ))


def _set_history(key):
    _history[key] = str(date.today())
    _save_history()


def _get_history(key):
    value = _history.get(key)
    if value is not None:
        return datetime.strptime(_history.get(key), '%Y-%m-%d').date()


def _save_history():
    with open(_LOG_FILE, 'wb') as f:
        pickle.dump(_history, f)


def _load_history():
    if not os.path.exists(_LOG_FILE):
        return False

    global _history
    with open(_LOG_FILE, 'rb') as f:
        _history = pickle.load(f)

    return True


def _parse_args():
    parser = argparse.ArgumentParser(description="Drama downloader")

    parser.add_argument('-d', dest='daemon', action='store_true', help='Daemon mode.')
    parser.add_argument('-c', dest='config', default=_CONF_FILE, help="Config file. Default is %s" % _CONF_FILE)
    parser.add_argument('-l', dest='log', default=_LOG_FILE, help="Log file. Default is %s" % _LOG_FILE)

    return parser.parse_args()


_schedule = sched.scheduler(time.time, time.sleep)


if __name__ == '__main__':
    args = _parse_args()

    if not args.daemon:
        download_drama(args)
        sys.exit(0)

    logger.info('Drama downloader is running ...')
    _schedule.enter(1, 0, download_drama, (args, ))
    _schedule.run()
