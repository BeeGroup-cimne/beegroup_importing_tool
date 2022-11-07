from neo4j import GraphDatabase

import settings
from utils.utils import read_config

config = read_config(settings.conf_file)
public_ns = "http://beegroup-cimne.com"

neo = GraphDatabase.driver(**config['neo4j'])
with neo.session() as session:
    usetypes = session.run("""Match (n:bigg__BuildingSpaceUseType) return n.uri""").data()
    main_organization = session.run("""Match (n:bigg__Organization) where not n.userID is null return n.uri""").data()

# groups_by organization
for org in main_organization:
    namespace = org['n.uri'].split("#")[0]
    for t in usetypes:
        ut = t['n.uri'].split("#")[1]
        with neo.session() as session:
            session.run(
                f"""
                Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{namespace}#GROUP-USETYPE-{ut}"}})
                WITH g
                Match ({{uri:"{t['n.uri']}"}})<-[:skos__broader*0..]-()<-[:bigg__hasBuildingSpaceUseType{{selected:TRUE}}]-()<-[:bigg__hasSpace]-(b)
                WHERE b.uri =~"{namespace}#.*"
                Merge (g)<-[:bigg__groupsForAnalytics]-(b)
                SET g.bigg__groupType="BuildingSpaceUseType"
                SET g.bigg__groupLabel="{ut}"
            """)
    with neo.session() as session:
        session.run(
            f"""
                Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{namespace}#GROUP-ALLBUILDINGS"}})
                WITH g
                Match (b:bigg__Building)
                WHERE b.uri =~"{namespace}#.*"
                Merge (g)<-[:bigg__groupsForAnalytics]-(b)
                SET g.bigg__groupType="OrganizationAllBuildings"
                SET g.bigg__groupLabel="ALLBUILDINGS"
        """)

# global groups
for t in usetypes:
    ut = t['n.uri'].split("#")[1]
    with neo.session() as session:
        session.run(
            f"""
            Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{public_ns}#GROUP-USETYPE-{ut}"}})
            WITH g
            Match ({{uri:"{t['n.uri']}"}})<-[:skos__broader*0..]-()<-[:bigg__hasBuildingSpaceUseType{{selected:TRUE}}]-()<-[:bigg__hasSpace]-(b)
            Merge (g)<-[:bigg__groupsForAnalytics]-(b)
            SET g.bigg__groupType="GlobalBuildingSpaceUseType"
            SET g.bigg__groupLabel="{ut}"
        """)
with neo.session() as session:
    session.run(
        f"""
            Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{public_ns}#GROUP-ALLBUILDINGS"}})
            WITH g
            Match (b:bigg__Building)
            Merge (g)<-[:bigg__groupsForAnalytics]-(b)
            SET g.bigg__groupType="Global"
            SET g.bigg__groupLabel="ALLBUILDINGS"
    """)

f"""
                Merge (g:bigg__AnalyticalGroup:Resource{{uri:"{namespace}#GROUP-ALLMEASURES"}})
                WITH g
                Match (b:bigg__EnergyEfficiencyMeasure)
                WHERE b.uri =~"{namespace}#.*"
                Merge (g)<-[:bigg__groupsForAnalytics]-(b)
                SET g.bigg__groupType="OrganizationAllMeasures"
                SET g.bigg__groupLabel="ALLMEASURES"
        """

neo = GraphDatabase.driver(**config['neo4j'])
with neo.session() as session:
    usetypes = session.run("""Match (n:bigg__EnergyEfficienyMeasureType) return n.uri""").data()

print(f"""
                Match (mm:bigg__EnergyEfficiencyMeasureType)
                with "{namespace}#GROUP-EEMTYPE-" + split(mm.uri,"#")[1] as uri
                Merge (g:bigg__AnalyticalGroup:Resource{{uri:uri}})
                WITH g
                Match (mm)<-[:skos__broader*0..]-()<-[:bigg__hasEnergyEfficiencyMeasureType]-(b)
                WHERE b.uri =~"{namespace}#.*"
                Merge (g)<-[:bigg__groupsForAnalytics]-(b)
                SET g.bigg__groupType="EnergyEfficiencyMeasureType"
                SET g.bigg__groupLabel=split(mm.uri,"#")[1]
""")