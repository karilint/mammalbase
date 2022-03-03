# exec(open('scripts\\script_test.py').read())

from mb.models import *
import pandas as pd
import io

def get_parent(id):
	try:
		me = MasterEntity.objects.get(pk=id)		
		if (me.entity.name) == 'Species':
			print('Species')
			return me
		elif (me.entity.name) == 'Subspecies':
			print('Subpecies')
			taxon = me.name.split(' ')
			genus = taxon[0]
			species = taxon[1]
			subspecies = taxon[2]
			try:
				pe = MasterEntity.objects.is_active().filter(reference_id = 4).filter(name = genus+' '+species)
				parent = pe[0]
				return parent
			except MasterEntity.DoesNotExist:
				print("Parent does not exist")
		else:
		   return null		
	except MasterEntity.DoesNotExist:
		print("Taxon does not exist")

# This returns master_entity_id for a species name
def get_master_species_id(string_taxon):
	try:
		me_qs = MasterEntity.objects.is_active().filter(reference_id = 4).filter(entity_id=1).filter(name = string_taxon)
		if len(me_qs)==0:
			return NONE
		else:
			me = me_qs[0]
			return me.id
	except MasterEntity.DoesNotExist:
		print("Taxon does not exist")

def get_master_species(id):
	try:
		er_qs = EntityRelation.objects.is_active().filter(source_entity_id=id).filter(relation_id=1).filter(data_status_id=5).filter(master_entity__reference_id=4)
		me = er_qs[0]
		return me
	except MasterEntity.DoesNotExist:
		print("Taxon does not exist")

# This returns both the Species id and its subspecies ids
def get_master_subspecies_ids(id):
	try:
		me = MasterEntity.objects.get(pk=id)
		spp_qs = MasterEntity.objects.is_active().filter(entity_id=7).filter(reference_id=4).filter(name__startswith=me.name+' ') | MasterEntity.objects.is_active().filter(id=id).filter(reference_id=4)
		spp_ids=spp_qs.values_list('id', flat=True).distinct()
		return spp_ids
	except MasterEntity.DoesNotExist:
		print("Taxon does not exist")
		return NONE

# This returns both the Species id and its Genus id
def get_master_genus_id(id):
	try:
		me = MasterEntity.objects.get(pk=id)
		genus = me.name.split()[0]
		qs = MasterEntity.objects.is_active().filter(entity_id=3).filter(reference_id=4).filter(name__startswith=genus) | MasterEntity.objects.is_active().filter(id=id).filter(reference_id=4)
		ids=qs.values_list('id', flat=True).distinct()
		return ids
	except MasterEntity.DoesNotExist:
		print("Taxon does not exist")
		return NONE


# This returns the source_entity_id's
def get_source_entity_ids(ids):
	try:
		er_qs = EntityRelation.objects.is_active().filter(master_entity_id__in=ids).filter(relation_id=1).filter(data_status_id=5).filter(master_entity__reference_id=4)
		se_ids = er_qs.values_list('source_entity_id', flat=True).distinct()
#		print(se_ids)
		return se_ids
	except EntityRelation.DoesNotExist:
		print("No relations exist")
		return NONE

# This returns Diet Sets for a list of source ids
# SEE THE FILTER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
####################################################
def get_diet_sets(ids):
	try:
#		ds_qs=DietSet.objects.is_active().filter(taxon_id__in=ids).filter(taxon__is_active=1).filter(id__lte=5606)
		ds_qs=DietSet.objects.is_active().filter(taxon_id__in=ids).filter(taxon__is_active=1)
		return ds_qs
	except EntityRelation.DoesNotExist:
		print("No relations exist")

def get_diet_set_items(id):
	try:
		dsi_qs=DietSetItem.objects.is_active().filter(diet_set_id=id).exclude(food_item__part_id=15).order_by('list_order')
		return dsi_qs
	except EntityRelation.DoesNotExist:
		print("No Diet Set Items exist")
		return NONE

def get_diet(id):
	try:
		me = MasterEntity.objects.get(pk=id)
		# etsi lisäksi mahdolliset subspecies
		ids = get_master_subspecies_ids(me.id)
#		print(ids)
		se_ids = get_source_entity_ids(ids)
		ds_qs = get_diet_sets(se_ids)

		# etsi genus diet
		if len(ds_qs)==0:
			ids = get_master_genus_id(id)
