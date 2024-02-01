import csv
from requests_html import HTMLSession

import json
import time as timing

from itertools import islice
from datetime import *
import random
import os

import sys


from flask import Flask, request, jsonify



def gather(ticker, assetClass):
    if (assetClass == "unavailable"):
        return "Unavailable ticker..."
    else:
        # Chromium session initialization, a browser that runs in background to load the URL provided. It has to be closed once the needed data is retrieved.
        s = HTMLSession()

        # URL: Specific NASDAQ endpoint that provides the option chain of a given stock with certain filters applied.
        url = f"https://api.nasdaq.com/api/quote/{ticker.lower()}/option-chain?assetclass={assetClass.lower()}&limit=300&fromdate=all&todate=undefined&excode=oprac&callput=call&money=out&type=all"
        r = s.get(url)
        print(s.get(url))

        try:
            json_obj = json.loads(r.content)
            s.close()
            if("data" in json_obj):
                if("table" in json_obj["data"]):
                    if("rows" in json_obj["data"]["table"]):
                        for item in islice(json_obj["data"]["table"]["rows"], 1, None):
                            if (item["expiryDate"] != None):
                                expiryDate = item["expiryDate"]
                                parseDate = datetime.strptime(expiryDate + " 2024", '%b %d %Y').date()
                                if (parseDate - date.today() > timedelta(0) 
                                    and item["c_Last"] != "--"
                                    and item["c_Ask"] != "--"
                                    and item["c_Volume"] != "--"
                                    and item["c_Bid"] != "--"):
                                    last = float(item["c_Last"])
                                    ask = float(item["c_Ask"])
                                    strike = float(item["strike"])
                                    roi = random.randint(8, 42)
                                    loss = random.uniform(3.93, 12)
                                    hold = random.randint(13, 78)
                                    exitPrice = round(last + last*roi/100, 2)
                                    stopLoss = round(last - last*loss/100, 2)
                                    if(last > 0.30 and ask > 0.30):
                                        return f"Ticker: ${ticker}\nBuy {expiryDate}, 2024 ${strike} Calls\nEntry Price: ${last} - ${ask}\nExit Price: ${exitPrice}\nStop Loss: ${stopLoss}\nPotential ROI: {roi}%\nEstimated Hold Time: {hold} Minutes"
                        return "Options not available..."
                                            
        except:
            return "Options not available..."                                       

app = Flask(__name__)
app.debug = True
@app.route("/gather",methods=["GET"])
def gather_api():
    requestTicker = request.args.get('ticker')
    print(requestTicker)
    with open('modifiedTickers.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(row)
            rowString = ', '.join(row)
            array = rowString.split(",")
            ticker = array[1]
            if ticker == requestTicker:
                assetClass = array[3]
                response = gather(ticker, assetClass)
                return jsonify({"response": response})
            else:
                continue
        return jsonify({"respose":"Ticker not found..."})
