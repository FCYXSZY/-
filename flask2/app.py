import time
import os
from waitress import serve
from flask import Flask
from jinja2 import Environment,FileSystemLoader
from markupsafe import Markup
from pyecharts.globals import CurrentConfig
import pandas as pd
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))
from flask import render_template
from pyecharts import  options as opts
from pyecharts.charts import  Bar,Line,Timeline,WordCloud,EffectScatter
import DAO
app = Flask(__name__)
data = ''
def pre():
    global data
    sql = "select * from test"
    data = DAO.select_data(sql)



def webFlow_base()->Bar:
    result = data.groupby('日期').agg({'浏览': 'sum'}).to_dict()['浏览']
    # result

    c = (
        Line()
        .add_xaxis(list(result.keys()))
        .add_yaxis('浏览量', list(result.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="网站每日流量变化图")
                         ,datazoom_opts=opts.DataZoomOpts(range_start=10,range_end=30))

    )
    return c
def firstTenWriter_base()->Timeline:
    t2 = Timeline()
    t2.add_schema(
        is_auto_play=True,
        is_loop_play=True,
        play_interval=4000
    )

    dates = data['日期'].unique()
    for date in dates:
        top10 = (
            data[data.日期 == date]
            .groupby('作者')
            .agg({'评分': 'mean'})
            .nlargest(10, '评分').round(2)  # 取前十
            .reset_index()
        )

        # 创建柱状图
        bar = (
            Bar()
            .add_xaxis(top10['作者'].tolist())
            .add_yaxis(
                "评分 (柱状图)",
                top10['评分'].tolist(),
                label_opts=opts.LabelOpts(
                    is_show=True,
                    position="inside",
                )
            )
        )

        # 创建折线图
        line = (
            Line()
            .add_xaxis(top10['作者'].tolist())
            .add_yaxis(
                "评分趋势 (折线图)",
                top10['评分'].tolist(),
                is_smooth=True,  # 平滑曲线
                label_opts=opts.LabelOpts(
                    is_show=True,  # 显示标签
                    formatter="{b}"  # 只显示名称 (作者)
                )
            )
        )

        # 将柱状图叠加到折线图上
        line.overlap(bar)

        # 设置折线图的 zindex 为 20，确保它在柱状图的上层
        line.set_series_opts(zindex=10)

        # 设置全局选项
        line.set_global_opts(
            title_opts=opts.TitleOpts(title=f"日期 {date} 前十作家评分"),
            xaxis_opts=opts.AxisOpts(name="作者", axislabel_opts=opts.LabelOpts(rotate=30)),  # 旋转 x 轴标签
            yaxis_opts=opts.AxisOpts(name="评分"),
            legend_opts=opts.LegendOpts(pos_top="5%")  # 调整图例位置
        )

        # 添加到时间轴
        t2.add(line, date)

    return t2

def writer_base() -> Timeline:
    # 动态展示网站作家每日评分变化
    t2 = Timeline()
    t2.add_schema(
        is_auto_play=True,
        is_loop_play=True,
        play_interval=2000
    )

    writers = data.作者.unique()
    for w in writers:
        item = data[data.作者 == w].groupby('日期').agg({'评分': 'mean'}).to_dict()['评分']

        bar = (
            Bar()
            .add_xaxis(list(item.keys()))
            .add_yaxis('评分', [round(val, 2) for val in item.values()],
                       label_opts=opts.LabelOpts(
                           is_show=True,  # 显示标签
                           position="top",  # 标签显示在柱状图上方
                           formatter= w  # `{b}` 将显示每个柱子对应的 x 轴值（这里是作者名字）
                            )
                    )
            .set_global_opts(title_opts=opts.TitleOpts(title="作家 {} 评分变化图".format(w)))
        )

        #     break;
        t2.add(bar, w)
    return t2


def hotWord_base()->WordCloud:
    # 热点标签生成
    label_value = {}

    for i in range(len(data)):
        if data['收藏'][i] >= 1000:
            temp = data['类型'][i].split(',')
            temp = [var.replace('[', '').replace(']', '').replace("'", '').strip() for var in temp]
            temp = [var for var in temp if not var.endswith("users入り")]
            for v in temp:
                if v not in label_value.keys():
                    label_value[v] = 0
                label_value[v] += data['评分'][i]
    label_value = label_value.items()

    # 创建词云图
    c = (
        WordCloud()
        .add(series_name="热点标签", data_pair=label_value, word_size_range=[20, 80])  # 调整字体大小范围
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="热点标签", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
        .set_series_opts(
            #设置为菱形
            shape="star",  # 设置为菱形
            word_gap=5,  # 设置词与词之间的间距
            rotation_range=[-90, 90]  # 允许词云旋转
        )
    )

    # 调整图表的宽度和高度（可选，视需要）
    c.width = "100%"  # 设置为100%的宽度，适应屏幕
    c.height = "1050px"  # 设置词云图的高度
    return c

def effectScatter()->EffectScatter:
    x_data = data.日期.unique()
    y_data = data.groupby('日期').agg({'评分': 'mean'}).to_dict()['评分']

    c = (EffectScatter()
                     .add_xaxis(list(x_data))
                     .add_yaxis('评分', [int(i) for i in list(y_data.values())])
                     .set_global_opts(title_opts=opts.TitleOpts(title="网站每日评分变化图")
                                      , datazoom_opts=opts.DataZoomOpts(range_start=10, range_end=30))
                     )

    return c
@app.route("/webFlow")
def index():
    c = webFlow_base()
    c.render("static/webFlow.html")
    time.sleep(0.5)
    return render_template("webFlow.html")

@app.route("/firstTenWriter")
def index2():
    c = firstTenWriter_base()
    c.render("static/firstTenWriter.html")
    time.sleep(0.5)
    return render_template("firstTenWriter.html")
@app.route("/writer")
def index3():
    c = writer_base()
    c.render("static/writer.html")
    time.sleep(0.5)
    return render_template("writer.html")

@app.route("/hotWord")
def index4():

    c = hotWord_base()
    c.render("static/hotWord.html")
    time.sleep(0.5)
    return render_template("hotword.html")

@app.route("/effectScatter")
def index5():
    print(1)
    c = effectScatter()
    c.render("static/effectScatter.html")
    time.sleep(0.5)
    print(2)
    return render_template("effectScatter.html")

@app.route("/")
def index6():
    image_dir = r'./static/assets/img'
    image_paths = []

    # 遍历目录获取图片路径
    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # 将图片路径添加到列表中
            static_image_path=os.path.join('static','assets', 'img', filename)
            if not os.path.exists(static_image_path):
                os.rename(os.path.join(image_dir, filename), static_image_path)
                print(f"移动文件: {filename} 到 {static_image_path}")
            image_paths.append(static_image_path)
    return render_template("index.html", image_paths=image_paths)


if __name__ == "__main__":
    pre()
    print(type(data))
    serve(app, host='0.0.0.0', port=8000)
    #app.run(host='0.0.0.0',port=5000)

