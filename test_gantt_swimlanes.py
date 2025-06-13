import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Create a sample dataframe with tasks that touch
data = {
    'Key': ['TASK-1', 'TASK-2', 'TASK-3', 'TASK-4', 'TASK-5', 'TASK-6', 'TASK-7'],
    'Summary': ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5', 'Task 6', 'Task 7'],
    'StartDate': [
        '2025-06-01', 
        '2025-06-05',  # This ends where TASK-1 ends
        '2025-06-07', 
        '2025-06-12',  # This starts where TASK-3 ends
        '2025-06-01',
        '2025-06-10',  # This starts where TASK-5 ends
        '2025-06-10'   # This starts at the same time as TASK-6
    ],
    'DueDate': [
        '2025-06-05', 
        '2025-06-10',
        '2025-06-12',
        '2025-06-15',
        '2025-06-10',
        '2025-06-15',
        '2025-06-20'
    ],
    'Team': ['Team A', 'Team A', 'Team A', 'Team A', 'Team B', 'Team B', 'Team B']
}

df = pd.DataFrame(data)

# Convert date strings to datetime.date objects
df['StartDate'] = pd.to_datetime(df['StartDate']).dt.date
df['DueDate'] = pd.to_datetime(df['DueDate']).dt.date
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
        start, end = row['StartDate'], row['DueDate']

        for level in range(len(levels) + 1):
            conflict = False
            for other_start, other_end in levels[level] if level < len(levels) else []:
                # Original overlap check
                overlap = start <= other_end and end >= other_start
                # Check if tasks touch (one ends exactly when another starts)
                touch = start == other_end or end == other_start
                # Check if one task starts the day after another ends (adjacency)
                adjacent = (start - timedelta(days=1) == other_end) or (other_start - timedelta(days=1) == end)
                if overlap or touch or adjacent:
                    conflict = True
                    break

            if not conflict:
                if level >= len(levels):
                    levels.append([])
                levels[level].append((start, end))
                sublane_assignments[row.name] = level
                break

    max_sublanes_per_team[team] = len(levels)
    
    # Print results for this team
    print(f"\nTeam: {team}")
    print(f"Sublanes required: {len(levels)}")
    for i, level in enumerate(levels):
        print(f"  Sublane {i}: {len(level)} tasks")

# Setup chart dimensions
min_date = df['StartDate'].min() - timedelta(days=1)
max_date = df['DueDate'].max() + timedelta(days=1)
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
    end = row['DueDate']
    # Use a slightly reduced width to avoid visual touching
    width = (end - start).days + 0.9

    ax.barh(
        y=y,
        width=width,
        left=start,
        height=0.4,
        align='center',
        color='skyblue',
        edgecolor='black'
    )

    # Add issue key as a label above the bar
    label = f"{row['Key']}"
    ax.text(start, y - 0.15, label, va='bottom', ha='left', fontsize=8)

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

# Format axes
ax.set_xlim(min_date, max_date)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
fig.autofmt_xdate()
ax.grid(axis='x', color='lightgrey', linestyle='-', linewidth=0.5)
ax.set_title("Test Gantt Chart - Tasks That Touch Should Be On Different Swimlanes")
plt.tight_layout()

# Display details of sublane assignments
print("\nTask Sublane Assignments:")
for idx, row in df.iterrows():
    print(f"{row['Key']} (Team {row['Team']}): Sublane {sublane_assignments.get(idx, 0)}")

# Save the chart
plt.savefig('test_gantt_swimlanes.png')
print("\nChart saved to test_gantt_swimlanes.png")

# Show the chart
plt.show(block=True)
