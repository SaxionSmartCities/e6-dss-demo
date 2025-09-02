#%%
import importlib
from datetime import datetime

import altair as alt
import numpy as np
import pandas as pd
import pysmile
import streamlit as st

from smile_info import SmileInfo

debug = False

UNKNOWN = 'Unknown'
show_detailed_outcome = False
show_expert_gui = False

categories =  ['Unknown', 'Washing Machine', 'Dishwasher', 'Fridge', 'Vacuum Cleaner', 'Personal Care']
categoryScales = np.array([10.0, 13.9, 13.2, 16.5, 10.3, 10.8])
categoryShapes = np.array([2.0, 2.2, 1.6, 2.2, 1.5, 1.3])
reuseOnlyIfPackaged = np.array([False, False, False, False, False, True])

# Prevent load error when the script is re-run, cache the resource
@st.cache_resource
def import_license():
    importlib.import_module("pysmile_license")

def print_header():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    title = "E6 Decision Support Demo"
    st.header(f":blue[{title}]")
    st.markdown(f"_{timestamp}_")
    print(f"{title} {timestamp}")

@st.cache_resource
def load_network(filename):
    net = pysmile.Network()
    net.read_file(filename)
    # Bayesian Network Information. We have our owb convenience wrapper
    return SmileInfo(net)


# Unfortunately, it is not possible to update the GUI after an application error
# What we need is a programmatic rerun to restore the GUI after an error

def set_evidence(node_id, value):
    success = True
    try:
        bni.set_evidence(node_id, value if value and value != UNKNOWN else None)
    except pysmile.SMILEException as e:
        success = False
        if e.error_code == -26:
            st.error(f"Error setting evidence for {node_id}: Conflicting evidence")
    return success

def get_age_category():
    posteriors = { k: v for k, v in bni.get_posteriors_by_id('actualAgeCategory').items() if v > 0 }
    label = ''
    if len(posteriors) == 1:
        label = list(posteriors.keys())[0]
    return label


def update_select_one(label, node_id, radio_widget = True, index=0, tooltip=None):
    options = bni.list_outcome_ids(node_id)
    # The following line conflicts with the initialization of the widget itself when index != 0
    # if node_id not in st.session_state:
    #     st.session_state[node_id] = UNKNOWN
    disabled = False
    if bni.has_propagated_evidence(node_id):
        evidence = bni.get_evidence(node_id)
        st.session_state[node_id] = evidence if evidence is not None else UNKNOWN
        disabled = True
    if radio_widget:
        st.radio(label, [UNKNOWN, *options], index=index, horizontal=True, key=node_id, disabled=disabled, help=tooltip)
        # , on_change=save_view_state, args=(node_id, st.session_state[node_id]))
    else:
        st.selectbox(label, [UNKNOWN, *options], index=index, key=node_id, disabled=disabled)
    set_evidence(node_id, st.session_state[node_id])

def update_gui():
    top_col1, top_col2 = st.columns(2, vertical_alignment='center')
    with top_col1:
        selected = st.selectbox("Device category", categories, index=0, key="deviceCategory")
        # st.selectbox("Device category", categories, index=categories.index(st.session_state['deviceCategory']), key='deviceCategory')
        index = categories.index(selected)
        shape = categoryShapes[index]
        scale = categoryScales[index]
        bni.set_cont_evidence("deviceCategoryScale", scale)
        bni.set_cont_evidence("deviceCategoryShape", shape)
    with top_col2:
        warranty_time = st.number_input("Warranty time (months)", min_value=1, max_value=24, value=12, key="warrantyTime")
        bni.set_cont_evidence('warrantyTime', warranty_time / 12.0)

    update_select_one("Brand category", "brand")

    age_col1, age_col2 = st.columns([1, 3], vertical_alignment='center')
    with age_col1:
        age_disabled = st.toggle('Unknown', value=True)
    with age_col2:
        age = st.slider("Age", min_value=0, max_value=20, value=8, disabled=age_disabled, key="age")
        bni.set_cont_evidence('actualAge', age if not age_disabled else None)

    update_select_one("Visual Condition", "visualCondition")
    update_select_one("Usage Intensity", "usageIntensity")
    update_select_one("Device is working", "deviceWorking", index=1, tooltip="Assume the device is fully functional (now or after repairs)?")
    st.divider()

    global show_expert_gui
    global show_detailed_outcome
    results_toggle_col1, results_toggle_col2 = st.columns(2, gap='large')
    with results_toggle_col1:
        show_expert_gui = st.toggle('Show probabilities', value=False)
    with results_toggle_col2:
        show_detailed_outcome = st.toggle('Show detailed evaluation', value=False)

