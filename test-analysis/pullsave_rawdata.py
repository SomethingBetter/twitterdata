'''
Created on 2018-Feb-21
This data Pulls data from Big Query and saves the dataframe 
as a pickle file. 

Note: The data pull is saved, to avoid running several times a 
query call to BigQuery, and only work on one initial dataset for
development of the analysis.
'''

import pandas_gbq as bq
import pickle
projectid = 'sandbox-161802'
data_frame = bq.read_gbq('SELECT * FROM twitterdata.example2', projectid)
print data_frame
data_frame.to_pickle('data_frame.pkl')

