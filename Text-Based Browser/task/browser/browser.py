import re
import sys
import os
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore

history = []

def download(url: str) -> str:
    # ensure url contains https:// in front of it
    if not url.startswith('https://') and not url.startswith('http://'):
        url = 'https://' + url
    try:
        r = requests.get(url, timeout=3)
    except requests.exceptions.RequestException:
        print('Some Error Occurred!  Normally, I\'d give you mor information, but that\'s not the point of this project!', file=sys.stderr)
        response = None
    else:
        if r:  #status code 2xx or 3xx

            # create soup object, usign the python built-in HTML parser
            soup = BeautifulSoup(r.content, 'html.parser')

            # returns an object list, which is a BS4 ResultSet object
            result_set = soup.body.find_all(re.compile('^(a|p|ul|ol|li|(h[1-6]))$'))

            for item in result_set:
                a_items = item.find_all('a')  # will be recursively true
                for item in a_items:
                    item.string = Fore.BLUE + item.get_text() + Fore.RESET

            # create a list of only the text contained between the specified tags (e.g. no attributes, just the tag's text)
            return_list = [item.get_text(strip=True) for item in result_set]
            return_list_names = [item.name for item in result_set]
            return_list_colored = [Fore.BLUE + item.get_text(strip=True) if item.name=='a' else item.get_text(strip=True) for item in result_set]

            response = '\n'.join(return_list_colored)

            save(url,response)
        else:
            response = 'URL error'
    finally:
        return response


def save(url: str, response: str):
    """This is a docstrin"""
    directory = sys.argv[1]
    # extract directory only, ignoring whatever comes after the '.'
    if url.startswith('https://'):
        start = len('https://')
    elif url.startswith('http://'):
        start = len('http://')
    else:
        start = 0

    file_name = url[start:url.index('.')]

    # create a directory, if it doesn't already exist.
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

    # create a file (or overwrite existing) with contents of response string
    with open(f'./{directory}/{file_name}','w',encoding='UTF-8') as file:
        file.write(response)
        file.flush()
        os.fsync(file.fileno())


def parse(url: str) -> str:
    url_only = re.compile('(https://|http://){0,1}[a-zA-z0-9\.\-]+\.[a-zA-z]+$')  # only the location, e.g. nytimes.com, added support for http(s)://
    dir_only = re.compile('^[a-zA-Z]+$')
    match_url = url_only.search(url)
    match_file = dir_only.search(url)

    if match_url:    # type is not it is a URL.<TLD> format
        talk_back = download(match_url.group())
    elif match_file:
        try:
            directory = sys.argv[1]
            with open(f'./{directory}/{match_file.group()}', 'r') as f:
                talk_back = f.read()  # read contents of file, return them
        except FileNotFoundError:
            talk_back = 'URL error'
    else:
        talk_back = 'URL error'

    return talk_back

def last_page():
    global history
    try:
        history.pop()
    except IndexError:
        pass
    response = history.pop() if history else None
    return response

def run_browser():
    # Initialize colorama
    init(autoreset=True)
    while True:
        response = None
        url_input = input()
        if url_input == 'exit':
            exit(0)  # successful exit
        elif url_input == 'back':
            response = last_page()
        else:
            response = parse(url_input)
            global history
            history.append(response)
        if response is not None:
            print(response)


# write your code here
if __name__ == '__main__':
    run_browser()
