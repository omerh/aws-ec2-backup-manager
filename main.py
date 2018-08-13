import boto3
import logging
import os
import sys
import datetime

# Init logger
logger = logging.getLogger(__name__)

# Set log level
if os.environ.get('LOG_LEVEL') is None:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.os.environ['LOG_LEVEL'])

# Set region
if os.environ.get('REGION') is None:
    region = 'eu-central-1'
else:
    region = os.environ['REGION']


# session = boto3.Session(profile_name='mm', region_name=region)
session = boto3.Session(region_name=region)
ec2 = session.resource('ec2')

today = datetime.date.today().strftime("%A")


def create_ec2_volume_snapshot(volume_name, volume_id, instance_id, instance_name):
    logger.info("Creating snapshot for volume {} with id of {} with day tag of {}".format(volume_name, volume_id, today))
    ec2.create_snapshot(
        Description="Snapshot for {} with id {} of ec2 instance {} with id".format(volume_name, volume_id,instance_name ,instance_id),
        VolumeId=volume_id,
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {
                        'Key': 'DeleteOn',
                        'Value': today
                    },
                    {
                        'Key': 'Name',
                        'Value': volume_name + '_' + instance_name + '_' + instance_id + '_' + today
                    },
                    {
                        'Key': 'volume_id',
                        'Value': volume_id
                    },
                    {
                        'Key': 'Originator',
                        'Value': 'Lambda'
                    },
                ]
            },
        ]
    )


def get_ec2_instance_for_backups():
    instances = ec2.instances.filter(Filters=[{'Name': 'tag:Backup', 'Values': ['Yes']}])
    if instances is None:
        return None
    else:
        return instances


def get_ec2_instance_volumes(instance):
    for volume in instance.block_device_mappings:
        logger.debug("volume ids: {}".format(volume['Ebs']['VolumeId']))
        logger.debug("volume ids: {}".format(volume['DeviceName']))
        logger.debug("Instance name is {}".format(instance.meta.data['KeyName']))
        instance_name = instance.meta.data['KeyName']
        if instance_name is None:
            instance_name = 'No_Name_Tag'

        if volume is not None:
            create_ec2_volume_snapshot(volume['DeviceName'], volume['Ebs']['VolumeId'], instance.id, instance_name)


def list_all_volumes_to_delete():
    filter = [
        {'Name': 'tag:DeleteOn', 'Values': [today]}
    ]
    client = session.client('ec2')
    snapshots_to_delete = client.describe_snapshots(Filters=filter)
    if snapshots_to_delete is not None:
        return snapshots_to_delete
    else:
        return None


def delete_snapshot(snapshot_id):
    logger.debug("Deleting snapthot {}".format(snapshot_id))
    try:
        client = session.client('ec2')
        response = client.delete_snapshot(
            SnapshotId=snapshot_id,
            DryRun=False,
        )
        logger.info("deleted snapthot {}".format(str(response)))
    except Exception as ex:
        logger.fatal("Failed to delete snapshot {} with the exception of {}".format(snapshot_id, str(ex)))


def lambda_handler(event, context):
    logger.info("Checking deleting old snapshots")
    volumes_list = list_all_volumes_to_delete()
    if volumes_list is not None:
        for volume in volumes_list['Snapshots']:
            logger.debug(volume)
            delete_snapshot(volume['SnapshotId'])
    else:
        logger.info("There are no snapshot to delete")

    logger.info("Listing all EC2 instances that needs backups")
    ec2_instances = get_ec2_instance_for_backups()
    if ec2_instances is None:
        logger.info("No backups needed")
    else:
        for ec2_instance in ec2_instances:
            logger.debug("Setting backups for {}".format(ec2_instance.id))
            logger.info("Getting list of Volumes for instance {}".format(ec2_instance.id))
            get_ec2_instance_volumes(ec2_instance)


if __name__ == "__main__":
    event = ''
    context = []

    # Logger
    channel = logging.StreamHandler(sys.stdout)
    channel.setFormatter(logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'))
    logger.addHandler(channel)

    lambda_handler(event, context)