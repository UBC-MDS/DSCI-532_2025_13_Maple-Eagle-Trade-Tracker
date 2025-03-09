import altair as alt
from data import get_agg_geom_data, get_processed_data

def get_map_chart(df):
    
    """Returns a geographical map chart object"""

    aggr_data = get_agg_geom_data(df)
    hover_selection = alt.selection_point(fields=['PROVINCE'], on='pointerover', empty=False)
    multi_selection = alt.selection_point(fields=['PROVINCE'], on='click', empty=False, toggle=True)
    
    default_color = alt.Color(
        'NET_TRADE:Q', 
        scale=alt.Scale(
            scheme='redyellowgreen',
            domain=[aggr_data["NET_TRADE"].min(), aggr_data["NET_TRADE"].max()],
            nice=False
        ),
        legend=alt.Legend(
            title="Net Trade (CAD)",
            format="~s",
            offset=-75  
        )
    )
    color_encoding = alt.condition(
        multi_selection,
        default_color,
        alt.value("#ECECEC" ) 
    )

  
    map_chart = alt.Chart(aggr_data).mark_geoshape(
        strokeWidth=2
    ).encode(
        tooltip=[
            alt.Tooltip('PROVINCE:N', title = 'Province:'), 
            alt.Tooltip('NET_TRADE:Q', format='~s', title = 'Net Trade (CAD):')
        ],
        color=color_encoding, 
        stroke=alt.condition(hover_selection, alt.value('white'), alt.value('#222222'))
    ).properties( # make this a proportion of the screen size
        width=800,
        height=450
    ).configure(
        background='transparent'
    ).project(
        'transverseMercator',
        rotate=[90, 0, 0]
    ).add_params(
        hover_selection,
        multi_selection
    )

    return map_chart