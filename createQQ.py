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
