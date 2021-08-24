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
include_params = "yes" # set as a yes/no value. Setting to "no" excludes all parameters from the report
params_separate_file = "yes" # set to "yes" to only write paramaters to a separate file. This is a sane default
include_subdomains = "yes" # set as a yes/no value. Setting to "no" excludes all subdomains from the report
generate_html = "yes"
output_md = "results/summary.md" # this directory must exist
output_html = "results/summary.html" # this directory must exist
url_source = "./source"
vendors_json = './murl_source/vendors_full.json'

# Create a whitelist of domains to omit from results
domain_whitelist_base = ['mozilla.org', 'firefox.com', 'mozilla.net', 'mozilla.com']
subdomain_whitelist_base = ['safebrowsing.googleapis.com']
domain_whitelist_bespoke = [] # add additional domains to omit from results 
domain_whitelist = domain_whitelist_base + domain_whitelist_bespoke

known_dupes_source = './murl_source/known_dupes.csv'
known_dupes_list = []

dupes = read_csv(known_dupes_source)
known_dupes_list = dupes['known_dupes'].tolist()

check_results_txt = ""

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

with open(vendors_json) as input:
	data = json.load(input)
	orgs = data['organizations']
	vendors_dataframe = pd.json_normalize(orgs)

df_vendors=vendors_dataframe.convert_dtypes()
#print(df_vendors.dtypes)

# prepare vendor list organized by associated_urls

for a, b in df_vendors.iterrows():
	for al in b['associated_urls']:
		data_purpose_list = []
		owner = b['organization_name']
		main_id = b['main_id']
		privacy_policy = b['policy_url']
		base_url = al
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
		vf_obj = pd.Series([owner, main_id, privacy_policy, base_url, data_purpose_list], index=df_vendors_flat.columns)
		df_vendors_flat = df_vendors_flat.append(vf_obj, ignore_index=True)

file_ext = "*.txt" # only get txt files - adjust as needed, set to *.* for all
count = 0

for path, subdirs, files in os.walk(url_source):
	for f in files:
		if fnmatch(f,file_ext):
			wln = f.replace(".txt","")
			wln = wln.replace("_", ".")
			if wln not in domain_whitelist:
				domain_whitelist.append(wln)
			else:
				pass
		else:
			pass

for path, subdirs, files in os.walk(url_source):
	for f in files:
		if fnmatch(f,file_ext):
			fn = os.path.join(path,f)
			count += 1
			no_match_list = []
			review_list = []
			with open(fn) as input:
				site_name = f.replace(".txt","")
				site_name = site_name.replace("_", ".")
				print(site_name)
				print("Processing " + f + "\n")
				for line in input:
					if line[0:7] == "http://":
						encrypted = "http"
						url = line.replace("http://", "")
					elif line[0:8] == "https://":
						encrypted = "https"
						url = line.replace("https://", "")
					else:
						encrypted = "WHOOOAAA"
						url = line
					ext = tldextract.extract(url)
					base_url = ext.registered_domain
					if base_url not in domain_whitelist: # add check here to make sure that the base_url is in the vendor list
						if ext.subdomain == "www" or len(ext.subdomain)< 1:
							subdomain = "None"
						else: 
							subdomain = '.'.join(ext[:3])

						if "?" in url:
							parameter = url[url.find("?")+1:].split()[0]
						else:
							parameter = "No parameters"

						df_vendor_data = df_vendors_flat[df_vendors_flat['base_url'] == base_url]
						if df_vendor_data.shape[0] > 0:
							for a, b in df_vendor_data.iterrows():
								owner = b['owner']
								match_id = b['main_id']
								privacy_policy = b['privacy_policy']
								data_purpose_list = b['data_purpose_list']
								domain_obj = pd.Series([site_name, base_url, subdomain, encrypted, parameter, match_id, url, owner, privacy_policy, data_purpose_list], index=df_domains_enchilada.columns)
								df_domains_enchilada = df_domains_enchilada.append(domain_obj, ignore_index=True)

						else: 
							owner = "unknown"
							match_id = "none"
							privacy_policy = ""
							data_purpose_list = []
							domain_obj = pd.Series([site_name, base_url, subdomain, encrypted, parameter, match_id, url, owner, privacy_policy, data_purpose_list], index=df_domains_enchilada.columns)
							df_domains_enchilada = df_domains_enchilada.append(domain_obj, ignore_index=True)

						if site_name not in site_list:
							site_list.append(site_name)
						else:
							pass

						if base_url not in domain_list:
							domain_list.append(base_url)
						else:
							pass


					else:
						pass

