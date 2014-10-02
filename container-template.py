#!/usr/bin/env python

import argparse

def main():
    """Entrypoint for script"""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')
    run_parser = subparsers.add_parser('run', help='Run a container from metadata file')
    run_parser.add_argument('json',
                       metavar='MYAPP.JSON',
                       help='JSON file')
    create_parser = subparsers.add_parser('create', help='Generate metadata based on a container')
    create_parser.add_argument('cuid',
                       metavar='CONTAINER_ID',
                       help='Container ID')
    create_parser.add_argument('-o', '--outfile',
                       help='Specify metadata output filename. Defaults to container ID.')
    create_parser.add_argument('-f', '--force',
                       action='store_true',
                       help='Overwrite existing metadata file. Defaults to false.')
    list_parser = subparsers.add_parser('list', help='List local metadata files')
    list_parser.add_argument('-l', '--local',
                       action='store_true',
                       help='List only files in current working directory')

    args = parser.parse_args()

    if args.action in "run":
        import docker_wrapper
        # TODO: use kwargs
        run = docker_wrapper.Run(args.action, args.json)
        run.start_container()

    elif args.action in "create":
        import metadata
        # TODO: use kwargs
        create = metadata.Create(args.cuid, args.outfile, args.force)
        create.metadata_file()
    elif args.action in "list":
        import metadata
        # TODO: use kwargs
        filelist = metadata.List(args.local)
        filelist.metadata_files()

if __name__ == '__main__':
    main()

