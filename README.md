# Incident Management and Automation Setup

## Overview
This project automates incident management using PagerDuty, Slack, AWS EventBridge, AWS Lambda, Jira, Confluence, and Zoom. The automation ensures streamlined alerting, ticket creation, and documentation processes.

## Workflow
1. **PagerDuty Alert Triggered**
   - An incident occurs, and a PagerDuty alert is triggered.
   
2. **Slack Notification**
   - The PagerDuty alert triggers a Slack notification for visibility.
   
3. **Amazon EventBridge Event Triggered**
   - The alert also triggers an event in Amazon EventBridge.
   
4. **AWS Lambda Execution**
   - The EventBridge rule invokes an AWS Lambda function.
   
5. **Jira Ticket Creation & Slack Notification**
   - The Lambda function creates a Jira ticket with incident details.
   - It also sends a Slack notification with the Jira ticket details.
   
6. **Incident Investigation & Resolution**
   - Engineers update the Jira ticket with investigation details.
   
7. **Confluence Page Creation**
   - Once the Jira ticket is marked as 'Done,' Jira automation creates a Confluence page using the ticket details.
   
8. **Zoom Meeting Creation**
   - Upon incident trigger, a Zoom meeting is automatically created via PagerDuty workflow.

## Project Structure
```
incident-automation/
│── lambda/
│   ├── ira_ticket.py
│── jira_automation/
│   ├── jira_automation.json
│── eventbridge/
│   ├── event_rule.json
│── docs/
│   ├── screenshots/
│── README.md
```

## Setup Guide
### 1. PagerDuty Setup
   - Configure PagerDuty alerts and workflows.
   - Define escalation policies and services.
   
### 2. Slack Integration
   - Setup Slack webhooks for notifications.
   - Create dedicated incident response channels.
   
### 3. Amazon EventBridge
   - Create an EventBridge rule to trigger Lambda functions based on PagerDuty events.
   
### 4. AWS Lambda
   - Deploy a Lambda function to handle Jira ticket creation and Slack notifications.
   - Use environment variables for configuration.
   
### 5. Jira Automation
   - Configure Jira automation to create a Confluence page on ticket closure.
   - Customize issue fields and labels for better tracking.
   
### 6. Zoom Integration
   - Configure PagerDuty workflow to create Zoom meetings for incidents.
   - Automate meeting invitations for relevant teams.

## Python Script for Jira Ticket Creation and Slack Notification
The Python script used in the AWS Lambda function can be found in the repository at:

📂 [`lambda/jira_ticket.py`](lambda/jira_ticket.py)

## Jira Automation for Confluence Page Creation
The JSON configuration for Jira automation that creates Confluence pages is available at:

📂 [`jira_automation/jira_automation.json`](jira_automation/jira_automation.json)

## Usage
- **Incident Trigger**: PagerDuty detects an issue and triggers an alert.
- **Notification**: Slack receives an automated alert with incident details.
- **Automated Response**: Jira ticket is created, and engineers are notified.
- **Incident Resolution**: Engineers investigate and update the Jira ticket.
- **Documentation**: Once the incident is resolved, a Confluence page is generated automatically.
- **Review & Learnings**: The team can review past incidents and improve response strategies.

## Screenshots
Add screenshots for each step in the `docs/screenshots/` directory to provide a visual guide on setting up the workflow.

## Security Considerations
- Store API tokens and credentials securely using AWS Secrets Manager.
- Restrict access to AWS Lambda, Jira, and Slack webhooks to authorized users only.
- Implement logging and monitoring for troubleshooting and auditing purposes.
