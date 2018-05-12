# coding:utf-8

import time
from selenium import webdriver
from bs4 import BeautifulSoup

import importlib

# 这里一定要设置编码格式，防止后面写入文件时报错
# 爬取QQ说说内容


friend = ''  # 朋友的QQ号，**朋友的空间要求允许你能访问**，这里可以输入自己的qq号
user = ''  # 你的QQ号
pw = ''  # 你的QQ密码

# 获取浏览器驱动
driver = webdriver.Chrome()

# 浏览器窗口最大化
driver.maximize_window()

# 浏览器地址定向为qq登陆页面
driver.get("http://i.qq.com")

# 定位到登录所在的frame
driver.switch_to.frame("login_frame")

# 自动点击账号登陆方式
driver.find_element_by_id("switcher_plogin").click()

# 账号输入框输入已知qq账号
driver.find_element_by_id("u").send_keys(user)

# 密码框输入已知密码
driver.find_element_by_id("p").send_keys(pw)

# 自动点击登陆按钮
driver.find_element_by_id("login_button").click()

time.sleep(0.1)
# 让webdriver操纵当前页
driver.switch_to.default_content()

# 跳到说说的url, friend可以任意改成你想访问的空间，比如这边访问自己的qq空间
driver.get("http://user.qzone.qq.com/" + friend + "/311")

try:
    # 找到关闭按钮，关闭提示框
    button = driver.find_element_by_id("dialog_button_1").click()
except:
    pass

next_num = 0  # 初始“下一页”的id
while True:
    # 下拉滚动条，使浏览器加载出全部的内容，
    # 这里是从0开始到5结束 分5 次加载完每页数据
    for i in range(0, 5):
        height = 20000 * i  # 每次滑动20000像素
        strWord = "window.scrollBy(0," + str(height) + ")"
        driver.execute_script(strWord)
        time.sleep(2)

    # 这里需要选中 说说 所在的frame，否则找不到下面需要的网页元素
    driver.switch_to.frame("app_canvas_frame")
    # 解析页面元素
    content = BeautifulSoup(driver.page_source, "html5lib")
    # 找到"feed_wrap"的div里面的ol标签
    ol = content.find("div", class_="feed_wrap").ol
    # 通过find_all遍历li标签数组
    lis = ol.find_all("li", class_="feed")

    # 将说说内容写入文件，使用 a 表示内容可以连续不清空写入
    with open('qq_word.txt', 'a', encoding='utf-8') as f:
        for li in lis:
            bd = li.find("div", class_="bd")
            #找到具体说说所在标签pre，获取内容
            ss_content = bd.pre.get_text()
            f.write(ss_content + "\n")

    # 当已经到了尾页，“下一页”这个按钮就没有id了，可以结束了
    if driver.page_source.find('pager_next_' + str(next_num)) == -1:
        break
    # 找到“下一页”的按钮，因为下一页的按钮是动态变化的，这里需要动态记录一下
    driver.find_element_by_id('pager_next_' + str(next_num)).click()
    # “下一页”的id
    next_num += 1
    # 因为在下一个循环里首先还要把页面下拉，所以要跳到外层的frame上
    driver.switch_to.parent_frame()
