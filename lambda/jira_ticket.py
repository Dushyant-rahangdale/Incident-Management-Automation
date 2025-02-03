import os
import json
import urllib3
import base64

# Ensure these environment variables are set
JIRA_URL = os.environ.get('JIRA_URL')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY')
PAGERDUTY_API_TOKEN = os.environ.get('PAGERDUTY_API_TOKEN')
SLACK_WEBHOOK_URL_1 = os.environ.get('SLACK_WEBHOOK_URL_1')
SLACK_WEBHOOK_URL_2 = os.environ.get('SLACK_WEBHOOK_URL_2')

def lambda_handler(event, context):
    try:
        detail = event.get('detail', {})
        if not detail:
            raise ValueError("Missing key in event payload: 'detail'")

        priority, summary, description, service_name, incident_url, created_at, trigger, severity = extract_details(detail)

        if priority in ["P1", "P2"] and trigger == "incident.trigger":
            labels = ["bug-prioritization", severity, "911"]
            jira_ticket_url = create_jira_ticket(summary, description, severity, incident_url, labels)
            send_slack_notification(jira_ticket_url, summary, description, severity, priority, service_name, incident_url, created_at)
            return {
                'statusCode': 200,
                'body': json.dumps({"message": "JIRA ticket created and Slack notifications sent successfully.", "jira_ticket_url": jira_ticket_url})
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({"message": "Either incident priority is not high enough or trigger is not 'incident.trigger' to create a JIRA ticket."})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }

def extract_details(detail):
    log_entries = detail.get('log_entries', [])
    if not log_entries:
        raise ValueError("Missing key in event payload: 'log_entries'")

    service_summary = log_entries[0].get('service', {}).get('summary', 'N/A')
    incident_url = log_entries[0].get('incident', {}).get('html_url', 'N/A')

    incident = detail.get('incident', {})
    service_name = incident.get('service', {}).get('summary', 'N/A')
    created_at = incident.get('created_at', 'N/A')
    priority = incident.get('priority', {}).get('name', 'N/A')
    trigger = detail.get('event', 'N/A')

    channel_details = log_entries[0].get('channel', {}).get('details', 'N/A')
    description = (
        f"Service Name: {service_name}\n"
        f"Incident URL: {incident_url}\n"
        f"Description: {channel_details}\n"
        f"Created At: {created_at}\n"
        f"Priority: {priority}"
    )

    severity = ""
    if priority == "P1":
        severity = "Sev-0"
    elif priority == "P2":
        severity = "Sev-1"

    return priority, f"Incident: {service_name} - {detail.get('title', 'No title')} - {created_at}", description, service_name, incident_url, created_at, trigger, severity

def create_jira_ticket(summary, description, severity, incident_url, labels):
    http = urllib3.PoolManager()
    url = f"{JIRA_URL}/rest/api/2/issue/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    }
    data = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": summary,
            "description": description,
            "customfield_10404": incident_url,
            "customfield_10155": {"value": severity},
            "issuetype": {
                "name": "Bug"
            },
            "labels": labels
        }
    }
    encoded_data = json.dumps(data).encode('utf-8')
    response = http.request('POST', url, headers=headers, body=encoded_data)

    if response.status != 201:
        raise Exception(f"Failed to create JIRA ticket: {response.status}, {response.data.decode('utf-8')}")

    response_data = json.loads(response.data.decode('utf-8'))
    jira_ticket_key = response_data['key']
    jira_ticket_url = f"{JIRA_URL}/browse/{jira_ticket_key}"

    return jira_ticket_url

def send_slack_notification(jira_ticket_url, summary, description, severity, priority, service_name, incident_url, created_at):
    http = urllib3.PoolManager()

    for webhook_url in [SLACK_WEBHOOK_URL_1, SLACK_WEBHOOK_URL_2]:
        slack_message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*:jira-new:    Jira Issue Created for Major Incident*"
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*  :alert:  Priority:* {priority}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*:confused_animated:  Impacted Service:* {service_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Issue Title:* {summary}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:* {severity}"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f":arrow_right: Document all significant findings related to the major incident in the JIRA issue for our comprehensive post-incident analysis."
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View JIRA Ticket"
                            },
                            "url": jira_ticket_url,
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View PagerDuty Incident"
                            },
                            "url": incident_url,
                            "style": "primary"
                        }
                    ]
                }
            ]
        }

        encoded_data = json.dumps(slack_message).encode('utf-8')
        response = http.request('POST', webhook_url, headers={'Content-Type': 'application/json'}, body=encoded_data)
