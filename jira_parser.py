import pandas as pd

# Custom fields mapping
STORY_POINTS_FIELD = "customfield_10010"
TEMP_DEV_FIELD = "customfield_11801"
QA_TESTER_FIELD = "customfield_13196"
START_DATE_FIELD = "customfield_13135"
TARGET_END_FIELD = "customfield_13192"
TEAM_FIELD = "customfield_11400"
SPRINT_FIELD = "customfield_10002"

def parse_issues_to_dataframe(jira_json):
    issues = jira_json.get("issues", [])
    parsed = []

    for issue in issues:
        fields = issue.get("fields", {})

        # Sprint extraction
        sprint_list = fields.get(SPRINT_FIELD)
        sprint_name = None
        if sprint_list and isinstance(sprint_list, list) and len(sprint_list) > 0:
            sprint_name = sprint_list[0].get("name")

        # IssueType extraction
        issuetype = fields.get("issuetype", {})
        issue_type_name = issuetype.get("name")
        issue_type_subtask = issuetype.get("subtask")
        issue_type_hierarchy = issuetype.get("hierarchyLevel")

        parsed_issue = {
            "Key": issue.get("key"),
            "Summary": fields.get("summary"),
            "Status": fields.get("status", {}).get("name"),
            "StatusCategory": fields.get("status", {}).get("statusCategory", {}).get("name"),
            "Created": fields.get("created"),
            "Resolved": fields.get("resolutiondate"),
            "StoryPoints": fields.get(STORY_POINTS_FIELD),
            "Assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            "TempDev": fields.get(TEMP_DEV_FIELD, {}).get("displayName") if fields.get(TEMP_DEV_FIELD) else None,
            "QATester": fields.get(QA_TESTER_FIELD, {}).get("displayName") if fields.get(QA_TESTER_FIELD) else None,
            "StartDate": fields.get(START_DATE_FIELD),
            "TargetEnd": fields.get(TARGET_END_FIELD),
            "Team": fields.get(TEAM_FIELD, {}).get("name") if fields.get(TEAM_FIELD) else None,
            "Sprint": sprint_name,
            "IssueType": issue_type_name,
            "IssueTypeSubtask": issue_type_subtask,
            "IssueTypeHierarchy": issue_type_hierarchy
        }

        parsed.append(parsed_issue)

    df = pd.DataFrame(parsed)
    return df
