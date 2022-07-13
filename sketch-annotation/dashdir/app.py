import re
import plotly.graph_objects as go
# import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, State
from skimage import data
import json

img = "https://images.unsplash.com/photo-1453728013993-6d66e9c9123a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8Zm9jdXN8ZW58MHx8MHx8&w=1000&q=80"
fig = go.Figure()

img_width = 1600
img_height = 900
scale_factor = 0.5

# Add invisible scatter trace.
# This trace is added to help the autoresize logic work.
fig.add_trace(
    go.Scatter(
        x=[0, img_width * scale_factor],
        y=[0, img_height * scale_factor],
        mode="markers",
        marker_opacity=0
    )
)

# Configure axes
fig.update_xaxes(
    visible=False,
    range=[0, img_width * scale_factor]
)

fig.update_yaxes(
    visible=False,
    range=[0, img_height * scale_factor],
    # the scaleanchor attribute ensures that the aspect ratio stays constant
    scaleanchor="x"
)

# Add image
fig.add_layout_image(
    dict(
        x=0,
        sizex=img_width * scale_factor,
        y=img_height * scale_factor,
        sizey=img_height * scale_factor,
        xref="x",
        yref="y",
        opacity=1.0,
        layer="below",
        sizing="stretch",
        source=img)
)

# Configure other layout
fig.update_layout(
    dragmode="drawrect",
    width=img_width * scale_factor,
    height=img_height * scale_factor,
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
)

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
        html.H3("Drag and draw annotations - use the modebar to pick a different drawing tool"),
        dcc.Graph(id="fig-image", figure=fig, config=config),
        html.Pre(id="annotations-data-pre"),
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
    Output("annotations-data-pre", "children"),
    Input("fig-image", "relayoutData"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data):
    if "shapes" in relayout_data:
        print("layout " + str(go.layout.annotation))
        return json.dumps(relayout_data["shapes"], indent=2)
    else:
        return dash.no_update


@app.callback(
    Output("fig-image", "figure"),
    Input('save_annotation', 'n_clicks'),
    State('fig-image', 'relayoutData'),
    State('text-input', 'value'),
    Input('submit-val', 'n_clicks'),

)
def save_data(save_clicks, relayout_data, inputText, submit_clicks):
    if submit_clicks:
        if not len(fig.layout.annotations) == submit_clicks:
            fig.add_annotation(
                text=inputText,
                showarrow=False,
                font=dict(
                    family="Courier New, monospace",
                    size=28,
                    color="white",

                ),
                x=img_width / 4,
                y=img_height / 2.5,
            )

    if save_clicks is not None and relayout_data:
        anno_num_index = re.search(r"\d", str(relayout_data))
        print("anno_num_index " + str(relayout_data)[anno_num_index.start()])
        print("n save " + str(save_clicks))
        print("layout " + str(fig.layout.shapes))
        # print("shapes " + str(fig.shapes))

        i = int(str(relayout_data)[anno_num_index.start()])
        print("relay " + str(relayout_data))

        # let dash do its thing if shapes are added
        if "shape" in str(relayout_data):
            pass
        # if text is changed, relay data wont have new x cordinates
        elif "text" in str(relayout_data):
            fig.update_annotations(Annotation(fig.layout.annotations[i]['x'], fig.layout.annotations[i]['y'],
                                              relayout_data[f'annotations[{i}].text']).__dict__, i)
        # if text is just moved relay data wont have text data
        else:
            fig.update_annotations(
                Annotation(relayout_data[f'annotations[{i}].x'], relayout_data[f'annotations[{i}].y'],
                           fig.layout.annotations[i]['text']).__dict__, i)
        print("layout   " + str(fig.layout))
    return fig


class Annotation:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text


if __name__ == "__main__":
    app.run_server(debug=True)
