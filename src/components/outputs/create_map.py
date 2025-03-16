import altair as alt
from data.data import get_agg_geom_data

def get_map_chart(df, selected_province):
    
    """Returns a geographical map chart object"""

    aggr_data = get_agg_geom_data(df)
    
    default_color = alt.Color(
        'NET_TRADE:Q', 
        scale=alt.Scale(
            scheme='redyellowgreen',
            domain=[aggr_data["NET_TRADE"].min(), aggr_data["NET_TRADE"].max()],
            nice=False
        ),
        legend=alt.Legend(
            title="Net Trade (CAD)",
            format=",.2f",
            orient="right", 
            offset=-75  
        )
    )
    
    color_encoding = default_color if not selected_province else alt.condition(
        alt.FieldOneOfPredicate(field='PROVINCE', oneOf=selected_province),
        default_color,
        alt.value("#ECECEC" ) 
    )

    hover_selection = alt.selection_point(fields=['PROVINCE'], on='pointerover', empty=False)
  
    map_chart = alt.Chart(aggr_data).mark_geoshape(
        strokeWidth=2
    ).encode(
        tooltip=[
            alt.Tooltip('PROVINCE:N', title = 'Province:'), 
            alt.Tooltip('NET_TRADE:Q', format=',.2f', title = 'Net Trade (CAD):')
        ],
        color=color_encoding, 
        stroke=alt.condition(hover_selection, alt.value('white'), alt.value('#222222')),
        order=alt.condition(hover_selection, alt.value(1), alt.value(0))
    ).properties( # make this a proportion of the screen size
        width=800,
        height=450
    ).configure(
        background='transparent'
    ).project(
        'transverseMercator',
        rotate=[90, 0, 0]
    ).add_params(
        hover_selection
    )

    return map_chart