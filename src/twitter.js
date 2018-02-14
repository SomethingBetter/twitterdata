// Copyright 2017 Google Inc.

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This file has been modified from the original at
// https://github.com/sararob/ml-talk-demos/blob/master/natural-language/twitter.js

'use strict';

// const request = require('request');
const Twitter = require('twitter');

// Local data
const config = require('../conf/local.json')

const client = new Twitter(config.twitter);

// Set up BigQuery
// Replace this with the name of your project and the path to your keyfile
const gcloud = require('google-cloud')({
  keyFilename: config.keyfile_path,
  projectId: config.cloud_project_id
});
const bigquery = gcloud.bigquery();
const dataset = bigquery.dataset(config.bigquery_dataset);
const table = dataset.table(config.bigquery_table);

// Replace searchTerms with whatever tweets you want to stream
// Details here: https://dev.twitter.com/streaming/overview/request-parameters#track
const searchTerms = 'mexico';

client.stream('statuses/filter', {track: searchTerms, language: 'en,es'}, function(stream) {

  stream.on('data', function(event) {
	  // Exclude tweets starting with "RT"
 		if ((event.text != undefined) && (event.text.substring(0,2) != 'RT')) {
      let row = {
        id: event.id_str,
        text: event.text,
        created_at: event.timestamp_ms,
        user_followers_count: (event.user.followers_count),
        hashtags: JSON.stringify(event.entities.hashtags),
        location: JSON.stringify(event.place)
      };
      // console.log(row);
      table.insert(row, function(error, insertErr, apiResp) {
        if (error) {
          console.log('err', error);
        } else if (insertErr.length == 0) {
          console.log('success!');
        }
      });
 		}
  });

  stream.on('error', function(error) {
    throw error;
  });
});


