import argparse


def main():
    parser = argparse.ArgumentParser(description='tw_stocker CLI')
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('download', help='Run full data download (init.py)')
    subparsers.add_parser('update', help='Run data update (update.py)')
    subparsers.add_parser('recommend', help='Run recommendation/report generation (recommend.py)')
    subparsers.add_parser('example', help='Run example script (example.py)')

    args = parser.parse_args()

    if args.command == 'download':
        import init

        init.main()
    elif args.command == 'update':
        import update

        update.main()
    elif args.command == 'recommend':
        import recommend

        recommend.main()
    elif args.command == 'example':
        import example

        example.main()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
