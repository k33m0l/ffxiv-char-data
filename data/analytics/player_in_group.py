import pandas
import matplotlib.pyplot as pyplot
import numpy

data = pandas.read_csv('../../resources/cleaned.csv')

players_in_fc = data['fc'].count()
players_not_in_fc = data['fc'].isna().sum()

print(f"Players in a group: {players_in_fc}")
print(f"Players without affiliation: {players_not_in_fc}")

textprops = {
    'size': 16,
    'color':'black',
    'weight':'bold'
}
explode = [0.2, 0]
data = numpy.array([players_in_fc, players_not_in_fc])
labels = ['In Free Company', 'No affiliation']
 
pyplot.pie(
    data,
    labels=labels,
    startangle=180,
    autopct='%1.2f%%',
    shadow=True,
    textprops=textprops,
    explode=explode,
)

pyplot.tight_layout()
pyplot.savefig('../results/player_free_company_diagram.png', bbox_inches='tight')

