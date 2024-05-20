"""
use-case : 1. District court Fetch overview details using party name and store in .txt file 
"""


import re
import os
import pdb
import json
import base64
import urllib3
import requests
import structlog
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urlencode


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = structlog.get_logger()
BASE_PATH = '2010_2024'
BASE_URL = "https://services.ecourts.gov.in"
PARTY_NAME_URL = f"{BASE_URL}/ecourtindia_v6/?p=casestatus/submitPartyName"


def start_dc_session():
    URL = f'{BASE_URL}/ecourtindia_v6/'
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'services.ecourts.gov.in',
        'Referer': "https://services.ecourts.gov.in",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }
    response = session.get(URL, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    app_token = soup.find('input', attrs={'id': 'app_token'}).get('value')
    captcha_image = soup.find('img', attrs={'id': 'captcha_image'}).get('src')
    captcha_url = f"{BASE_URL}/{captcha_image}"
    cookies = response.cookies.get_dict()
    return (session, app_token, captcha_url, cookies)


def dc_captcha_solver(session, cookies, app_token):
    print("inside_dc_captcha_solver")
    retry = 0
    max_retry = 10

    while max_retry > retry:
        print('inside while loop')
        try:
            url = 'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/getCaptcha'

            captch_extra_headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Connection': 'keep-alive',
                'Host': 'services.ecourts.gov.in',
                'Origin': 'https://services.ecourts.gov.in',
                'Referer': 'https://services.ecourts.gov.in/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
            }

            data = {
                'ajax_req': True,
                'app_token': app_token
            }
             
            captcha_response = session.post(url, data = data, headers=captch_extra_headers, cookies = cookies)
            print(captcha_response.text)
            captcha_response = json.loads(captcha_response.text)

            if 'div_captcha' not in captcha_response:
                return None
            
            div_captcha = captcha_response['div_captcha']
            new_app_token = captcha_response['app_token']

            soup = BeautifulSoup(div_captcha, 'html.parser')
            
            captcha_image = soup.find('img', attrs = {'id': 'captcha_image'}).get('src')
            captcha_url = f"https://services.ecourts.gov.in{captcha_image}"
            captcha_response = session.get(captcha_url, headers=captch_extra_headers)

            captcha_image = base64.b64encode(captcha_response.content)

            body = {'image': captcha_image}
            resp = requests.post(url="http://18.217.244.33:3000/captcha/dc", json=body)
            print(resp.json())

            response = resp.json()

            solved_text = response["message"]
            captcha_pattern = r"\b[a-z0-9]{6}\b"
            captcha_match = re.search(captcha_pattern, solved_text)
            if solved_text and len(solved_text) == 6 and captcha_match:
                return (solved_text, new_app_token)
        except Exception as e:
            log.error(f"Error inside captcha solver: {e}")
            pass
        retry += 1

    return None


def dc_partywise_overview_details(session, **kwarg):
    retry = 0
    max_retry = 10

    while max_retry > retry:
        try:
            # pdb.set_trace()
            filepath = kwarg.get("filepath")
            name = kwarg.get("name", " ")
            year = kwarg.get("year")
            case_status = kwarg.get("case_status")
            state_code = kwarg.get("state_code")
            district_code = kwarg.get("district_code")
            court_complex_code = kwarg.get("court_complex_code")
            est_code = kwarg.get("est_code")
            captcha_url = kwarg.get("captcha_url")
            app_token = kwarg.get("app_token")
            cookies = kwarg.get('cookies')

            captcha_items = dc_captcha_solver(session=session,cookies=cookies, app_token=app_token)
            if captcha_items is None:
                retry += 1
                continue
            
            solved_text, new_app_token = captcha_items
            print(solved_text, new_app_token)
            kwarg['app_token'] = new_app_token
            if new_app_token is None:
                retry += 1
                sleep(2)
                continue

            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Connection': 'keep-alive',
                "Content-Length": "<calculated when request is sent>",
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://services.ecourts.gov.in',
                'Referer': 'https://services.ecourts.gov.in/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
            }
            payload = {
                "petres_name": name,
                "rgyearP": year,
                "case_status": case_status,
                "fcaptcha_code": solved_text,
                "state_code": state_code,
                "dist_code": district_code,
                "court_complex_code": court_complex_code,
                "est_code": est_code,
                "ajax_req": "true",
                "app_token": new_app_token,
            }

            # print(payload)
            log.info("Captcha", solved_text=solved_text)
            # captcha_code = input("Enter captch ; ")
            # payload = urlencode(payload)
            response = session.post(url=PARTY_NAME_URL, headers=headers, data=payload, verify=False, cookies = cookies)
            # pdb.set_trace()
            if response.status_code == 200:
                response_json = response.json()
                if "errormsg" in response_json:
                    retry += 1
                    log.info("Error message", msg=response_json['errormsg'])
                    app_token = response_json['app_token']
                    sleep(2)
                    continue

                log.info('Writing File')
                chunk_size = 10 * 1024 * 1024
                ct = 0
                # write response in file
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            f.flush()
                            del chunk
                            ct += 1
                            log.info("Chucks ", count=ct)
                new_filename = filepath.replace("_temp", "")
                log.info("File renaming")
                os.rename(filepath, new_filename)
                return True
        except Exception as e:
            print(e)

        retry += 1
    return False

def populate_dc_overview_details(**kwargs):
    retry = 0
    max_retry = 10
    while max_retry > retry:
        try:
            state_name = kwargs.get("state_name")
            state_name = state_name.replace(" ", "").lower()
            name = kwargs.get("name")
            year = kwargs.get("year")
            case_status = kwargs.get("case_status")
            state_code = kwargs.get("state_code")
            district_code = kwargs.get("district_code")
            court_complex_code = kwargs.get("court_complex_code")
            est_code = kwargs.get("est_code")

            PATH = f"{BASE_PATH}/{state_name}"
            if not os.path.exists(PATH):
                os.makedirs(PATH)

            filename = f"{state_code}_{district_code}_{court_complex_code}_{est_code}_{case_status}_{year}"
            filepath = f"{PATH}/{filename}_temp.txt"
            is_exist_filepath = f"{PATH}/{filename}.txt"

            if os.path.exists(is_exist_filepath):
                continue

            (session, app_token, captcha_url, cookies) = start_dc_session()
            log.info("Session start...")
            log.info("State & District Codes", state_code=state_code, district_code=district_code)
            response = dc_partywise_overview_details(
                session=session,
                filepath=filepath,
                name=name,
                year=year,
                case_status=case_status,
                state_code=state_code,
                district_code=district_code,
                court_complex_code=court_complex_code,
                est_code=est_code,
                captcha_url=captcha_url,
                app_token=app_token,
                cookies=cookies
            )
            if response:
                return
        except Exception as e:
            print(e)


def main(year, case_status, name):
    checks = [{
        "state_name": "Bihar",
        "state_code": "8",
        "district_code": "16",
        "court_complex_code": "1080044",
        "est_code": "null",
    }]
    for check in checks:
        state_name = check.get("state_name")
        state_code = check.get("state_code")
        district_code = check.get("district_code")
        court_complex_code = check.get("court_complex_code")
        est_code = check.get("est_code")

        populate_dc_overview_details(
            state_name=state_name,
            name=name,
            year=year,
            case_status=case_status,
            state_code=state_code,
            district_code=district_code,
            court_complex_code=court_complex_code,
            est_code=est_code,
        )


if __name__ == "__main__":
    year = "2022"
    name = " "
    case_status = "Both"  # "Pending", "Disposed", "Both"
    main(year=year, name=name, case_status=case_status)
