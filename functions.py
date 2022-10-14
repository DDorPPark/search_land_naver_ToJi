# 네이버부동산 법정동코드 크롤링 & 파싱
import json
import logging
import pandas as pd
import re
import requests
import time

from bs4 import BeautifulSoup

raw_data = {
        '용지종류',
        '거래타입',
        '광역시/도',
        '시군구',
        '동읍면',
        '지번주소',
        '매매가',
        '면적(m²)',
        '면적(평)',
        '평당가',
        '부동산',
        '부동산연락처'
}

data_frame = pd.DataFrame()









header = {
    'Accept'            : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding'   : 'gzip, deflate, br',
    'Accept-Language'   : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host'              : 'new.land.naver.com',
    'Referer'           : 'https://new.land.naver.com/offices?ms=37.2704568,127.0117896,17&a=TJ&b=A1&e=RETAIL',
    'Connection'        : 'keep-alive',
    'sec-ch-ua'         : '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile'  : '?0',
    'Sec-Fetch-Dest'    : 'empty',
    'Sec-Fetch-Mode'    : 'cors',
    'Sec-Fetch-Site'    : 'none',
    'Sec-Fetch-User'    : '?1',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent'        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}

header_item = {
    'Accept'            : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding'   : 'gzip, deflate, br',
    'Accept-Language'   : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host'              : 'new.land.naver.com',
    'Referer'           : 'https://m.land.naver.com/',
    'Connection'        : 'keep-alive',
    'sec-ch-ua'         : '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile'  : '?0',
    'sec-ch-ua-platform': "Windows",
    'Sec-Fetch-Dest'    : 'iframe',
    'Sec-Fetch-Mode'    : 'navigate',
    'Sec-Fetch-Site'    : 'same-origin',
    'Sec-Fetch-User'    : '?1',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent'        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}


def transform_cityname(arg_cityName):
    if (arg_cityName == "서울"):
        arg_cityName = "서울시"
    elif (arg_cityName == "경기"):
        arg_cityName = "경기도"
    elif (arg_cityName == "인천"):
        arg_cityName = "인천시"
    elif (arg_cityName == "부산"):
        arg_cityName = "부산시"
    elif (arg_cityName == "대전"):
        arg_cityName = "대전시"
    elif (arg_cityName == "대구"):
        arg_cityName = "대구시"
    elif (arg_cityName == "울산"):
        arg_cityName = "울산시"
    elif (arg_cityName == "세종"):
        arg_cityName = "세종시"
    elif (arg_cityName == "광주"):
        arg_cityName = "광주시"
    elif (arg_cityName == "강원"):
        arg_cityName = "강원도"
    elif (arg_cityName == "충북"):
        arg_cityName = "충청북도"
    elif (arg_cityName == "충남"):
        arg_cityName = "충청남도"
    elif (arg_cityName == "경북"):
        arg_cityName = "경상북도"
    elif (arg_cityName == "경남"):
        arg_cityName = "경상남도"
    elif (arg_cityName == "전북"):
        arg_cityName = "전라북도"
    elif (arg_cityName == "전남"):
        arg_cityName = "전라남도"
    elif (arg_cityName == "제주"):
        arg_cityName = "제주도"

    return arg_cityName


def parse_regcode_to_list(arg_response):
    #request.get으로 받은 response를 json -> dict로 변환
    response_json = arg_response.json()
    logging.info(response_json)
    #변환된 dict내부에 regionList로 묶여있으므로 한껍데기 벗기기
    regionList = response_json['regionList']
    logging.info(regionList)
    return regionList


def match_regcode(arg_regionList, arg_cityName):
    for index_cortarNo in range(len(arg_regionList)):
        if (arg_regionList[index_cortarNo]['cortarName'] == arg_cityName):
            return arg_regionList[index_cortarNo]['cortarNo']

    logging.warning("there is no matched cortarNo!!")


def get_regcode(arg_url, arg_cortarNo):

    url = arg_url + arg_cortarNo

    response = requests.get(url, headers=header)

    ret_regionList = parse_regcode_to_list(response)

    return ret_regionList


def get_regcode_from_list(arg_url, arg_list_regcode):

    for index_cortarNo in range(len(arg_list_regcode)):
        time.sleep(0.05)

        if (index_cortarNo == 0):
            ret_list_cortarNo = get_regcode(arg_url, arg_list_regcode[index_cortarNo]['cortarNo'])
        else:
            ret_list_cortarNo.extend(get_regcode(arg_url, arg_list_regcode[index_cortarNo]['cortarNo']))

    return ret_list_cortarNo


def parse_item_list(arg_response_item_info):

    #request.get으로 받은 response를 json -> dict로 변환
    response_json = arg_response_item_info.json()

    #변환된 dict 껍데기 벗기기
    itemList = response_json['data']['ARTICLE']

    return itemList


def get_item_list(arg_url):

    response = requests.get(arg_url, headers=header)
    #logging.info(response.content)

    ret_itemList = parse_item_list(response)
    #logging.info(ret_itemList)
    return ret_itemList


#해당 function은, 추후 pattern정리가 가능할때 되살려서 사용할 예정
def remove_pattern_from_json(arg_str):
#"windows.App=" 이라는 패턴이 있어, 이를 제거하기 위함

    if(re.search(r'=', arg_str)):

#"windows.App = {" 패턴의 위치 확인
        search_index = re.search(r'=', arg_str)

#패턴의 앞부분 제거
        ret_str = arg_str[search_index.end():]
        #logging.info(ret_str)

    return ret_str


def get_data_with_pandas(arg_json_dict, index_list_all_item):

    if 'buildingTypeName' in arg_json_dict['state']['article']['article']:
        data_frame.loc[index_list_all_item, '용지종류']         = arg_json_dict['state']['article']['article']['buildingTypeName']

    if 'tradeTypeName' in arg_json_dict['state']['article']['article']:
        data_frame.loc[index_list_all_item, '거래타입']         = arg_json_dict['state']['article']['article']['tradeTypeName']
    if 'cityName' in arg_json_dict['state']['article']['article']:
        data_frame.loc[index_list_all_item, '광역시/도']        = arg_json_dict['state']['article']['article']['cityName']
    if 'divisionName' in arg_json_dict['state']['article']['article']:
        data_frame.loc[index_list_all_item, '시군구']          = arg_json_dict['state']['article']['article']['divisionName']
    if 'sectionName' in arg_json_dict['state']['article']['article']:
        data_frame.loc[index_list_all_item, '동읍면']          = arg_json_dict['state']['article']['article']['sectionName']
    if 'detailAddress' in arg_json_dict['state']['article']['location']:
        data_frame.loc[index_list_all_item, '상세주소']          = arg_json_dict['state']['article']['location']['detailAddress']
    if 'jibunAddress' in arg_json_dict['state']['article']['article']:
        data_frame.loc[index_list_all_item, '지번주소']         = arg_json_dict['state']['article']['article']['jibunAddress']

    if 'area1' in arg_json_dict['state']['article']['addition']:
        data_frame.loc[index_list_all_item, '면적(m²)']              = arg_json_dict['state']['article']['addition']['area1']
        data_frame.loc[index_list_all_item, '면적(평)']      =     data_frame.loc[index_list_all_item, '면적(m²)'] * 0.3025

    if 'dealPrice' in arg_json_dict['state']['article']['price']:
        data_frame.loc[index_list_all_item, '매매가(만원)']           = arg_json_dict['state']['article']['price']['dealPrice']
    if 'priceBySpace' in arg_json_dict['state']['article']['price']:
        data_frame.loc[index_list_all_item, '평당가(만원)']        = arg_json_dict['state']['article']['price']['priceBySpace']

#    totalPrice          = arg_json_dict['state']['article']['articleTax']['totalPrice']
#    acquisitionTax      = arg_json_dict['state']['article']['articleTax']['acquisitionTax']
#    eduTax              = arg_json_dict['state']['article']['articleTax']['eduTax']
#    specialTax          = arg_json_dict['state']['article']['articleTax']['specialTax']

    if 'realtorName' in arg_json_dict['state']['article']['realtor']:
        data_frame.loc[index_list_all_item, '부동산']         = arg_json_dict['state']['article']['realtor']['realtorName']

    if 'address' in arg_json_dict['state']['article']['realtor']:
        data_frame.loc[index_list_all_item, '부동산주소']             = arg_json_dict['state']['article']['realtor']['address']

    if 'representativeTelNo' in arg_json_dict['state']['article']['realtor']:
        data_frame.loc[index_list_all_item, '연락처']         = arg_json_dict['state']['article']['realtor']['representativeTelNo']


#    print(data_frame)


def get_item_info(arg_url_item, arg_list_all_item):

    print("매물 총 개수 : " + str(len(arg_list_all_item)))
    for index_list_all_item in range(len(arg_list_all_item)):
        #time.sleep(0.1)
        print("매물 정보를 가져오는중.. index : " + str(index_list_all_item))
        if 'itemId' in arg_list_all_item[index_list_all_item]:
            url_item = arg_url_item + arg_list_all_item[index_list_all_item]["itemId"] + "?newMobile"
#            logging.info(url_item)
            response_item = requests.get(url_item, headers=header_item)
            soup_response_item = BeautifulSoup(response_item.text, 'html.parser')

#            script body태그 내의 모든 script태그의 내용을 추출. 현재 3번째 script태그의 내용만 필요하므로, 주석처리
#            soup_scripts = soup_response_item.find("body").find_all("script")

#           아랫줄로 추출된 script의 내용을 보면, json형태로 부동산에 관련된 모든 정보가 나와있음.
#           그 중, 우리에게 필요한 정보만 추출할 것
#           이번 작업은 토지 전용이기때문에 상관없지만, 추후 주거매물로 갈 경우, 층수 등의 정보를 추가로 추출해야함.
            soup_scripts = soup_response_item.find("body").select("script")[2].text

#           내용중 필요없는 pattern을 제거한 string을 추출
            ret_script = remove_pattern_from_json(soup_scripts)

#           위에서 추출한 str을 json dict 형식으로 변환
            ret_json_dict = json.loads(ret_script)

            get_data_with_pandas(ret_json_dict, index_list_all_item)

        else:
            print("no itemId. NVM")

        if (index_list_all_item == 100):
            try:
                data_frame.to_excel("result_land_100.xlsx")
            except IndexError as e:
                data_frame.to_excel("result_land_100_indexerror.xlsx")

        if (index_list_all_item == 1000):
            try:
                data_frame.to_excel("result_land_1000.xlsx")
            except IndexError as e:
                data_frame.to_excel("result_land_1000_indexerror.xlsx")

        if (index_list_all_item == 10000):
            try:
                data_frame.to_excel("result_land_10000.xlsx")
            except IndexError as e:
                data_frame.to_excel("result_land_10000_indexerror.xlsx")

        if (index_list_all_item == 20000):
            try:
                data_frame.to_excel("result_land_20000.xlsx")
            except IndexError as e:
                data_frame.to_excel("result_land_20000_indexerror.xlsx")

        if (index_list_all_item == len(arg_list_all_item)):
            try:
                data_frame.to_excel("result_land_end.xlsx")
            except IndexError as e:
                data_frame.to_excel("result_land_end_indexerror.xlsx")

def export_data_frame():
    try:
        data_frame.to_excel("result_land_total.xlsx")
    except IndexError as e:
        data_frame.to_excel("result_land_total_indexerror.xlsx")