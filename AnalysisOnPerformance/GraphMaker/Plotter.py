from typing import Counter

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from adjustText import adjust_text

FILEPATHBASE = r"C:\Users\Marco Wenzel\Desktop\VG\PersonPlot"

def plotTimeline(dictMove, dictTime,API):
    print("dictMove len:"+ str(len(dictMove)))
    print("dictTime len:"+ str(len(dictTime)))
    print("dictMove: "+str(dictMove))
    print("dictTime: "+ str(dictTime))
    dater = [datetime.datetime.strftime(ii, "%H:%M:%S") for ii in dictTime]
    a = zip(dictMove, dater)
    b = list(a)
    multip=Counter(b).most_common()
    print(multip)
    fig, ax = plt.subplots(figsize=(15, 8))
    start = min(dater)
    stop = max(dater)
    for (x,y) in zip(dictMove,dater):
        ax.scatter(y, 0, s=100, facecolor='w', edgecolor='k', zorder=9999)
        for k in multip:
            print("y: ",y)
            print("k[0]: ",k[0])
            print("k[1]: ", k[1])
            if (y==k[0][1]):
                print("entro")
                if(x>0):
                    x=k[1]
                else:
                    x=-k[1]
        if x>0:
            ax.plot((y, y), (0, x), c='r', alpha=.7)
            ax.text(y, x, y,
                fontsize=10, horizontalalignment='center',verticalalignment='bottom',rotation=45,
                backgroundcolor=(1., 1., 1., .3))
        else:
            ax.plot((y, y), (0, x), c='b', alpha=.7)
            ax.text(y, x, y,
                    fontsize=10, horizontalalignment='center', verticalalignment='top', rotation=45,
                    backgroundcolor=(1., 1., 1., .3))
    #plt.plot(dictTime, dictMove)


    plt.ylabel("OUT or IN")
    plt.text(0.5, 1.08, "Person Detection From API: "+API,
             horizontalalignment='center',
             fontsize=20,
             transform = ax.transAxes)
    ax.get_xaxis().set_major_locator(mdates.SecondLocator(interval=0))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.autofmt_xdate()
    plt.setp((
              list(ax.spines.values())), visible=False)
    plt.show()

    fig.savefig(FILEPATHBASE+API+'.png')


