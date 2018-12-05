# -*- coding: UTF-8 -*-
import time
import json
import sys
import requests

'''
名称：安全教育学习无人值守脚本

作者：bufbrane(请访问bufbrane.com)

开发环境：
    系统版本：Windows10 64-bit
    Python版本：3.6.5 64-bit
    requests库版本：2.19.1

测试环境：
    系统版本：Ubuntu 18.04 LTS 64-bit
    Python版本：2.7.15 64-bit
    requests库版本：2.20.1

注意事项：
1. 使用方法：命令行运行（如下），参数为学号和密码（默认密码123456）
$ python safety_study.py <student_id> [password]

2. 本脚本需要安装requests库和json库，使用pip命令安装：
# pip install requests 
# pip install json

3. 此学习网站需要客户端每分钟发送一次学习数据，因此本脚本必须保持运行直至时间刷满2小时。
PS.必须保证运行满2个小时，尚无改进方法（毕竟前端调用无力改变后端的脑残设定）
Linux用户可以试试作为后台进程运行。

4. 如果想并行刷多个人的学习时间，建议用shell脚本开多进程。
本脚本暂未提供刷多个人的学习时间的功能（因为这样有潜在的风险）

'''

hostIP = "http://222.197.182.137"
UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"


# POST模拟登录，拿到登陆后的cookies（这一步必须完成）
class ExamLogin(object):

    def __init__(self, uestc_id="", password=""):
        self.cookies = ""
        self.endpoint = r"/exam_login.php"
        self.url = "".join([hostIP, self.endpoint])
        self.headers = \
            {
                "Accept": accept,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
                "User-Agent": UserAgent,
                "Referer": hostIP,
                "Content-Type": "application/x-www-form-urlencoded",
                "Upgrade-Insecure-Requests": "1",
                "Proxy-Connection": "keep-alive",
                "Content-Length": "90",
                "Cache-Control": "max-age=0",
                "Origin": hostIP
            }
        self.data = "xuehao=" + uestc_id + "&" + \
                    "password=" + password + \
                    "&postflag=1&cmd=login&role=0&%CC%E1%BD%BB=%B5%C7%C2%BC" # 这一串是固定内容，不要修改

    def get_page(self):
        r = requests.post(self.url, headers=self.headers, data=self.data)
        r.raise_for_status()
        self.cookies = r.cookies["wsess"]

    def get_cookies(self):
        return self.cookies


# 定时发送POST签到（60秒一次）
class TimingPost(object):
    def __init__(self, cookies="", uestc_id=""):
        self.uestc_id = uestc_id
        self.cookies = dict(wsess=cookies)
        self.endpoint = r"/exam_xuexi_online.php"
        self.url = "".join([hostIP, self.endpoint])
        self.headers = \
            {
                "Host": "222.197.182.137",
                "Content-Length": "16",
                "Accept": "*/*",
                "Origin": hostIP,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": UserAgent,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": hostIP + "/redir.php?catalog_id=121&object_id=2737",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
                "Connection": "close"
            }
        self.data = "cmd=xuexi_online"

    def get_page(self):
        r = requests.post(url=self.url, headers=self.headers, cookies=self.cookies, data=self.data)
        r.raise_for_status()
        jtext = json.loads(r.text)
        print( "学号：", self.uestc_id, "学习时间：", jtext['shichang'])


def main():

    # 从shell读取命令
    if len(sys.argv) == 1:
        print("Usage: python ./safety_study.py <student_id> [password]")
        print("The student_id is UESTC student id which consists of 13 numbers")
        print("The initial password is '123456'")
        exit(-1)
    elif len(sys.argv) == 2:
        uestc_id = sys.argv[1]
        password = "123456"
    elif len(sys.argv) == 3:
        uestc_id = sys.argv[1]
        password = sys.argv[2]

    # 模拟登录
    login = ExamLogin(uestc_id, password)
    login.get_page()

    # 获取登录后的cookies
    cookies = login.get_cookies()

    # 提示信息
    print("本脚本每分钟会向系统注册一次，请务必保持本脚本一直运行！")

    # 每分钟POST一次学习动态（稳妥起见至少运行125分钟）
    for i in range(125):
        TimingPost(cookies, uestc_id).get_page()
        time.sleep(60)  # 这里是阻塞调用。愚以为没有必要在此使用非阻塞，毕竟后端计时不是并发的，有些事急不得

if __name__ == '__main__':
    main()