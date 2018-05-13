自学过一段时间的python，用django自己做了个[网站](http://blog.manjiexiang.cn/)，也用`requests`+`BeautifulSoup`爬虫过些简单的网站，周末研究学习了一波，准备爬取QQ空间的说说，并把内容存在txt中，读取生成云图。     
好久不登qq了，空间说说更是几年不玩了，里面满满的都是上学时候的回忆，看着看着就笑了，笑着笑着就...哈哈哈~~  
无图言虚空

![](https://user-gold-cdn.xitu.io/2018/5/12/1635369c27d464b3?w=2000&h=1200&f=png&s=1409607)  
当年的我还是那么风华正茂、幽默风趣...  
言归正传，本次使用的是`selenium`模拟登录+`BeautifulSoup4`爬取数据+`wordcloud`生成词云图  
#### BeautifulSoup安装
`pip install beautifulsoup4`  
这里有beautifulsoup4 的 [官方文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html)  
还需要用到解析器，我选择的是`html5lib`解析器`pip install html5lib`  
下表列出了主要的解析器,以及它们的优缺点:

解析器	| 使用方法	| 优势	| 劣势
---|---| --- | ---
Python标准库 | BeautifulSoup(markup, "html.parser")| Python的内置标准库      执行速度适中  文档容错能力强| Python 2.7.3 or 3.2.2)前 的版本中文档容错能力差
lxml HTML 解析器 | BeautifulSoup(markup, "lxml")|速度快  文档容错能力强|需要安装C语言库
lxml XML 解析器	|BeautifulSoup(markup, ["lxml", "xml"])         BeautifulSoup(markup, "xml") | 速度快 唯一支持XML的解析器|需要安装C语言库
html5lib|BeautifulSoup(markup, "html5lib")	|最好的容错性 以浏览器的方式解析文档  生成HTML5格式的文档|速度慢 不依赖外部扩展

#### selenium模拟登录
使用selenium模拟登录QQ空间，安装`pip install selenium`  
我用的是chrom浏览器，`webdriver.Chrome()`，获取Chrome浏览器的驱动。  
这里还需要下载安装对应浏览器的驱动，否则在运行脚本时，会提示 
`chromedriver executable needs to be in PATH`错误，用的是mac，网上找的一篇下载驱动的文章，https://blog.csdn.net/zxy987872674/article/details/53082896  
同理window的也一样，下载对应的驱动，解压后，将下载的**.exe 放到Python的安装目录，例如 D:\python 。 同时需要将Python的安装目录添加到系统环境变量里。

qq登录页http://i.qq.com，利用webdriver打开qq空间的登录页面  
```
driver = webdriver.Chrome()
driver.get("http://i.qq.com")
```
![](https://user-gold-cdn.xitu.io/2018/5/12/163536e12d050219?w=520&h=300&f=jpeg&s=67430)  
打开之后右击检查查看页面元素，发现帐号密码登录在`login_frame`里，先定位到所在的frame，`driver.switch_to.frame("login_frame")`  ，再自动点击 帐号密码登录 按钮，自动输入帐号密码登录，并且打开说说页面，详细代码如下
```
friend = '' # 朋友的QQ号，**朋友的空间要求允许你能访问**，这里可以输入自己的qq号
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
 # 让webdriver操纵当前页
driver.switch_to.default_content()
 # 跳到说说的url, friend可以任意改成你想访问的空间，比如这边访问自己的qq空间
driver.get("http://user.qzone.qq.com/" + friend + "/311")
```

这个时候可以看到已经打开了qq说说的页面了，**注意** 部分空间打开之后会出现一个提示框，需要先模拟点击事件关闭这个提示框  

![](https://user-gold-cdn.xitu.io/2018/5/12/1635371e3cdf6fec?w=470&h=300&f=jpeg&s=52704)  
tm我以前竟然还有个黄钻，好可怕~~，空间头像也是那么的年轻、主流...
```
try:
    #找到关闭按钮，关闭提示框
    button = driver.find_element_by_id("dialog_button_111").click()
except:
    pass
```
同时因为说说内容是动态加载的，需要自动下拉滚动条，加载出全部的内容，再模拟点击 下一页 加载内容。具体代码见下面。  
#### BeautifulSoup爬取说说
F12查看内容，可以找到说说在`feed_wrap`这个`<div>`，`<ol>`里面的`<li>`标签数组里面，具体每条说说内容在`<div>` `class="bd"`的`<pre>`标签中。  
![](https://user-gold-cdn.xitu.io/2018/5/12/16353779f970d155?w=725&h=300&f=jpeg&s=85233)  
```

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

```
至此QQ说说已经爬取下来，并且保存在了`qq_word`文件里  
接下来生成词云图
#### 词云图
使用`wordcloud`包生成词云图，`pip install wordcloud`  
这里还可以使用`jieba`分词，我并没有使用，因为我觉得qq说说的句子读起来才有点感觉，个人喜好，用`jieba`分词可以看到说说高频次的一些词语。  
设置下wordcloud的一些属性，**注意** 这里要设置`font_path`属性，否则汉字会出现乱码。  
这里还有个要提醒的是，如果使用了虚拟环境的，不要在虚拟环境下运行以下脚本，否则可能会报错 `RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework. See the Python documentation for more information on installing Python as a framework on Mac OS X. Please either reinstall Python as a framework, or try one of the other backends. If you are using (Ana)Conda please install python.app and replace the use of 'python' with 'pythonw'. See 'Working with Matplotlib on OSX' in the Matplotlib FAQ for more information.` ，我就遇到了这种情况，`deactivate` 退出了虚拟环境再跑的
```
# coding:utf-8

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 生成词云
def create_word_cloud(filename):
    # 读取文件内容
    text = open("{}.txt".format(filename), encoding='utf-8').read()
    # 设置词云
    wc = WordCloud(
        # 设置背景颜色
        background_color="white",
        # 设置最大显示的词云数
        max_words=2000,
        # 这种字体都在电脑字体中，window在C:\Windows\Fonts\下，mac我选的是/System/Library/Fonts/PingFang.ttc 字体
        font_path='/System/Library/Fonts/PingFang.ttc',
        height=1200,
        width=2000,
        # 设置字体最大值
        max_font_size=100,
        # 设置有多少种随机生成状态，即有多少种配色方案
        random_state=30,
    )

    myword = wc.generate(text)  # 生成词云
    # 展示词云图
    plt.imshow(myword)
    plt.axis("off")
    plt.show()
    wc.to_file('qq_word.png')  # 把词云保存下


if __name__ == '__main__':
    create_word_cloud('qq_word')

```
至此，爬取qq说说内容，并生成词云图。  
源码github地址: [https://github.com/taixiang/spiderQQ](https://github.com/taixiang/spiderQQ)

 
欢迎关注我的博客：[http://blog.manjiexiang.cn/](http://blog.manjiexiang.cn/)  
欢迎关注微信号：春风十里不如认识你  
![image.png](https://upload-images.jianshu.io/upload_images/7569533-cfeb1f55473a2143.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

