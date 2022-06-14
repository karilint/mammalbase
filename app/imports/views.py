from json import load
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from mb.forms import SourceAttributeForm
from mb.models import (ChoiceValue,DietSet, DietSetItem, EntityClass, EntityRelation, FoodItem, MasterReference
	, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod)
from utils.views import *	# MB Utils
from .tools import *

import logging
import numpy as np
import pandas as pd
import re

@login_required
def import_test(request):
	if "GET" == request.method:
		#cit = 'Johnson, C. N. (1994) Nutritional ecology of a mycophagous marsupial in relation to production of hypogeous fungi. Ecology 75, 2015–2021.'
		#d = get_referencedata_from_crossref(cit)
		#d = {'status': 'ok', 'message-type': 'work-list', 'message-version': '1.0.0', 'message': {'facets': {}, 'total-results': 759227, 'items': [{'indexed': {'date-parts': [[2022, 3, 31]], 'date-time': '2022-03-31T23:41:59Z', 'timestamp': 1648770119649}, 'reference-count': 0, 'publisher': 'Wiley', 'issue': '7', 'license': [{'start': {'date-parts': [[2015, 9, 1]], 'date-time': '2015-09-01T00:00:00Z', 'timestamp': 1441065600000}, 'content-version': 'tdm', 'delay-in-days': 7640, 'URL': 'http://doi.wiley.com/10.1002/tdm_license_1.1'}], 'content-domain': {'domain': [], 'crossmark-restriction': False}, 'published-print': {'date-parts': [[1994, 10]]}, 'DOI': '10.2307/1941606', 'type': 'journal-article', 'created': {'date-parts': [[2006, 5, 9]], 'date-time': '2006-05-09T15:33:30Z', 'timestamp': 1147188810000}, 'page': '2015-2021', 'source': 'Crossref', 'is-referenced-by-count': 42, 'title': ['Nutritional Ecology of a Mycophagous Marsupial in Relation to Production of Hypogeous Fungi'], 'prefix': '10.1002', 'volume': '75', 'author': [{'given': 'C. N.', 'family': 'Johnson', 'sequence': 'first', 'affiliation': []}], 'member': '311', 'published-online': {'date-parts': [[1994, 10, 1]]}, 'container-title': ['Ecology'], 'language': 'en', 'link': [{'URL': 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.2307%2F1941606', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'text-mining'}, {'URL': 'https://onlinelibrary.wiley.com/doi/full/10.2307/1941606', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'similarity-checking'}], 'deposited': {'date-parts': [[2018, 8, 1]], 'date-time': '2018-08-01T04:20:42Z', 'timestamp': 1533097242000}, 'score': 111.94692, 'resource': {'primary': {'URL': 'http://doi.wiley.com/10.2307/1941606'}}, 'issued': {'date-parts': [[1994, 10]]}, 'references-count': 0, 'journal-issue': {'issue': '7', 'published-print': {'date-parts': [[1994, 10]]}}, 'URL': 'http://dx.doi.org/10.2307/1941606', 'archive': ['Portico'], 'ISSN': ['0012-9658'], 'issn-type': [{'value': '0012-9658', 'type': 'print'}], 'subject': ['Ecology, Evolution, Behavior and Systematics'], 'published': {'date-parts': [[1994, 10]]}}, {'indexed': {'date-parts': [[2022, 5, 27]], 'date-time': '2022-05-27T10:49:58Z', 'timestamp': 1653648598802}, 'reference-count': 47, 'publisher': 'Wiley', 'issue': '6', 'license': [{'start': {'date-parts': [[2001, 11, 1]], 'date-time': '2001-11-01T00:00:00Z', 'timestamp': 1004572800000}, 'content-version': 'tdm', 'delay-in-days': 0, 'URL': 'http://doi.wiley.com/10.1002/tdm_license_1.1'}, {'start': {'date-parts': [[2002, 3, 26]], 'date-time': '2002-03-26T00:00:00Z', 'timestamp': 1017100800000}, 'content-version': 'vor', 'delay-in-days': 145, 'URL': 'http://onlinelibrary.wiley.com/termsAndConditions#vor'}], 'content-domain': {'domain': [], 'crossmark-restriction': False}, 'published-print': {'date-parts': [[2001, 11]]}, 'DOI': '10.1046/j.0021-8790.2001.00564.x', 'type': 'journal-article', 'created': {'date-parts': [[2003, 3, 12]], 'date-time': '2003-03-12T03:05:54Z', 'timestamp': 1047438354000}, 'page': '945-954', 'source': 'Crossref', 'is-referenced-by-count': 40, 'title': ['Effects of season and fire on the diversity of hypogeous fungi consumed by a tropical mycophagous marsupial'], 'prefix': '10.1111', 'volume': '70', 'author': [{'given': 'Karl', 'family': 'Vernes', 'sequence': 'first', 'affiliation': []}, {'given': 'Michael', 'family': 'Castellano', 'sequence': 'additional', 'affiliation': []}, {'given': 'Christopher N.', 'family': 'Johnson', 'sequence': 'additional', 'affiliation': []}], 'member': '311', 'published-online': {'date-parts': [[2002, 3, 26]]}, 'reference': [{'key': '10.1046/j.0021-8790.2001.00564.x-BIB8|cit2', 'doi-asserted-by': 'crossref', 'first-page': '575', 'DOI': '10.2307/2388395', 'article-title': 'Responses of ground-foraging ant communities to three experimental fire regimes in a savanna forest of tropical Australia', 'volume': '23', 'author': 'Andersen', 'year': '1991', 'journal-title': 'Biotropica'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB4|cit3', 'doi-asserted-by': 'crossref', 'first-page': '767', 'DOI': '10.1038/29507', 'article-title': 'A million-year record of fire in sub-Saharan Africa', 'volume': '394', 'author': 'Bird', 'year': '1998', 'journal-title': 'Nature'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB15|cit4', 'doi-asserted-by': 'crossref', 'first-page': '237', 'DOI': '10.1016/0378-1127(89)90084-4', 'article-title': 'Mycophagy and spore dispersal by small mammals in Bavarian forests', 'volume': '26', 'author': 'Blaschke', 'year': '1989', 'journal-title': 'Forest Ecology and Management'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB2|cit5', 'first-page': '64', 'article-title': 'Long-term fire incidence in coastal forests of British Columbia', 'volume': '72', 'author': 'Brown', 'year': '1998', 'journal-title': 'Northwest Science'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB29|cit6', 'doi-asserted-by': 'crossref', 'first-page': '667', 'DOI': '10.1007/BF00051966', 'article-title': 'domain: a flexible modelling procedure for mapping potential distributions of plants and animals', 'volume': '2', 'author': 'Carpenter', 'year': '1993', 'journal-title': 'Biodiversity and Conservation'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB18|cit7', 'first-page': '273', 'volume-title': 'Fire and the Australian Biota', 'author': 'Catling', 'year': '1981'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB23|cit8', 'unstructured': 'Christensen , P.E.S. 1980 The biology of Bettongia penicillata Gray, 1837, and Macropus eugenii (Desmarest, 1817) in relation to fire. Department of Western Australia'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB33|cit9', 'doi-asserted-by': 'crossref', 'first-page': '195', 'DOI': '10.1080/00049158.1998.10674740', 'article-title': 'The Precautionary Principle and grazing, burning and medium sized mammals in northern New South Wales', 'volume': '61', 'author': 'Christensen', 'year': '1998', 'journal-title': 'Australian Forestry'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB38|cit10', 'doi-asserted-by': 'crossref', 'first-page': '223', 'DOI': '10.1111/j.1442-9993.1992.tb00801.x', 'article-title': 'Is the relationship among mycophagous marsupials, mycorrhizal fungi and plants dependent on fire?', 'volume': '17', 'author': 'Claridge', 'year': '1992', 'journal-title': 'Australian Journal of Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB36|cit11', 'doi-asserted-by': 'crossref', 'first-page': '175', 'DOI': '10.1023/A:1008962711138', 'article-title': 'Diversity and habitat relationships of hypogeous fungi. II. Factors influencing the occurrence and number of taxa', 'volume': '9', 'author': 'Claridge', 'year': '2000', 'journal-title': 'Biodiversity and Conservation'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB13|cit12', 'doi-asserted-by': 'crossref', 'first-page': '251', 'DOI': '10.1111/j.1442-9993.1994.tb00489.x', 'article-title': 'Mycophagy among Australian mammals', 'volume': '19', 'author': 'Claridge', 'year': '1994', 'journal-title': 'Australian Journal of Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB22|cit13', 'doi-asserted-by': 'crossref', 'first-page': '207', 'DOI': '10.1111/j.1442-9993.1992.tb00799.x', 'article-title': 'Establishment of ectomycorrhizae on the roots of two species of Eucalyptus from fungal spores contained in the faeces of the long-nosed potoroo (Potorous tridactylus)', 'volume': '17', 'author': 'Claridge', 'year': '1992', 'journal-title': 'Australian Journal of Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB26|cit14', 'unstructured': 'Davidson , C. 1991 Recovery plan for the northern bettong (Bettongia tropica)'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB37|cit15', 'doi-asserted-by': 'crossref', 'first-page': '449', 'DOI': '10.1111/j.1469-8137.1990.tb00413.x', 'article-title': 'Ectomycorrhiza formation in Eucalyptus. IV. Ectomycorrhizas in the sporocarps of the hypogeous fungi Mesophellia and Castorium in Eucalypt forests of Western Australia', 'volume': '114', 'author': 'Dell', 'year': '1990', 'journal-title': 'New Phytologist'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB1|cit16', 'doi-asserted-by': 'crossref', 'first-page': '749', 'DOI': '10.1007/BF00329051', 'article-title': 'Changes of the forest-savanna boundary in Brazilian Amazonia during the Holocene revealed by stable isotope ratios of soil organic carbon', 'volume': '108', 'author': 'Desjardins', 'year': '1996', 'journal-title': 'Oecologia'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB39|cit17', 'doi-asserted-by': 'crossref', 'first-page': '1201', 'DOI': '10.1007/BF02059754', 'article-title': 'Detection of hypogeous fungi by the Tasmanian bettong (Bettongia gaimardi: Marsupialia; Macropodoidea)', 'volume': '20', 'author': 'Donaldson', 'year': '1994', 'journal-title': 'Journal of Chemical Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB14|cit18', 'first-page': '1', 'article-title': 'Fungus consumption (mycophagy) by small animals', 'volume': '52', 'author': 'Fogel', 'year': '1978', 'journal-title': 'Northwest Science'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB11|cit19', 'doi-asserted-by': 'crossref', 'first-page': '1332', 'DOI': '10.2307/1938861', 'article-title': 'Fire and mammalian secondary succession in an Australian coastal heath', 'volume': '63', 'author': 'Fox', 'year': '1982', 'journal-title': 'Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB12|cit20', 'doi-asserted-by': 'crossref', 'first-page': '321', 'DOI': '10.2307/3545142', 'article-title': 'Changes in the structure of mammal communities over successional time scales', 'volume': '59', 'author': 'Fox', 'year': '1990', 'journal-title': 'Oikos'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB19|cit21', 'first-page': '74', 'article-title': 'Priorities for fire research in Australia', 'volume': '19', 'author': 'Gill', 'year': '1989', 'journal-title': 'Bulletin of the Ecological Society of Australia'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB47|cit22', 'unstructured': 'Grant , J.D. Naylor , L.M. 1993 Surveys for the northern brush-tailed bettong Bettongia tropica on the Mount Carbine Tableland and Mount Lewis, north-east Queensland.'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB34|cit23', 'doi-asserted-by': 'crossref', 'first-page': '319', 'DOI': '10.1071/PC940319', 'article-title': 'Recent contraction of wet sclerophyll forest in the wet tropics of Queensland due to invasion by rainforest', 'volume': '1', 'author': 'Harrington', 'year': '1994', 'journal-title': 'Pacific Conservation Biology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB6|cit24', 'doi-asserted-by': 'crossref', 'first-page': '97', 'DOI': '10.1071/BT9900097', 'article-title': 'Fire-related dynamics of a Banksia woodland in southwestern Western Australia', 'volume': '38', 'author': 'Hobbs', 'year': '1990', 'journal-title': 'Australian Journal of Botany'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB44|cit25', 'doi-asserted-by': 'crossref', 'first-page': '464', 'DOI': '10.2307/2390070', 'article-title': 'Mycophagy and spore dispersal by a rat-kangaroo: consumption of ectomycorrhizal taxa in relation to their abundance', 'volume': '8', 'author': 'Johnson', 'year': '1994', 'journal-title': 'Functional Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB25|cit26', 'doi-asserted-by': 'crossref', 'first-page': '467', 'DOI': '10.1007/BF00341344', 'article-title': 'Interactions between fire, mycophagous mammals, and dispersal of ectomycorrhizal fungi in Eucalyptus forest', 'volume': '104', 'author': 'Johnson', 'year': '1995', 'journal-title': 'Oecologia'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB21|cit27', 'doi-asserted-by': 'crossref', 'first-page': '503', 'DOI': '10.1016/S0169-5347(96)10053-7', 'article-title': 'Interactions between mammals and ectomycorrhizal fungi', 'volume': '11', 'author': 'Johnson', 'year': '1996', 'journal-title': 'Trends in Ecology and Evolution'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB28|cit28', 'doi-asserted-by': 'crossref', 'first-page': '549', 'DOI': '10.1071/WR96034', 'article-title': 'Ecology of the northern bettong, Bettongia tropica, a tropical mycophagist', 'volume': '24', 'author': 'Johnson', 'year': '1997', 'journal-title': 'Wildlife Research'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB17|cit29', 'first-page': '3', 'volume-title': 'Fire and the Australian Biota', 'author': 'Kemp', 'year': '1981'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB42|cit30', 'doi-asserted-by': 'crossref', 'first-page': '47', 'DOI': '10.1038/322047a0', 'article-title': 'Climatic change and Aboriginal burning in north-east Australia during the last two glacial/interglacial cycles', 'volume': '322', 'author': 'Kershaw', 'year': '1986', 'journal-title': 'Nature'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB35|cit31', 'volume-title': 'Ecological Methodology', 'author': 'Krebs', 'year': '1999'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB45|cit32', 'doi-asserted-by': 'crossref', 'first-page': '47', 'DOI': '10.1016/S0006-3207(96)00164-4', 'article-title': 'A distributional survey and habitat model for the endangered northern bettong (Bettongia tropica) in tropical Queensland', 'volume': '82', 'author': 'Laurance', 'year': '1997', 'journal-title': 'Biological Conservation'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB40|cit33', 'doi-asserted-by': 'crossref', 'first-page': '53', 'DOI': '10.1111/j.1442-9993.1987.tb00927.x', 'article-title': 'Interrelationships among some ectomycorrhizal trees, hypogeous fungi and small mammals: Western Australian and northwestern American parallels', 'volume': '12', 'author': 'Malajczuk', 'year': '1987', 'journal-title': 'Australian Journal of Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB10|cit34', 'doi-asserted-by': 'crossref', 'first-page': '803', 'DOI': '10.1071/WR9930803', 'article-title': 'The effects of fire-driven succession and rainfall on small mammals in spinifex grassland at Uluru National Park, Northern Territory', 'volume': '20', 'author': 'Masters', 'year': '1993', 'journal-title': 'Wildlife Research'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB7|cit35', 'doi-asserted-by': 'crossref', 'first-page': '239', 'DOI': '10.1111/j.1442-9993.1995.tb00535.x', 'article-title': 'Effects of fire frequency on the plant species composition of sandstone communities in the Sydney region: inter-fire interval and time-since-fire', 'volume': '20', 'author': 'Morrison', 'year': '1995', 'journal-title': 'Australian Journal of Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB16|cit36', 'doi-asserted-by': 'crossref', 'first-page': '1543', 'DOI': '10.1890/0012-9658(1997)078[1543:SCAACO]2.0.CO;2', 'article-title': 'Standing crop and animal consumption of fungal sporocarps in Pacific Northwest forests', 'volume': '78', 'author': 'North', 'year': '1997', 'journal-title': 'Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB9|cit37', 'first-page': '352', 'article-title': 'Disturbance, spatial heterogeneity and biotic diversity fire succession in arid Australia', 'volume': '8', 'author': 'Pianka', 'year': '1992', 'journal-title': 'Research and Exploration'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB5|cit38', 'first-page': '23', 'volume-title': 'Fire and the Australian Biota', 'author': 'Singh', 'year': '1981'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB41|cit39', 'first-page': '425', 'volume-title': 'Fire and the Australian Biota', 'author': 'Stocker', 'year': '1981'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB24|cit40', 'doi-asserted-by': 'crossref', 'first-page': '409', 'DOI': '10.1111/j.1442-9993.1991.tb01068.x', 'article-title': 'Plants, fungi and bettongs: a fire-dependent co-evolutionary relationship', 'volume': '6', 'author': 'Taylor', 'year': '1991', 'journal-title': 'Australian Journal of Ecology'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB3|cit41', 'doi-asserted-by': 'crossref', 'first-page': '1159', 'DOI': '10.1023/A:1008952428475', 'article-title': 'Environmental change and rain forests on the Sunda shelf of southeast Asia: drought, fire and the biological cooling of biodiversity hotspots', 'volume': '8', 'author': 'Taylor', 'year': '1999', 'journal-title': 'Biodiversity and Conservation'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB43|cit42', 'unstructured': 'Vernes , K.A. 1999 Fire, fungi and a tropical mycophagist: ecology of the northern bettong (Bettongia tropica) in fire-prone sclerophyll forest PhD Thesis'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB30|cit43', 'doi-asserted-by': 'crossref', 'first-page': '305', 'DOI': '10.1016/S0006-3207(00)00086-0', 'article-title': 'Immediate effects of fire on survivorship of the northern bettong (Bettongia tropica): an endangered Australian marsupial', 'volume': '96', 'author': 'Vernes', 'year': '2000', 'journal-title': 'Biological Conservation'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB32|cit44', 'doi-asserted-by': 'crossref', 'unstructured': 'Vernes , K. Haydon , D.T. 2001 Effect of fire on northern bettong ( Bettongia tropica ) foraging behaviour Austral Ecology', 'DOI': '10.1046/j.1442-9993.2001.01141.x'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB31|cit45', 'doi-asserted-by': 'crossref', 'first-page': '141', 'DOI': '10.1071/WR00054', 'article-title': 'Stability of nest range, home range and movement of the northern bettong (Bettongia tropica) following moderate-intensity fire in a tropical woodland, north-eastern Queensland', 'volume': '28', 'author': 'Vernes', 'year': '2001', 'journal-title': 'Wildlife Research'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB20|cit46', 'doi-asserted-by': 'crossref', 'first-page': '125', 'DOI': '10.1071/BT9940125', 'article-title': 'Fire and environmental heterogeneity in southern temperate forest ecosystems: implications for management', 'volume': '42', 'author': 'Williams', 'year': '1994', 'journal-title': 'Australian Journal of Botany'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB46|cit47', 'unstructured': 'Winter , J.W. 1992 Population assessment of the northern brushtail bettong on the Mt Windsor Tableland, north-eastern Queensland'}, {'key': '10.1046/j.0021-8790.2001.00564.x-BIB27|cit48', 'first-page': '294', 'volume-title': 'Mammals of Australia', 'author': 'Winter', 'year': '1995'}], 'container-title': ['Journal of Animal Ecology'], 'language': 'en', 'link': [{'URL': 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1046%2Fj.0021-8790.2001.00564.x', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'text-mining'}, {'URL': 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1046%2Fj.0021-8790.2001.00564.x', 'content-type': 'application/pdf', 'content-version': 'vor', 'intended-application': 'text-mining'}, {'URL': 'http://onlinelibrary.wiley.com/wol1/doi/10.1046/j.0021-8790.2001.00564.x/fullpdf', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'similarity-checking'}], 'deposited': {'date-parts': [[2020, 9, 23]], 'date-time': '2020-09-23T00:31:16Z', 'timestamp': 1600821076000}, 'score': 58.617214, 'resource': {'primary': {'URL': 'http://doi.wiley.com/10.1046/j.0021-8790.2001.00564.x'}}, 'subtitle': ['<i>Effects of fire on marsupial mycophagy</i>'], 'issued': {'date-parts': [[2001, 11]]}, 'references-count': 47, 'journal-issue': {'issue': '6', 'published-print': {'date-parts': [[2001, 11]]}}, 'URL': 'http://dx.doi.org/10.1046/j.0021-8790.2001.00564.x', 'archive': ['Portico'], 'ISSN': ['0021-8790'], 'issn-type': [{'value': '0021-8790', 'type': 'print'}], 'subject': ['Animal Science and Zoology', 'Ecology, Evolution, Behavior and Systematics'], 'published': {'date-parts': [[2001, 11]]}}], 'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}}
		#create_mr(cit, d)
		return render(request, "import/import_test.html")
	try:
		csv_file = request.FILES["csv_file"]
		df = pd.read_csv(csv_file)
		trim_df(df)
		check = Check(request)

		if check.check_all(df) != True:
			return HttpResponseRedirect(reverse("import_test"))
		else:
			for row in df.itertuples():
				create_dietset(row)
			success_message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
			messages.add_message(request, 50 ,success_message, extra_tags="import-message")
			messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
			return HttpResponseRedirect(reverse("import_test"))

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_test"))



