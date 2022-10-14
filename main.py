# -*- coding: utf-8 -*-

import logging

import functions
import json
import time

logging.basicConfig(level=logging.INFO)

#--법정동코드 관련 url정보----------------------------------------------------------
url_get_regCode = "https://new.land.naver.com/api/regions/list?cortarNo="
initial_cortarNo = "0000000000"

#--item list를 얻어오기 위해 필요한 url정보------------------------------------------
### sample URL of sale info
#url_sample = "https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4182035000&rletTpCd=TJ&tradTpCd=A1&z=19"
#logging.info(url_sample)

type_realestate = "TJ"
type_trade = "A1"

#--item list를 통해 실질적으로 각 item의 내용을 얻어오기 위한 url정보--------------------
url_item = "https://m.land.naver.com/article/info/"


#---------------------------------------

#검색하고자 하는 도시 입력
print("검색을 원하는 도시를 입력하세요.(ex1. 경기도), (ex2. 서울), (ex3. 서울시)")
input_city = input("입력 : ")

#입력된 도시명을 정규화. ex) 서울 -> 서울시, 경기 -> 경기도, 전북 -> 전라북도
ret_city = functions.transform_cityname(input_city)

#대한민국 광역시/도의 법정동코드 리스트를 가져옴
ret_list_region = functions.get_regcode(url_get_regCode, initial_cortarNo)

#입력받은 도시명과 일치하는 법정동코드를 리턴
ret_get_regCode = functions.match_regcode(ret_list_region, ret_city)

#입력받은 도시 내의 모든 시/군/구 법정동 코드를 가져오기
ret_list_sigungu = functions.get_regcode(url_get_regCode, ret_get_regCode)

#입력받은 도시 내의 모든 읍/면/동 법정동 코드를 가져오기
ret_list_all_cortarNo = functions.get_regcode_from_list(url_get_regCode, ret_list_sigungu)

#logging.info(ret_list_all_cortarNo)



#리턴받은 법정동코드를 이용해, 모든 부동산매물 리스트를 가져오기
for index_list_cortarNo in range(len(ret_list_all_cortarNo)):
    time.sleep(0.01) # 너무 빠르게 반복하면 크롤링 시도가 차단될 위험이 있기 때문에, 적당한 딜레이를 주자

    print("부동산 매물 총 개수 : " + str(len(ret_list_all_cortarNo)))
    print("부동산 매물 리스트 가져오는중.. index : " + str(index_list_cortarNo))
    cortarNo = str(ret_list_all_cortarNo[index_list_cortarNo]['cortarNo'])
#    logging.info(cortarNo)

    # Todo. 부동산, 거래 type. 당장은 토지만 적용하고, 나중에 다른 종류 물건도 추가 적용예정
    url_article = "https://m.land.naver.com/cluster/clusterList?" \
                  + "view=atcl&cortarNo=" \
                  + cortarNo \
                  + "&rletTpCd=" \
                  + type_realestate \
                  + "&tradTpCd=" \
                  + type_trade \
                  + "&z=19"

#    logging.info(url_article)

#Todo. 현재는 ARTICLE 내의 모든 정보를 리스트화 하는데, 실질적으로 필요한 것은 'itemId'값 뿐이므로, 추후 최적화
    if (index_list_cortarNo == 0):
        ret_list_all_item = functions.get_item_list(url_article)
    else:
        ret_list_all_item.extend(functions.get_item_list(url_article))

#logging.info(ret_list_all_item)

#ret_list_all_item에, 내가 선택한 광역시/도의 모든 item list가 있음. 해당 list를 순회하며, itemId를 통해 각 item의 내용을 크롤링
ret_item_info = functions.get_item_info(url_item, ret_list_all_item)

functions.export_data_frame()
