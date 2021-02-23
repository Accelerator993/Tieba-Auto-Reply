#! python3.7.4
# -*- coding:utf-8 -*-
# By Accelerator993

import json
import os
import time
import re
import pickle
from selenium import webdriver # 从selenium导入webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait #显式等待
from selenium.webdriver.support import expected_conditions as EC #显式等待条件
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


#get直接返回，不再等待界面加载完成（百度登录页加载比较慢，不需要加载那么多东西）
desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["pageLoadStrategy"] = "none"


# 环境配置
chromedriver = "C:\Program Files\Google\Chrome\Application" #你的浏览器安装位置
os.environ["webdriver.Chrome.driver"] = chromedriver


# 创建一个浏览器对象


class ShuiTie1():
    def __init__(self, username, userpwd, bar, zhiding,shuitieshu,reply_text):
        self.wd = webdriver.Chrome(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver") #webdriver的位置
        # 以wd代替webdriver      # 打开Chrome浏览器

        # 以无头模式打开浏览器
        '''
        opt = Options()
        opt.add_argument('--headless')
        opt.add_argument('--disable-gpu')
        self.wd = webdriver.Chrome(options=opt)
        '''
        self.wd.maximize_window()  # 全屏
        self.wd.implicitly_wait(10)  # 设置隐式等待为5秒
        self.url = 'https://tieba.baidu.com'
        self.username = username
        self.userpwd = userpwd

        self.zhiding = zhiding  # 输入每个吧中的置顶帖数量
        self.shuitieshu=shuitieshu #输入每个贴吧水几贴
        self.reply_text=reply_text #记录水贴内容
        # self.wd.set_page_load_timeout(45) #设置网页超时时间
        # self.wd.set_script_timeout(45)


        self.Login()  # 登陆百度贴吧
        time.sleep(3)

        self.bar=bar
        self.Select_Bar()  # 选择进入的贴吧
        self.pos_url = []  # 初始化存储获取到的帖子的链接
        time.sleep(10)
        self.Get_Url()  # 获取当前首页所有帖子的链接
        time.sleep(10)
        self.Send_Msg()  # 在每个帖子中回复消息
        self.wd.get(self.url) # 返回贴吧首页
        time.sleep(10)
        self.quit()


    def getTaobaoCookies(self):
        print("Please login in Tieba")
        # 点击通过用户名密码登陆
        self.wd.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__footerULoginBtn"]').click()
        # 输入用户名及密码
        self.wd.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__userName"]').send_keys(self.username)
        self.wd.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__password"]').send_keys(self.userpwd)
        time.sleep(2)

        # 点击登录按钮
        self.wd.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__submit"]').click()
        # 贴吧登陆大概率需要验证，此处留下60秒验证登陆
        # try:
        #     self.wd.find_element_by_xpath('//*[@id="TANGRAM__18__button_send_mobile"]').click() #点击发送验证码按钮
        # except:
        #     pass
        time.sleep(30)
        while True:
            print(self.wd.current_url)
            self.wd.get(self.url)
            time.sleep(10)
            if self.wd.current_url=="https://tieba.baidu.com/":
                break
            # if login in successfully, url  jump to tieba.baidu.com

        print("Login successfully!")
        self.tbCookies = self.wd.get_cookies()
        cookies = {}
        for item in self.tbCookies:
            cookies[item['name']] = item['value']
        outputPath = open('tiebaCookies.pickle', 'wb')
        pickle.dump(cookies, outputPath)
        outputPath.close()
        return cookies




    def readTaobaoCookies(self):
        # if have cookies file ,use it
        # if not , getTiebaCookies()
        if os.path.exists('tiebaCookies.pickle'):
            readPath = open('tiebaCookies.pickle', 'rb')
            tbCookies = pickle.load(readPath)
        else:
            tbCookies = self.getTaobaoCookies()
        return tbCookies


    def Login(self):
        self.wd.get(self.url)
        time.sleep(20)
        tbCookies = self.readTaobaoCookies()

        self.wd.get(self.url)
        for cookie in tbCookies:
            self.wd.add_cookie({
                "domain": ".baidu.com",
                "name": cookie,
                "value": tbCookies[cookie],
                "path": '/',
                "expires": None
            })
        self.wd.get(self.url)

    def Select_Bar(self):  # 在搜索框输入要进入的贴吧并点击进入
        self.wd.find_element_by_id('wd1').send_keys(self.bar)
        time.sleep(1)
        self.wd.find_element_by_xpath('//*[@id="tb_header_search_form"]/span[1]/a').click()

    def Get_Url(self):  # 获取当前首页的帖子的链接
        html = self.wd.page_source
        # 此处本来是想用xpath来获取链接的，但是要获取的路径class标签中有空格，试了一下通过xpath没有获取到，
        # 后改用re来匹配，用re匹配有一个缺点，会匹配到置顶帖，包括吧规贴...所以在后续发送信息时会跳过这些帖子
        res = '<a rel="noreferrer" href="(.*?)".*?target="_blank" class="j_th_tit ">'
        self.pos_url = re.findall(res, html)  # 存储首页所有帖子的链接

    def Send_Msg(self):
        # with open('Msg.txt', 'r', encoding='utf-8') as f:  # 读取水贴的信息
        #     Msg = f.readlines()
        cishu=0 #初始化水贴计数器
        for i in range(self.zhiding, len(self.pos_url)):  # 有zhiding条置顶帖，在这里跳过
            # msg = Msg[i % len(Msg)]  # 循环选取要发送的信息

            msg= self.reply_text
            url = self.url + self.pos_url[i]  # 获取帖子的链接
            url_next = self.url + self.pos_url[i+1]
            self.wd.get(url)
            time.sleep(10)
            # title = self.wd.find_element_by_xpath('//h3').text  # 获取帖子的主题
            js = "window.scrollTo(0, document.body.scrollHeight)"
            self.wd.execute_script(js)  # 滑动滚动条到底部
            time.sleep(4)
            try:
                self.wd.find_element_by_id('ueditor_replace').send_keys(f'{msg}')  # 向输入框中添加信息
                time.sleep(4)
                current_window=self.wd.current_window_handle
                self.wd.find_element_by_xpath('//*[@id="tb_rich_poster"]/div[3]/div[3]/div/a').click() #//div[@class="j_floating"]//a[@title="Ctrl+Enter快捷发表"]
                print(f"水贴成功：{url}, 发送消息为:{msg} 下一水贴地址为{url_next}")
                time.sleep(1)
            except:
                print('此贴被删除或者是已被禁言')
                continue
            try: # close windows
                windows=self.wd.window_handles
                windows.remove(current_window)
                self.wd.switch_to.window(windows[1])
                self.wd.close()  # 关闭浏览器新窗口
                self.wd.switch_to.window(windows[0])
                self.wd.close()  # 关闭浏览器新窗口
                self.wd.switch_to.window(current_window)
            except:
                pass
            cishu=cishu+1 #计数器+1
            if cishu>self.shuitieshu:
                break #中止水贴
            time.sleep(20)  # 水贴间隔




if __name__ == '__main__':
    # Exp = ShuiTie('你的贴吧用户名', '你的贴吧密码', ['贴吧名'], 前面几贴不水（避开置顶帖），一个贴吧一次水几贴,水贴内容)
    bars=['你要水贴的贴吧']
    # 在这里修改你的设置，用因为分隔符,和引号""隔开你想要水的贴吧吧名
    for bar in bars:
        Exp = ShuiTie1('用户名','密码', bar, 5,7,"听说这个挺多经验的， ิۖิۣ ۣۣۖۖۖۖิۖิิۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۖ~\n\t\t　ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิ ۖิิۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิ\n\t\t ิۖิۣ ۣۣۖۖۖۖิۖิิۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۖ\n\t\t　ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิ ۖิิۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิۖิิ ۣۣۖۖ ۖ ۣۣۖۖิ ۖิิۣۣۖۖิۣ ۣۣۖۖۖิ")
        #在这里修改你的设置，如果是第一次运行或者cookie失效则请注意在登录是手动进行登录验证操作

