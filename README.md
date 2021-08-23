# MOAR URLs - MURL

MURL takes a list of URLs and maps their domains to any indentified adtech vendors. 

To use MURL, you need a .txt file with a list of urls or domains. If you are testing multiple sites or scenarios, split each site into a separate .txt file.

A common use case for MURL is to export all urls seen in a proxy capture or a pcap file, and the map those calls to the companies that own the domains.

MURL generates a report that lists out each tested site, with each company contacted during testing for each site. Any domains that were contacted but not mapped to an owner are listed at the end of the report. 

## Usage details

After cloning the repo, create two directories in the base: <code>source</code> and <code>results</code>.

You will place all source .txt files in the <code>source</code> directory, and all reports will be stored in the <code>results</code> directory. 

You can change these locations, but be sure to adjust the corresponding values in the python script.

## Naming your .txt files

When creating the text files that store urls, your file name should contain the name of the domain you are testing. For example, if you are testing nytimes.com, your file name should be <code>nytimes_com.txt</code>. 