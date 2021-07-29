import requests
import random
import time
import re
import datetime
import json
##################参数####################
##########COOKIE可以手动指定你的cookie#####
##########覆盖之后cookie.txt失效##########
COOKIE=''
AUTOCOMMENT=True#修改为False则不自动复制热评回复
BOARDID=''#需要在哪个板块操作 5433318--为开发版公测 5428803--开发版内测 ，请确保有对应的浏览权限。
##########################################
#点赞评论都是这种
base_header = {
    "Host": "prod.api.xiaomi.cn",
    "Connection": "keep-alive",
    "sec-ch-ua": 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "Accept": "application/json",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Origin": "https://www.xiaomi.cn",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.xiaomi.cn/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
thumbup_API = 'https://prod.api.xiaomi.cn/community/post/thumbUp'
thumbup_data = {
    'X-CSRF-TOKEN': '',  # 防止csrf
    'postId': '',  # 帖子编号
    'vip_community_pc_ph': '',  # 账号相关
}
comment_API = 'https://prod.api.xiaomi.cn/community/post/comment/add'
comment_data = {
    'X-CSRF-TOKEN': '',
    'postId': '',  # 帖子编号
    'text': '',  # 评论文本内容
    'requestId': '',  # {cookie中的cUserId}:{时间戳,年份换为2001后的结果}:"{文本内容前四位}
    'vip_community_pc_ph': ''  # cookie中有
}
commentup_API = 'https://prod.api.xiaomi.cn/community/post/comment/thumbUp'
commentup_data = {
    'X-CSRF-TOKEN': '',
    'postId': '',  # 帖子编号
    'commentId': '',  # 评论编号
    'vip_community_pc_ph': '',  # 账号相关
}


class XM_BBS():
    def __init__(self, base_cookie) -> None:
        self.info = {}
        r = re.findall('([\S]*?)=([\S]*);?', base_cookie)
        if len(r) == 0:
            print("cookie错误！")
            exit(0)
        r = dict(r)
        for i in r:
            r[i] = r[i].replace(";", '')
        self.info = r

    @staticmethod
    def GenCsrfToken():
        token = ''
        random.seed(time.time())
        for i in range(8):
            d = random.randint(0, 65536)
            token += str(d)
        return token

    @staticmethod
    def XM_Time():
        t = datetime.datetime.now().replace(year=2001)
        if (t.second > 30):
            t = t.replace(second=30)
        else:
            t = t.replace(second=0)
        return int(t.timestamp())*1000

    def GenCookie(self):
        csrf_token = XM_BBS.GenCsrfToken()
        tmp = self.info
        tmp['X-CSRF-TOKEN'] = csrf_token
        cookie_str = ''
        for i in self.info:
            if cookie_str:
                cookie_str += "; "
            cookie_str += "{}={}".format(i, self.info[i])
        return cookie_str, csrf_token

    def thumbup(self, post_id):
        (cookie, csrf_token) = self.GenCookie()
        headers = base_header
        headers['Cookie'] = cookie
        data = thumbup_data
        data['X-CSRF-TOKEN'] = (None, csrf_token)
        data['postId'] = (None, post_id)
        data['vip_community_pc_ph'] = (None, self.info['vip_community_pc_ph'])
        res = requests.post(url=thumbup_API, headers=headers, files=data)
        res = res.json()
        try:
            if res['message'] == 'ok':
                return True
            else:
                print(res['message'])
                return False
        except:
            print(res)
            exit(-1)
    #stype latest
    def GetPosts(self, after, stype='hot', boardId=''):
        (cookie, csrf_token) = self.GenCookie()
        headers = base_header
        headers['Cookie'] = cookie
        if after == 0:
            after = ''
        #这个是获取已进入圈子的帖子的API
        if boardId == '':
            API = 'https://prod.api.xiaomi.cn/community/board/followed/announce/list?after={after}&limit=10&stype={stype}'.format(
                after=after,
                stype=stype
                )
        else:
            API = 'https://prod.api.xiaomi.cn/community/board/search/announce/list?after={after}&limit=10&boardId={boardId}&profileType=1&displayName=%E5%85%A8%E9%83%A8'.format(
                after=after,
                boardId=boardId
                )
        res = requests.get(url=API, headers=headers)
        return res.json()

    def Comment(self, text: str, postId):
        (cookie, csrf_token) = self.GenCookie()
        headers = base_header
        headers['Cookie'] = cookie
        data = comment_data
        data['X-CSRF-TOKEN'] = (None, csrf_token)
        data['postId'] = (None, postId)
        data['text'] = (None, text)
        IdStr = json.dumps(text, ensure_ascii=False)
        if len(IdStr) < 5:
            requestId = '{}:{}:{}'.format(
                self.info['cUserId'], XM_BBS.XM_Time(), IdStr)
        else:
            requestId = '{}:{}:{}'.format(
                self.info['cUserId'], XM_BBS.XM_Time(), IdStr[0:5])
        data['requestId'] = (None, requestId)
        data['vip_community_pc_ph'] = (None, self.info['vip_community_pc_ph'])
        res = requests.post(url=comment_API, headers=headers, files=data)
        res = res.json()
        try:
            if res['message'] == 'ok':
                return True
            else:
                print(res['message'])
                return False
        except:
            print(res)
            exit(-1)

    def thumbup_comment(self, post_id, commentId):
        (cookie, csrf_token) = self.GenCookie()
        headers = base_header
        headers['Cookie'] = cookie
        data = commentup_data
        data['X-CSRF-TOKEN'] = (None, csrf_token)
        data['postId'] = (None, post_id)
        data['commentId'] = (None, commentId)
        data['vip_community_pc_ph'] = (None, self.info['vip_community_pc_ph'])
        res = requests.post(url=commentup_API, headers=headers, files=data)
        res = res.json()
        try:
            if res['message'] == 'ok':
                return True
            else:
                print(res['message'])
                return False
        except:
            print(res)
            exit(-1)

    def GetComments(self, postId, after, sorttype=1):
        (cookie, csrf_token) = self.GenCookie()
        headers = base_header
        headers['Cookie'] = cookie
        if after == 0:
            after = ''
        API = 'https://prod.api.xiaomi.cn/community/post/comments?postId={postId}&after={after}&limit=10&sortType={sorttype}'.format(
            postId=postId, after=after, sorttype=sorttype)
        res = requests.get(url=API, headers=headers)
        return res.json()

#对一个帖子下方的评论进行点赞，并用热评回复（慎用）
def LikeComment(Client: XM_BBS, postId):
    counts = 10
    base = 0
    count = 0
    while (base < counts):
        comments = Client.GetComments(postId, base)
        counts = comments['entity']['total']
        res = comments['entity']['records']
        for i in res:
            count += 1
            if Client.thumbup_comment(postId, i['commentId']):
                print("["+str(count)+"]"+"评论"+'"'+i['text']+'"'+"点赞成功！")
                if AUTOCOMMENT and (count == 1):
                    if (Client.Comment(i['text'], postId)):
                        print("复制热评回复成功")
            else:
                return
        base += 10
        time.sleep(0.3)

#stype为帖子排序类型，lastest或hot
def AutoLike(Client: XM_BBS, stype='hot'):
    c = 0
    after=''
    for i in range(0, 1000): #最大1000
        posts = Client.GetPosts(after, stype ,boardId=BOARDID)
        after=posts['entity']['after']
        res = posts['entity']['records']
        for j in res:
            if not Client.thumbup(j['id']):
                exit(0)
            else:
                c += 1
                print("["+str(c)+"]"+'"'+j['summary']+'"'+"帖子点赞成功!")
                LikeComment(Client, j['id'])
            time.sleep(0.5)


if __name__ == '__main__':
    cookie=''
    if not COOKIE:
        try:
            with open("cookie.txt",'r',encoding='utf-8') as f:
                cookie=f.read()
        except:
            print("未在代码中指定cookie且cookie.txt不存在")
            exit(-1)
    else:
        cookie=COOKIE
    Client = XM_BBS(cookie)
    AutoLike(Client)
