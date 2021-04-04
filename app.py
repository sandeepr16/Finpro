from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from GoogleNews import GoogleNews
from nsetools import Nse
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy
import datetime
from pandas_datareader import data as wb
import os
import requests
app = Flask(__name__, template_folder='templates')
nse = Nse()
tg = nse.get_top_gainers()
tl = nse.get_top_losers()
nseid = ''


@app.route('/', methods=['GET'])
def Home():
    return render_template('index.html')


@app.route('/ind', methods=['GET'])
def ind():
    return render_template('index.html')


@app.route('/comp', methods=['GET'])
def comp():
    return render_template('stockf.html')


@app.route('/single', methods=['GET', 'POST'])
def single():
    for filename in os.listdir('static/images/'):
        if filename.startswith('graph'):
            os.remove('static/images/' + filename)
    s1 = request.form["companyname"]
    if(s1 == ''):
        return render_template('error.html')
    name1, st1, we1, op1, tt1, x1, y1, url1 = myfun(s1, 0)
    return render_template('blog-single.html', urla=url1, compname=name1, strn=st1, weak=we1, oppr=op1, thrt=tt1, headings=x1, values=y1, name11="STRENGTH", name2="WEAKNESS", name3="OPPURTUNITIES", name4="THREATS", tit="SWOT ANALYSIS")


@app.route('/nnn', methods=['GET', 'POST'])
def nnn():
    googlenews = GoogleNews()
    googlenews.search('NSE news')
    googlenews.clear()
    googlenews.getpage(0)
    result = googlenews.result()
    news = []
    ns = []
    for i in range(6):
        ns.append(result[i]['title'])
        ns.append(result[i]['date'])
        ns.append(result[i]['desc'])
        ns.append(result[i]['link'])
        news.append(ns)
        ns = []
    return render_template('snews.html', ne=news)


@app.route('/snews', methods=['GET', 'POST'])
def snews():
    s1 = request.form["companyname"]
    x = getnews(s1)
    return render_template('snews.html', ne=x)


def getnews(s):
    filedf = pd.read_csv('News.csv')
    nse = filedf[filedf['Company Name'] == s]
    nse = list(nse['NSE'])
    nse1 = nse[0]
    dfr = pd.DataFrame(filedf.loc[filedf['NSE'] == nse1].dropna(axis=1))
    qx = list(dfr.columns[3:])
    qyy = dfr.values.tolist()[0][3:]
    l = [qyy[:4], qyy[4:8], qyy[8:]]
    return l


@app.route('/predict', methods=['GET'])
def predict():
    return render_template("predic.html")


@app.route('/beta', methods=['POST'])
def beta():
    s = request.form["companyname"]
    filedf = pd.read_csv('News.csv')
    nse = filedf[filedf['Company Name'] == s]
    nse = list(nse['NSE'])
    b1 = nse[0]
    x = b1+'.NS'
    tickers = [x, '^NSEI']
    data = pd.DataFrame()
    for t in tickers:
        data[t] = wb.DataReader(t, data_source='yahoo', start=datetime.datetime.now(
        ) - datetime.timedelta(days=5*365), end=datetime.datetime.now())['Close']
    returns = np.log(data / data.shift(1))
    coveriance = returns.cov() * 250
    cov_with_market = coveriance.iloc[0, 1]
    market_var = returns.iloc[:, 1].var() * 250
    beta = cov_with_market / market_var
    stock_expected_return = 0.0604 + beta * 0.075
    # Risk Free Premium and Risk Free Returns(10 Year Gov Bond) as on 1 Oct 2020
    sharpe_ratio = (stock_expected_return - 0.05996) / \
        (returns.iloc[:, 0].std() * 250 ** 0.5)
    beta = round(beta, 2)
    stock_expected_return = str(round(stock_expected_return, 2)*100)+"%"
    sharpe_ratio = str(round(sharpe_ratio, 2)*100)+"%"
    return render_template("predic.html", compname=s, beta=beta, sre=stock_expected_return, sr=sharpe_ratio)


@app.route('/gainloss', methods=['GET'])
def gainloss():
    dfg = pd.DataFrame(columns=['Stock', 'Price', 'Gain'])
    dfl = pd.DataFrame(columns=['Stock', 'Price', 'Loss'])
    url = 'https://www.moneycontrol.com/stocks/marketstats/nsegainer/index.php'
    data = requests.get(url)
    soup = BeautifulSoup(data.text,  'lxml')
    gdp_table = soup.find_all("td", attrs={"class": "PR"})
    gtitles = []
    gtabledata = []
    gprice = []
    gpercentage = []
    for i in range(5):
        gdp_table_data = gdp_table[i].find_all("a")
        gtitles.append(gdp_table_data[0].text)
    table = soup.find(text=gtitles[1]).find_parent("table")
    print(table)
    for row in table.find_all("tr")[:]:
        gtabledata.append([cell.get_text(strip=True)
                           for cell in row.find_all("td")])
    j = 1
    for i in range(5):
        gprice.append(gtabledata[j][3])
        gpercentage.append(gtabledata[j][5])
        j += 7
    lurl = 'https://www.moneycontrol.com/stocks/marketstats/nseloser/index.php'
    ldata = requests.get(lurl)
    lsoup = BeautifulSoup(ldata.text,  'lxml')
    lgdp_table = lsoup.find_all("td", attrs={"class": "PR"})
    ltitles = []
    ltabledata = []
    lprice = []
    lpercentage = []
    for i in range(5):
        lgdp_table_data = lgdp_table[i].find_all("a")
        ltitles.append(lgdp_table_data[0].text)
    ltable = lsoup.find(text=ltitles[1]).find_parent("table")
    for row in ltable.find_all("tr")[:]:
        ltabledata.append([cell.get_text(strip=True)
                           for cell in row.find_all("td")])
    lj = 1
    for i in range(5):
        lprice.append(ltabledata[lj][3])
        lpercentage.append(ltabledata[lj][5])
        lj += 7

    dfg['Stock'] = gtitles
    dfg['Price'] = gprice
    dfg['Gain'] = gpercentage
    dfl['Stock'] = ltitles
    dfl['Price'] = lprice
    dfl['Gain'] = lpercentage
    return render_template('gainloss.html', sg=dfg['Stock'], pg=dfg['Price'], gg=dfg['Gain'], sl=dfl['Stock'], pl=dfl['Price'], ll=dfl['Loss'])