site_list.sort()
domain_list.sort()

#df_domains_enchilada.to_csv("domains_enchilada.csv", encoding='utf-8', index=False)

del [[df_vendors, vendors_dataframe]]
gc.collect()
df_domains_base=pd.DataFrame()
df_vendors=pd.DataFrame()
df_vendors_dataframe = pd.DataFrame()

df_match = df_domains_enchilada[df_domains_enchilada['owner'] != "unknown"]
df_no_match = df_domains_enchilada[df_domains_enchilada['owner'] == "unknown"]

df_match = df_match.sort_values(by='owner', ascending="true")
df_no_match = df_no_match.sort_values(by='base_url', ascending="true")

## Top level summary of all tests.
found_domains = df_domains_enchilada['base_url'].nunique()
matched_domains = df_match['base_url'].nunique()
matched_owners = df_match['match_id'].nunique()
top_level_txt = f"# Testing Summary\n\nIn this testing, {len(site_list)} sites were tested. During testing, {found_domains} third parties were called. {matched_domains} of these third parties are connected to {matched_owners} owners."
top_level_txt = top_level_txt + f"\nSites examined include:\n\n"
for s in site_list:
	top_level_txt = top_level_txt + f" * {s}\n"
top_level_txt = top_level_txt + "\n\n"

report = pd.Series(["all", top_level_txt, "00 summary"], index=df_report.columns)
df_report = df_report.append(report, ignore_index=True)

