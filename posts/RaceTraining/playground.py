import numpy as np


def color_test():
    import plotly
    import plotly.graph_objs as go
    traces = []
    # rb = plotly.colors.sequential.RdBu_r
    rb = plotly.colors.colorscale_to_colors(plotly.colors.PLOTLY_SCALES['RdBu'])
    randn = np.random.normal(3., 1., 1000)
    dx = 6. / len(rb)
    for i, col in enumerate(rb):
        traces.append(
            go.Histogram(x=randn[np.where((randn >= i * dx) & (randn < (i + 1) * dx))],
                         xbins=dict(start=0, end=6.0, size=0.2),
                         marker_color=rb[i]))
    fig = go.Figure(data=traces, layout=go.Layout(barmode='stack'))
    fig.show()


if __name__ == '__main__':
    color_test()
    a = 1
