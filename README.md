# aws-ec2-backup-manager

AWS Lambda for volume snapshots

Until AWS will spread the life cycle manager to all regions this works ok.
This is for 7 days retention but can easily be changed.

Add to the lambda environment variables for `LOG_LEVEL` and `REGION`

The IAM for the lambda is:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeTags",
                "ec2:CreateTags",
                "ec2:DescribeVolumes",
                "ec2:CreateSnapshot",
                "ec2:DescribeSnapshots"
            ],
            "Resource": "*"
        }
    ]
}
```
