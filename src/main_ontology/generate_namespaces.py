import glob
import rdflib
import requests
from utils.rdf.rdf_functions import get_namespace_subject

main_files = [
    {
        "n": "ontology/ontologies/Bigg.ttl",
        "f": "https://nextcloud.tech.beegroup-cimne.com/s/N8tcFQdrHm35Sie/download"
    },
    {
        "n": "ontology/dictionaries/bigg_enums.ttl",
        "f": "https://nextcloud.tech.beegroup-cimne.com/s/j2jQbdSNPoK8tan/download"
    },
    {
        "n": "ontology/dictionaries/countries.ttl",
        "f": "https://nextcloud.tech.beegroup-cimne.com/s/SJqYLco7R4wtTP4/download"
    },
    {
        "n": "ontology/dictionaries/units.ttl",
        "f": "https://nextcloud.tech.beegroup-cimne.com/s/x2roDryH93xr35d/download"
    }
]
ONTOLOGY = "ontology/ontologies/*"
DICTIONARY = "ontology/dictionaries/*"
STORE_NAMESPACES = "ontology/namespaces_definition.py"
STORE_CLASS_DEFINITIONS = "ontology/bigg_classes.py"
ThingClass = rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Thing')


def static_namespaces():
    return """from rdflib.term import URIRef
from rdflib.namespace import ClosedNamespace
"""


def static_class():
    import_line = STORE_NAMESPACES.split(".")[0].replace("/", ".")
    return f"""from rdflib import RDF, Literal, Graph, URIRef
from {import_line} import *


class BIGGObjects(object):
    __rdf_type__ = "__invalid__"
    __rdf_namespace__ = "__invalid__"

    @classmethod
    def set_namespace(cls, namespace):
        cls.__rdf_namespace__ = namespace

    def __init__(self, subject):
        self.subject = self.__rdf_namespace__[subject]
        if self.__class__ == BIGGObjects.__class__:
            raise NotImplementedError("The BiggObject is abstract")

    def get_graph(self):
        g = Graph()
        for tt in self.__rdf_type__:
            g.add((self.subject, RDF.type, eval(tt)))
        for k, v in vars(self).items():
            if k != "subject" and v:
                if isinstance(v, URIRef):
                    g.add((self.subject, Bigg[k], v))
                else:
                    g.add((self.subject, Bigg[k], Literal(v)))
        return g
    """


def namespace_definition_dictionary(dictionary_name, namespace_uri, dictionary):
    enums = dictionary.query("""Select Distinct ?s WHERE{?s a ?o}""")
    object_str = f"""
{dictionary_name.lower()}_terms = [{", ".join([f'"{get_namespace_subject(x[0])[1]}"' for x in enums])}]

{dictionary_name} = ClosedNamespace(uri="{namespace_uri}", terms={dictionary_name.lower()}_terms)
"""
    return object_str


def namespace_definition_ontology(ontology_name, namespace_uri, onto):
    class_def = onto.query("Select ?class Where {?class a owl:Class}")
    data_properties = onto.query(
        f"Select ?dt WHERE {{ ?dt a owl:DatatypeProperty }}")
    object_properties = onto.query(
        f"Select ?dt WHERE {{ ?dt a owl:ObjectProperty }}")

    object_str = f"""

{ontology_name.lower()}_class_terms = [{", ".join([f'"{x[0].split("#")[1]}"' for x in class_def])}]
{ontology_name.lower()}_dprop_terms = [{", ".join([f'"{x[0].split("#")[1]}"' for x in data_properties])}]
{ontology_name.lower()}_oprop_terms = [{", ".join([f'"{x[0].split("#")[1]}"' for x in object_properties])}]

{ontology_name.lower()}_terms = {ontology_name.lower()}_class_terms + {ontology_name.lower()}_dprop_terms + {ontology_name.lower()}_oprop_terms

{ontology_name} = ClosedNamespace(uri="{namespace_uri}", terms={ontology_name.lower()}_terms)
"""
    return object_str


