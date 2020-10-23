import argparse
import csv
import datetime as d
import json
import sys
from configparser import ConfigParser
from getpass import getpass as g
from os.path import abspath, expanduser, exists, join, realpath
from typing import Dict, Tuple, Any
from warnings import warn

import requests
from bs4 import BeautifulSoup as bs

siteRoot = 'https://mydramalist.com'

if exists(abspath(expanduser('~/.config/exportMDL.ini'))):
    _configDir = abspath(expanduser('~/.config/exportMDL.ini'))
else:
    _configDir = abspath(join(realpath(__file__), '..', 'exportMDL.ini'))
_config = ConfigParser()
_config.read(_configDir)
if not _config['USER']:
    _config['USER'] = {'username': '', 'password': ''}
    with open(_configDir, 'w') as c:
        _config.write(c)
_logDir = expanduser(_config['DIRECTORIES']['log'])


def _login() -> "RequestCookieJar":
    def userInfo():
        print('USERNAME:')
        username = input('>>>')
        print('PASSWORD:')
        password = g('>>>')
        return [username, password]

    def loginFail(loginDetails):
        response = requests.post(url=f'{siteRoot}/signin',
                                 data={'username': loginDetails[0],
                                       'password': loginDetails[1]})

        try:
            cookies = response.request._cookies
            _ = cookies['jl_sess']
            loginDetails = None
        except KeyError:
            cookies = None
            warn('Error: Incorrect login information')
            loginDetails = userInfo()
            print("Attempting to login with the new information")
        return loginDetails, cookies

    details = [_config['USER']['username'], _config['USER']['password']]
    details = userInfo() if not all(details) else details

    keys = attempt = 0
    while not keys and attempt < 3:
        details, keys = loginFail(details)
        attempt += 1
    if not keys and attempt == 3:
        print('Failed to login\nCheck username and password again.')
        sys.exit(1)
    else:
        print('Successfully logged in')
    return keys


def soup(link: str, params: Dict[str, str] = None, headers: Dict[str, str] = None, cookies: "RequestsCookieJar" = None,
         data: Dict[str, str] = None, JSON: bool = False, timeout: int = 5, attempts: int = 3):
    while attempts:
        try:
            if not JSON:
                return bs(
                    requests.get(link, params=params, headers=headers, cookies=cookies, data=data,
                                 timeout=timeout).content, 'lxml')
            else:
                return json.loads(
                    requests.get(link, params=params, headers=headers, cookies=cookies, data=data,
                                 timeout=timeout).content)
        except requests.exceptions.ConnectTimeout:
            attempts -= 1
    raise ConnectionRefusedError("Failed to connect to MyDramaList")


# Retrieved from @Greenstick on StackOverFlow in post /questions/3173320
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=80, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def paramHeaders(keys: "RequstsCookieJar", refererURL: str, undef: bool = False) -> Tuple[
    Dict[str, str], Dict[str, str]]:
    headers = {
        'origin': siteRoot,
        'referer': refererURL,
    }
    parameters = {
        'token': keys['jl_sess'],
        'lang': 'en-US' if not undef else 'undefined'
    }
    return headers, parameters


