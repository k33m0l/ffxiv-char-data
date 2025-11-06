import pandas
import matplotlib.pyplot as pyplot
import matplotlib.patheffects as effects

data = pandas.read_csv('../../resources/cleaned.csv')
explode = (0.05,0.05,0.05)
textprops = {
    'size': 16,
    'color':'black',
    'weight':'bold'
}
data['City-state'].value_counts().plot.pie(
    autopct='%1.2f%%',
    startangle=90,
    explode=explode,
    shadow=True,
    textprops=textprops,
)

pyplot.tight_layout()
pyplot.savefig('../results/starting_city.png', bbox_inches='tight')

