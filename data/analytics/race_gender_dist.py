import pandas
import matplotlib.pyplot as pyplot

data = pandas.read_csv('../../resources/cleaned.csv')

print(data.sample(10)[['Race', 'Gender']])

counts = pandas.crosstab(data['Race'], data['Gender'])
percentage = counts.div(counts.sum(axis=1), axis=0)

textprops = {
    'size': 16,
    'color':'black',
    'weight':'bold',
}

ax = percentage.plot.bar(
    stacked=True,
    color=['#fc03f0', '#4266f5'],
    #logy=True,
)
labels = [f'{i:.0%}' for i in percentage.to_numpy().flatten(order='F')]

for i, patch in enumerate(ax.patches):
    x, y = patch.get_xy()
    x += patch.get_width() / 2
    y += patch.get_height() / 2
    ax.annotate(labels[i], (x, y), ha='center', va='center', c='white')

pyplot.xticks(rotation=45, ha='right')
pyplot.tight_layout()
pyplot.savefig('../results/race_gender_percentage.png', bbox_inches='tight')

print(counts)
counts_plot = counts.plot.bar(
    color=['#fc03f0', '#4266f5'],
)
counts_plot.axhline(y=417_398, color='b', linestyle='-')

pyplot.xticks(rotation=45, ha='right')
pyplot.tight_layout()
pyplot.savefig('../results/race_gender_count.png', bbox_inches='tight')
