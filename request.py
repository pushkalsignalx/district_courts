import requests

def make_request1():
    cookies = {
        'JSESSION': '32498716',
        'PHPSESSID': 'h6m2istgp9dan7ufe6kmift5vs',
        'PHPSESSID': 'gh24iq6l1uqgeg54ea8acraaq8',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://services.ecourts.gov.in/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://services.ecourts.gov.in',
        'Connection': 'keep-alive',
        # 'Cookie': 'JSESSION=32498716; PHPSESSID=h6m2istgp9dan7ufe6kmift5vs; PHPSESSID=gh24iq6l1uqgeg54ea8acraaq8',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    data = {
        'state_code': '8',
        'dist_code': '',
        'ajax_req': 'true',
        'app_token': '9a280ae5f6dd137efdc10b703dc26cbec5411ebb39fd2b34b656cd0fc75f4897',
    }

    response = requests.post(
        'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillcomplex',
        cookies=cookies,
        headers=headers,
        data=data,
    )
    return response


def maker_request2():

    cookies = {
        'JSESSION': '98444005',
        'PHPSESSID': '99lm1h7brtbdb078q33jijcvjs',
        'PHPSESSID': 'gh24iq6l1uqgeg54ea8acraaq8',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://services.ecourts.gov.in/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://services.ecourts.gov.in',
        'Connection': 'keep-alive',
        # 'Cookie': 'JSESSION=98444005; PHPSESSID=99lm1h7brtbdb078q33jijcvjs; PHPSESSID=gh24iq6l1uqgeg54ea8acraaq8',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    data = {
        'state_code': '8',
        'dist_code': '16',
        'court_complex_code': '1080044',
        'ajax_req': 'true',
        'app_token': '4c0e3c6e571c8ba25a4138ad2881546e1dc9448e3e995cd04d671c6e1b463261',
    }

    response = requests.post(
        'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillCourtEstablishment',
        cookies=cookies,
        headers=headers,
        data=data,
    )

    return response
    
def write_response(response):
    with open ('response.html', 'w') as f:
        f.write(response.text)

        
if __name__ == '__main__':
    response = maker_request2()
    write_response(response)
    print(response.text)