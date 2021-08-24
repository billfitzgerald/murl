from bs4 import BeautifulSoup
from pprint import pprint
from fnmatch import fnmatch
import pandas as pd
from pandas import read_csv
import gc
import re
import os
import sys
import datetime
import tldextract
import csv
import json
import uuid
import shutil
import pyfiglet
import markdown

# adjustable values for the doc
vendors_json = './murl_source/vendors_full.json'
known_dupes_source = './murl_source/known_dupes.csv'
known_dupes_list = []
dupes_count = 0

dupes = read_csv(known_dupes_source)
known_dupes_list = dupes['known_dupes'].tolist()

with open(vendors_json) as input:
	data = json.load(input)
	orgs = data['organizations']
	vendors_dataframe = pd.json_normalize(orgs)

df_vendors=vendors_dataframe.convert_dtypes()
#print(df_vendors.dtypes)

associated_url_list = []
review_url_list = []
data_purpose_list = []
data_purp_unique = []
org_list = []
for a, b in df_vendors.iterrows():
	for al in b['associated_urls']:
		if al not in associated_url_list:
			associated_url_list.append(al)
		else:
			dupes_count += 1
			if al not in known_dupes_list:
				review_url_list.append(al)
			else:
				pass
#		with open ("urls.csv", 'a') as urls:
#			al = f"{al}\n"
#			urls.write(al)
	for x in b['other_data_tools']:
		data_purpose_list.append(x)
	for x in b['purp_consent']:
		data_purpose_list.append(x)
	for x in b['purp_li']:
		data_purpose_list.append(x)
	for x in b['purp_spec_purp']:
		data_purpose_list.append(x)
	for x in b['purp_feat']:
		data_purpose_list.append(x)
	for x in b['purp_spec_feat']:
		data_purpose_list.append(x)
for dpl in data_purpose_list:
	if dpl not in data_purp_unique:
		data_purp_unique.append(dpl)
	else:
		pass
data_purp_unique.sort()
#for d in data_purp_unique:
#	print(f"{d}: {data_purpose_list.count(d)}")

if len(review_url_list) > 0:
	for r in review_url_list:
		print(f"{r}: {review_url_list.count(r)}")
else:
	print(f"There were {dupes_count} domains that appeared 2 or more times, and {len(known_dupes_list)} domains in the list of verified duplicate domains.")
