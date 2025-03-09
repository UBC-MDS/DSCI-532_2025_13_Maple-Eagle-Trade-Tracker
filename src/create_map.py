import altair as alt
from data import get_agg_geom_data, get_processed_data

def get_map_chart(df, selected_province):
    
    """Returns a geographical map chart object"""

    aggr_data = get_agg_geom_data(df)

    default_color = alt.Color(
                        'NET_TRADE:Q', 
                        scale=alt.Scale(scheme='redyellowgreen'),
                        legend=alt.Legend(title="Net Trade")
                    )
    color_encoding = default_color if not selected_province or "All" in selected_province else alt.condition(
        alt.FieldOneOfPredicate(field='PROVINCE', oneOf=selected_province),
        default_color,
        alt.value("#ECECEC" ) 
    )

    hover = alt.selection_point(fields=['PROVINCE'], on='pointerover', empty=False)

    map_chart = alt.Chart(aggr_data, width=700, height=300).mark_geoshape(
        strokeWidth=2
    ).encode(
        tooltip=[alt.Tooltip('PROVINCE:N', title = 'Province:'), 
                 alt.Tooltip('NET_TRADE:Q', format=',', title = 'Net Trade:')],
        color=color_encoding, 
        stroke=alt.condition(hover, alt.value('white'), alt.value('#222222')),
        order=alt.condition(hover, alt.value(1), alt.value(0))
    ).properties( # make this a proportion of the screen size
        width=1000,
        height=500
    ).configure(
        background='transparent'
    ).project(
        'transverseMercator',
        rotate=[90, 0, 0]
    ).add_params(
        hover
    )

    return map_chart