@login_required
def import_diet_set(request): # pragma: no cover
	data = {}
	if "GET" == request.method:
		return render(request, "import/import_diet_set.html", data)
    # if not GET, then proceed
	try:
		csv_file = request.FILES["csv_file"]
		df = pd.read_csv(csv_file, sep='|', decimal=".")
		df['percentage'] = df['percentage'].str.replace(',','.')

		import_headers = list(df.columns.values)
		accepted_headers = ['verbatimScientificName', 'taxonRank', 'verbatimLocality', 'time_period', 'cited_reference', 'sex', 'individualCount', 'study_time', 'measurementMethod', 'food_item', 'percentage', 'references']
		print_headers = ', '.join(accepted_headers)
		if not import_headers == accepted_headers:
			messages.error(request,'The import file contains wrong headers. The required headers are: %s' % (print_headers))
			return HttpResponseRedirect(reverse("diet_set-import"))

		df['sort_order'] = range(1, 1+len(df))

		# All References
#		r_df = df.loc[df['references'] >= '', ['references']]
		r_df = df.loc[df['references'].notnull(), ['references']]

		r_df.drop_duplicates(inplace = True)
		r_df['source_reference_id'] = 0

#		t_df = df.loc[df['verbatimScientificName'] > '', ['verbatimScientificName', 'taxonRank', 'references']]
		t_df = df.loc[df['verbatimScientificName'].notnull(), ['verbatimScientificName', 'taxonRank', 'references']]
		t_df.drop_duplicates(inplace = True)
		t_df['taxon_id'] = 0
		t_df['taxon_id'] = t_df['taxon_id'].astype('Int64')
		t_df['source_entity'] = 0
		t_df['master_entity'] = 0

		l_df = df.loc[df['verbatimLocality'].notnull(), ['verbatimLocality', 'references']]
		l_df.drop_duplicates(inplace = True)
		l_df['location_id'] = 0
		l_df['location_id'] = l_df['location_id'].astype('Int64')

