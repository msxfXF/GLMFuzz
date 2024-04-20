import requests
import time 
cookies = {
    'cookieLanguageKey': '0F34391E1ED476FAD959C955E2AB24B7',
    'lang': 'AD643F7130FA406D5FFB6C7FFDA6DB85',
    'JSESSIONID': 'BAB66J81-W3XJ98Q7BAWAL484LSPA3-CF52YOUL-AB',
    'tmp0': 'eNrz4A12DQ729PeL9%2FV3cfUxiKjOTLFScnJ0MjPzsjDUDTeO8LK0CDR3cgx39DGxMPEJDnA01nV2MzWK9A%2F10XV0UtJJLrEyNDc0MjG1NDY0NDOw0ElMRhPIrbAyqOWKL0mKL8nPTs2L54wwMy11Ca7yqIwCAGcRIng%3D',
    'cna': 'MPyYHm6vx00CAWonglpDTw5y',
    'xlly_s': '1',
    'offer': 'C8ECD4ABB78ACC97BEE1F83AD3D843633B5C9BB6EC32B67BC1B839E166D98EF47A22D0D35B604E9F75C6DF2411E6A45F2A71E216DE4B013A1A940BE2DA06B0E4BA70E6D32D38D6CDF9567FDDA461CBE61074CADC6A671503785B6DBA5FCC5A2C',
    'tfstk': 'fTRnLv_TaGZfrVU-xCfIs2lJNqDOOk15f3FR2_IrQGS69MB-RzXPj3fJJYMCE_j9xTdpzDtkZG-6eL3Cehvkv31LFT8zra-OTT9d2MIlZUtmWmhxMeTCN6oxDjp8cOgPG8PzauIaQZgR-NwsMeTQ7BLMFXcYE9hMj2jy495Z_wIaTW-zT1uGzaEUUW-y7Vb5barP4azNba_fza8zdcIdYgOZl0vF7XtJtCbhIALdbA-W1wAcDe8shxg5-9j28GmxuQ1hEHXH6Xqf-d8DvwxSGW1FEpJVTQmmt18XBH7M4m2lbKABZtdnm-seOgtcTdmat_5etKBfZx4CWBYwGTAIx5SHfFJAOIo_Zn89kB66ZmqNVpQf_wvizRSFUgrbQ-uDH7_ZyC27F971SiaQKhyA73hP6V0g3wXF5wPtSV27k971Si3iS-5RLN_U6',
    'isg': 'BKOjl04RwZjvMY4o7f7HQY1FMuFNmDfaNw7wC9UAo4J5FME2X2pPK-0CD-Qago_S',
}

headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'bx-v': '2.5.11',
    'cache-control': 'no-cache',
    # 'cookie': 'cookieLanguageKey=0F34391E1ED476FAD959C955E2AB24B7; lang=AD643F7130FA406D5FFB6C7FFDA6DB85; JSESSIONID=BAB66J81-W3XJ98Q7BAWAL484LSPA3-CF52YOUL-AB; tmp0=eNrz4A12DQ729PeL9%2FV3cfUxiKjOTLFScnJ0MjPzsjDUDTeO8LK0CDR3cgx39DGxMPEJDnA01nV2MzWK9A%2F10XV0UtJJLrEyNDc0MjG1NDY0NDOw0ElMRhPIrbAyqOWKL0mKL8nPTs2L54wwMy11Ca7yqIwCAGcRIng%3D; cna=MPyYHm6vx00CAWonglpDTw5y; xlly_s=1; offer=C8ECD4ABB78ACC97BEE1F83AD3D8436352795E25AAA947310EEECFD5CE84532E7A22D0D35B604E9F75C6DF2411E6A45F2A71E216DE4B013A1A940BE2DA06B0E4BA70E6D32D38D6CDF9567FDDA461CBE61074CADC6A671503785B6DBA5FCC5A2C; tfstk=fMBxLsYwmunANsNGhiNl_2gz44qlHtIVyZSIIFYm1aQR5a-GiOAGwdQPklr4_SW8BaQw1tvcmaQOJwfDjKsgBFQfthO1IFXt0TQKIx44gGM9Ida3-J2h0mJwCyD2kGTnunxv5RAsGQOBsfnz-J2hc7ycKrU3bCFTBFx6CnOjG8ZJfhJs5I_6PQtBxq96CNs72hxjCqGjh3sWvhcGDY8a1eDOUmcL-flSvxkVe3UaAiLWsBqMMIIVVUFUXTHeMesXyAahaH8vPHB77qYNeg6XxawoHdIWXwpfwzMAWi1F7H_beqtAGMIHwOzIB355uQxAwlGWlMTfAKXiPoLNnZB9g9anUE1RUOpcZrHH7C1l3BW0PxpCTivc1aZsCFCWfgocK9pln2YpjjE82flwG3j2dHxZYu4pT3L3qZGZ_Qhe2eq8GflwG3-J-uvr_fR-T; isg=BBQUxB0ZDtVA6Jmddit4_DaI5VSGbThXPLNHnq738h8imZTjRn7W5u5fmJEBUnCv',
    'pragma': 'no-cache',
    'referer': 'https://corehr.alibaba-inc.com/offer/nickV2.htm',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}
def check_nickname(name):
    params = {
        'id': '382357',
        'nickName': name,
        '_': '1712482729757',
    }

    response = requests.get(
        'https://corehr.alibaba-inc.com/offer/newOfferRpc/checkNickInfo.json',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    res = response.json()
    return "已存在" not in res['content']



for i in "曦惜夕希兮昔":
    for j in "程辰晨宸尘":
        if check_nickname(i+j):
            print(f"可用: {i+j}")
            time.sleep(0.1)
        else:
            # print(f"已存在: {i+j}")
            time.sleep(0.1)
        if check_nickname(j+i):
            print(f"可用: {j+i}")
            time.sleep(0.1)
        else:
            # print(f"已存在: {i+j}")
            time.sleep(0.1)

