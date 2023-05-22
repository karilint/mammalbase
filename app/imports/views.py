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
def import_diet_set(request):
	if "GET" == request.method:
		return render(request, "import/import_diet_set.html")
	try:
		file = request.FILES["csv_file"]
		df = pd.read_csv(file, sep='\t')
		trim_df(df)
		check = Check(request)
		force = "force" in request.POST
		if check.check_valid_author(df) == False:
			return HttpResponseRedirect(reverse("import_diet_set"))
		if check.check_all_ds(df, force) != True:
			return HttpResponseRedirect(reverse("import_diet_set"))
		else:
			for row in df.itertuples():
				create_dietset(row, df)
			success_message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
			messages.add_message(request, 50 ,success_message, extra_tags="import-message")
			messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
			return HttpResponseRedirect(reverse("import_diet_set"))

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_diet_set"))

@login_required # väliaikainen
def import_proximate_analysis(request):
	if "GET" == request.method:
		return render(request, "import_proximate_analysis.html")

@login_required
def import_ets(request):
	if "GET" == request.method:
		return render(request, "import/import_ets.html")
	try:
		csv_file = request.FILES["csv_file"]
		df = pd.read_csv(csv_file, sep='\t')
		trim_df(df)
		check = Check(request)

		if check.check_valid_author(df) == False:
			return HttpResponseRedirect(reverse("import_ets"))
		if check.check_all_ets(df) != True:
			return HttpResponseRedirect(reverse("import_ets"))
		else:
			headers =  list(df.columns.values)
			for row in df.itertuples():
				create_ets(row, headers)
			success_message = "File imported successfully. "+ str(df.shape[0])+ " rows of data was imported."
			messages.add_message(request, 50 ,success_message, extra_tags="import-message")
			messages.add_message(request, 50 , df.to_html(), extra_tags="show-data")
			return HttpResponseRedirect(reverse("import_ets"))

	except Exception as e:
		logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect(reverse("import_ets"))


"""@login_required
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
		
			if source_reference.master_reference == None:
				source_reference.master_reference = mr_new
				source_reference.save()

			
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

	return HttpResponseRedirect(reverse("diet_set-import"))"""
