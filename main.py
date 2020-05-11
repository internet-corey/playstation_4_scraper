# stdlib
import argparse
import os

# files
import functions as fn
import locations as locs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--scrape',
        help=(
            'scrape the ps4 storefront, specify 1 or 2 for first or'
            'second daily run, or any other int for an extra run'
        ),
        type=int
    )
    parser.add_argument(
        '-m',
        '--mp',
        help='number of times to run through carousel placements',
        type=int
    )
    parser.add_argument(
        '-c',
        '--checks',
        help='checks for new and ended promos in specified directory'
    )
    parser.add_argument(
        '-d',
        '--dedupe',
        help='removes dupe images from specified directory'
    )
    args = parser.parse_args()

    if args.scrape == 1:
        if args.mp:
            fn.scrape('first', args.mp)
        else:
            fn.scrape('first')
    elif args.scrape == 2:
        if args.mp:
            fn.scrape('second', args.mp)
        else:
            fn.scrape('second')
    elif args.scrape == 3:
        if args.mp:
            fn.scrape('extra', args.mp)
        else:
            fn.scrape('extra')
    elif args.checks:
        if os.path.isdir(args.checks):
            fn.promo_checks(args.checks)
        else:
            print('Error. Given argument is not a directory.')
    elif args.dedupe:
        if os.path.isdir(args.dedupe):
            for location in locs.promo_crops:
                fn.dupe_remover(args.dedupe, location)
        else:
            print('Error. Given argument is not a directory.')
