import pandas
import matplotlib.pyplot as pyplot
import numpy

data = pandas.read_csv('../../resources/cleaned.csv')

in_team = len(data[data['pvp'] != 'Unaligned'])
without_team = len(data[data['pvp'] == 'Unaligned'])

print(f'Player in PVP team {in_team}')
print(f'Plaer without PVP team {without_team}')

textprops = {
    'size': 16,
    'color':'black',
    'weight':'bold'
}
explode = [0.2, 0]
data = numpy.array([in_team, without_team])
labels = ['In PVP Team', 'No PVP Team']

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
pyplot.savefig('../results/player_pvp_team_diagram.png', bbox_inches='tight')

