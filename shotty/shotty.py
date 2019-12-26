import boto3
import botocore
import click
import sys

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Comand for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only snapshots for project(tag project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all):
    "List EC2 snapshots"
    instances = filter_instances(project)
    for i in instances.all():
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(','.join((
                s.id,
                v.id,
                i.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))
                if s.state == "completed" and not list_all: break
    return

@cli.group('volumes')
def volumes():
    """Command for volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project(tag project:<name>)")
def list_volumes(project):
    "List EC2 volumes"
    instances = filter_instances(project)
    for i in instances.all():
        for v in i.volumes.all():
            print(','.join((
            v.id,
            i.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot', help='Create snapshots for all volumes')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("Creating snapshot for {0}".format(v.id))
            v.create_snapshot(Description="Created by SnapshotAnlyzer 30000")
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()
    print("Job's done!")
    return


@instances.command('list')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = filter_instances(project)
    for i in instances.all():
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(','.join((
        i.id,
        i.instance_type,
        i.placement['AvailabilityZone'],
        i.state['Name'],
        i.public_dns_name,
        tags.get('Project','<no project>')
        )))
    return

@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
    "Stop EC2 Instances"
    instances = filter_instances(project)
    print(instances)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')
def start_instances(project):
    "Start EC2 Instances"
    instances = filter_instances(project)
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}. ".format(i.id) + str(e))
            continue
    return

if __name__ == '__main__':
    cli()
