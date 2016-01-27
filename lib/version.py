# coding: utf8

import requests

from .consts import GITHUB_REPOS, GITHUB_API_DOMAIN

def check_version():
  headers = {
      'Accept': 'application/vnd.github.v3+json',
  }

  url = '%s/repos/%s/releases/latest' % (GITHUB_API_DOMAIN, GITHUB_REPOS)
  r = requests.get(url, headers=headers)
  if not r.ok:
    return

  return r.json().get('tag_name')





