import numpy as np
import plotly.graph_objs as go

yspeed = [4, 5, 6, 7, 8]  # miles/hr
ypace = [60. / y for y in yspeed]  # min/mile
data = []
data.append(go.Scatter(x=[1, 2, 3, 4, 5, 6], y=[8, 7, 6, 5, 4.5, 4]))
# data.append(go.Scatter(x=[np.nan], y=[np.nan], yaxis='y2'))
data.append(go.Scatter(x=[1, 2, 3, 4, 5, 6], y=[7, 6, 5, 4, 3, 2], yaxis='y2'))
layout = go.Layout(yaxis=dict(tickvals=yspeed),
                   yaxis2=dict(tickvals=yspeed, ticktext=ypace, overlaying='y', side='right'))
fig = go.Figure(data=data, layout=layout)
fig.show()
a = 1