#			print(ids)
			se_ids = get_source_entity_ids(ids)
			ds_qs = get_diet_sets(se_ids)
		
		return ds_qs

	except MasterEntity.DoesNotExist:
		print("Taxon does not exist")


with io.open('C:\\Users\\lintulaa\\Google Drive\\Articles\\Article Diet\\Results\\Results07122021\\cluster_members_ward_100.txt','r',encoding='utf8') as f:
#with io.open('C:\\Users\\lintulaa\\Google Drive\\Articles\\Article Diet\\Results\\New results 20211020\\cluster_members_ward_100.txt','r',encoding='utf8') as f:
	rows = f.readlines()

## process Unicode text
#with io.open(filename,'w',encoding='utf8') as f:
#    f.write(text)

#f = open("C:\\Users\\lintulaa\\Google Drive\\Articles\\Article Diet\\Results\\New results 20211020\\cluster_members_ward_100.txt", "r")
#clusters = pd.DataFrame({'Cluster':[], 'Abbr':[], 'n':[], 'Members':[]})
clusters_df = pd.DataFrame({'Cluster':[], 'Members':[]})

for row in rows:
	if row.startswith("Cluster:"):
#		if row.startswith("Cluster: 10"):
#			break
		members = []
		cluster_data = row.split(" ")
		cluster_id = cluster_data[1]
	elif row.startswith("\n"):
		clusters_df = clusters_df.append(pd.DataFrame({'Cluster': [cluster_id],'Members': [members]}), ignore_index = True)
#		print(cluster_id, members)
	else:
		taxon = row.split(";")
		string_taxon = taxon[0] + ' ' + taxon[1]
		string_taxon = string_taxon.replace("\n", "")
		taxon_id = get_master_species_id(string_taxon)
		members.append(taxon_id)

cluster_desc_df = pd.DataFrame(columns=['cluster', 'species', 'diet_item', 'part', 'share', 'hierarchy'])
for index, row in clusters_df.iterrows():
	taxa = clusters_df.iloc[index,]['Members']
	print(taxa)
	sum_months = 0

	for taxon in taxa:
		ds_qs = get_diet(taxon)
		if len(ds_qs) > 0:
			for ds in ds_qs:
				dsi_qs = get_diet_set_items(ds.id)
				months = 12
				if(ds.time_period is None):
					months = 12
				else:
					months = ds.time_period.time_in_months
				sum_months = sum_months + months
				for i, dsi in enumerate(dsi_qs, start=1):
					if i != dsi.list_order:
						print(dsi.id)
						break

					n=len(dsi_qs)
					proportion=round(2*(n+1-i)/(n*(n+1)),6)
					print(taxon)
					print(dsi.id)
					df2 = pd.DataFrame(
						[[ index
		#					, kingdom
						, taxon
						, dsi.food_item.tsn.completename
						, dsi.food_item.part.caption
						, proportion*(months/12)
						, dsi.food_item.tsn.hierarchy
						]]
		#					, columns=['cluster', 'species', 'kingdom', 'diet_item', 'part', 'share', 'hierarchy']
						, columns=['cluster', 'species', 'diet_item', 'part', 'share', 'hierarchy']
						)
					cluster_desc_df = cluster_desc_df.append(df2, ignore_index = True)

	cluster_desc_df.loc[cluster_desc_df['cluster'] == index, 'share'] = cluster_desc_df.share/(sum_months/12)


	# For diet description summaries
	aggregations = {
		"share" :['sum','max', 'median','min'],
		"species": ['nunique']
		}

	#http://www.notespoint.com/pandas-multi-column-aggregation/
	x=cluster_desc_df.groupby(['cluster','part', 'diet_item', 'hierarchy']).agg(aggregations).reset_index().sort_values(by=[('share', 'sum')], ascending=False)
	y=cluster_desc_df.groupby(['cluster']).agg({'species': ['nunique']}).reset_index().sort_values(by=[('cluster')], ascending=False)
	x=x.merge(y, left_on='cluster', right_on='cluster')
	#x.reset_index(drop=True, inplace=True)
	x.columns = x.columns.get_level_values(0) + '_' +  x.columns.get_level_values(1)
	#x.groupby(['cluster_','kingdom_','part_', 'diet_item_', 'hierarchy_'])[('share_sum')].cumsum()
	x['cumulative_percentage']=x.groupby(['cluster_'])[('share_sum')].cumsum()

	x.to_excel (r'C:\Users\lintulaa\Google Drive\Articles\Article Diet\TEMP\export_dataframe_20211207.xlsx', index = False, header=True)
