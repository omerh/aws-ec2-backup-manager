# aws-ec2-backup-manager
AWS Lambda for volume snapshots

Until AWS will spread the life cycle manager to all regions this works ok.
This is for 7 days retention but can easily be changed.

Add to the lambda environment variables for `LOG_LEVEL` and `REGION`

Make sure to give lambda role for EC2 CreateSnapshot and Readonly volumes and DescribeTags