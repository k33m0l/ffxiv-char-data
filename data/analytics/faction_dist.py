import pandas
import matplotlib.pyplot as pyplot
import matplotlib.patheffects as effects

data = pandas.read_csv('../../resources/cleaned.csv')
explode = (0.05,0.05,0.05)
textprops = {
    'size': 16,
    'color':'white',
    'weight':'bold'
}
data['City-state'].value_counts().plot.pie(
    autopct='%1.1f%%',
    startangle=90,
    explode=explode,
    shadow=True,
    textprops=textprops,
    frame=True,
)

pyplot.tight_layout()
pyplot.show()
