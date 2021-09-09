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

# Create a whitelist of domains to omit from results
domain_whitelist_base = ['mozilla.org', 'firefox.com', 'mozilla.net', 'mozilla.com']
subdomain_whitelist_base = ['safebrowsing.googleapis.com'] # need to implement this
domain_whitelist_bespoke = [] # add additional domains to omit from results 
domain_whitelist = domain_whitelist_base + domain_whitelist_bespoke

##########################################
# Do not edit any values below this line #
##########################################

vendor_base = "./tracker-radar/entities/"
domains_base = "./tracker-radar/domains/US/"

check_results_txt = ""

no_match_list = []
review_list = []
site_list = []
domain_list = []
subdomain_list = []

df_vendors_lookup = pd.DataFrame(columns=['basefile', 'owner', 'base_url', 'lookupfile'])
df_vl = pd.DataFrame(columns=['basefile', 'owner', 'domain', 'lookupfile'])
df_domains_enchilada = pd.DataFrame(columns=['site_name', 'base_url', 'subdomain', 'encrypted', 'parameter', 'url', 'owner', 'privacy_policy'])											
df_report = pd.DataFrame(columns=['site_name', 'report_txt', 'section'])

def create_text(filename,text):
	with open (filename, 'a') as file:
		file.write(text)

## create lookup records for domains
file_ext = "*.json" 
count = 0
sum_count = 0

for path, subdirs, files in os.walk(vendor_base):
	for f in files:
		if fnmatch(f,file_ext):
			fn = os.path.join(path,f)
			with open(fn) as input:
				count += 1
				data = json.load(input)
				owner = data['name']
				basefile = f
				dom_list = data['properties']
				for d in dom_list:
					lookupfile = d + ".json"
					d_obj = pd.Series([basefile, owner, d, lookupfile], index=df_vendors_lookup.columns)
					df_vendors_lookup = df_vendors_lookup.append(d_obj, ignore_index=True)
				if count == 500:
					sum_count = sum_count + count
					count = 0
					print(f"Processed {sum_count} records.")
				else:
					pass
		else:
			pass
sum_count = sum_count + count
print(f"\nFinished processing {sum_count} records in total. Moving on to do some real work.\n")
count = 0
sum_count = 0

file_ext = "*.txt" 

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
					if base_url not in domain_whitelist:
						if ext.subdomain == "www" or len(ext.subdomain)< 1:
							subdomain = "None"
						else: 
							subdomain = '.'.join(ext[:3])

						if "?" in url:
							parameter = url[url.find("?")+1:].split()[0]
						else:
							parameter = "No parameters"

						df_vendor_data = df_vendors_lookup[df_vendors_lookup['base_url'] == base_url]
						if df_vendor_data.shape[0] > 0:
							for a, b in df_vendor_data.iterrows():
								owner = b['owner']
								vendor_info = b['lookupfile']
								vfile_path = os.path.join(domains_base,vendor_info)
								if os.path.isfile(vfile_path) == True:
									with open(vfile_path) as vd:
										vendata = json.load(vd)
										x = vendata['owner']
										pp_count = 0
										for y in x:
											if y == "privacyPolicy":
												privacy_policy = x[y]
												pp_count += 1
											else:
												pass
										if pp_count == 0:
											privacy_policy = "none listed"
										print(privacy_policy)
										for swb in subdomain_whitelist_base:
											full = tldextract.extract(swb)
											sub = full.subdomain
											base = full.registered_domain
											if sub == subdomain and base == base_url:
												pass
											else: 
												domain_obj = pd.Series([site_name, base_url, subdomain, encrypted, parameter, url, owner, privacy_policy], index=df_domains_enchilada.columns)
												df_domains_enchilada = df_domains_enchilada.append(domain_obj, ignore_index=True)
								else:
									print(f"\nNo matching file for {vfile_path}\n")
						else: 
							owner = "unknown"
							privacy_policy = ""
							# TODO iterate through the list of subdomain_whitelist_base 
							# TODO if the url is from a whitelisted subdomain, don't write the record
							domain_obj = pd.Series([site_name, base_url, subdomain, encrypted, parameter, url, owner, privacy_policy], index=df_domains_enchilada.columns)
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

print(site_list)
print(domain_list)

df_domains_enchilada.to_csv("domains_enchilada.csv", encoding='utf-8', index=False)


del [df_vendors_lookup]
gc.collect()
df_vendors_lookup=pd.DataFrame()

df_match = df_domains_enchilada[df_domains_enchilada['owner'] != "unknown"]
df_no_match = df_domains_enchilada[df_domains_enchilada['owner'] == "unknown"] 

df_match = df_match.sort_values(by='owner', ascending="true")
df_no_match = df_no_match.sort_values(by='base_url', ascending="true")

## Top level summary of all tests.
found_domains = df_domains_enchilada['base_url'].nunique()
matched_domains = df_match['base_url'].nunique()
matched_owners = df_match['owner'].nunique()
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
	matched_owners = df_domains_site['owner'].nunique()
	matched_owners_list = df_domains_site.owner.unique()
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
		df_own = df_domains_site[df_domains_site['owner'] == m]
		owner = df_own['owner'].iloc[0]
		site_intro_txt = site_intro_txt + f" * {owner}\n"
		owners_txt = f"### {owner_count}. {owner}\n\n"
		# get count of number of unique privacy policies - if greater than 1, handle them differently
		pp_unique = df_own.privacy_policy.unique()
		for ppu in pp_unique:
			df_own_pp = df_own[df_own['privacy_policy'] == ppu]
			privacy_policy = df_own['privacy_policy'].iloc[0]
			owners_txt = owners_txt + f'[Privacy policy]({privacy_policy} "Privacy policy for {owner}")\n\n'
			own_doms = df_own_pp.base_url.unique()
			own_doms.sort()
			owners_txt = owners_txt + "\n#### Domains contacted\n\n"
			for od in own_doms:	
				own_doms_subs = []
				df_own_doms = df_own_pp[df_own_pp['base_url'] == od]
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