# For Site A, we observed B third party domains get contacted as a result of our testing.
# Site-specific summaries
for s in site_list:
	site_name = s
	site_parties_name = []
	site_parties_id = []
	unmatched_parties = []
	site_domain = []
	welcome_banner = pyfiglet.figlet_format(s)
	print(welcome_banner)
	df_domains_site = df_match[df_match['site_name'].str.contains(s)]
	df_domains_unmatched = df_no_match[df_no_match['site_name'].str.contains(s)]

	matched_domains = df_domains_site['base_url'].nunique()
	matched_owners = df_domains_site['match_id'].nunique()
	matched_owners_list = df_domains_site.match_id.unique()
	unmatched_domains = df_domains_unmatched['base_url'].nunique()
	unmatched_domains_list = df_domains_unmatched.base_url.unique()
	unmatched_domains_list.sort()
	found_domains = matched_domains + unmatched_domains
	owners_list = df_domains_site.owner.unique()
	owners_list.sort()
	domains_list = df_domains_site.base_url.unique()
	domains_list.sort()
	print(owners_list)

	site_intro_txt = f"\n# {site_name}\n\nDuring testing, {found_domains} domains were contacted. {matched_domains} domains were controlled by {matched_owners} organizations."
	site_intro_txt = site_intro_txt + "\nOrganizations contacted include:\n\n"
	owners_txt_full = ""
	owner_count = 0

	for m in matched_owners_list:
		owner_count += 1
		df_own = df_domains_site[df_domains_site['match_id'] == m]
		owner = df_own['owner'].iloc[0]
		site_intro_txt = site_intro_txt + f" * {owner}\n"
		owners_txt = f"### {owner_count}. {owner}\n\n"
		if len(df_own['privacy_policy'].iloc[0]) > 5:
			privacy_policy = df_own['privacy_policy'].iloc[0]
			owners_txt = owners_txt + f'[Privacy policy]({privacy_policy} "Privacy policy for {owner}")\n\n'
		else:
			pass
		owners_txt = owners_txt + "#### Data purpose\n\n"
		data_p = df_own['data_purpose_list'].iloc[0]
		if len(data_p) > 1:
			for dap in data_p:
				if dap != '[]' and dap != "None":
					owners_txt = owners_txt + f" * {dap}\n"
				else:
					pass
		else:
			owners_txt = owners_txt + "No info.\n"
		own_doms = df_own.base_url.unique()
		own_doms.sort()
		owners_txt = owners_txt + "\n#### Domains contacted\n\n"
		for od in own_doms:	
			own_doms_subs = []
			df_own_doms = df_own[df_own['base_url'] == od]
			own_doms_subs = df_own_doms.subdomain.unique()
			own_doms_subs.sort()
			owners_txt = owners_txt + f" * {od}\n"
			if include_subdomains == "yes":
				for ods in own_doms_subs:
					if ods != '[]' and ods != "None": 
						owners_txt = owners_txt + f"    - {ods}\n"
					else:
						pass
				owners_txt = owners_txt + "\n"
			else:
				pass

		owners_txt_full = owners_txt_full + owners_txt
	
	unmatched_domains_txt = f"\n### Unmatched domains\n\n"
	for ud in unmatched_domains_list:
		unmatched_domains_txt = unmatched_domains_txt + f" * {ud}\n"

	if include_params == "yes":
		params_txt_full = "\n#### URLs with parameters:\n\n"
		df_params = df_domains_enchilada[(df_domains_enchilada['site_name'] == s) & (df_domains_enchilada['parameter'] != "No parameters")]
		df_params = df_params.sort_values(by='base_url', ascending="true")
		params_domains = df_params.base_url.unique()
		for par in params_domains:
			params_txt = f" * *{par}*\n\n"
			df_params_filtered = df_params[df_params['base_url'] == par]
			for o, p in df_params_filtered.iterrows():
				url_par = p['url']
				params_txt = params_txt + f"<code>{url_par}</code>\n\n"
			params_txt_full = params_txt_full + params_txt
		
		if params_separate_file == "yes":
			params_txt_full = f"# {s}\n\n" + params_txt_full
			create_text("results/parameters.txt", params_txt_full)
		else:
			report = pd.Series([s, params_txt_full, "DDDUrl Parameters"], index=df_report.columns)
			df_report = df_report.append(report, ignore_index=True)
		
	else:
		pass

	site_intro_txt = site_intro_txt + "\n"
	report = pd.Series([s, site_intro_txt, "AAAGeneral Information"], index=df_report.columns)
	df_report = df_report.append(report, ignore_index=True)

	report = pd.Series([s, owners_txt_full, "BBBOrganizations Contacted"], index=df_report.columns)
	df_report = df_report.append(report, ignore_index=True)

	report = pd.Series([s, unmatched_domains_txt, "CCCUnmatched Domains"], index=df_report.columns)
	df_report = df_report.append(report, ignore_index=True)


df_intro = df_report[df_report['site_name'] == "all"].sort_values(by='section', ascending = "true")
for i, j in df_intro.iterrows():
	text_write = j['report_txt']
	create_text(output_md, text_write)

for s in site_list:	
	df_output = df_report[df_report['site_name'] == s].sort_values(by='section', ascending = "true")
	section_count = 0
	for o, p in df_output.iterrows():
		if section_count > 0:
			section = p['section'][3:]
			text_write = f"---\n\n## Section {section_count}: {section}\n\n"
			text_write = text_write + p['report_txt']
		else:
			text_write = p['report_txt']
		section_count += 1
		create_text(output_md, text_write)

if generate_html == 'yes':
	with open(output_md, 'r') as f:
		text = f.read()
		html = markdown.markdown(text)
	create_text(output_html, html)
#	with open(output_html, 'w') as g:
#		g.write(html)


	# Report:
	# tested site name - DONE - site_name
	# count of identified third party domains, with owners - DONE - matched_domains
	# count of unidentified domains - DONE - unmatched_domains
	# base_url of unidentified domains
	# Domain owner
	# data purpose
	# domain
	# subdomain
	# parameters

	# filter domains with no match - get the list of domains
	# filter by match ID
	# get owner
	# get data purpose
	# get base_url
	# for each base_url, get all subdomains
	# for subdomain, get parameters
