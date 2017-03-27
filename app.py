from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime,timedelta
import requests
import json
import pandas as pd
from pandas import DataFrame, to_datetime
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh import embed

import time

#quandl.ApiConfig.api_key = 'FAP42o7yZGu6XznAiLze'
#data = quandl.get_table('WIKI/PRICES')

def tickers():

    options = request.form.getlist('feature')
    stock = request.form['stock']
        stock = stock.upper()

    rn = datetime.now()
    start_date = (rn - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = rn.strftime('%Y-%m-%d')
    req_url = 'https://www.quandl.com/api/v3/datasets/WIKI/'+stock+'.json?start_date='+start_date+'&end_date='+end_date+'&order=asc&api_key=FAP42o7yZGu6XznAiLze'
    r = requests.get(req_url)
        
    request_df = DataFrame(r.json()) 
    df = DataFrame(request_df.ix['data','dataset'], columns = request_df.ix['column_names','dataset'])
    df.columns = [x.lower() for x in df.columns]
    df = df.set_index(['date'])
    df.index = to_datetime(df.index)
    

    p = figure(x_axis_type = "datetime")
    if 'open' in options:
        p.line(df.index, df['open'], color='yellow', legend='Opening Price')
    if 'high' in options:
        p.line(df.index, df['high'], color='red', legend='Highest Price')
    if 'close' in options:
        p.line(df.index, df['close'], color='black', legend='Closing Price')
    return p


app = Flask(__name__)


@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('milestone.html')
      
 
 @app.route('/output',methods=['GET','POST'])
def chart():
    plot = ticker()
    script, div = embed.components(plot)
    return render_template('page.html', script=script, div=div)
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