#		tp_df = df.loc[df['time_period'] > '', ['time_period', 'references']]
		tp_df = df.loc[df['time_period'].notnull(), ['time_period', 'references']]
		tp_df.drop_duplicates(inplace = True)
		tp_df['time_period_id'] = 0
		tp_df['time_period_id'] = tp_df['time_period_id'].astype('Int64')

#		g_df = df.loc[df['sex'] > '', ['sex']]
		g_df = df.loc[df['sex'].notnull(), ['sex']]
		g_df.drop_duplicates(inplace = True)

#		tr_df = df.loc[df['taxonRank'] >= '', ['taxonRank']]
		tr_df = df.loc[df['taxonRank'].notnull(), ['taxonRank']]
		tr_df.drop_duplicates(inplace = True)

		ss_df = df.loc[df['individualCount'] > 0, ['individualCount']]
#		ss_df = df[['individualCount']].dropna()
		ss_df.drop_duplicates(inplace = True)

#		m_df = df.loc[df['measurementMethod'] > '', ['measurementMethod', 'references']]
		m_df = df.loc[df['measurementMethod'].notnull(), ['measurementMethod', 'references']]
#		m_df = df[['measurementMethod']].dropna()
		m_df.drop_duplicates(inplace = True)
		m_df['method_id'] = 0
		m_df['method_id'] = m_df['method_id'].astype('Int64')