def dramaList(keys: "RequestsCookieJar", suppress: bool = False, *args) \
        -> Dict[str, Dict[int, Dict[str, Any]]]:
    profileLink = f"{siteRoot}/profile"
    headers, parameters = paramHeaders(keys, profileLink)
    listLink = f"{siteRoot}{soup(profileLink, headers=headers, cookies=keys).find('a', text='My Watchlist')['href']}"
    listSoup = soup(listLink, headers=headers, cookies=keys)
    lists = {
        'Watching': listSoup.find(id='list_1') if 'watching' in args else None,
        'Completed': listSoup.find(id='list_2') if 'completed' in args else None,
        'Plan to watch': listSoup.find(id='list_3') if 'plan_to_watch' else None,
        'On hold': listSoup.find(id='list_4') if 'hold' else None,
        'Dropped': listSoup.find(id='list_5') if 'drop' else None,
        'Not interested': soup(f"{listLink}/not_interested", headers=headers, cookies=keys).find(id='list_6')
        if 'not_interested' else None
    }

    def userInfo(ID):
        infoSoup = soup(f"{siteRoot}/v1/users/watchaction/{ID}",
                        params=parameters,
                        headers=headers,
                        cookies=keys,
                        JSON=True)['data']
        return {
            'Started on': None if infoSoup['date_start'] == '0000-00-00'
            else d.datetime.strptime(infoSoup['date_start'], '%Y-%m-%d'),
            'Ended on': None if infoSoup['date_finish'] == '0000-00-00'
            else d.datetime.strptime(infoSoup['date_finish'], '%Y-%m-%d'),
            'Re-watched': infoSoup['times_rewatched']
        }

    for key in [i for i in lists if lists[i]]:
        try:
            lists[key] = {
                int(show['id'][2:]): {
                    'Title': show.find(class_='title').text,
                    'Country of Origin': show.find(class_='sort2').text,
                    # 'year': int(show.find(class_='sort3').text),
                    'Show type': show.find(class_='sort4').text,
                    'Rating': float(show.find(class_='score').text)
                    if show.find(class_='score') or float(show.find(class_='score').text) != 0.0 else None,
                    'Episodes watched': int(show.find(class_='episode-seen').text)
                    if show.find(class_='episode-seen') else 0,
                    'Total episodes': int(show.find(class_='episode-total').text)
                    if show.find(class_='episode-seen') else 0,
                } for show in lists[key].tbody.find_all('tr')
            }
        except (AttributeError, KeyError):
            lists[key] = None
    totalShows = len([i for j in lists if lists[j] for i in lists[j]])
    for key in [i for i in lists if lists[i]]:
        for i, showID in enumerate(lists[key], start=i + 1 if 'i' in locals() else 1):
            lists[key][showID].update(userInfo(showID))
            printProgressBar(i, totalShows, prefix=f'Retrieving {i}/{totalShows}') if not suppress else True
    return lists


def exportList(fileName: str, suppress: bool = False, *args) -> None:
    myDramaList = dramaList(_login(), suppress, *args)
    flatList = {show: {**{'Status': status}, **myDramaList[status][show]}
                for status in myDramaList if myDramaList[status]
                for show in myDramaList[status]}
    with open(join(_logDir, f"{fileName}.csv"), 'w', encoding='utf-8-sig') as e:
        fieldNames = ['Title', 'Status', 'Episodes watched', 'Total episodes',
                      'Country of Origin', 'Show type', 'Rating', 'Started on', 'Ended on', 'Re-watched']
        csvFile = csv.DictWriter(e, fieldnames=fieldNames, dialect='excel', extrasaction='raise')
        csvFile.writeheader()
        csvFile.writerows(flatList[show] for show in flatList)
    print(f"File saved as {join(_logDir, f'{fileName}.csv')}")


def main(argv) -> None:
    parser = argparse.ArgumentParser(
        description="Exports the dramalist from MyDramaList.com as a .csv file",
        epilog="Further documentation will be available at <https://github.com/arifer612/exportMDL>"
    )
    add = parser.add_argument

    add(
        '-f', '--file',
        type=str,
        metavar="FILE",
        default='MyDramaList',
        help="Filename to save the dramalist"
    )
    add(
        '-o', '--only',
        type=str,
        nargs='*',
        metavar="CATEGORY",
        default=[],
        help="List of categories to export."
    )
    add(
        '-e', '--exclude',
        type=str,
        nargs='*',
        metavar="CATEGORY",
        default=[],
        help="List of categories to exclude."
    )
    add(
        '-q', '--quiet',
        action='store_true',
        default=False,
        help="Hides everything on-screen except the bare minimum."
    )

    fields = {
        'watching': True,
        'completed': True,
        'plan_to_watch': True,
        'hold': True,
        'drop': True,
        'not_interested': False
    }

    args = parser.parse_args(argv)

    if args.only:
        args.exclude = []
    for cat in fields:
        if cat in args.exclude:
            fields[cat] = False
        if args.only and cat not in args.only:
            fields[cat] = False

    warning = [i for i in set(args.only) | set(args.exclude) if i not in fields]
    if warning:
        warn(f"<{'>, <'.join(warning)}> are not recognised categories. "
             f"Use exportMDL -h to see which categories are accepted.")

    exportList(args.file, args.quiet, *[i for i in fields if fields[i]])


if __name__ == '__main__':
    main(sys.argv[1:])
