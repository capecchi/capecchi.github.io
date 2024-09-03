import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

# df = 'C:/Users/willi/PyCharmProjects/capecchi.github.io/posts/AirQuality/aggregate_master.geojson'

direc = 'C:/Users/willi/PyCharmProjects/capecchi.github.io/posts/AirQuality/'
dfs = [f'{direc}bc_master.geojson', f'{direc}co_master.geojson', f'{direc}no2_master.geojson',
       f'{direc}o3_master.geojson', f'{direc}pm10_master.geojson', f'{direc}pm25_master.geojson',
       f'{direc}so2_master.geojson']
vals = []
for df in dfs:
    with open(df, 'r') as f:
        data = json.load(f)
        for feat in data['features']:
            vals.append(feat['properties']['value'])
vals.sort()

fs = (15, 6)
font = 17

fig = plt.figure(figsize=fs)
plt.rcParams.update({'font.size': font})
plt.plot(vals, 'o')
plt.ylabel('Concentration')
plt.xlabel('Index (arb)')
plt.yscale('log')
plt.grid()

fig, ax = plt.subplots(figsize=fs)
nvals = np.array(vals)
hh = []
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 600000]
for i in range(len(bins) - 1):
    # hh.append(len(np.where(nvals >= bins[i] & nvals < bins[i + 1])))
    hh.append(len(nvals[(nvals < bins[i + 1]) & (nvals >= bins[i])]))
print(f'{len(np.where(nvals <= 100)[0]) / len(vals)}')
lbls = [f'{b}' for b in bins[1:]]
lbls[-1] = '>1000'
ax.bar(range(len(hh)), hh)
ax.set_xticks(range(len(hh)), labels=lbls, rotation=45)
ax.set_xlabel('Concentration Bins')
ax.set_ylabel('# Records')
plt.tight_layout()

plt.show()

if __name__ == '__main__':
    pass