def show_results():
    labels = [
        # 'P(Perceived quality)',
        'P(Commercial viability)',
        'P(Spare parts quality)',
        'P(OK at age)',
        'P(Fail in warranty)',
    ]
    values = [
        # bni.get_posterior('perceivedQuality', 'High') * 100,
        bni.get_posterior('saleability', 'Good') * 100,
        bni.get_posterior('sparePartsQuality', 'Good') * 100,
        bni.get_posterior('deviceWorking', 'OK') * 100,
        bni.get_posterior('deviceStillWorking', 'Fail') * 100,
    ]
    prob_df = pd.DataFrame({'prob': values, 'var': labels})

    st.dataframe(data=prob_df, hide_index=True, column_order=("var", "prob"),
                 column_config={
                     "prob": st.column_config.NumberColumn(
                         "Probability %",
                         min_value=0.0,
                         max_value=100.0,
                         format="%.1f",
                     ),
                     "var": st.column_config.TextColumn("Variable")
                 })

    probability_bars = alt.Chart(prob_df).mark_bar().encode(
        x=alt.X('prob').title('Probability').scale(domain=(0, 100)),
        y=alt.Y('var', ).title('').sort(None)
    )
    st.altair_chart(probability_bars)
    # st.write(f'Age category: {get_age_category()}')


def show_traffic_light(label, color):
    st.html(f'''
        <div style="display: flex; flex-flow: row nowrap; justify-items: space-between; align-items: center; width: 350px;">
            <span style="flex: 1 1 auto">{label}</span>
            <div style="display:flex; flex-flow: row nowrap; flex: none; border: 2px solid grey; border-radius: 5px; gap: 5px; padding: 5px; background-color: darkgray;">
                <span style="flex: none; border-radius: 50%; width: 40px; height: 40px; background-color: {color if color == "red" else "lightgrey"}; border: 1px solid grey"></span>
                <span style="flex: none; border-radius: 50%; width: 40px; height: 40px; background-color: {color if color == "orange" else "lightgrey"}; border: 1px solid grey"></span>
                <span style="flex: none; border-radius: 50%; width: 40px; height: 40px; background-color: {color if color == "green" else "lightgrey"}; border: 1px solid grey"></span>
            </div>
        </div>
    ''')

def eval_kpi(cfgs):
    colors = np.array([c['color'] for c in cfgs])
    return "green" if np.all(colors == "green") else "red" if np.any(colors == "red") else "orange"

def show_evaluation():
    configs = (
    {
    #     'label': 'Perceived quality',
    #     'cutoff': [40, 60],
    #     'value': bni.get_posterior('perceivedQuality', 'High') * 100,
    #     'kpi': [],
    # }, {
        'label': 'Commercial viability',
        'cutoff': [40, 60],
        'value': bni.get_posterior('saleability', 'Good') * 100,
        'kpi': ['reuse'],
    }, {
        'label': 'Spare parts quality',
        'cutoff': [40, 60],
        'value': bni.get_posterior('sparePartsQuality', 'Good') * 100,
        'kpi': ['spares'],
    }, {
        'label': 'Risk of warranty return',
        'cutoff': [93, 95],
        'value': bni.get_posterior('deviceStillWorking', 'OK') * 100,
        'kpi': ['reuse'],
    })
    for cfg in configs:
        cfg['color'] = "red" if cfg['value'] < cfg['cutoff'][0] else "green" if cfg['value'] >= cfg['cutoff'][1] else "orange"
    reuse_configs = filter(lambda c: 'reuse' in c['kpi'], configs)
    spares_configs = filter(lambda c: 'spares' in c['kpi'], configs)
    reuse_color = eval_kpi(reuse_configs)
    spares_color = eval_kpi(spares_configs)
    st.divider()
    lights_col1, lights_col2 = st.columns(2, gap='large')
    with lights_col1:
        show_traffic_light('Reuse', reuse_color)
        show_traffic_light('Spare parts', spares_color)
    with lights_col2:
        if show_detailed_outcome:
            for cfg in configs:
                show_traffic_light(cfg['label'], cfg['color'])
    if show_expert_gui:
        st.divider()
        st.markdown("_Probabilities are conditioned on values set above!_\n")
        show_results()

def print_debug_info():
    try:
        # bni.print_node_info_by_id('actualAge')
        # bni.print_node_info_by_id('normAge')
        # bni.print_node_info_by_id('effectiveAge')
        # bni.print_node_info_by_id('technicalCondition')
        bni.print_posteriors_by_id('technicalCondition')
        # bni.print_node_info_by_id('actualAgeCategory')
        bni.print_posteriors_by_id('actualAgeCategory')

    except pysmile.SMILEException as e:
        print(e)


##############  Start main program  ################
import_license()
print_header()

# Bayesian Network Information. We have our owb convenience wrapper 'SmileInfo'.
bni = load_network("e6-dss.xdsl")

# Run the GUI
update_gui()

# Calculate the beliefs
bni.update_beliefs()

show_evaluation()
if debug:
    print_debug_info()