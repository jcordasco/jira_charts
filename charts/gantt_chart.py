from chart_registry_v2 import register_chart
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@register_chart("gantt")
def gantt_chart(df, export_path=None):
    """
    Generate a Gantt chart from a dataframe of issues.
    
    Args:
        df: pandas DataFrame containing issue data with at least StartDate, TargetEnd, and Team columns
        export_path: Optional path to save the chart to an image file
        
    Returns:
        pandas DataFrame with the processed data, including Sublane assignments
    """
    logger.info("Generating Gantt chart (non-blocking rendering)...")

    if df.empty:
        logger.warning("No data to chart.")
        return None

    # Prepare data
    df['StartDate'] = pd.to_datetime(df['StartDate'], errors='coerce').dt.date
    df['TargetEnd'] = pd.to_datetime(df['TargetEnd'], errors='coerce').dt.date
    df = df.dropna(subset=['StartDate', 'TargetEnd']).copy()
    df['Team'] = df['Team'].fillna("Team Unassigned")
    df = df.sort_values(['Team', 'StartDate']).reset_index(drop=True)

    # Organize issues in swimlanes
    teams = df['Team'].unique()
    team_offsets = {team: i for i, team in enumerate(teams)}
    sublane_assignments = {}
    max_sublanes_per_team = {}
    
    # Prevent overlapping tasks with sublane assignment
    for team in teams:
        team_rows = df[df['Team'] == team].copy()
        levels = []

        for _, row in team_rows.iterrows():
            start, end = row['StartDate'], row['TargetEnd']

            for level in range(len(levels) + 1):
                conflict = False
                for other_start, other_end in levels[level] if level < len(levels) else []:
                    if start <= other_end and end >= other_start:
                        conflict = True
                        break

                if not conflict:
                    if level >= len(levels):
                        levels.append([])
                    levels[level].append((start, end))
                    sublane_assignments[row.name] = level
                    break

        max_sublanes_per_team[team] = len(levels)

    # Setup chart dimensions
    min_date = df['StartDate'].min() - timedelta(days=1)
    max_date = df['TargetEnd'].max() + timedelta(days=1)
    total_lanes = sum(max_sublanes_per_team[team] for team in teams)
    fig_height = max(6, total_lanes * 0.6)
    fig, ax = plt.subplots(figsize=(14, fig_height))

    # Calculate y-positions for each team
    y_positions = {}
    offset = 0
    for team in teams:
        y_positions[team] = offset
        offset += max_sublanes_per_team[team]

    # Plot each issue as a horizontal bar
    for idx, row in df.iterrows():
        team = row['Team']
        sublane = sublane_assignments.get(idx, 0)
        y = y_positions[team] + sublane

        start = row['StartDate']
        end = row['TargetEnd']
        width = (end - start).days + 1

        ax.barh(
            y=y,
            width=width,
            left=start,
            height=0.4,
            align='center',
            color='skyblue',
            edgecolor='black'
        )

        # Add issue key as a label
        label = f"{row['Key']}"
        ax.text(start, y, label, va='center', ha='left', fontsize=8)

    # Set up y-axis ticks and labels for teams
    yticks = []
    ylabels = []
    for team in teams:
        yticks.append(y_positions[team] + (max_sublanes_per_team[team] - 1) / 2)
        ylabels.append(team)

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()  # Invert y-axis to show teams from top to bottom

    # Add team separator lines
    for team in teams[1:]:
        y = y_positions[team]
        ax.axhline(y=y - 0.5, color='lightgrey', linewidth=1, linestyle='--')

    # Add today marker
    today = datetime.today().date()
    if min_date <= today <= max_date:
        ax.axvline(today, color='red', linewidth=1.5, linestyle='-')

    # Format axes
    ax.set_xlim(min_date, max_date)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()
    ax.grid(axis='x', color='lightgrey', linestyle='-', linewidth=0.5)
    ax.set_title("Jira Gantt Chart")
    plt.tight_layout()

    # Save or display the chart
    if export_path:
        plt.savefig(export_path)
        logger.info(f"Chart exported to: {export_path}")
    else:
        plt.show(block=False)

    # Return processed dataframe for export
    df_export = df.copy()
    df_export['Sublane'] = df_export.index.map(lambda idx: sublane_assignments.get(idx, 0))
    return df_export
