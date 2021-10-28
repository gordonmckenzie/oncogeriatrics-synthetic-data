from matplotlib import pyplot as plt
from matplotlib.axis import XAxis
import pandas as pd
from sdv.timeseries import PAR
import plotly.express as px

#df = pd.read_csv('organs/abpm.csv', parse_dates=['time'])
# today = pd.Timestamp('today').strftime('%Y-%m-%d')

# df['time'] = pd.to_datetime(df['time']).apply(lambda x: today + " " + x.strftime(r'%H:%M:%S'))

# print(df.time)

# model = PAR(sequence_index="time")

# model.fit(df)

# model.save('organs/abpm.pkl')

loaded = PAR.load('organs/abpm.pkl')

newdata = loaded.sample()

fig: px.line = px.line(newdata, x='time', y=newdata[['sbp','dbp']].columns)
fig.add_vline(x="2021-10-26 10:30:00")
fig.add_vline(x="2021-10-26 12:00:00")
fig.update_layout(
    xaxis = dict(
        type = 'date',
        tick0 = '10:30:00',
        tickvals = [
            '2021-10-26 10:30:00', 
            '2021-10-26 11:00:00', 
            '2021-10-26 11:30:00', 
            '2021-10-26 12:00:00',
            '2021-10-26 12:30:00',
            '2021-10-26 13:00:00',
            '2021-10-26 13:30:00',
            '2021-10-26 14:00:00',
            '2021-10-26 14:30:00',
            '2021-10-26 15:00:00',
            '2021-10-26 15:30:00'
            '2021-10-26 16:00:00', 
            '2021-10-26 16:30:00',
            '2021-10-26 17:00:00',
            '2021-10-26 17:30:00',
            '2021-10-26 18:00:00',
            '2021-10-26 18:30:00'
            '2021-10-26 19:00:00', 
            '2021-10-26 19:30:00',
            '2021-10-26 20:00:00',
            '2021-10-26 20:30:00'
            '2021-10-26 21:00:00', 
            '2021-10-26 21:30:00',
            '2021-10-26 22:00:00',
            '2021-10-26 22:30:00',
            '2021-10-26 23:00:00',
            '2021-10-26 23:30:00'
            '2021-10-26 00:00:00', 
            '2021-10-26 00:30:00',
            '2021-10-26 01:00:00', 
            '2021-10-26 01:30:00', 
            '2021-10-26 02:00:00',
            '2021-10-26 02:30:00',
            '2021-10-26 03:00:00',
            '2021-10-26 03:30:00',
            '2021-10-26 04:00:00',
            '2021-10-26 04:30:00',
            '2021-10-26 05:00:00',
            '2021-10-26 05:30:00'
            '2021-10-26 06:00:00', 
            '2021-10-26 06:30:00',
            '2021-10-26 07:00:00',
            '2021-10-26 07:30:00',
            '2021-10-26 08:00:00',
            '2021-10-26 08:30:00'
            '2021-10-26 09:00:00', 
            '2021-10-26 09:30:00',
            '2021-10-26 10:00:00'
        ],
        tickmode = 'linear',
        dtick = (86400000.0 / 24),
    ),
    yaxis = dict(
        range = [0, 240],
        dtick = 30
    )
)
fig.add_trace(
    go.Scatter(
        x=x+x[::-1], # x, then x reversed
        y=y_upper+y_lower[::-1], # upper, then lower reversed
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    )
)
fig.show()