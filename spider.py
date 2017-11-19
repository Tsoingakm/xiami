import requests
from bs4 import BeautifulSoup
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_page(baseurl,header,page):
    url = baseurl + 'c=' + str(page)
    try:
        r = requests.get(url,headers = header)
        r.raise_for_status()
        r.encoding = 'utf-8'
        html = r.text
        return(html)
    except Exception:
        print('链接网页失败',url)

def get_song_url(html):
    urllist = []
    soup = BeautifulSoup(html,'html.parser')
    infos = soup.find_all('div',class_="info")
    for info in infos:
        song_urls = info.strong
        song_url = song_urls.a['href']
        urllist.append(song_url)
    return urllist

def get_song_page(fullurl):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    try:
        r = requests.get(fullurl,headers = header)
        r.raise_for_status()
        r.encoding = 'utf-8'
        html = r.text
        return(html)
    except Exception:
        print('打开网页失败',fullurl)

def get_info(code):
    a = []
    b = []
    c = []
    soup = BeautifulSoup(code,'html.parser')
    titles = soup.title
    title = titles.string.split(',')[1].split('M')[0]#获取歌曲名字
    singer = soup.find('table',id="albums_info")
    infos = singer.find_all('a')
    for info in infos:
        a.append(info.string)
        if None in a:
            a.remove(None)
    album = a[0]#专辑
    del a[0]#将专辑元素删除
    singers = a#剩下的就是歌手了
    plays = soup.find_all('li',class_="line")
    for i in plays:
        for play in i:
            b.append(play)
    sharetimes = b[2]#获取分享数
    comments = soup.find('a',href='#wall')
    for comment in comments.strings:
        c.append(comment)
    commenttimes = c[0]#获取评论数
    return {
        '歌曲名字':title,
        '专辑名字':album,
        '歌手':singers,
        '分享':sharetimes,
        '评论':commenttimes
    }

def save_to_mongo(result):
    print('正在储存到mongo数据库...')
    if db[MONGO_TABLE].insert(result):
        print('储存成功')
        return True
    else:
        return False


def start():
    baseurl = 'https://www.xiami.com/chart/data?'
    header = {
        'Cookie':"gid=151107690665882; _xiamitoken=e9abffed3ac222e1f3ba5bbc2e269455; _unsign_token=dbe360c3db092257188de28beff8cfea; UM_distinctid=15fd3364b4c50-0671a345b55a7a-6a11157a-1fa400-15fd3364b4d42d; cna=FLwqEShyaAsCAQ6QNO28G2Eo; __XIAMI_SESSID=93a85dae947ae929cde0cc26af08d9f2; bdshare_firstime=1511077442514; XMPLAYER_url=/song/playlist/id/1797642805/object_name/default/object_id/0; CNZZDATA921634=cnzz_eid%3D1780468110-1511076716-null%26ntime%3D1511076716; CNZZDATA2629111=cnzz_eid%3D1183398237-1511075039-null%26ntime%3D1511075039; XMPLAYER_isOpen=1; XMPLAYER_addSongsToggler=0; XMPLAYER_volumeValue=0.06; __guestplay=MTc5NzY0MjgwNSwy; isg=Avf3mtdOYd-iGeVTDQXDm8OHhuuBFM12kmjtKEmmYUYt-BI6UYqBbReQrm9c",
        'Host':'www.xiami.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    page = 102
    html = get_page(baseurl,header,page)
    for songurl in get_song_url(html):
        fullurl = 'http://www.xiami.com' + songurl
        code = get_song_page(fullurl)
        result = get_info(code)
        save_to_mongo(result)


start()