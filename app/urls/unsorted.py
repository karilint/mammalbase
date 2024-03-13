""" urls.unsorted - URLs yet to be sorted out
    Ideally this file is non existing
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from mb import views

urlpatterns = [
    path(
            'im',
            views.index_mammals,
            name='index_mammals'),
    path(
	    'ipa',
	    views.index_proximate_analysis,
	    name='index_proximate_analysis'),
    path(
            'ar/<int:pk>/',
	    views.attribute_relation_detail,
	    name='attribute_relation-detail'),
    path(
	    'ar/<int:pk>/delete/',
	    views.attribute_relation_delete.as_view(),
	    name='attribute_relation-delete'),
    path(
	    'ar/<int:pk>/edit/',
	    views.attribute_relation_edit,
	    name='attribute_relation-edit'),
    path(
	    'ar/<int:sa>/new/',
	    views.attribute_relation_new,
	    name='attribute-relation-new'),
    path(
	    'csor/<int:cso>/new/',
	    views.choiceset_option_relation_new,
	    name='choiceset_option_relation-new'),
    path(
	    'csor/<int:pk>/',
	    views.choiceset_option_relation_detail,
	    name='choiceset_option_relation-detail'),
    path(
	    'csor/<int:pk>/delete/',
	    views.choiceset_option_relation_delete.as_view(),
	    name='choiceset_option_relation-delete'),
    path(
	    'csor/<int:pk>/edit/',
	    views.choiceset_option_relation_edit,
	    name='choiceset_option_relation-edit'),
    path(
	    'data/',
	    views.data_check_detail,
	    name='data_check-detail'),
    path(
	    'er/<int:pk>/',
	    views.entity_relation_detail,
	    name='entity_relation-detail'),
    path(
	    'er/<int:pk>/delete/',
	    views.entity_relation_delete.as_view(),
	    name='entity_relation-delete'),
    path(
	    'er/<int:pk>/edit/',
	    views.entity_relation_edit,
	    name='entity_relation-edit'),
    path(
	    'ma/',
	    views.master_attribute_list,
	    name='master_attribute-list'),
    path(
	    'ma/<int:pk>/',
	    views.master_attribute_detail,
	    name='master_attribute-detail'),
    path(
	    'ma/<int:pk>/delete/',
	    views.master_attribute_delete.as_view(),
	    name='master_attribute-delete'),
    path(
	    'ma/<int:pk>/edit/',
	    views.master_attribute_edit,
	    name='master_attribute-edit'),
    path(
	    'mac/<int:pk>/',
	    views.master_choiceset_option_detail,
	    name='master_choiceset_option-detail'),
    path(
	    'mac/<int:pk>/delete/',
	    views.master_choiceset_option_delete.as_view(),
	    name='master_choiceset_option-delete'),
    path(
	    'mac/<int:pk>/edit/',
	    views.master_choiceset_option_edit,
	    name='master_choiceset_option-edit'),
    path(
	    'mac/new/<int:master_attribute>/',
	    views.master_attribute_master_choiceset_option_new,
	    name='master_attribute_master_choiceset_option-new'),
    path(
	    'me/',
	    views.master_entity_list,
	    name='master_entity-list'),
    path(
	    'me/<int:pk>/',
	    views.master_entity_detail,
	    name='master_entity-detail'),
    path(
	    'me/<int:pk>/delete/',
	    views.master_entity_delete.as_view(),
	    name='master_entity-delete'),
    path(
	    'me/<int:pk>/edit/',
	    views.master_entity_edit,
	    name='master_entity-edit'),
    path(
	    'mer/',
	    views.master_entity_reference_list,
	    name='master_entity_reference-list'),
    path(
	    'mr/<int:pk>/',
	    views.master_reference_detail,
	    name='master_reference-detail'),
    path(
	    'mr/<int:pk>/delete/',
	    views.master_reference_delete.as_view(),
	    name='master_reference-delete'),
    path(
	    'mr/<int:pk>/edit/',
	    views.master_reference_edit,
	    name='master_reference-edit'),
    path(
	    'pa/',
	    views.proximate_analysis_list,
	    name='proximate_analysis-list'),
    path(
	    'pa/<int:pk>/',
	    views.proximate_analysis_detail,
	    name='proximate_analysis-detail'),
    path(
	    'pa/<int:pk>/delete/',
	    views.proximate_analysis_delete.as_view(),
	    name='proximate_analysis-delete'),
    path(
	    'pa/<int:pk>/edit/',
	    views.proximate_analysis_edit,
	    name='proximate_analysis-edit'),
    path(
	    'pai/',
	    views.proximate_analysis_item_list,
	    name='proximate_analysis_item-list'),
    path(
	    'pai/<int:pk>/',
	    views.proximate_analysis_item_detail,
	    name='proximate_analysis_item-detail'),
    path(
	    'pai/<int:pk>/delete/',
	    views.proximate_analysis_item_delete.as_view(),
	    name='proximate_analysis_item-delete'),
    path(
	    'pai/<int:pk>/edit/',
	    views.proximate_analysis_item_edit,
	    name='proximate_analysis_item-edit'),
    path(
	    'par/',
	    views.proximate_analysis_reference_list,
	    name='proximate_analysis_reference-list'),
    path(
	    'par/<int:pk>/',
	    views.proximate_analysis_reference_detail,
	    name='proximate_analysis_reference-detail'),
    path(
	    'pat/',
	    views.view_proximate_analysis_table_list,
	    name='view-proximate_analysis-table-list'),
    path(
	    'sa/',
	    views.source_attribute_list,
	    name='source_attribute-list'),
    path(
	    'sa/<int:pk>/',
	    views.source_attribute_detail,
	    name='source_attribute-detail'),
    path(
	    'sa/<int:pk>/delete/',
	    views.source_attribute_delete.as_view(),
	    name='source_attribute-delete'),
    path(
	    'sa/<int:pk>/edit/',
	    views.source_attribute_edit,
	    name='source_attribute-edit'),
    path(
	    'sac/<int:pk>/',
	    views.source_choiceset_option_detail,
	    name='source_choiceset_option-detail'),
    path(
	    'sac/<int:pk>/delete/',
	    views.source_choiceset_option_delete.as_view(),
	    name='source_choiceset_option-delete'),
    path(
	    'sac/<int:pk>/edit/',
	    views.source_choiceset_option_edit,
	    name='source_choiceset_option-edit'),
    path(
	    'sac/new/<int:source_attribute>/',
	    views.source_attribute_source_choiceset_option_new,
	    name='source_attribute_source_choiceset_option-new'),
    path(
	    'sav/<int:pk>/',
	    views.source_choiceset_option_value_detail,
	    name='source_choiceset_option_value-detail'),
    path(
	    'sav/<int:pk>/delete/',
	    views.source_choiceset_option_value_delete.as_view(),
	    name='source_choiceset_option_value-delete'),
    path(
	    'sav/<int:pk>/edit/',
	    views.source_choiceset_option_value_edit,
	    name='source_choiceset_option_value-edit'),
    path(
	    'sav/<int:se>/<int:sac>/new',
	    views.source_choiceset_option_value_new,
	    name='source_choiceset_option_value-new'),
    path(
	    'save-group-ordering',
	    views.save_new_ordering,
	    name='save-group-ordering'),
    path(
	    'se/',
	    views.source_entity_list,
	    name='source_entity-list'),
    path(
	    'se/<int:pk>/',
	    views.source_entity_detail,
	    name='source_entity-detail'),
    path(
	    'se/<int:pk>/delete/',
	    views.source_entity_delete.as_view(),
	    name='source_entity-delete'),
    path(
	    'se/<int:pk>/edit/',
	    views.source_entity_edit,
	    name='source_entity-edit'),
    path(
	    'serelation/new/<int:source_entity>/',
	    views.source_entity_relation_new,
	    name='source_entity-relation-new'),
    path(
	    'smv/<int:pk>/',
	    views.source_measurement_value_detail,
	    name='source_measurement_value-detail'),
    path(
	    'smv/<int:pk>/edit/',
	    views.source_measurement_value_edit,
	    name='source_measurement_value-edit'),
    path(
	    'smv/<int:pk>/delete/',
	    views.source_measurement_value__delete.as_view(),
	    name='source_measurement_value-delete'),
    path(
	    'smv/new/<int:sa>/<int:se>/',
	    views.source_measurement_value_new,
	    name='source-measurementvalue-new'),
    path(
	    'sr/',
	    views.source_reference_list,
	    name='source_reference-list'),
    path(
	    'sr/<int:pk>/',
	    views.source_reference_detail,
	    name='source_reference-detail'),
    path(
	    'sr/<int:pk>/delete/',
	    views.source_reference_delete.as_view(),
	    name='source_reference-delete'),
    path(
	    'sr/<int:pk>/edit/',
	    views.source_reference_edit,
	    name='source_reference-edit'),
    path(
	    'sr/new',
	    views.source_reference_new,
	    name='source_reference-new'),
    path(
	    'srattribute/new/<int:source_reference>/<int:type>/',
	    views.source_reference_attribute_new,
	    name='source_reference-attribute-new'),
    path(
	    'srattribute/new/<int:source_reference>/<int:source_entity>/',
	    views.source_entity_attribute_new,
	    name='source_entity-attribute-new'),
    path(
	    'srm/new/<int:source_reference>/<int:source_entity>/',
	    views.source_entity_measurement_new,
	    name='source_entity-measurement-new'),
    path(
	    'tp/',
	    views.time_period_list,
	    name='time_period-list'),
    path(
	    'tp/<int:pk>/',
	    views.time_period_detail,
	    name='time_period-detail'),
    path(
	    'tp/<int:pk>/delete/',
	    views.time_period_delete.as_view(),
	    name='time_period-delete'),
    path(
	    'tp/<int:pk>/edit/',
	    views.time_period_edit,
	    name='time_period-edit'),
    path(
	    'tsn/',
	    views.tsn_list,
	    name='tsn-list'),
    path(
	    'tsn/<int:tsn>/',
	    views.tsn_detail,
	    name='tsn-detail'),
    path(
	    'tsn/<int:pk>/delete/',
	    views.tsn_delete.as_view(),
	    name='tsn-delete'),
    path(
	    'tsn/<int:tsn>/edit/',
	    views.tsn_edit,
	    name='tsn-edit'),
    path(
	    'tsn/new',
	    views.tsn_new,
	    name='tsn-new'),
    path(
	    'tsn/search',
	    views.tsn_search,
	    name='tsn-search'),
]


# Old and obsolete ??
# path(
#	    'rnames/',
#	    views.name_list,
#	    name='name_list'),
# path(
#	    'rnames/name/<int:pk>/',
#	    views.name_detail,
#	    name='name_detail'),
# path(
#	    'rnames/name/new',
#	    views.name_new,
#	    name='name_new'),
# path(
#	    'rnames/name/<int:pk>/edit/',
#	    views.name_edit,
#	    name='name_edit'),
# path(
#	    'rnames/qualifier/<int:pk>/',
#	    views.qualifier_detail,
#	    name='qualifier-detail'),
# path(
#	    'mb/names/',
#	    views.MasterReferenceListView.as_view(
#	    ),
#	    name='names'),
# path(
#	    'mr/',
#	    views.master_reference_list,
#	    name='master_reference-list'),
