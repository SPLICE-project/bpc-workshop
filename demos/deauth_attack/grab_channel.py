import pandas as pd
import os

def erro_func():
    print("Channel not found")
    os._exit(-1)

def succ_func(chan, bssid, essid):
    print("Target CH = " + str(chan));
    print("BSSID = " + bssid);
    print("ESSID = " + essid);
    os._exit(chan)

##get data into dataframe
try:
    df = pd.read_csv("capt-01.csv")
except:
    print("Not enough capture time!")
## 
try:
    chn=int(df[' channel'].iloc[0])
    if(chn > 0 and chn < 15):
        succ_func(chn, df['BSSID'].iloc[0], df[' ESSID'].iloc[0])
    else:
        erro_func()

except:
    erro_func()
