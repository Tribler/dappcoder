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
        CREATE TABLE IF NOT EXISTS projects(
        id                 INTEGER NOT NULL,
        public_key         TEXT NOT NULL,
        name               TEXT NOT NULL,
        specifications     TEXT NOT NULL,
        deadline           BIGINT NOT NULL,
        reward             DOUBLE NOT NULL,
        currency           TEXT NOT NULL,
        min_reviews        INTEGER NOT NULL,
        notary_signature   TEXT NOT NULL,
        
         PRIMARY KEY (id, public_key)
         );
         
         CREATE TABLE IF NOT EXISTS submissions(
         id                 INTEGER NOT NULL,
         public_key         TEXT NOT NULL,
         project_id         INTEGER NOT NULL,
         project_pk         TEXT NOT NULL,
         submission         TEXT NOT NULL,
         
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

    def get_next_project_id(self, public_key):
        """
        Get the next project ID for a given public key.
        """
        last_id = list(self.execute("SELECT MAX(id) FROM projects WHERE public_key = ?", (database_blob(public_key),)))[0][0]
        if not last_id:
            last_id = 0
        return last_id + 1

    def add_project(self, block):
        """
        Add a project to the database, from a given block
        """
        tx = block.transaction
        sql = "INSERT INTO projects(id, public_key, name, specifications, deadline, reward, currency, min_reviews, notary_signature) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.execute(sql, (tx['id'], database_blob(block.public_key), database_blob(tx['name']), database_blob(tx['specifications']),
                           tx['deadline'], tx['reward'], database_blob(tx['currency']), tx['min_reviews'], database_blob(tx['notary_signature'])))
        self.commit()

    def get_projects(self):
        projects = list(self.execute("SELECT * FROM projects;"))
        projects_list = []
        for app_request in projects:
            request_dict = {
                "id": app_request[0],
                "public_key": str(app_request[1]).encode('hex'),
                "name": str(app_request[2]),
                "specifications": str(app_request[3]),
                "deadline": app_request[4],
                "reward": app_request[5],
                "currency": str(app_request[6]),
                "min_reviews": app_request[7],
                "notary_signature": str(app_request[8]).encode('hex'),
            }
            projects_list.append(request_dict)

        return projects_list

    def get_project(self, project_pk, project_id):
        if not self.has_project(project_pk, project_id):
            return None

        project = list(self.execute("SELECT * FROM projects WHERE id = ? AND public_key = ?", (project_id, database_blob(project_pk))))[0]
        return {
            "id": project[0],
            "public_key": str(project[1]).encode('hex'),
            "name": str(project[2]),
            "specifications": str(project[3]),
            "deadline": project[4],
            "reward": project[5],
            "currency": str(project[6]),
            "min_reviews": project[7],
            "notary_signature": str(project[8]).encode('hex'),
        }

    def has_project(self, public_key, request_id):
        return len(list(self.execute("SELECT * FROM projects WHERE id = ? and public_key = ?", (request_id, database_blob(public_key))))) > 0

    def get_next_submission_id(self, public_key):
        """
        Get the next submission ID for a given public key.
        """
        last_id = list(self.execute("SELECT MAX(id) FROM submissions WHERE public_key = ?", (database_blob(public_key),)))[0][0]
        if not last_id:
            last_id = 0
        return last_id + 1

    def add_submission(self, block):
        """
        Add a submission to the database, from a given block
        """
        tx = block.transaction
        last_id = list(self.execute("SELECT MAX(id) FROM submissions"))[0][0]
        if not last_id:
            last_id = 0
        sql = "INSERT INTO submissions(id, public_key, project_id, project_pk, submission) VALUES(?, ?, ?, ?, ?)"
        self.execute(sql, (last_id + 1, database_blob(block.public_key), tx['project_id'], database_blob(tx['project_pk']), database_blob(tx['submission'])))
        self.commit()

    def has_submission(self, public_key, submission_id):
        return len(list(self.execute("SELECT * FROM submissions WHERE id = ? and public_key = ?", (submission_id, database_blob(public_key))))) > 0

    def get_submissions_for_user(self, public_key):
        """
        Get submissions for a specific user
        """
        submissions = list(self.execute("SELECT * FROM submissions WHERE public_key = ?", (database_blob(public_key), )))
        submissions_list = []
        for submission in submissions:
            submission_dict = {
                "id": submission[0],
                "public_key": str(submission[1]).encode('hex'),
                "project_id": int(submission[2]),
                "project_pk": str(submission[3]).encode('hex'),
                "submission": str(submission[4]),
            }
            submissions_list.append(submission_dict)

        return submissions_list

    def get_reviews_for_user(self, public_key):
        """
        Get reviews for a specific user
        """
        reviews = list(self.execute("SELECT * FROM reviews WHERE public_key = ?", (database_blob(public_key), )))
        reviews_list = []
        for review in reviews_list:
            review_dict = {
                "id": review[0],
                "public_key": str(review[1]).encode('hex'),
                "submission_id": int(review[2]),
                "submission_pk": str(review[3]).encode('hex'),
                "review": str(review[4]),
            }
            reviews_list.append(review_dict)

        return reviews_list

    def get_next_review_id(self, public_key):
        """
        Get the next review ID for a given public key.
        """
        last_id = list(self.execute("SELECT MAX(id) FROM reviews WHERE public_key = ?", (database_blob(public_key),)))[0][0]
        if not last_id:
            last_id = 0
        return last_id + 1

    def add_review(self, block):
        """
        Add a review to the database, from a given block
        """
        tx = block.transaction
        sql = "INSERT INTO reviews(id, public_key, submission_id, submission_pk, review) VALUES(?, ?, ?, ?, ?)"
        self.execute(sql, (tx['id'], database_blob(block.public_key), tx['submission_id'], database_blob(tx['submission_pk']), database_blob(tx['review'])))
        self.commit()

    def has_review(self, public_key, review_id):
        return len(list(self.execute("SELECT * FROM reviews WHERE id = ? and public_key = ?", (review_id, database_blob(public_key))))) > 0

    def get_reviews(self, submission_pk, submission_id):
        """
        Get all reviews for a specific submission.
        """
        reviews = list(self.execute("SELECT * FROM reviews WHERE submission_id = ? AND submission_pk = ?", (submission_id, database_blob(submission_pk))))
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
