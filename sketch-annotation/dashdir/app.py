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
        'annotationText': False,
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

)
def text_entry(n_clicks, value):
    if n_clicks != 0:
        fig.add_annotation(
            text=value,
            showarrow=False,
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="Purple",


            ),
            captureevents=True,
            x=2,
            y=2,
        )
    # if annotation_data is not None:
    #     x = []
    #     y = []
    #     text = []
    #     for i in annotation_data:
    #         x.append(i['x'])
    #         y.append(i['y'])
    #         text.append(i['text'])
    #     fig.add_trace(px.scatter(x=x, y=y, text=text))
    #     annotation_data = []
    #
    #     n_clicks = 0
    #     value = ""
    # # print(fig)
    return fig


@app.callback(
    Output('annotation_storage', 'data'),
    Input('save_annotation', 'n_clicks'),
    State('fig-image', 'relayoutData'),
    Input('annotation_storage', 'data'),

)
def save_data(n_clicks, relayout_data, annotations):
    if (annotations is None) | (annotations == {}):
        annotations = []

    if n_clicks != 0 and relayout_data:
        n_clicks = 0


        print("2" + str(fig.layout.annotations))
        print(len(fig.layout.annotations))
        i=len(fig.layout.annotations)-1
        print("3" + str(relayout_data))
        annotations.append(Annotation(relayout_data[f'annotations[{i}].x'], relayout_data[f'annotations[{i}].y'],
                                      str(fig.layout.annotations[i]['text'])).__dict__)
        print(*annotations)
        fig.update_annotations(Annotation(relayout_data[f'annotations[{i}].x'], relayout_data[f'annotations[{i}].y'],
                                          str(fig.layout.annotations[i]['text'])).__dict__)
        return annotations


class Annotation:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

#
# @app.callback(
#     Output("fig-image", "figure"),
#     Input("fig-image", "figure"),
#     Input('annotation_storage', 'data'),
#
# )
# def update_pic(pic, data):
#     if data:
#         fig = pic
#         x = []
#         y = []
#         text = []
#         for i in data:
#             x.append(i['x'])
#             y.append(i['y'])
#             text.append(i['text'])
#         fig.add_trace(px.Scatter(x=x, y=y, text=text))
#         data = []
#         return fig
#

if __name__ == "__main__":
    app.run_server(debug=True)
