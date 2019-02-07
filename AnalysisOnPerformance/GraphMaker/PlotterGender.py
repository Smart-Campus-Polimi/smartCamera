from typing import Counter
import numpy as np
import matplotlib.pyplot as plt
import pymysql.cursors
import matplotlib.dates as mdates
import datetime
FILEPATHBASE = r"C:\Users\Marco Wenzel\Desktop\VG\GenderPlot"

def genderPie(countM,countF,API):
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    data=[countM,countF]
    gender=["Male","Female"]

    def func(pct, allvals):
        print (pct)
        absolute = int(pct/100.*np.sum(allvals))
        print(absolute)
        return "{:.1f}%\n({:d} person)".format(pct, absolute)


    wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data),
                                      textprops=dict(color="w"))

    print("male:"+ str(countM))
    print("female:"+ str(countF))
    ax.legend(wedges, gender,
              title="Ingredients",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=8, weight="bold")

    ax.set_title("Gender Pie")

    plt.show()

    fig.savefig(FILEPATHBASE+API+'.png')