#		fi_df = df.loc[df['food_item'] >= '', ['food_item', 'references']]
		fi_df = df.loc[df['food_item'].notnull(), ['food_item', 'references']]
		fi_df.drop_duplicates(inplace = True)
		fi_df['fi_id'] = 0
		fi_df['fi_id'] = fi_df['fi_id'].astype('Int64')

#		p_df = df.loc[df['percentage'] > '', ['percentage']]
		p_df = df.loc[df['percentage'].notnull(), ['percentage']]
		p_df['percentage'] = p_df['percentage'].astype('float64')

#		p_df = df[['percentage']].dropna()
		p_df.drop_duplicates(inplace = True)

		ds_df = df.loc[df['references'] >= '', ['verbatimScientificName', 'taxonRank', 'verbatimLocality', 'time_period', 'cited_reference', 'sex', 'individualCount', 'study_time', 'measurementMethod', 'references']]
		ds_df.drop_duplicates(inplace = True)

		if not csv_file.name.endswith('.csv'):
			messages.error(request,'File is not CSV type. Please choose another file!')
			return HttpResponseRedirect(reverse("diet_set-import"))
        #if file is too large, return
		if csv_file.multiple_chunks():
			messages.error(request,"Uploaded file is too big (%.2f MB). Please make the file smaller." % (csv_file.size/(1000*1000),))
			return HttpResponseRedirect(reverse("diet_set-import"))
		#if Taxon is missing
		if df['verbatimScientificName'].isnull().values.any() == True:
			messages.error(request,"%.0f data row(s) are missing verbatimScientificName. Please fix the data content and try again." % (df['verbatimScientificName'].isnull().sum()))
			return HttpResponseRedirect(reverse("diet_set-import"))
		#if Food Item is missing
		if df['food_item'].isnull().values.any() == True:
			messages.error(request,"%.0f data row(s) are missing Food Items. Please fix the data content and try again." % (df['food_item'].isnull().sum()))
			return HttpResponseRedirect(reverse("diet_set-import"))
		#if Reference is missing
		if df['references'].isnull().values.any() == True:
			messages.error(request,"%.0f data row(s) are missing References. Please fix the data content and try again." % (df['references'].isnull().sum()))
			return HttpResponseRedirect(reverse("diet_set-import"))
		#if sex variable is not found
		sex_all = ChoiceValue.objects.is_active().filter(choice_set__iexact='Gender')
		for index, row in g_df.iterrows():
