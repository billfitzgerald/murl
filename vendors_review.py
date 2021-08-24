from bs4 import BeautifulSoup
from pprint import pprint
from fnmatch import fnmatch
import pandas as pd
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

# Create a whitelist of domains to omit from results
'''
no_match_list = []
review_list = []
site_list = []
domain_list = []
subdomain_list = []

df_vendors_flat = pd.DataFrame(columns=['owner', 'main_id', 'privacy_policy', 'base_url', 'data_purpose_list'])
df_domains_base = pd.DataFrame(columns=['site_name', 'base_url', 'subdomain', 'encrypted', 'parameters', 'match_id', 'url'])
df_domains_enchilada = pd.DataFrame(columns=['site_name', 'base_url', 'subdomain', 'encrypted', 'parameter', 'match_id', 'url', 'owner', 'privacy_policy', 'data_purpose_list'])											
df_report = pd.DataFrame(columns=['site_name', 'report_txt', 'section'])

def create_text(filename,text):
	with open (filename, 'a') as file:
		file.write(text)
'''

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
			review_url_list.append(al)
		with open ("urls.csv", 'a') as urls:
			al = f"{al}\n"
			urls.write(al)
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

for r in review_url_list:
	print(f"{r}: {review_url_list.count(r)}")

#print(f"This is the review list: {review_url_list}")
