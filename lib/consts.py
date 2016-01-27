# coding: utf8

import os

CONF_FILE = 'config.ini'
LOG_FILE = 'history.log'
CODE_FILE = 'code.jpg'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

SUPPORT_SITES = {
    'http://cn163.net': "//div[@id='entry']//strong[2]/preceding-sibling::a[1]/@href",
    'http://kanmeiju.net': "//div[@class='vpl'][1]//a[contains(@href, 'ed2k://')][last()]/@href",
}

GITHUB_REPOS = 'goorockey/drama-downloader'
GITHUB_API_DOMAIN = 'https://api.github.com'