#			print ("Index: {}".format(index))
			sex = sex_all.filter(caption__iexact=row['sex'])
			if len(sex)>0:
				g_df.at[index,'sex_id']=sex[0].id
#				print ("Found Id {}: {}".format(g_df.at[index,'sex_id'],row.sex))
			else:
#				print ("NOT Found: {}".format(row.sex))
				messages.error(request,"%s is not a valid Sex variable. Please fix the data content and try again." % (row.sex))
				return HttpResponseRedirect(reverse("diet_set-import"))
		#if taxonRank variable is not found
		tr_all = EntityClass.objects.all()
		for index, row in tr_df.iterrows():
#			print ("Index: {}".format(index))
			tr = tr_all.filter(name__iexact=row['taxonRank'])
			if len(tr)>0:
				tr_df.at[index,'taxonRank_id']=tr[0].id
#				print ("Found Id {}: {}".format(tr_df.at[index,'taxonRank_id'],row.taxonRank))
			else:
#				print ("NOT Found: {}".format(row.taxonRank))
				messages.error(request,"%s is not a valid taxonRank variable. Please fix the data content and try again." % (row.taxonRank))
				return HttpResponseRedirect(reverse("diet_set-import"))

# Main checks done, next insert new data
		# SourceReference
		sr_all = SourceReference.objects.all()
