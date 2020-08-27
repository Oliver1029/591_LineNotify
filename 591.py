import requests
import json
import pprint
import os
from lxml import html
from bs4 import BeautifulSoup as bs
from datetime import datetime


def getHouseDetail(house):
    post_id = str(house["post_id"])
    post_url = "https://rent.591.com.tw/rent-detail-" + post_id + ".html"
    # print(type(post_id)) 
    area = str(house["area"])
    # print(type(area))       
    price = house["price"]
    # print(type(price))       
    posttime = house["posttime"]    
    layout_str = house["layout_str"]
    layout = layout_str[21:27]
    # print(len(layout_str))
    floorInfo = house["floorInfo"]
    fulladdress = house["fulladdress"] 
    unit = house["unit"]        
    section_name = house["section_name"]
    coverImageURL = house["cover"]       
    # print(house["posttime"])
    
    currentTime = datetime.now()
    currentTime_string = currentTime.strftime("%Y/%m/%d %H:%M:%S")

    # saveDir = './images/' 
    # if not os.path.isdir(saveDir):
    #     os.mkdir(saveDir)
        
    # imagePath = saveDir + post_id + '.jpg'

    # img = requests.get(coverImageURL)
    # with open(imagePath, 'wb') as f:
    #     f.write(img.content) 
    lineNotify(post_url, area, price, posttime, layout, floorInfo, fulladdress, unit, section_name, coverImageURL, currentTime_string)
 
 
def lineNotify(post_url, area, price, posttime, layout, floorInfo, fulladdress, unit, section_name, coverImageURL, currentTime_string):
    headers = {
        "Authorization": "Bearer " + "Your Line token",
        # "Content-Type": "application/x-www-form-urlencoded"
    }
    
    params = {
        "message": 
            "\n 發送通知時間: " + currentTime_string +
            "\n 名稱: " + fulladdress +
            "\n 租金: " + price + unit +
            "\n 地區: " + section_name +
            "\n 坪數: " + area +
            "\n 格局: " + layout +
            "\n " + floorInfo +
            "\n 更新時間: " + posttime +
            # "\n cover: " + imagePath +
            "\n 文章連結: " + post_url 
    }
    
    payload = {
          'imageThumbnail':coverImageURL,
          'imageFullsize':coverImageURL
    }

    # files = {'imageFile': open(imagePath, 'rb')}
    
    # r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = params, files = files)
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = params, data = payload)
    # print(r.status_code)  # 200


url_HomePage = "https://rent.591.com.tw/?kind=0&region=1"
url = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=1"
url_conditional_homePage = "https://rent.591.com.tw/?kind=1&region=1&rentprice=12000,24000&pattern=3"
url_conditional_data = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=1&searchtype=1&region=1&rentprice=12000,24000&pattern=3'
url_conditional_data_2 = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=1&searchtype=1&region=1&rentprice=12000,24000&pattern=3&firstRow=60&totalRows=73'
# referer_URL = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=1'

# 抓取搜尋結果的物件總數量
result_URL_homePage = requests.get(url_conditional_homePage)
tree_url_HomePage = html.fromstring(result_URL_homePage.text)
totalRecord = list(set(tree_url_HomePage.xpath('//*/span[@class="R"]')))[0].text
totalPage = int(totalRecord) // 30 + 1
print(totalPage)

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}

# use the requests.Session() function to store cookies
session_requests = requests.session()

# 先連到 591 租屋網首頁，取得 HTML source code 中的 CSRF token，以及 cookie
result = session_requests.get(url_HomePage, headers = headers)
tree = html.fromstring(result.text)

# print (result.text)
# print(res.text)
authenticity_token = list(set(tree.xpath('//meta[@name="csrf-token"]/@content')))[0]

# print(authenticity_token)
# print(result.cookies)

# 請求 591租屋網 分頁第一頁 的資料，並帶入 CSRF token 以及 cookie 於 header 中
headers['cookie'] = '; '.join([x.name + '=' + x.value for x in result.cookies])
headers['X-CSRF-Token'] =  authenticity_token
# headers['content-type'] = 'application/x-www-form-urlencoded'
# headers['Referer'] = referer_URL
# print(headers['X-CSRF-Token'] )
# print(headers['cookie'])
for page in range(totalPage):
    # print(page)
    if(page == 0):
        url_target = url_conditional_data
    else:
        firstRow = str(30 * page)
        url_target = url_conditional_data + "&firstRow=" + firstRow + "&totalRows=" + totalRecord
        
    response = requests.get(url_target, headers=headers)

    # 將取得的資料以 json 格式編碼
    responese_parsed = (response.json())
    # print(responese_parsed)
    # print(type(responese_parsed))
    topData = responese_parsed["data"]["topData"]
    data = responese_parsed["data"]["data"]
    # length_topData = len(topData)
    length_data = len(data)
    # print("length_topData:", length_topData)
    print("length_data:", length_data)
    i = 0
    count = 0
    for i in range(length_data):
        # print(data[i]["posttime"])
        # print(data[i]["posttime"][-3:])
        if(data[i]["posttime"][-3:] == "小時內"):
            if(int(data[i]["posttime"][:-3]) <= 6):
                getHouseDetail(data[i])
                # print(data[i]["fulladdress"])
                posttime = data[i]["posttime"]
                count += 1
        elif(data[i]["posttime"][-3:] == "分鐘內"):
            # print(data[i]["fulladdress"])
            getHouseDetail(data[i])
            count += 1
            
    print("object count:", count)