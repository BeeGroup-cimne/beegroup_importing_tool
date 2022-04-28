import os

import rdflib

ONTOLOGIES = "utils/rdf_utils/ontology/ontologies"
DICTIONARIES = "utils/rdf_utils/ontology/dictionaries"
STORE_NAMESPACES = "utils/rdf_utils/ontology/namespaces_definition.py"
STORE_CLASS_DEFINITIONS = "utils/rdf_utils/ontology/bigg_classes.py"


def get_namespace_subject(s):
    if "#" in s:
        namespace_uri = s.split("#")[0] + "#"
        subject = s.split("#")[1]
    else:
        add_slash = s.endswith("/")
        s = s[:-1] if s.endswith("/") else s
        namespace_uri = "/".join([p for p in s.split("/")][:-1]) + "/"
        subject = s.split("/")[-1] + ("/" if add_slash else "")
    return namespace_uri, subject


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
        g.add((self.subject, RDF.type, self.__rdf_type__))
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
    for class_def in onto.query("""Select ?class Where {?class a owl:Class}"""):
        object_str += f"""
        
class {class_def[0].split("#")[1]}(BIGGObjects):
    __rdf_type__ = {ontology_name}.{class_def[0].split("#")[1]}
"""
        d_properties = []
        for data_properties in onto.query(
                f"Select ?dt WHERE {{ {{?dt a owl:DatatypeProperty}} UNION {{?dt a owl:ObjectProperty}} . ?dt rdfs:domain {class_def[0].n3()} }}"):
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


def get_rdf(path, rdf_file):
    name = rdf_file.split(".")[0]
    rdf = rdflib.graph.Graph()
    rdf.load(f"{path}/{rdf_file}", format="ttl")
    return name, rdf


def ontology_params(owl_file):
    ontology_name, onto = get_rdf(ONTOLOGIES, owl_file)
    for x in onto.namespaces():
        if x[0] == owl_file.split("/")[-1].split(".")[0].lower():
            break
    namespace_uri = x[1].toPython()

    return ontology_name, namespace_uri, onto


def dictionary_params(dict_file):
    dict_name, dicti = get_rdf(DICTIONARIES, dict_file)
    s = next(dicti.subjects()).toPython()
    namespace_uri = get_namespace_subject(s)[0]
    return dict_name, namespace_uri, dicti


def generate_definition_file():
    with open(f"{STORE_NAMESPACES}", "w") as file:
        file.write(static_namespaces())
    for owl_file in os.listdir(ONTOLOGIES):
        with open(f"{STORE_NAMESPACES}", "a") as file:
            file.write(namespace_definition_ontology(*ontology_params(owl_file)))
    for owl_file in os.listdir(DICTIONARIES):
        with open(f"{STORE_NAMESPACES}", "a") as file:
            file.write(namespace_definition_dictionary(*dictionary_params(owl_file)))


def generate_class_file():
    with open(f"{STORE_CLASS_DEFINITIONS}", "w") as file:
        file.write(static_class())
    for owl_file in os.listdir(ONTOLOGIES):
        with open(f"{STORE_CLASS_DEFINITIONS}", "a") as file:
            file.write(ontology_class_implementations(*ontology_params(owl_file)))


if __name__ == "__main__":
    generate_definition_file()
    generate_class_file()
