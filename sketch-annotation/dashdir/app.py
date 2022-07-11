import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, State
from skimage import data
import json

img = data.chelsea()
fig = px.imshow(img)
fig.update_layout(dragmode="drawrect")
config = {
    'editable': True,
    # more edits options: https://dash.plotly.com/dash-core-components/graph
    'edits': {
        'annotationPosition': True,
        'annotationText': True,
        'shapePosition': True
    },
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
        "addtext",

    ],

}

# Build App
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H3("Drag and draw annotations"),
        dcc.Graph(id="fig-image", figure=fig, config=config),
        html.Pre(id="annotations-pre"),
        dcc.Input(id="text-input", type='text'),
        html.Button('add text to image', id='submit-val', n_clicks=0),
        dcc.Store(id="clicked", data="clickData", storage_type="memory"),
        html.Button(
            id='save_annotation',
            children='Save',
        ),
        dcc.Store(
            id='annotation_storage',
            data='Editable Annotation',
        )
    ]
)


# modifiying drawn shapes
@app.callback(
    Output("annotations-pre", "children"),
    Input("fig-image", "relayoutData"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data):
    for key in relayout_data:
        if "shapes" in key:
            return json.dumps(f'{key}: {relayout_data[key]}', indent=2)

    return dash.no_update


# text annotaion button

@app.callback(
    Output("fig-image", "figure"),
    Input('submit-val', 'n_clicks'),
    State('text-input', 'value'),
    Input('fig-image', 'selectedData')

)
def text_entry(n_clicks, value, clickData):
    if n_clicks != 0:
        fig.add_annotation(
            showarrow=False,
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="Purple"
            ),
            captureevents=True,
        )

        n_clicks = 0
        value = ""
    print(fig)
    print(clickData)

    return fig


# @app.callback(
#     Output("clicked", "clickData"),
#     Input('save_annotation', 'n_clicks'),
#     Input('fig-image', 'selectedData')
#
# )
# def text_entry(n_clicks, selectedData):
#     if n_clicks != 0:
#         print(fig)
#         print(selectedData)
#
#     return selectedData
#

if __name__ == "__main__":
    app.run_server(debug=True)
