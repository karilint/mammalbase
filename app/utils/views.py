from django.shortcuts import render

import requests
import json

def get_master_reference(ref):
	try:
		parameters = {
			"query": ref,
			"rows": 2
		}
		ref_l=ref.lower().replace(',', '').replace(':', '').replace('.', '').replace('"', '').split()
		r = requests.get("https://api.crossref.org/works", params=parameters)
		j = r.json()
		
		# 200: Everything went okay, and the result has been returned (if any).
		if r.status_code == 200:
			if 'items' in j['message']:
				items = j['message']['items']
				for item in (items):
					title = ''.join(item['title'])	#.join makes list as a string
					title_l=title.lower().replace(',', '').replace(':', '').replace('.', '').replace('"', '').split()
					#https://www.pythonpip.com/python-tutorials/how-to-find-string-in-list-python/
					matching = [s for s in title_l if any(xs in s for xs in ref_l)]
					match = len(matching)/(len(title_l)-1)*100
					print(matching)
					print(title_l)
					print(ref_l)
					print(match)
					if match >=100:
						if 'author' in item:
							authors = item['author']
							for index, author in enumerate(authors):
								if index == 0:
									if 'family' in author:
										if author['family'].lower() in ref.lower():
											citation = ''
											if 'given' in author:
												first_author = author['family']+', '+author['given']
												citation = first_author
											else:
												first_author = ''
											if 'created' in item:
												year = item['created']['date-parts'][0][0]
												citation = citation+', '+str(year)
											else:
												year = None
											citation = citation+', '+title
											if 'container-title' in item:
												container_title = ''.join(item['container-title'])
												citation = citation+', '+container_title
											else:
												container_title = ''
											if 'volume' in item:
												volume = ''.join(item['volume'])
												citation = citation+', vol. '+str(volume)
											else:
												volume = None
											if 'issue' in item:
												issue = ''.join(item['issue'])
												citation = citation+', no. '+issue
											else:
												issue = ''
											if 'page' in item:											
												page = ''.join(item['page'])
												citation = citation+', pp. '+page
											else:
												page = ''
											if 'DOI' in item:
												doi = ''.join(item['DOI'])
												citation = citation+'. doi:'+doi
											else:
												doi = ''
											if 'type' in item:
												type = ''.join(item['type'])
											else:
												item = ''
											reference = {
												"first_author": first_author,
												"title": title,
												"type": type,
												"doi": doi,
												"year": year,
												"container_title": container_title,
												"volume": volume,
												"issue": issue,
												"page": page,
												"citation": citation
											}								
											return reference
	except Exception as e:
		print(e)
