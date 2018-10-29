"""
This file contains everything related to persistence for DAppCrowd.
"""
from __future__ import absolute_import

import os

from pyipv8.ipv8.database import Database, database_blob
from pyipv8.ipv8.util import is_unicode

DATABASE_DIRECTORY = os.path.join(u"sqlite")


class DAppCrowdDatabase(Database):
    """
    Persistence layer for the DAppCrowd Community.
    Connection layer to SQLiteDB.
    Ensures a proper DB schema on startup.
    """
    LATEST_DB_VERSION = 1

    def __init__(self, working_directory, db_name):
        """
        Sets up the persistence layer ready for use.
        :param working_directory: Path to the working directory
        that will contain the the db at working directory/DATABASE_PATH
        :param db_name: The name of the database
        """
        if working_directory != u":memory:":
            db_path = os.path.join(working_directory, os.path.join(DATABASE_DIRECTORY, u"%s.db" % db_name))
        else:
            db_path = working_directory
        super(DAppCrowdDatabase, self).__init__(db_path)
        self._logger.debug("DAppCrowd database path: %s", db_path)
        self.db_name = db_name
        self.open()

    def get_schema(self):
        """
        Return the schema for the database.
        """
        return u"""
        CREATE TABLE IF NOT EXISTS apprequests(
        id                 INTEGER NOT NULL,
        public_key         TEXT NOT NULL,
        name               TEXT NOT NULL,
        specifications     TEXT NOT NULL,
        deadline           BIGINT NOT NULL,
        reward             DOUBLE NOT NULL,
        currency           TEXT NOT NULL,
        min_reviews        INTEGER NOT NULL,
        notary_signature   TEXT NOT NULL,
        block_validators   INTEGER NOT NULL,
        
         PRIMARY KEY (id, public_key)
         );
         
         CREATE TABLE IF NOT EXISTS submissions(
         id                 INTEGER NOT NULL,
         public_key         TEXT NOT NULL,
         apprequest_id      INTEGER NOT NULL,
         apprequest_pk      TEXT NOT NULL,
         submission         TEXT NOT NULL,
         num_reviews        INTEGER NOT NULL,
         
         PRIMARY KEY (id, public_key)
         );
         
         CREATE TABLE IF NOT EXISTS reviews(
         id                 INTEGER NOT NULL,
         public_key         TEXT NOT NULL,
         submission_id      INTEGER NOT NULL,
         submission_pk      TEXT NOT NULL,
         review             TEXT NOT NULL,
         
         PRIMARY KEY (id, public_key)
         );
         
        CREATE TABLE IF NOT EXISTS option(key TEXT PRIMARY KEY, value BLOB);
        DELETE FROM option WHERE key = 'database_version';
        INSERT INTO option(key, value) VALUES('database_version', '%s');
        """ % str(self.LATEST_DB_VERSION)

    def get_upgrade_script(self, current_version):
        """
        Return the upgrade script for a specific version.
        :param current_version: the version of the script to return.
        """
        return None

    def add_app_request(self, block):
        """
        Add an app request to the database, from a given block
        """
        tx = block.transaction
        last_id = list(self.execute("SELECT MAX(id) FROM apprequests"))[0][0]
        if not last_id:
            last_id = 0
        sql = "INSERT INTO apprequests(id, public_key, name, specifications, deadline, reward, currency, min_reviews, notary_signature, block_validators) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.execute(sql, (last_id + 1, database_blob(block.public_key), database_blob(tx['name']), database_blob(tx['specifications']),
                           tx['deadline'], tx['reward'], database_blob(tx['currency']), tx['min_reviews'], database_blob(tx['notary_signature']), 0))
        self.commit()

    def get_app_requests(self):
        app_requests = list(self.execute("SELECT * FROM apprequests;"))
        requests_list = []
        for app_request in app_requests:
            request_dict = {
                "id": app_request[0],
                "public_key": str(app_request[1]).encode('hex'),
                "name": str(app_request[2]),
                "specifications": str(app_request[3]),
                "deadline": app_request[4],
                "reward": app_request[5],
                "currency": str(app_request[6]),
                "min_validators": app_request[7],
                "notary_signature": str(app_request[8]).encode('hex'),
                "block_validators": app_request[9]
            }
            requests_list.append(request_dict)

        return requests_list

    def add_submission(self, block):
        """
        Add a submission to the database, from a given block
        """
        tx = block.transaction
        last_id = list(self.execute("SELECT MAX(id) FROM submissions"))[0][0]
        if not last_id:
            last_id = 0
        sql = "INSERT INTO submissions(id, public_key, apprequest_id, apprequest_pk, submission, num_reviews) VALUES(?, ?, ?, ?, ?, ?)"
        self.execute(sql, (last_id + 1, database_blob(block.public_key), database_blob(tx['apprequest_id']), database_blob(tx['apprequest_pk']), database_blob(tx['submission']), 0))
        self.commit()

    def get_submissions(self):
        """
        Get all submission
        """
        submissions = list(self.execute("SELECT * FROM submissions"))
        submissions_list = []
        for submission in submissions:
            submission_dict = {
                "id": submission[0],
                "public_key": str(submission[1]).encode('hex'),
                "apprequest_id": int(submission[2]),
                "apprequest_pk": str(submission[3]).encode('hex'),
                "submission": str(submission[4]),
                "num_reviews": submission[5]
            }
            submissions_list.append(submission_dict)

        return submissions_list

    def add_review(self, block):
        """
        Add a review to the database, from a given block
        """
        tx = block.transaction
        last_id = list(self.execute("SELECT MAX(id) FROM reviews"))[0][0]
        if not last_id:
            last_id = 0
        sql = "INSERT INTO reviews(id, public_key, submission_id, submission_pk, review) VALUES(?, ?, ?, ?, ?)"
        self.execute(sql, (last_id + 1, database_blob(block.public_key), database_blob(tx['submission_id']), database_blob(tx['submission_pk']), database_blob(tx['review'])))
        self.commit()

    def get_reviews(self, submission_id, submission_pk):
        """
        Get all reviews for a specific submission.
        """
        reviews = list(self.execute("SELECT * FROM reviews WHERE submission_id = ? AND submission_pk = ?", (database_blob(submission_id), database_blob(submission_pk))))
        reviews_list = []
        for review in reviews:
            submission_dict = {
                "id": review[0],
                "public_key": str(review[1]).encode('hex'),
                "submission_id": int(review[2]),
                "submission_pk": str(review[3]).encode('hex'),
                "review": str(review[4]),
            }
            reviews_list.append(submission_dict)

        return reviews_list

    def open(self, initial_statements=True, prepare_visioning=True):
        return super(DAppCrowdDatabase, self).open(initial_statements, prepare_visioning)

    def close(self, commit=True):
        return super(DAppCrowdDatabase, self).close(commit)

    def check_database(self, database_version):
        """
        Ensure the proper schema is used by the database.
        :param database_version: Current version of the database.
        :return:
        """
        assert is_unicode(database_version)
        assert database_version.isdigit()
        assert int(database_version) >= 0
        database_version = int(database_version)

        if database_version < self.LATEST_DB_VERSION:
            self.executescript(self.get_schema())

        return self.LATEST_DB_VERSION
