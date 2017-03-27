import pandas as pd
import numpy as np
import matplotlib as plt
import quandl
import requests
from flask import Flask, render_template, request, redirect
import datetime as dt
import bokeh
from bokeh.embed import components
from bokeh.plotting import figure
import os

#quandl.ApiConfig.api_key = 'FAP42o7yZGu6XznAiLze'

#data = quandl.get_table('WIKI/PRICES') 

#fetch quandl dataset
def fetch_quandl(ticker, apiKey) :

    ticker = ticker.upper()

    now = dt.datetime.now().date()
    then = now - dt.timedelta(days=30)
    then = "&start_date=" + then.strftime("%Y-%m-%d")
    now  = "&end_date=" + now.strftime("%Y-%m-%d")

    r = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/' + ticker + '.json?api_key=FAP42o7yZGu6XznAiLze' + now + then)

    if r.status_code < 400 :
        # name of stock's company
        name = r.json()['dataset']['name']
        name = name.split('(')[0]

        # get data
        dat = r.json()['dataset']
        df = DataFrame(dat['data'], columns=dat['column_names'] )
        df = df.set_index(pd.DatetimeIndex(df['Date']))

    else :
        print "Stock ticker not valid"
        df = None
        name = None

    return df, name


#create plot
def stockplot(df, priceReq, tickerText ):

    print "priceReq : ", priceReq, type(priceReq)

    p = figure(x_axis_type="datetime", width=800, height=600)


    if type(priceReq) == list :
        for req in priceReq:
            p.line(df.index, df[priceReq[req]], legend=req, line_width='3')
    else :
        p.line(df.index, df[priceReq], legend=priceReq, line_width='3')

    p.title = tickerText + " Prices"

    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.legend.orientation = "up_left"

    if 0:
        bokeh.io.output_file('templates/page.html')
        bokeh.io.save(p)

    script, div = components(p)
    return script, div
    
                 
app = Flask(__name__)

app.vars = {}


@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('milestone.html')

@app.route('/plotpage', methods=['POST'])
def plotpage():
    tickStr = request.form['tickerText']
    reqList = request.form['priceCheck'] # checkboxes

    app.vars['ticker'] = tickStr.upper()
    app.vars['priceReqs'] = reqList

    df,name = fetch_quandl(app.vars['ticker'], app.vars['apiKey'])


    if not type(df) == DataFrame :
        msg = "Invalid Ticker."
        return render_template('milestone.html', msg=msg)
    else:
        script, div = make_figure(df, app.vars['priceReqs'], app.vars['ticker'] )
        return render_template('page.html', script=script, div=div, ticker=name)



if __name__ == '__main__':
    #app.run(debug = True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