def ontology_class_implementations(ontology_name, namespace_uri, onto):
    object_str = ""
    class_def_super = {}
    class_with_superclass = onto.query(
        f"""Select ?class ?super Where {{
            ?class a owl:Class . 
            ?class rdfs:subClassOf ?super 
            FILTER(?class != <{ThingClass}>).
        }}"""
    )
    for s in class_with_superclass:
        try:
            class_def_super[s[0]].append(s[1])
        except:
            class_def_super[s[0]] = [s[1]]
    class_def = onto.query(
        f"""
         Select ?class Where {{
             ?class a owl:Class .
             FILTER(?class != <{ThingClass}>).
             FILTER NOT EXISTS {{
                 ?class rdfs:subClassOf ?n}}.
         }}
         """)
    for s in class_def:
        class_def_super[s[0]] = []

    for s in class_def_super:
        class_def_super[s].append(ThingClass)

    for class_d, super_class in class_def_super.items():
        joined_py_class = [f"{ontology_name}.{class_d.split('#')[1]}"] + [f"{ontology_name}.{x.split('#')[1]}" for x in
                                                                          super_class]
        object_str += f"""

class {class_d.split("#")[1]}(BIGGObjects):
    __rdf_type__ = {joined_py_class}
"""

        joined_class = [class_d] + super_class
        union_query = " UNION ".join([f"{{ ?dt rdfs:domain {sclass.n3()}}}" for sclass in joined_class])
        query_d_prop = f"""
        Select ?dt WHERE {{ 
        {{?dt a owl:DatatypeProperty}} UNION {{?dt a owl:ObjectProperty}} .
        {union_query} .
        }}"""
        d_properties = []
        for data_properties in onto.query(query_d_prop):
            d_properties.append(f"""{data_properties[0].split("#")[1]}""")
        object_str += f"""
    def __init__(self, subject, {",".join([f"{k}=None" for k in d_properties])}):
        super().__init__(subject)"""
        for prop in d_properties:
            object_str += f"""
        self.{prop} = {prop}"""
        object_str += """
        """

    return object_str


def get_rdf(rdf_file):
    name = rdf_file.split("/")[-1].split(".")[0]
    rdf = rdflib.graph.Graph()
    rdf.parse(rdf_file, format="ttl")
    return name, rdf


def ontology_params(owl_file):
    ontology_name, onto = get_rdf(owl_file)
    for x in onto.namespaces():
        if x[0] == owl_file.split("/")[-1].split(".")[0].lower():
            break
    namespace_uri = x[1].toPython()

    return ontology_name, namespace_uri, onto


def dictionary_params(dict_file):
    dict_name, dicti = get_rdf(dict_file)
    s = next(dicti.subjects()).toPython()
    namespace_uri = get_namespace_subject(s)[0]
    return dict_name, namespace_uri, dicti


def generate_definition_file():
    with open(f"{STORE_NAMESPACES}", "w") as file:
        file.write(static_namespaces())

    for owl_file in glob.glob(ONTOLOGY):
        with open(f"{STORE_NAMESPACES}", "a") as file:
            file.write(namespace_definition_ontology(*ontology_params(owl_file)))
    for owl_file in glob.glob(DICTIONARY):
        with open(f"{STORE_NAMESPACES}", "a") as file:
            file.write(namespace_definition_dictionary(*dictionary_params(owl_file)))


def generate_class_file():
    with open(f"{STORE_CLASS_DEFINITIONS}", "w") as file:
        file.write(static_class())
    for owl_file in glob.glob(ONTOLOGY):
        with open(f"{STORE_CLASS_DEFINITIONS}", "a") as file:
            file.write(ontology_class_implementations(*ontology_params(owl_file)))


def download_main_files(additional=None):
    for f in main_files:
        f_cont = requests.get(f['f'])
        open(f["n"], 'w').write(f_cont.text)


if __name__ == "__main__":
    download_main_files()
    generate_definition_file()
    generate_class_file()
