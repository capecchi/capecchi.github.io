import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pace_predictor_method_development import extract_coords_gpx, compute_grade_pace, smooth_run_coords_distwindow2

'''
Analyze Teanaway 100 race data
Visualize grade of trail
'''

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

basedirec = 'C:/Users/willi/PyCharmProjects/capecchi.github.io/posts/PacePredictor/data/'
gpx = f'{basedirec}/teanaway_100.gpx'
fs = 15
plt.rcParams.update({'font.size': fs})
fgsz1 = (15, 7)
fgsz2 = (20, 7)
gr_binwidth = 2
grade_bin_cntrs = np.arange(-100, 102, 2)
spm_minpmile = 26.8224
m_per_mile = 1609.34

coords0 = extract_coords_gpx(gpx)  # [lon, lat, elev, dcum, dstep, Nones, Nones]
coords1 = smooth_run_coords_distwindow2(coords0, 20)
fig1, ax1 = plt.subplots()
ax1.plot(coords0[:, 3] / m_per_mile, coords0[:, 2])
ax1.plot(coords1[:, 3] / m_per_mile, coords1[:, 2], label='smooth')
ax1.set_xlabel('dist (mi)')
ax1.set_ylabel('elev (m)')

# cc = coords1[::5][:1500, :]  # just look at first climb
# gg, _ = compute_grade_pace(cc)
coords1 = coords1[::5]
gp, gp_pred = compute_grade_pace(coords1)

fig, ax = plt.subplots()
grade = sorted(abs(gp[:, 0]))
gradex = coords1[1:, 3] / coords1[-1, 3]
pcts = [.25, .5, .75]
grade_pcts = np.interp(pcts, gradex, grade)
ax.plot(grade, gradex)
ax.plot(grade_pcts, pcts, 'o')
ax.set_xlabel('grade')
ax.set_ylabel('fraction')
print(
    f'75% above {grade_pcts[0]:.1f}% grade\n50% above {grade_pcts[1]:.1f}% grade\n25% above {grade_pcts[2]:.1f}% grade')

plt.show()

if __name__ == '__main__':
    pass