@app.route('/swot', methods=['GET', 'POST'])
def swot():
    for filename in os.listdir('static/images/'):
        if filename.startswith('graph'):
            os.remove('static/images/' + filename)
    s1 = request.form["companyname"]
    if(s1 == ''):
        return render_template('error.html')
    name1, st1, we1, op1, tt1, x1, y1, url1 = myfun(s1, 0)
    s2 = request.form["companyname1"]
    if (s2 == ''):
        return render_template('error.html')
    name2, st2, we2, op2, tt2, x2, y2, url2 = myfun(s2, 1)
    return render_template("stock.html", urla=url1, urlb=url2, compname=name1, strn=st1, weak=we1, oppr=op1, thrt=tt1, headings=x1, values=y1, compname1=name2, strn1=st2, weak1=we2, oppr1=op2, thrt1=tt2, headings1=x2, values1=y2, name11="STRENGTH", name2="WEAKNESS", name3="OPPURTUNITIES", name4="THREATS")


def myfun(s, count):
    new_graph_name = ""
    imgurl = ""
    df = pd.read_csv('Swot.csv')
    nse = df[df['Title'] == s]
    nse = list(nse['NSE'])
    nse1 = nse[0]
    p = df[df["NSE"] == nse1]
    st = []
    we = []
    op = []
    tt = []
    for x in p["Strength"]:
        x = list(map(str, x.split("', '")))
        for o in x:
            st.append(o.replace("']", "").replace("['", ""))
    for x in p["Weakness"]:
        x = list(map(str, x.split("', '")))
        for o in x:
            we.append(o.replace("']", "").replace("['", ""))
    for x in p["Oppurtunity"]:
        x = list(map(str, x.split("', '")))
        for o in x:
            op.append(o.replace("']", "").replace("['", ""))
    for x in p["Threat"]:
        x = list(map(str, x.split("', '")))
        for o in x:
            tt.append(o.replace("']", "").replace("['", ""))
    filedf = pd.read_csv('BaseData.csv')
    dfr = pd.DataFrame(filedf.loc[filedf['NSE'] == nse1].dropna(axis=1))
    qx = list(dfr.columns[3:])
    qyy = dfr.values.tolist()[0][3:]
    qy = []
    for j in range(len(qyy)):
        qy.append(qyy[j])
    Finaldf = []
    for k in range(4):
        filelist = ["Quarterly.csv", "pandlNetp.csv",
                    "Cash-flow.csv", "Balance Sheet.csv"]
        filedf = pd.read_csv(filelist[k])
        dfr = pd.DataFrame(filedf.loc[filedf['NSE'] == nse1].dropna(axis=1))
        qxx = list(dfr.columns[3:])
        qyyyy = dfr.values.tolist()[0][3:]
        qyyy = []
        for j in range(len(qyyyy)):
            qyyy.append(qyyyy[j])
        Finaldf.append(qxx)
        Finaldf.append(qyyy)
    plottitle = ["", "Quarterly Results",
                 "Profit and Loss", "Cash Flow", "Balance Sheet"]
    xlabels = ['', 'Quarters', 'Years', 'Years']
    ylabels = ['', 'Net Profit', 'Net Profit', 'Net Cash Flow']
    fig, ax = plt.subplots(4, 1, figsize=(18, 20))
    it = 0
    for i in range(3):
        ax[i].plot(Finaldf[it], Finaldf[it+1])
        ax[i].axhline(0, color='black')
        ax[i].set_xlabel(xlabels[i+1])
        ax[i].set_ylabel(ylabels[i+1])
        ax[i].set_title(plottitle[i+1])
        it = it+2
    x = np.arange(len(Finaldf[7]))
    width = 0.3
    rects1 = ax[3].bar(x - width/2, Finaldf[7], width, label='Assets')
    rects2 = ax[3].bar(x + width/2, Finaldf[7], width, label='Liabilities')
    ax[3].set_ylabel('Amount in Crores')
    ax[3].set_title(plottitle[4])
    ax[3].set_xticks(x)
    ax[3].set_xticklabels(Finaldf[6])
    ax[3].legend()
    if count == 0:
        new_graph_name = "graph" + str(time.time()) + ".png"
        plt.savefig('static/images/' + new_graph_name)
        imgurl = 'static/images/' + new_graph_name
    else:
        new_graph_name = "graph1" + str(time.time()) + ".png"
        plt.savefig('static/images/' + new_graph_name)
        imgurl = 'static/images/' + new_graph_name
    return s, st, we, op, tt, qx, qy, imgurl


if __name__ == "__main__":
    app.run(debug=True)
