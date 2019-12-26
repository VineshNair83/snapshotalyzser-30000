## About

This project is a demo and uses boto3 to manage AWD EC2 instance snapshots

## Configuring

shotty uses the configuration file created by AWS cli. e.g.

`aws configure --profile shotty`

## Running

`pipenv run "python shotty/shotty.py <command> <subcommand> <--project=PROJECT>"`

*command* is instances, volumes, or snapshots\n
*subcommand* - depends on command\n
*project* is optional
