# stdlib
from operator import itemgetter
import argparse

# 3rd party
import pyodbc
from pandas import read_csv


def hash_id_updater(retailer):
    '''updates HashIds db table with latest IDs from CSV file.
    retailer: str; "PS4" or "XB1".
    not yet implemented.
    '''
    # connection to the SQL db
    conn = pyodbc.connect(
        '''
        Driver={ODBC Driver 17 for SQL Server};
        Server=.;
        Database=DMT;
        Trusted_Connection=yes;
        '''
    )
    cursor = conn.cursor()

    # gets latest ID from db table
    latest_id = cursor.execute(
        '''
        SELECT TOP 1 [HashId]
        FROM [DMT].[RetailTracker].[HashIds]
        ORDER BY [HashId] DESC;
        '''
    )

    # creates a list of tuples [(HashId, RetailerId, HashValue)] from
    # IDs csv file, filtered by Hash IDs greater than the latest_id from the db
    idfile = 'example/filepath/{retailer}_scraper/reference_directory/{retailer}_ids.csv'
    df = read_csv(idfile)
    records_list = list(df.to_records(index=False))
    hashlist = [i for i in records_list if i[0] > latest_id]

    # fixes any empty/incorrect values in hashlist and re-sorts on hash_ids
    for thing in hashlist:
        hash_id, retailer_id, hash_value = thing
        if hash_id is None or hash_value is None:
            hashlist.remove(thing)
            continue
        elif retailer_id is None:
            retailer_id = 13
            hashlist[hashlist.index(thing)] = (hash_id, retailer_id, hash_value)
            continue
    hashlist.sort(key=itemgetter(0))

    # inserts new values into db
    insert_sql = (
        '''
        INSERT INTO [DMT].[RetailTracker].[HashIds] (HashId, RetailerId, HashValue)
        VALUES (?, ?, ?);
        '''
    )
    cursor.executemany(
        insert_sql,
        hashlist
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store_true')
    parser.add_argument('-x', action='store_true')
    args = parser.parse_args()

    if args.p:
        hash_id_updater('PS4')
    elif args.x:
        hash_id_updater('XB1')
    else:
        print('Error! Argument should be -p or -x.')
