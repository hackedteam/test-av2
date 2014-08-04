import argparse


def main2():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                       help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                       const=sum, default=max,
                       help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print args.accumulate(args.integers)

def main():
    parser = argparse.ArgumentParser(description='AVMonitor master.')
    
    parser.add_argument('action', choices=['update', 'revert', 'dispatch', 'test'])
    parser.add_argument('--vm', required=False)
    parser.add_argument('-p', '--pool', default=2)
    args = parser.parse_args()

    print args
    print args.action
    print args.vm


if __name__ == "__main__":
    main()