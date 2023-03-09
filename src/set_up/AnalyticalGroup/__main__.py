from neo4j import GraphDatabase
import settings
from utils.utils import read_config
from copy import deepcopy
import itertools
config = read_config(settings.conf_file)


def create_groups_query(group_classes, item, namespace, group_label, allitems):
    group_query = ""
    for index, group_class in enumerate(group_classes):
        if group_classes[group_class]["uri_part"]['type'] == "__query__":
            group_query += f"""MATCH (n{index}:{group_class})
                               WITH *, {group_classes[group_class]["uri_part"]['obtain'].format(node=f"n{index}")} AS uri{index}
                           """
        elif group_classes[group_class]["uri_part"]['type'] == "__list__":
            group_query += f"""UNWIND {group_classes[group_class]["uri_part"]['obtain']} AS uri{index}
                           """

    group_id = "-".join([x['identifier'] for _, x in group_classes.items()])
    uri_group = "+'-'+".join([f"uri{i}" for i in range(len(group_classes))])
    uri_group = "-'+" + uri_group if uri_group else "'"
    uri = f"{group_label}-{group_id if group_id else allitems}"
    group_query += f"""WITH *, '{namespace}#{uri}{uri_group} as uri
                   """
    # Create the group
    group_query += f"""MERGE (g:bigg__AnalyticalGroup:Resource{{uri:uri}})
                       SET g.bigg__groupType=[{','.join(["'"+ v['group_field']+ "'" for _, v in group_classes.items()])}]
                       SET g.bigg__groupLabel=[{",".join([f'uri{index}' for index in range(len(group_classes))])}]
                      WITH *, g
                   """
    # filter items
    group_query += f"""Match(item:{item})  
                      WHERE item.uri =~"{namespace}#.*"
                   """
    for index, group_class in enumerate(group_classes):
        group_query += "WITH *, item"
        group_query += group_classes[group_class]['query'].format(node=f"n{index}", uri=f"uri{index}")

    # LINK items with group
    group_query += f"""
                      FOREACH (_ IN CASE WHEN item IS NOT NULL THEN [1] END | MERGE (g)<-[:bigg__groupsForAnalytics]-(item)) 

                   """
    return group_query



group_classes_EEM = {
    "bigg__EnergyEfficiencyMeasureType": {
        "group_field": "EnergyEfficiencyMeasureType",
        "identifier": "EEMTYPE",
        "query": """
            Match ({node})<-[:skos__broader*0..]-()<-[:bigg__hasEnergyEfficiencyMeasureType]-(item:bigg__EnergyEfficiencyMeasure)
        """,
        "uri_part": {
            "type": "__query__",
            "obtain": """split({node}.uri,"#")[1]"""
        }
    },
    "bigg__Area": {
        "identifier": "AREA",
        "group_field": "Area",
        "query": """
                Match ({{uri: "http://bigg-project.eu/ontology#GrossFloorArea"}})<-[:bigg__hasAreaType]
                -(area:bigg__Area)<-[:bigg__hasArea{{selected:true}}]-()-[:bigg__isAssociatedWithElement]->
                ()-[:bigg__isAffectedByMeasure]->(item:bigg__EnergyEfficiencyMeasure)
                WITH *,
                CASE 
                    WHEN {uri}="S" 
                    THEN
                        CASE 
                            WHEN toFloat(area.bigg__areaValue) < 500 THEN item
                            ELSE null
                        END 
                    WHEN {uri}="M"
                    THEN    
                         CASE 
                            WHEN toFloat(area.bigg__areaValue)>=500 and toFloat(area.bigg__areaValue)<2000 THEN item
                            ELSE null
                        END 
                    WHEN {uri}="L"
                        THEN
                         CASE 
                            WHEN toFloat(area.bigg__areaValue)>=2000 THEN item
                            ELSE null
                        END
                    END as item
        """,
        "uri_part": {
            "type": "__list__",
            "obtain": ["S", "M", "L"]
        }
    }
}


group_classes_BUILDINGS = {
    "bigg__BuildingSpaceUseType": {
        "group_field": "BuildingSpaceUseType",
        "identifier": "BTYPE",
        "query": """
            Match ({node})<-[:skos__broader*0..]-()<-[:bigg__hasBuildingSpaceUseType]-()<-[:bigg__hasSpace]-(item:bigg__Building)
        """,
        "uri_part": {
            "type": "__query__",
            "obtain": """split({node}.uri,"#")[1]"""
        }
    },
    "bigg__Area": {
        "identifier": "AREA",
        "group_field": "Area",
        "query": """
                Match ({{uri: "http://bigg-project.eu/ontology#GrossFloorArea"}})<-[:bigg__hasAreaType]
                -(area:bigg__Area)<-[:bigg__hasArea{{selected:true}}]-()<-[:bigg__hasSpace]-(item:bigg__Building)
                WITH *,
                CASE 
                    WHEN {uri}="S" 
                    THEN
                        CASE 
                            WHEN toFloat(area.bigg__areaValue) < 500 THEN item
                            ELSE null
                        END 
                    WHEN {uri}="M"
                    THEN    
                         CASE 
                            WHEN toFloat(area.bigg__areaValue)>=500 and toFloat(area.bigg__areaValue)<2000 THEN item
                            ELSE null
                        END 
                    WHEN {uri}="L"
                        THEN
                         CASE 
                            WHEN toFloat(area.bigg__areaValue)>=2000 THEN item
                            ELSE null
                        END
                    END as item
        """,
        "uri_part": {
            "type": "__list__",
            "obtain": ["S", "M", "L"]
        }
    }
}


