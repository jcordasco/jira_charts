import pandas as pd
import plotly.express as px
import tempfile
import os
from jira_client import api_request
from jira_parser import parse_issues_to_dataframe

def assign_lanes(df):
    df = df.sort_values(by=["StartDate", "TargetEnd"]).copy()
    lanes = []
    end_times = []

    for _, row in df.iterrows():
        assigned = False
        for lane_num, lane_end in enumerate(end_times):
            if row["StartDate"] > lane_end:
                end_times[lane_num] = row["TargetEnd"]
                lanes.append(lane_num)
                assigned = True
                break

        if not assigned:
            end_times.append(row["TargetEnd"])
            lanes.append(len(end_times) - 1)

    df["Lane"] = lanes
    return df

def gantt_chart_for_sprint(sprint_name, export_path=None):
    try:
        print(f"Querying issues for sprint: {sprint_name}")

        jql = f'Sprint = "{sprint_name}"'
        result = api_request(endpoint="search", params={"jql": jql}, paginate=True)
        df = parse_issues_to_dataframe(result)

        if df.empty:
            print("No issues found for this sprint.")
            return

        df = df.dropna(subset=["StartDate", "TargetEnd"])

        if df.empty:
            print("No issues with both StartDate and TargetEnd to plot.")
            return

        df["StartDate"] = pd.to_datetime(df["StartDate"])
        df["TargetEnd"] = pd.to_datetime(df["TargetEnd"])
        df["Team"] = df["Team"].fillna("Unassigned")

        # Build sub-lanes per team
        stacked = []
        for team, group in df.groupby("Team"):
            group = assign_lanes(group)
            group["Subrow"] = group["Lane"]
            group["Swimlane"] = [f"{team}" if lane == 0 else "" for lane in group["Lane"]]
            stacked.append(group)

            # Add blank spacer row for visual separation after each team
            spacer = {
                "Key": None, "Summary": None, "Status": None, "StatusCategory": None, "Created": None,
                "Resolved": None, "StoryPoints": None, "Assignee": None, "TempDev": None, "QATester": None,
                "StartDate": None, "TargetEnd": None, "Team": "", "Subrow": None, "Swimlane": "", "Lane": None,
                "DisplayRow": f"spacer_{team}"
            }
            stacked.append(pd.DataFrame([spacer]))

        df_stacked = pd.concat(stacked, ignore_index=True)

        # Build artificial Y-axis label that stacks while keeping team label only once
        df_stacked["DisplayRow"] = df_stacked.apply(
            lambda row: f"{row['Team']}" if pd.notna(row["Team"]) and row["Team"] != "" and row["Swimlane"] != "" else row["DisplayRow"],
            axis=1
        )

        if export_path:
            df_stacked.to_csv(export_path, index=False)
            print(f"Exported chart data to {export_path}")

        # Filter out spacer rows for plotting bars
        df_plot = df_stacked[df_stacked["StartDate"].notna()]

        # Plot
        fig = px.timeline(
            df_plot,
            x_start="StartDate",
            x_end="TargetEnd",
            y="DisplayRow",
            color="Team",
            text="Key"
        )

        fig.update_yaxes(
            categoryorder="array",
            categoryarray=list(reversed(df_stacked["DisplayRow"].tolist())),
            title="Team"
        )

        fig.update_traces(textposition='inside')

        # Daily ticks on x-axis
        fig.update_xaxes(
            dtick="D1",
            tickformat="%Y-%m-%d"
        )

        fig.update_layout(
            title=f"Gantt Chart for Sprint: {sprint_name}",
            xaxis_title="Date",
            margin=dict(l=20, r=20, t=40, b=20),
            height=300 + (40 * len(df_stacked))
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
            fig.write_html(tmpfile.name)
            os.startfile(tmpfile.name)

    except Exception as e:
        print(f"Error generating Gantt chart: {e}")
