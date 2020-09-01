#!/venv/bin/python

import os
import requests
import sys
import getopt
import json
import datetime as d
from getpass import getpass as g
from configparser import ConfigParser
from bs4 import BeautifulSoup as bs

siteRoot = 'https://mydramalist.com'

configDir = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', 'config.conf'))
config = ConfigParser()
config.read(configDir)

logDir = os.path.expanduser(config['DIRECTORIES']['log'])  # Directory to export file to


def login():
    def userInfo():  # Retrieves username and password
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
            token = cookies['jl_sess']
            loginDetails = None
        except KeyError:
            cookies = None
            print('!!Incorrect email or password!!')
            loginDetails = userInfo()
            print("Attempting to login again\n...")
        return loginDetails, cookies

    details = [config['USER']['username'], config['USER']['password']]
    details = userInfo() if not all(details) else details

    keys = attempt = 0
    while not keys and attempt < 3:
        details, keys = loginFail(details)
        attempt += 1
    if not keys and attempt == 3:
        print('Failed to login\nCheck username and password again.')
    else:
        print('Successfully logged in')
    return keys


def soup(link, params=None, headers=None, cookies=None, data=None, JSON=False, timeout=5, attempts=3):
    attempt = 0
    while attempt < attempts:
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
            attempt += 1
    raise ConnectionRefusedError


# Retrieved from @Greenstick on StackOverFlow in post /questions/3173320
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=80, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def paramHeaders(keys, refererURL, undef=False):
    headers = {
        'origin': siteRoot,
        'referer': refererURL,
    }
    parameters = {
        'token': keys['jl_sess'],
        'lang': 'en-US' if not undef else 'undefined'
    }
    return headers, parameters


def dramaList(keys, watching=True, complete=True, plan_to_watch=True, hold=True, drop=True, not_interested=True,
              suppress=False):
    profileLink = f"{siteRoot}/profile"
    headers, parameters = paramHeaders(keys, profileLink)
    listLink = f"{siteRoot}{soup(profileLink, headers=headers, cookies=keys).find('a', text='My Watchlist')['href']}"
    listSoup = soup(listLink, headers=headers, cookies=keys)
    lists = {
        'watching': listSoup.find(id='list_1') if watching else None,
        'completed': listSoup.find(id='list_2') if complete else None,
        'plan_to_watch': listSoup.find(id='list_3') if plan_to_watch else None,
        'on_hold': listSoup.find(id='list_4') if hold else None,
        'dropped': listSoup.find(id='list_5') if drop else None,
        'not_interested': soup(f"{listLink}/not_interested", headers=headers, cookies=keys).find(id='list_6')
        if not_interested else None
    }

    def userInfo(ID):
        infoSoup = soup(f"{siteRoot}/v1/users/watchaction/{ID}",
                        params=parameters,
                        headers=headers,
                        cookies=keys,
                        JSON=True)['data']
        return {
            'date-start': None if infoSoup['date_start'] == '0000-00-00'
            else d.datetime.strptime(infoSoup['date_start'], '%Y-%m-%d'),
            'date-end': None if infoSoup['date_finish'] == '0000-00-00'
            else d.datetime.strptime(infoSoup['date_finish'], '%Y-%m-%d'),
            'rewatched': infoSoup['times_rewatched']
        }

    for key in [i for i in lists if lists[i]]:
        try:
            lists[key] = {
                int(show['id'][2:]): {
                    'title': show.find(class_='title').text,
                    'country': show.find(class_='sort2').text,
                    'year': int(show.find(class_='sort3').text),
                    'type': show.find(class_='sort4').text,
                    'rating': float(show.find(class_='score').text)
                    if show.find(class_='score') or float(show.find(class_='score').text) != 0.0 else None,
                    'progress': int(show.find(class_='episode-seen').text) if show.find(class_='episode-seen') else 0,
                    'total': int(show.find(class_='episode-total').text) if show.find(class_='episode-seen') else 0,
                } for show in lists[key].tbody.find_all('tr')
            }
        except AttributeError:
            lists[key] = None

    totalShows = len([i for j in lists if lists[j] for i in lists[j]])
    for key in [i for i in lists if lists[i]]:
        for i, showID in enumerate(lists[key], start=i+1 if 'i' in locals() else 1):
            lists[key][showID].update(userInfo(showID))
            printProgressBar(i, totalShows, prefix=f'Retrieving {i}/{totalShows}') if not suppress else True
    return lists


def exportList(fileName, watching, complete, plan_to_watch, hold, drop, not_interested):
    keys = login()
    myDramaList = dramaList(keys, watching, complete, plan_to_watch, hold, drop, not_interested)
    with open(os.path.join(logDir, f"{fileName}.tsv"), 'w') as e:
        e.write(f"Title\tStatus\tEpisodes watched\tTotal episodes\tCountry of Origin\t"
                f"Show type\tRating\tStarted on\tEnded on\tRe-watched\n")
        e.writelines([
            f"{show['title']}\t{status}\t{show['progress']}\t{show['total']}\t{show['country']}\t"
            f"{show['type']}\t{show['rating']}\t{str(show['date-start']).split(' ')[0] if show['date-start'] else ''}\t"
            f"{str(show['date-end']).split(' ')[0] if show['date-end'] else ''}\t{show['rewatched']}\n"
            for status in myDramaList if myDramaList[status] for show in myDramaList[status].values()
        ])
    print(f"File saved as {os.path.join(logDir, f'{fileName}.tsv')}")


def main(argv):
    fileName = 'MyDramaList'
    watching = complete = hold = drop = plan_to_watch = not_interested = True
    try:
        opts, args = getopt.getopt(argv, "f:he:o:", ['filename=', 'help', 'except=', 'only='])
        for opt, arg in opts:
            if opt in ['-f', '--filename']:
                fileName = arg
            if opt in ['-e', '--except']:
                exceptions = arg.split(',')
                watching -= 'watching' in exceptions
                complete -= 'complete' in exceptions
                hold -= 'hold' in exceptions
                drop -= 'drop' in exceptions
                plan_to_watch -= 'plan_to_watch' in exceptions
                not_interested -= 'not_interested' in exceptions
            if opt in ['-o', '--only']:
                overwrite = arg.split(',')
                watching = 'watching' in overwrite
                complete = 'complete' in overwrite
                hold = 'hold' in overwrite
                drop = 'drop' in overwrite
                plan_to_watch = 'plan_to_watch' in overwrite
                not_interested = 'not_interested' in overwrite
            if opt in ['-h', '--help']:
                print('-----------------------------------------------------------------------------------------\n'
                      '--------This script exports your drama list as a .tsv file from MyDramaList.com----------\n'
                      '\n'
                      'Use the configuration file to set the directory to save your login details.\n'
                      '\n'
                      'usage: exportMDL.py [-f --filename <filename>] [--help]\n'
                      '                     [-e --exception <exception1,exception2...>]\n'
                      '\n'
                      '-f     Specifies filename\n\n'
                      '-e     Specifies list exceptions. Exceptions MUST be separated by a comma without spaces.\n'
                      '       The available options are:\n'
                      '       (watching, complete, hold, drop, plan_to_watch, not_interested)\n'
                      '\n'
                      '-h     Shows the help page'
                      '\n'
                      '-------------------Leave the filename unset to use default filename----------------------\n'
                      '-----------------------------------------------------------------------------------------'
                      )
                sys.exit()
    except getopt.GetoptError:
        pass
    exportList(fileName, watching, complete, plan_to_watch, hold, drop, not_interested)


if __name__ == '__main__':
    main(sys.argv[1:])