#		The fastest way to loop: https://www.dataindependent.com/pandas/pandas-iterate-over-rows/
		for index, reference in r_df.iterrows():
#			print ("Index: {}".format(index))
			sr = sr_all.filter(citation__iexact=reference['references'])
			if len(sr)>0:
				r_df.at[index,'source_reference_id']=sr[0].id
				source_reference=sr[0]
				print ("Found Id {}: {}".format(r_df.at[index,'source_reference_id'],reference['references']))
			else:
				source_reference = SourceReference(citation=reference['references'], status=1)
				source_reference.save()
				r_df.at[index,'source_reference_id']=source_reference.id

			# Check for the MasterReference
			r = get_master_reference(source_reference.citation)
			print(r)
			if r:
				mr = MasterReference.objects.is_active().filter(title__iexact=r['title']).filter(first_author__iexact=r['first_author'])
				if len(mr)>0:
					mr_new = mr[0]
					print(mr_new.id)
				else:
					mr_new = MasterReference(first_author=r['first_author'],
						title=r['title'],
						type=r['type'],
						doi=r['doi'],
						year=r['year'],
						container_title=r['container_title'],
						volume=r['volume'],
						issue=r['issue'],
						page=r['page'],
						citation=r['citation'])
					print(mr_new)
					mr_new.save()

				# Check MasterReference for the SourceReference. If not, add it
				print(source_reference.master_reference)
				if source_reference.master_reference == None:
					source_reference.master_reference = mr_new
					source_reference.save()

#				print ("New Id {}: {}".format(r_df.at[index,'source_reference_id'],reference['references']))

		# Update the Reference, Sex and taxonRank id's
		l_df = pd.merge(l_df, r_df, on = 'references', how = "inner")
		tp_df = pd.merge(tp_df, r_df, on = 'references', how = "inner")
		m_df = pd.merge(m_df, r_df, on = 'references', how = "inner")
		fi_df = pd.merge(fi_df, r_df, on = 'references', how = "inner")
		t_df = pd.merge(t_df, r_df, on = 'references', how = "inner")
		t_df = pd.merge(t_df, tr_df, on = 'taxonRank', how = "inner")

		# SourceLocation
		sl_all = SourceLocation.objects.all()
		for index, row in l_df.iterrows():
#			print ("Index: {}".format(index))
			r = SourceReference.objects.get(pk=row.source_reference_id)
			sl = sl_all.filter(name__iexact=row['verbatimLocality']).filter(reference_id=row['source_reference_id'])
			if len(sl)>0:
				l_df.at[index,'location_id']=sl[0].id
#				print ("Found Id {}: {}".format(l_df.at[index,'source_reference_id'],row['verbatimLocality']))
			else:
				l = SourceLocation(name=row['verbatimLocality'], reference=r)
				l.save()
				l_df.at[index,'location_id']=l.id
#				print ("New Id {}: {}".format(l_df.at[index,'source_reference_id'],row['verbatimLocality']))

		# TimePeriod
		tp_all = TimePeriod.objects.all()
		for index, row in tp_df.iterrows():
#			print ("Index: {}".format(index))
			r = SourceReference.objects.get(pk=row.source_reference_id)
			tp = tp_all.filter(name__iexact=row['time_period']).filter(reference_id=row['source_reference_id'])
			if len(tp)>0:
				tp_df.at[index,'time_period_id']=tp[0].id
#				print ("Found Id {}: {}".format(tp_df.at[index,'source_reference_id'],row['time_period']))
			else:
				tp = TimePeriod(name=row['time_period'], reference=r)
				tp.save()
				tp_df.at[index,'time_period_id']=tp.id
#				print ("New Id {}: {}".format(tp_df.at[index,'source_reference_id'],row['time_period']))

		# SourceMethod
		sm_all = SourceMethod.objects.all()
		for index, row in m_df.iterrows():
#			print ("Index: {}".format(index))
			r = SourceReference.objects.get(pk=row.source_reference_id)
			sm = sm_all.filter(name__iexact=row['measurementMethod']).filter(reference_id=row['source_reference_id'])
			if len(sm)>0:
				m_df.at[index,'method_id']=sm[0].id
				print ("Found Method Id {}: Reference {} Method {}".format(m_df.at[index,'method_id'], m_df.at[index,'source_reference_id'],row['measurementMethod']))
			else:
				sm = SourceMethod(name=row['measurementMethod'], reference=r)
				sm.save()
				m_df.at[index,'method_id']=sm.id
				print ("New Method Id {}: Reference {} Method {}".format(m_df.at[index,'method_id'], m_df.at[index,'source_reference_id'],row['measurementMethod']))

		# FoodItem
		fi_all = FoodItem.objects.all()
		for index, row in fi_df.iterrows():
			r = SourceReference.objects.get(pk=row.source_reference_id)
			fi = fi_all.filter(name__iexact=row['food_item'])
			if len(fi)>0:
				fi_df.at[index,'fi_id']=fi[0].id
#				print ("Found Id {}: {}".format(fi_df.at[index,'fi_id'],row['food_item']))
			else:
				fi = FoodItem(name=row['food_item'], tsn=None )
				fi.save()
				fi_df.at[index,'fi_id']=fi.id
