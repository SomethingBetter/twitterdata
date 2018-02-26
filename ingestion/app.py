import tweepy
from google.cloud import bigquery
import logging
from ruamel.yaml import YAML
import time

logging.basicConfig(level=logging.INFO)


class BigQueryWrapper(object):
    def __init__(self, credentials, project_id, dataset_id, table_id):
        self.credentials = credentials
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.init()

    def init(self):
        self.client = bigquery.Client.from_service_account_json(self.credentials)
        dataset_ref = self.client.dataset(self.dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        table_ref = dataset.table(self.table_id)

        self.table = bigquery.Table(table_ref)
        self.table = self.client.get_table(self.table)

        logging.info('Table descriptionfor {}: {}'.format(self.table.table_id,
                                                          self.table.description))

    def insert(self, row):
        errors = self.client.insert_rows(self.table, row)
        return errors


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, bigQueryWrapper):
        super(MyStreamListener, self).__init__()
        self.bigQueryWrapper = bigQueryWrapper

    def on_status(self, status):
        if status.text is not None and status.text != '':
            rows = [(
                status.id_str,
                status.text,
                str(time.mktime(status.created_at.timetuple())),
                status.user.followers_count,
                str(status.entities['hashtags']),
                status.user.location
            )]
            errors = self.bigQueryWrapper.insert(rows)
            if (len(errors) > 0):
                for e in errors:
                    logging.error('BigQuery Error: ' + str(e))

    def on_error(self, status_code):
        logging.error('error: ' + str(status_code))


def get_auth(config):
    auth = tweepy.OAuthHandler(config['consumer_key'],
                               config['consumer_secret'])
    auth.set_access_token(config['access_token_key'],
                          config['access_token_secret'])
    return auth


def get_config():
    yaml = YAML(typ='safe')
    with open('conf/local.yaml') as data:
        return yaml.load(data)


def main():
    config = get_config()
    bigQueryWrapper = BigQueryWrapper(config['keyfile_path'],
                                      config['cloud_project_id'],
                                      config['bigquery_dataset'],
                                      config['bigquery_table'])
    myStreamListener = MyStreamListener(bigQueryWrapper)
    auth = get_auth(config['twitter'])
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
    myStream.filter(track=['mexico'])


if __name__ == "__main__":
    main()