public_ns = "http://beegroup-cimne.com"

group_label = "GROUP"
namespace = "https://icaen.cat"

# group_classes = group_classes_EEM
# all_groups = "ALLMEASURES"
# item = "bigg__EnergyEfficiencyMeasure"
group_classes = group_classes_BUILDINGS
all_groups = "ALLBUILDINGS"
item = "bigg__Building"

# create combinations true_false mask
mask = list(itertools.product([True, False], repeat=len(group_classes)))
neo = GraphDatabase.driver(**config['neo4j'])
for combination in mask:
    other = deepcopy(group_classes)
    for index, group_class in enumerate(group_classes):
        available = combination[index]
        if not available:
            del other[group_class]
    query = create_groups_query(other, item, namespace, group_label, all_groups)
    print("_____")
    print(query)
    with neo.session() as s:
        s.run(query)
    print("____")

#
# from neo4j import GraphDatabase
#
# import settings
# from utils.utils import read_config
#
# config = read_config(settings.conf_file)
# public_ns = "http://beegroup-cimne.com"
#
# neo = GraphDatabase.driver(**config['neo4j'])
# with neo.session() as session:
#     usetypes = session.run("""Match (n:bigg__BuildingSpaceUseType) return n.uri""").data()
#     main_organization = session.run("""Match (n:bigg__Organization) where not n.userID is null return n.uri""").data()
#
# # groups_by organization
# for org in main_organization:
#     namespace = org['n.uri'].split("#")[0]
#     for t in usetypes:
#         ut = t['n.uri'].split("#")[1]
#         with neo.session() as session:
#             session.run(
#                 f"""
#                 Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{namespace}#GROUP-USETYPE-{ut}"}})
#                 WITH g
#                 Match ({{uri:"{t['n.uri']}"}})<-[:skos__broader*0..]-()<-[:bigg__hasBuildingSpaceUseType{{selected:TRUE}}]-()<-[:bigg__hasSpace]-(b)
#                 WHERE b.uri =~"{namespace}#.*"
#                 Merge (g)<-[:bigg__groupsForAnalytics]-(b)
#                 SET g.bigg__groupType="BuildingSpaceUseType"
#                 SET g.bigg__groupLabel="{ut}"
#             """)
#     with neo.session() as session:
#         session.run(
#             f"""
#                 Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{namespace}#GROUP-ALLBUILDINGS"}})
#                 WITH g
#                 Match (b:bigg__Building)
#                 WHERE b.uri =~"{namespace}#.*"
#                 Merge (g)<-[:bigg__groupsForAnalytics]-(b)
#                 SET g.bigg__groupType="OrganizationAllBuildings"
#                 SET g.bigg__groupLabel="ALLBUILDINGS"
#         """)
#
# # global groups
# for t in usetypes:
#     ut = t['n.uri'].split("#")[1]
#     with neo.session() as session:
#         session.run(
#             f"""
#             Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{public_ns}#GROUP-USETYPE-{ut}"}})
#             WITH g
#             Match ({{uri:"{t['n.uri']}"}})<-[:skos__broader*0..]-()<-[:bigg__hasBuildingSpaceUseType{{selected:TRUE}}]-()<-[:bigg__hasSpace]-(b)
#             Merge (g)<-[:bigg__groupsForAnalytics]-(b)
#             SET g.bigg__groupType="GlobalBuildingSpaceUseType"
#             SET g.bigg__groupLabel="{ut}"
#         """)
# with neo.session() as session:
#     session.run(
#         f"""
#             Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{public_ns}#GROUP-ALLBUILDINGS"}})
#             WITH g
#             Match (b:bigg__Building)
#             Merge (g)<-[:bigg__groupsForAnalytics]-(b)
#             SET g.bigg__groupType="Global"
#             SET g.bigg__groupLabel="ALLBUILDINGS"
#     """)
#
# f"""
#                 Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{namespace}#GROUP-ALLMEASURES"}})
#                 WITH g
#                 Match (b:bigg__EnergyEfficiencyMeasure)
#                 WHERE b.uri =~"{namespace}#.*"
#                 Merge (g)<-[:bigg__groupsForAnalytics]-(b)
#                 SET g.bigg__groupType="OrganizationAllMeasures"
#                 SET g.bigg__groupLabel="ALLMEASURES"
#         """
#
# neo = GraphDatabase.driver(**config['neo4j'])
# with neo.session() as session:
#     usetypes = session.run("""Match (n:bigg__EnergyEfficienyMeasureType) return n.uri""").data()
#
# print(f"""
#                 Match (mm:bigg__EnergyEfficiencyMeasureType)
#                 with "{namespace}#GROUP-EEMTYPE-" + split(mm.uri,"#")[1] as uri
#                 Merge (g:bigg__AnalyticalGroup:Resource{{uri:uri}})
#                 WITH g
#                 Match (mm)<-[:skos__broader*0..]-()<-[:bigg__hasEnergyEfficiencyMeasureType]-(b:bigg__EnergyEfficiencyMeasure)
#                 WHERE b.uri =~"{namespace}#.*"
#                 Merge (g)<-[:bigg__groupsForAnalytics]-(b)
#                 SET g.bigg__groupType="EnergyEfficiencyMeasureType"
#                 SET g.bigg__groupLabel=split(mm.uri,"#")[1]
# """)
#