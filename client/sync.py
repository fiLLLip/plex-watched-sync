# sync.py

import sqlite3
import requests
import json
import sys
import time
import props

BASE_URL = props.BASE_URL
SERVER_ID = props.SERVER_ID
DB_PATH = props.DB_PATH
ADMIN_ACCOUNT_REAL_ID = props.ADMIN_ACCOUNT_REAL_ID


def get_request(url, data=None):
    r = requests.get(url, data=json.dumps(data), headers={'X-server-id': SERVER_ID})
    if r.status_code == 404 or r.status_code == 403:
        return None
    return r.json()


def put_request(url, data=None):
    r = requests.put(url, data=json.dumps(data), headers={'X-server-id': SERVER_ID})
    if r.status_code == 404 or r.status_code == 403:
        return None
    return r.json()


class WebService:
    """
    :type base_url:str
    """
    base_url = None

    def __init__(self, base_url):
        self.base_url = base_url

    def get_account_url(self, account_id):
        return self.base_url + '/account/' + str(account_id)

    def get_server_url(self, server_id):
        return self.base_url + '/server' + str(server_id)

    def get_watched_by_account(self, account_id):
        result_json = get_request(self.get_account_url(account_id))
        if result_json is None:
            return None
        return result_json['watched']

    def update_watched_by_account(self, account_id, watched):
        obj = {'watched': list(watched)}
        result = put_request(self.get_account_url(account_id), obj)
        if result is None:
            return None
        return result


class Plex:
    connection = None

    def __init__(self, path):
        try:
            self.connection = sqlite3.connect(path)
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def get_accounts(self):
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM accounts")
        rows = cur.fetchall()
        accounts = set()
        for row in rows:
            if row[0] == 1:
                accounts.add(ADMIN_ACCOUNT_REAL_ID)
            else:
                accounts.add(int(row[0]))
        return accounts

    def get_watched_by(self, account_id):
        cur = self.connection.cursor()
        cur.execute("SELECT guid FROM metadata_item_settings WHERE view_count > 0 AND account_id = ?", (account_id,))
        rows = cur.fetchall()
        items = set()
        for row in rows:
            items.add(row[0])
        return items

    def update_watched(self, account_id, watched):
        local_db_watched = self.get_watched_by(account_id)
        if watched is None:
            watched = set()
        watched = set(watched)
        in_cloud_but_not_in_local_db = watched - local_db_watched
        print "Found " + str(len(in_cloud_but_not_in_local_db)) + " items not in local db for accound_id " + str(
            account_id)
        select_item_sql = "SELECT * FROM metadata_items WHERE guid = ?"
        select_sql = "SELECT view_count FROM metadata_item_settings WHERE account_id = ? AND guid = ?"
        insert_sql = "INSERT INTO metadata_item_settings (account_id, guid, view_count, last_viewed_at, created_at, updated_at, skip_count) VALUES (?, ?, ?, ?, ?, ?, ?)"
        update_sql = "UPDATE metadata_item_settings SET view_count = 1, last_viewed_at = ? WHERE account_id = ? AND guid = ?"
        cur = self.connection.cursor()
        inserted = 0
        updated = 0
        skipped = 0
        for watch_id in in_cloud_but_not_in_local_db:
            cur.execute(select_item_sql, (watch_id,))
            if cur.fetchone() is None:
                skipped += 1
                continue
            cur.execute(select_sql, (account_id, watch_id,))
            row = cur.fetchone()
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 2016-06-15 21:41:38
            if row is None:
                # Insert
                cur.execute(insert_sql, (account_id, watch_id, 1, now, now, now, 0,))
                self.connection.commit()
                inserted += 1
            else:
                # Update, view_count is most likely 0
                cur.execute(update_sql, (now, account_id, watch_id,))
                self.connection.commit()
                updated += 1
        print "Skipped " + str(skipped) + ", inserted " + str(inserted) + ", updated " + str(
            updated) + " items for account_id " + str(account_id) + " in local db"


ws = WebService(BASE_URL)
plex = Plex(DB_PATH)


def update_watched():
    accounts = plex.get_accounts()
    for account_id in accounts:
        print "Checking account_id " + str(account_id)
        if account_id == ADMIN_ACCOUNT_REAL_ID:
            local_account_id = 1
        else:
            local_account_id = account_id
        watched = plex.get_watched_by(local_account_id)
        if watched is not None and len(watched) > 0:
            res = ws.update_watched_by_account(account_id, watched)
            print "Added " + str(res['added']) + " items to cloud for account " + str(account_id)
        watched = ws.get_watched_by_account(account_id)
        plex.update_watched(local_account_id, watched)


start = time.time()
update_watched()
end = time.time()
elapsed = end - start
print "Used " + str(elapsed) + " seconds"
