import pandas_gbq as bq
projectid = 'sandbox-161802'
data_frame = bq.read_gbq('SELECT * FROM twitterdata.example', projectid)
print data_frame
