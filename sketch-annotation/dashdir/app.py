import re
import plotly.graph_objects as go
# import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, State
from skimage import data
import json

img = "https://images.unsplash.com/photo-1453728013993-6d66e9c9123a?ixlib=rb-1.2.1&ixid" \
      "=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8Zm9jdXN8ZW58MHx8MHx8&w=1000&q=80 "
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
        opacity=0.5,
        layer="below",
        sizing="stretch",
        source=img)
)

# Configure other layout
fig.update_layout(
    width=img_width * scale_factor,
    height=img_height * scale_factor,
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
)

# https://community.plotly.com/t/shapes-and-annotations-become-editable-after-using-config-key/18585
config = {
    # 'editable': True,
    # # more edits options: https://dash.plotly.com/dash-core-components/graph
    'edits': {
        'annotationPosition': True,
        'annotationText': True,
        # 'shapePosition': True
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
        html.Button('clear image', id="clean-reset", n_clicks=0),
        dcc.ConfirmDialog(
            id='confirm-reset',
            message='Warning! All progress wil be lost! Are you sure you want to continue?',
        ),

    ]
)


@app.callback(
    Output('confirm-reset', 'displayed'),
    Input('confirm-reset', 'submit_n_clicks'),
    Input('clean-reset', 'n_clicks'))
def display_confirm(submit, reset):
    if reset and not submit:
        return True
    if reset and submit:
        if reset>submit:
            return True
    return False


@app.callback(
    Output("fig-image", "figure"),
    Output('submit-val','n_clicks'),
    Output('confirm-reset', 'submit_n_clicks'),
    Output('clean-reset', 'n_clicks'),
    Input('fig-image', 'relayoutData'),
    State('text-input', 'value'),
    Input('submit-val', 'n_clicks'),
    Input('confirm-reset', 'submit_n_clicks'),
    Input('clean-reset', 'n_clicks'),
)
def save_data(relayout_data, inputText, submit_clicks, confirm,reset):
    # adding new text
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
            return fig, submit_clicks, confirm, reset

    # relayout_data gives back user changes data
    print("relay")
    print(relayout_data)
    if relayout_data:

        # adding or removing shapes
        if "'shapes':" in str(relayout_data):
            counter = 0
            fig.layout.shapes = ()
            # all shapes on screen will be returned in relay data upon new shape creation.
            for i in relayout_data['shapes']:
                fig.add_shape(i)

        # changing shapes
        elif "shapes[" in str(relayout_data):
            # using regex to find which shape was changed
            shape_num_index = re.search(r"\d", str(relayout_data))
            i = int(str(relayout_data)[shape_num_index.start()])

            # changing dictionary keys so we can update the shape change easily
            dictnames = list(relayout_data.keys())
            new_dict = {}
            counter = 0
            for name in dictnames:
                dictnames[counter] = name[10:]
                counter = counter + 1
            for key, n_key in zip(relayout_data.keys(), dictnames):
                new_dict[n_key] = relayout_data[key]
            fig.update_shapes(new_dict, i)

        # if text is changed, "annotations" wil be part of the relayout data
        elif "annotations" in str(relayout_data):
            fig.update_annotations(captureevents=True)
            # using regex to find which annotation was changed
            anno_num_index = re.search(r"\d", str(relayout_data))
            i = int(str(relayout_data)[anno_num_index.start()])

            # if text content is changed "text" will be in relay data
            if "text" in str(relayout_data):
                fig.update_annotations(Annotation(fig.layout.annotations[i]['x'], fig.layout.annotations[i]['y'],
                                                  relayout_data[f'annotations[{i}].text']).__dict__, i)

            # if text is just moved relay data wont have "text" in data
            else:
                fig.update_annotations(
                    Annotation(relayout_data[f'annotations[{i}].x'], relayout_data[f'annotations[{i}].y'],
                               fig.layout.annotations[i]['text']).__dict__, i)

    # resetting image
    if confirm:
        fig.layout.shapes = ()
        fig.layout.annotations = ()
        return fig, 0, 0, 0

    return dash.no_update, submit_clicks, confirm, reset



class Annotation:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