#				print ("New Id {}: {}".format(fi_df.at[index,'fi_id'],row['food_item']))

		# SourceEntity (verbatimScientificName)
		se_all = SourceEntity.objects.all()
		for index, row in t_df.iterrows():
			r = SourceReference.objects.get(pk=row.source_reference_id)
			e = EntityClass.objects.get(pk=row.taxonRank_id)
			se = se_all.filter(name__iexact=row['verbatimScientificName']).filter(entity_id=row['taxonRank_id']).filter(reference_id=row['source_reference_id'])
			if len(se)>0:
				t_df.at[index,'taxon_id']=se[0].id
				source_entity=se[0]
				print ("Found Id {}: {} is a {}".format(t_df.at[index,'source_reference_id'],row['verbatimScientificName'],row['taxonRank']))
			else:
				# Add new SourceEntity
				source_entity = SourceEntity(name=row['verbatimScientificName'],entity=e,reference=r)
				source_entity.save()
				t_df.at[index,'taxon_id']=source_entity.id
				print ("New Id {}: {} is a {}".format(t_df.at[index,'source_reference_id'],row['verbatimScientificName'],row['taxonRank_id']))

			# Search for EntityRelations having the same verbatimScientificName and EntityClass
			print(source_entity.name)
			try: 
				er = EntityRelation.objects.is_active().filter(source_entity__name__iexact=source_entity.name).filter(data_status_id=5).filter(master_entity__reference_id=4).filter(relation__name__iexact='Taxon Match')[0]
				print(er.id)
				print(er.source_entity.reference.id)
				print(er.master_entity)
				entity_relation = EntityRelation(master_entity=er.master_entity
					,source_entity=source_entity
					,relation=er.relation
					,data_status=er.data_status
					,relation_status=er.relation_status
					,remarks=er.remarks)
				try:
					entity_relation.save()
					print ("New Entity Relation Id {}".format(entity_relation.id))
				except:
					print('Pass')
					pass
			except IndexError: 
				print("An IndexError occurred: No relations found") 

				# Check MasterReference for the SourceReference. If not, add it
			"""
			if source_reference.master_reference == None:
				source_reference.master_reference = mr_new
				source_reference.save()

			"""
		# Update DietSet with Id's
		ds_df = pd.merge(ds_df, r_df[['references', 'source_reference_id']],on='references', how='inner') # Must have a reference
		ds_df = pd.merge(ds_df, t_df[['source_reference_id', 'verbatimScientificName', 'taxon_id']],on=['source_reference_id', 'verbatimScientificName'], how='inner') # Must have a source_taxon_id
		ds_df = pd.merge(ds_df, tr_df[['taxonRank', 'taxonRank_id']],on='taxonRank', how='inner') # Must have a taxonRank_id
		if len(g_df)>0:
			ds_df = pd.merge(ds_df, g_df[['sex', 'sex_id']],on='sex', how='left')
			ds_df.sex_id.fillna(0,inplace=True)
		else:
			ds_df['sex_id'] = 0
		if len(l_df)>0:
			ds_df = pd.merge(ds_df, l_df[['source_reference_id', 'verbatimLocality', 'location_id']],on=['source_reference_id', 'verbatimLocality'], how='left')
			ds_df.location_id.fillna(0,inplace=True)
		else:
			ds_df['location_id'] = 0
		if len(tp_df)>0:
			ds_df = pd.merge(ds_df, tp_df[['source_reference_id', 'time_period', 'time_period_id']],on=['source_reference_id', 'time_period'], how='left')
			ds_df.time_period_id.fillna(0,inplace=True)
		else:
			ds_df['time_period_id'] = 0
		if len(m_df)>0:
			ds_df = pd.merge(ds_df, m_df[['source_reference_id', 'measurementMethod', 'method_id']],on=['source_reference_id', 'measurementMethod'], how='left')
			ds_df.method_id.fillna(0,inplace=True)
		else:
			ds_df['method_id'] = 0

		# DietSet
		ds_all = DietSet.objects.is_active()
		for index, row in ds_df.iterrows():
			ds=ds_all.filter(
				reference_id=row.source_reference_id).filter(
				taxon_id=row.taxon_id)
			if row.location_id == 0:
				ds= ds.filter(location__isnull=True)
			else:
				ds= ds.filter(location_id=row.location_id)

			if row.sex_id == 0:
				ds= ds.filter(gender__isnull=True)
			else:
				ds= ds.filter(gender_id=row.sex_id)

			if pd.isna(row.individualCount) == True:
				ds= ds.filter(sample_size=0)
			else:
				ds= ds.filter(sample_size=row.individualCount)

			if pd.isna(row.study_time) == True:
				ds= ds.filter(study_time__isnull=True)
			else:
				ds= ds.filter(study_time=row.study_time)

			if row.method_id == 0:
				ds= ds.filter(method__isnull=True)
			else:
				ds= ds.filter(method_id=row.method_id)

			if row.time_period_id == 0:
				ds= ds.filter(time_period__isnull=True)
			else:
				ds= ds.filter(time_period_id=row.time_period_id)

			if pd.isna(row.cited_reference) == True:
				ds= ds.filter(cited_reference__isnull=True)
			else:
				ds= ds.filter(cited_reference=row.cited_reference)

#			print ("Id count {}: {} {} {} {} {} {} {} {} {}".format(
#				len(ds),
#				row.source_reference_id,
#				row.taxon_id,
#				row.location_id,
#				row.sex_id,
#				row.individualCount,
#				row.study_time,
#				row.method_id,
#				row.time_period_id,
#				row.cited_reference))

			if len(ds)>0:
				ds_df.at[index,'ds_id']=ds[0].id
