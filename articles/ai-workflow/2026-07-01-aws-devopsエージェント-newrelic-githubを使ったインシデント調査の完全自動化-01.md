---
id: "2026-07-01-aws-devopsエージェント-newrelic-githubを使ったインシデント調査の完全自動化-01"
title: "AWS DevOpsエージェント × NewRelic × Githubを使ったインシデント調査の完全自動化"
url: "https://zenn.dev/falcon_tech/articles/ae71c9fb4ceb95"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

```
{
  "Comment": "",
  "StartAt": "ParseEvent",
  "States": {
    "ParseEvent": {
      "Type": "Pass",
      "QueryLanguage": "JSONata",
      "Assign": {
        "Type": "{% $lookup($states.input, 'detail-type') %}",
        "AgentSpaceId": "{% $states.input.detail.metadata.agent_space_id %}",
        "TaskId": "{% $states.input.detail.metadata.task_id %}",
        "ExecutionId": "{% $states.input.detail.metadata.execution_id %}",
        "SummaryRecordId": "{% $exists($states.input.detail.data.summary_record_id) ? $states.input.detail.data.summary_record_id : '' %}"
      },
      "Output": {},
      "Next": "GetBacklogTask"
    },
    "GetBacklogTask": {
      "Type": "Task",
      "QueryLanguage": "JSONata",
      "Resource": "arn:aws:states:::aws-sdk:devopsagent:getBacklogTask",
      "Arguments": {
        "AgentSpaceId": "{% $AgentSpaceId %}",
        "TaskId": "{% $TaskId %}"
      },
      "Assign": {
        "IncidentId": "{% $states.result.Task.Reference.ReferenceId %}",
        "IssueActivatedAt": "{% $fromMillis($number($match($states.result.Task.Description, /issueActivatedAt=([^&]+)/).groups[0]), '[Y0001]-[M01]-[D01]T[H01]:[m01]:[s01]', '+0900') & '+09:00' %}",
        "ConditionName": "{% $match($states.result.Task.Description, /conditionName=([^&]+)/).groups[0] %}",
        "ImpactedEntity": "{% $match($states.result.Task.Description, /impactedEntity=(.+)&issuePageUrl=/).groups[0] %}",
        "IssuePageUrl": "{% $match($states.result.Task.Description, /issuePageUrl=(.+)$/).groups[0] %}",
        "PrimaryTaskId": "{% $exists($states.result.Task.PrimaryTaskId) ? $states.result.Task.PrimaryTaskId : '' %}",
        "StatusReason": "{% $exists($states.result.Task.StatusReason) ? $states.result.Task.StatusReason : '' %}"
      },
      "Output": {},
      "Next": "RouteByType",
      "TimeoutSeconds": 30,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Output": "{% $states.errorOutput %}",
          "Next": "FailureGetBacklogTask"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ]
    },
    "RouteByType": {
      "Type": "Choice",
      "QueryLanguage": "JSONata",
      "Choices": [
        {
          "Condition": "{% $Type = 'Investigation Created' %}",
          "Next": "CreateGitHubIssue"
        }
      ],
      "Default": "FindGitHubIssue"
    },
    "CreateGitHubIssue": {
      "Type": "Task",
      "QueryLanguage": "JSONata",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": {
        "FunctionName": "arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:function:devops-agent-rca-lambda",
        "Payload": {
          "execution_id": "{% $states.context.Execution.Id %}",
          "action": "create_issue",
          "title": "{% '[アラート検知] ' & $ConditionName & ' ' & $IssueActivatedAt & ' ' & $IncidentId %}",
          "body": "{% 'アラートを検知しました。調査を開始します。\n\n調査が完了次第、結果をコメントに記載します。\n\n# 詳細\n監視名: ' & $ConditionName & '\n検知時刻: ' & $IssueActivatedAt & '\n対象リソース: ' & $ImpactedEntity & '\nインシデントID: ' & $IncidentId & '\n調査タスクID: ' & $TaskId & '\n\n調査の進捗情報はDevOpsエージェントの[インシデントレスポンスページ](https://XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.aidevops.global.app.aws/investigation/' & $TaskId & ')で、アラームの詳細はNewRelicの[Issueページ](' & $IssuePageUrl & ')で確認して下さい。' %}",
          "type": "Alert",
          "labels": [
            "devops-agent:progress"
          ],
          "assignees": "{% [] %}",
          "mentions": "{% ['XXXX-X-XXX', 'XXXX-XXXXX', 'XXXX-XXXXXXXX', 'XXXX-XXXXX'] %}"
        }
      },
      "Output": {},
      "Next": "SuccessCreateGitHubIssue",
      "TimeoutSeconds": 30,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Output": "{% $states.errorOutput %}",
          "Next": "FailureCreateGitHubIssue"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ]
    },
    "FindGitHubIssue": {
      "Type": "Task",
      "QueryLanguage": "JSONata",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": {
        "FunctionName": "arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:function:devops-agent-rca-lambda",
        "Payload": {
          "execution_id": "{% $states.context.Execution.Id %}",
          "action": "find_issue",
          "incident_id": "{% $IncidentId %}",
          "labels": [
            "devops-agent:progress"
          ]
        }
      },
      "Assign": {
        "GitHubIssueNumber": "{% $states.result.Payload.issue_number %}"
      },
      "Output": {},
      "Next": "RouteByCommentType",
      "TimeoutSeconds": 30,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Output": "{% $states.errorOutput %}",
          "Next": "FailureFindGitHubIssue"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ]
    },
    "RouteByCommentType": {
      "Type": "Choice",
      "QueryLanguage": "JSONata",
      "Choices": [
        {
          "Condition": "{% $Type = 'Investigation Completed' %}",
          "Next": "ListJournalRecords"
        },
        {
          "Condition": "{% $Type = 'Investigation Linked' %}",
          "Next": "SetLinkedCommentBody"
        }
      ],
      "Default": "SetOtherCommentBody"
    },
    "ListJournalRecords": {
      "Type": "Task",
      "QueryLanguage": "JSONata",
      "Resource": "arn:aws:states:::aws-sdk:devopsagent:listJournalRecords",
      "Arguments": {
        "AgentSpaceId": "{% $AgentSpaceId %}",
        "ExecutionId": "{% $ExecutionId %}",
        "RecordType": "investigation_summary_md"
      },
      "Assign": {
        "CommentBody": "{% $string(($filter($states.result.Records, function($r) { $r.RecordId = $SummaryRecordId }))[0].Content) %}"
      },
      "Output": {},
      "Next": "AddGitHubIssueComment",
      "TimeoutSeconds": 30,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Output": "{% $states.errorOutput %}",
          "Next": "FailureListJournalRecords"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ]
    },
    "SetLinkedCommentBody": {
      "Type": "Pass",
      "QueryLanguage": "JSONata",
      "Assign": {
        "CommentBody": "{% 'この調査は既存の調査にリンクされました。\n\n# リンク先調査\n調査タスクID: ' & $PrimaryTaskId & '\n\n調査の詳細は、DevOpsエージェントの[インシデントレスポンスページ](https://XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.aidevops.global.app.aws/investigation/' & $PrimaryTaskId & ')で確認して下さい。\n\n# リンク理由\n' & $StatusReason %}"
      },
      "Output": {},
      "Next": "AddGitHubIssueComment"
    },
    "SetOtherCommentBody": {
      "Type": "Pass",
      "QueryLanguage": "JSONata",
      "Assign": {
        "CommentBody": "{% $Type = 'Investigation Failed' ? '調査が失敗しました' : $Type = 'Investigation Timed Out' ? '調査がタイムアウトしました' : $Type = 'Investigation Cancelled' ? '調査がキャンセルされました' : $Type = 'Investigation Skipped' ? '調査がスキップされました' : '' %}"
      },
      "Output": {},
      "Next": "AddGitHubIssueComment"
    },
    "AddGitHubIssueComment": {
      "Type": "Task",
      "QueryLanguage": "JSONata",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": {
        "FunctionName": "arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:function:devops-agent-rca-lambda",
        "Payload": {
          "execution_id": "{% $states.context.Execution.Id %}",
          "action": "add_comment",
          "issue_number": "{% $GitHubIssueNumber %}",
          "body": "{% $CommentBody %}",
          "mentions": "{% ['XXXX-X-XXX', 'XXXX-XXXXX', 'XXXX-XXXXXXXX', 'XXXX-XXXXX'] %}"
        }
      },
      "Output": {},
      "Next": "UpdateGitHubIssueLabels",
      "TimeoutSeconds": 30,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Output": "{% $states.errorOutput %}",
          "Next": "FailureAddGitHubIssueComment"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ]
    },
    "UpdateGitHubIssueLabels": {
      "Type": "Task",
      "QueryLanguage": "JSONata",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": {
        "FunctionName": "arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:function:devops-agent-rca-lambda",
        "Payload": {
          "execution_id": "{% $states.context.Execution.Id %}",
          "action": "update_labels",
          "issue_number": "{% $GitHubIssueNumber %}",
          "labels": [
            "devops-agent:finish"
          ]
        }
      },
      "Output": {},
      "Next": "SuccessUpdateGitHubIssueLabels",
      "TimeoutSeconds": 30,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Output": "{% $states.errorOutput %}",
          "Next": "FailureUpdateGitHubIssueLabels"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ]
    },
    "SuccessCreateGitHubIssue": {
      "Type": "Succeed"
    },
    "SuccessUpdateGitHubIssueLabels": {
      "Type": "Succeed"
    },
    "FailureGetBacklogTask": {
      "Type": "Fail",
      "Error": "FailureGetBacklogTask",
      "Cause": "Failed to get backlog task from DevOps Agent"
    },
    "FailureCreateGitHubIssue": {
      "Type": "Fail",
      "Error": "FailureCreateGitHubIssue",
      "Cause": "Failed to create GitHub issue"
    },
    "FailureFindGitHubIssue": {
      "Type": "Fail",
      "Error": "FailureFindGitHubIssue",
      "Cause": "No GitHub issue found with devops-agent:progress label and matching IncidentId"
    },
    "FailureListJournalRecords": {
      "Type": "Fail",
      "Error": "FailureListJournalRecords",
      "Cause": "Failed to retrieve investigation summary from DevOps Agent journal records"
    },
    "FailureAddGitHubIssueComment": {
      "Type": "Fail",
      "Error": "FailureAddGitHubIssueComment",
      "Cause": "Failed to add comment to GitHub issue"
    },
    "FailureUpdateGitHubIssueLabels": {
      "Type": "Fail",
      "Error": "FailureUpdateGitHubIssueLabels",
      "Cause": "Failed to update GitHub issue labels"
    }
  }
}
```
