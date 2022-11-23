from bs4 import BeautifulSoup
import urllib3
import time
import os

os.makedirs('data/img', exist_ok=True)

indexes = [
    "http://www.chinadaily.com.cn/",
    "http://www.chinadaily.com.cn/china",
    "http://www.chinadaily.com.cn/world",
    "http://www.chinadaily.com.cn/business",
    "http://www.chinadaily.com.cn/life",
    "http://www.chinadaily.com.cn/culture",
    "http://www.chinadaily.com.cn/travel",
    "http://www.chinadaily.com.cn/sports",
    "http://www.chinadaily.com.cn/opinion",
    "http://www.chinadaily.com.cn/regional"
]

http = urllib3.PoolManager()
for index in indexes:
    print("Scraping index: " + index)
    r = http.request('GET', index)
    soup = BeautifulSoup(r.data, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href == None:
            continue
        if href.find("www.chinadaily.com.cn/a/") < 0:
            # print("not news,skip!")
            continue
        if os.path.exists(os.path.join("data", href[href.find("a/") + 2:].replace("/","_"))):
            print("already downloaded,skip!")
            continue

        r = http.request('GET', "http:" + href,redirect=False)
        if r.status == 302 or r.status == 301:
            # print("Redirected,skip!")
            continue

        soupnews = BeautifulSoup(r.data, 'html.parser')
        if soupnews.find(id="div_currpage") != None:
            # print("multi page,skip!")
            continue

        print(href)
        

        with open(os.path.join("data", href[href.find("a/") + 2:].replace("/","_")),"w",encoding="utf-8") as f:
            title = soupnews.find(name="h1").get_text()
            if soupnews.find(id="bread-nav") != None:
                category = soupnews.find(id="bread-nav").get_text()
            else:
                category = "Unknown"
            f.write("""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{}</title>
    </head>
    <body>
        <h1>{}</h1>
        <h2>{}</h2>""".format(title, title, category))

            content = soupnews.find(id="Content")
            for cont in content.children:
                if cont.name == "figure":
                    img = cont.find('img')
                    if img == None:
                        continue
                    imgsrc = img.get('src')
                    with open(os.path.join("data","img",imgsrc[imgsrc.find("images/") + 7:]).replace("/","_"), 'wb') as fi:
                        fi.write(http.request('GET', "http:" + imgsrc).data)
                    f.write("<img src=\"{}\">".format(os.path.join("img",imgsrc[imgsrc.find("images/") + 7:]).replace("/","_")))
                elif cont.name == "p":
                    f.write(str(cont))


            f.write("""</body>
    </html>""")
        time.sleep(2)