#				print ("Found Id {}: ".format(ds_df.at[index,'ds_id']))
			else:
				ds_new = DietSet(
					reference_id=row.source_reference_id,
					taxon_id=row.taxon_id)
				if row.location_id > 0:
					ds_new.location_id = row.location_id
				if row.sex_id > 0:
					ds_new.gender_id = row.sex_id
				if pd.isna(row.individualCount) == False:
					ds_new.sample_size = row.individualCount
				if pd.isna(row.study_time) == False:
					ds_new.study_time = row.study_time
				if row.method_id > 0:
					ds_new.method_id = row.method_id
				if row.time_period_id > 0:
					ds_new.time_period_id = row.time_period_id
				if pd.isna(row.cited_reference) == False:
					ds_new.cited_reference = row.cited_reference
				print('All OK here')
				print ("location_id {}: ".format(ds_new.location_id))
				print ("gender_id {}: ".format(ds_new.gender_id))
				print ("sample_size {}: ".format(ds_new.sample_size))
				print ("study_time {}: ".format(ds_new.study_time))
				print ("method_id {}: ".format(ds_new.method_id))
				print ("time_period_id {}: ".format(ds_new.time_period_id))
				print ("cited_reference {}: ".format(ds_new.cited_reference))

				ds_new.save()
				ds_df.at[index,'ds_id']=ds_new.id
#					print ("New Id {}: {} is a {}".format(ds_df.at[index,'ds_id'],row['verbatimScientificName'],ds_df.at[index,'source_reference_id']))

		#Cloning the dataframe for diet set items
		dsi_df = df.copy()
		# Update DietSetItems with Id's
		dsi_df = pd.merge(dsi_df, r_df[['references', 'source_reference_id']],on='references', how='inner') # Must have a reference
		dsi_df = pd.merge(dsi_df, t_df[['source_reference_id', 'verbatimScientificName', 'taxon_id']],on=['source_reference_id', 'verbatimScientificName'], how='inner') # Must have a source_taxon_id
		dsi_df = pd.merge(dsi_df, fi_df[['source_reference_id', 'food_item', 'fi_id']],on=['source_reference_id', 'food_item'], how='inner') # Must have a food item
		if len(g_df)>0:
			dsi_df = pd.merge(dsi_df, g_df[['sex', 'sex_id']],on='sex', how='left')
			dsi_df.sex_id.fillna(0,inplace=True)
		else:
			dsi_df['sex_id'] = 0
		if len(l_df)>0:
			dsi_df = pd.merge(dsi_df, l_df[['source_reference_id', 'verbatimLocality', 'location_id']],on=['source_reference_id', 'verbatimLocality'], how='left')
			dsi_df.location_id.fillna(0,inplace=True)
		else:
			dsi_df['location_id'] = 0
		if len(tp_df)>0:
			dsi_df = pd.merge(dsi_df, tp_df[['source_reference_id', 'time_period', 'time_period_id']],on=['source_reference_id', 'time_period'], how='left')
			dsi_df.time_period_id.fillna(0,inplace=True)
		else:
			dsi_df['time_period_id'] = 0
		if len(m_df)>0:
			dsi_df = pd.merge(dsi_df, m_df[['source_reference_id', 'measurementMethod', 'method_id']],on=['source_reference_id', 'measurementMethod'], how='left')
			dsi_df.method_id.fillna(0,inplace=True)
		else:
			dsi_df['method_id'] = 0
		dsi_df = pd.merge(dsi_df, ds_df[['source_reference_id', 'taxon_id', 'sex_id', 'location_id', 'time_period_id', 'method_id', 'individualCount', 'study_time', 'cited_reference', 'ds_id']],on=['source_reference_id', 'taxon_id', 'sex_id', 'location_id', 'time_period_id', 'method_id', 'individualCount', 'study_time', 'cited_reference'], how='left')
		dsi_df = dsi_df.sort_values(by='sort_order')
		dsi_df["list_order"] = dsi_df.groupby(['ds_id']).cumcount()+1


#		print(dsi_df[['source_reference_id', 'taxon_id', 'fi_id', 'sex_id', 'location_id', 'time_period_id', 'method_id', 'ds_id']])

		#DietSetItem
		for index, row in dsi_df.iterrows():
			dsi_new=DietSetItem(diet_set_id=row.ds_id, food_item_id=row.fi_id)
			dsi = DietSetItem.objects.is_active()
			dsi = dsi.filter(
				diet_set_id=row.ds_id).filter(
				food_item_id=row.fi_id)
			if pd.isna(row.percentage) == True:
				dsi= dsi.filter(percentage=0)	#The default is 0 for percentage
			else:
				dsi_new.percentage=str(row.percentage).replace(',','.').replace('nan','0')
#				dsi= dsi.filter(percentage=row.percentage.replace(',','.'))
				dsi= dsi.filter(percentage=row.percentage)

#			n = dsi_df.loc[dsi_df['ds_id'] == row.ds_id].groupby(['ds_id'])['list_order'].max()
#			n = n.values[0]	# n is pandas.core.series.Series type
#			percentage = round(2*(n+1-row.list_order)/(n*(n+1)),3)
#			dsi_new.percentage=percentage
			dsi_new.list_order=row.list_order

			if len(dsi)>0:
				dsi_df.at[index,'dsi_id']=dsi[0].id
				dsi_new=dsi[0]
				dsi_new.list_order=row.list_order
				dsi_new.percentage=str(row.percentage).replace(',','.').replace('nan','0')
				dsi_new.save()
				print ("Found DSI: ", dsi_new)

#				print(row.ds_id, row.list_order, n, percentage)
			else:
				print ("NEW DSI: ", dsi_new)
#				print ("NEW DSI: ", row.ds_id, row.verbatimScientificName, row.verbatimLocality, row.time_period, row.cited_reference, row.sex, row. individualCount, row. study_time, row.measurementMethod, row.food_item, row.percentage)
				dsi_new.save()

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))

	return HttpResponseRedirect(reverse("diet_set-import"))
