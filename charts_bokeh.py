import pandas as pd
import numpy as np
import tempfile
import os
from bokeh.io import output_file, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange, HoverTool, LabelSet, DatetimeTicker, Span
from jira_client import api_request
from jira_parser import parse_issues_to_dataframe

def assign_lanes(df):
    df = df.sort_values(by=["StartDate", "AdjustedEnd"]).copy()
    lanes = []
    end_times = []

    for _, row in df.iterrows():
        assigned = False
        for lane_num, lane_end in enumerate(end_times):
            if row["StartDate"] > lane_end:
                end_times[lane_num] = row["AdjustedEnd"]
                lanes.append(lane_num)
                assigned = True
                break
        if not assigned:
            end_times.append(row["AdjustedEnd"])
            lanes.append(len(end_times) - 1)
    df["Lane"] = lanes
    return df

def gantt_chart_for_sprint_bokeh(sprint_name, export_path=None):
    print(f"Querying issues for sprint: {sprint_name}")

    jql = f'Sprint = "{sprint_name}"'
    result = api_request(endpoint="search", params={"jql": jql}, paginate=True)
    df = parse_issues_to_dataframe(result)

    if df.empty:
        print("No issues found for this sprint.")
        return

    df = df.dropna(subset=["StartDate", "TargetEnd"])
    if df.empty:
        print("No issues with valid StartDate and TargetEnd to plot.")
        return

    df["StartDate"] = pd.to_datetime(df["StartDate"])
    df["TargetEnd"] = pd.to_datetime(df["TargetEnd"])
    df["Team"] = df["Team"].fillna("Unassigned")
    df["AdjustedEnd"] = df["TargetEnd"] + pd.Timedelta(days=1)

    # Assign lanes
    stacked = []
    for team, group in df.groupby("Team"):
        group = assign_lanes(group)
        group["Swimlane"] = group["Team"] + f" (lane " + group["Lane"].astype(str) + ")"
        stacked.append(group)

    df_stacked = pd.concat(stacked)
    df_stacked["y"] = list(zip(df_stacked["Team"], df_stacked["Lane"].astype(str)))
    df_stacked["width"] = (df_stacked["AdjustedEnd"] - df_stacked["StartDate"]).dt.total_seconds() * 1000
    df_stacked["center"] = df_stacked["StartDate"] + (df_stacked["AdjustedEnd"] - df_stacked["StartDate"]) / 2

    # === Adaptive label logic with debug support ===
    CHAR_PIXELS = 30         # More conservative estimate, tune for your font
    PX_PER_DAY = 100        # Chart's x-scaling; increase if bars appear too short
    MS_PER_DAY = 86400000
    MS_PER_PX = MS_PER_DAY / PX_PER_DAY
    LABEL_PADDING = 50      # Extra space to prevent near-overflow

    def should_label_be_above(row):
        bar_width_px = row["width"] / MS_PER_PX
        key_width_px = len(row["Key"]) * CHAR_PIXELS
        # DEBUG: print out actual numbers to tune further
        print(f"{row['Key']}: bar_width={bar_width_px:.1f}px, key_width={key_width_px}px, inside={key_width_px + LABEL_PADDING <= bar_width_px}")
        return key_width_px + LABEL_PADDING > bar_width_px

    df_stacked["label_above"] = df_stacked.apply(should_label_be_above, axis=1)

    export_columns = [
        'y', 'StartDate', 'TargetEnd', 'AdjustedEnd', 'width', 'center',
        'Key', 'Summary', 'Assignee', 'label_above'
    ]
    df_stacked = df_stacked[export_columns]

    if export_path:
        df_stacked.to_csv(export_path, index=False)
        print(f"Exported chart data to {export_path}")

    teams = list(df_stacked["y"].apply(lambda t: t[0]).unique())
    max_lanes = df_stacked.groupby(df_stacked["y"].apply(lambda t: t[0]))["y"].apply(
        lambda s: max(int(lane[1]) for lane in s)
    )

    factors = []
    for team in teams:
        for lane in range(max_lanes[team] + 1):
            factors.append((team, str(lane)))

    source_inside = ColumnDataSource(df_stacked[df_stacked["label_above"] == False].reset_index(drop=True))
    source_above = ColumnDataSource(df_stacked[df_stacked["label_above"] == True].reset_index(drop=True))
    source_all = ColumnDataSource(df_stacked.reset_index(drop=True))

    p = figure(
        title=f"Gantt Chart for Sprint: {sprint_name}",
        x_axis_type="datetime",
        height=300 + 55 * len(factors),
        width=1200,
        y_range=FactorRange(*reversed(factors)),
        tools="xpan,reset,save",
        toolbar_location="above"
    )

    p.rect(x='center', y='y', width='width', height=0.55, source=source_all, fill_color="steelblue", line_color="black")

    labels_inside = LabelSet(
        x='center',
        y='y',
        text='Key',
        source=source_inside,
        text_align='center',
        text_baseline='middle',
        text_font_size='9pt',
        text_color='black'
    )
    p.add_layout(labels_inside)

    labels_above = LabelSet(
        x='center',
        y='y',
        text='Key',
        source=source_above,
        text_align='center',
        y_offset=15,          # Bumped up for more clearance
        text_baseline='bottom',
        text_font_size='9pt',
        text_color='black'      # RED for debug; change to 'black' when happy!
    )
    p.add_layout(labels_above)

    hover = HoverTool(
        tooltips=[
            ("Key", "@Key"),
            ("Summary", "@Summary"),
            ("Assignee", "@Assignee"),
            ("Start", "@StartDate{%Y-%m-%d}"),
            ("End", "@TargetEnd{%Y-%m-%d}")
        ],
        formatters={"@StartDate": "datetime", "@TargetEnd": "datetime"}
    )
    p.add_tools(hover)

    min_date = df_stacked["StartDate"].min()
    max_date = df_stacked["AdjustedEnd"].max()
    total_days = (max_date - min_date).days + 1

    p.xaxis.ticker = DatetimeTicker()
    p.xaxis.ticker.desired_num_ticks = total_days

    now = pd.Timestamp.now().normalize()
    today_line = Span(location=now.value / 1e6, dimension='height',
                      line_color='red', line_width=2, line_dash='dashed')
    p.add_layout(today_line)

    p.ygrid.grid_line_color = "gray"
    p.ygrid.grid_line_dash = "dotted"
    p.yaxis.axis_label = "Team"
    p.xaxis.axis_label = "Date"
    p.xaxis.major_label_orientation = 0.785

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
        output_file(tmpfile.name)
        save(p)
        os.startfile(tmpfile.name)
