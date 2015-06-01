__author__ = 'vlad'
import py2neo
from py2neo import Graph, Node, Relationship, authenticate
import json
import requests


def get_objects(name):
    """
    fetches objects from my register

    name: method, author, category
    returns: dictionary
    """
    request = requests.get('http://127.0.0.1:5010/api/' + str(name))
    api_data = json.loads(request.text)
    print(api_data)
    return api_data["objects"]

def get_objects2(name):
    """
    fetches objects from second register
    name: experts, documents, commission orders, legal_issues, expertises
    returns: dictionary
    """
    request = requests.get('http://polar-journey-8507.herokuapp.com/api/' + str(name))
    api_data = json.loads(request.text)
    return api_data


# categories = get_objects('category')
def import_api_data():
    authenticate("localhost:7474", "neo4j", "1111")
    graph = Graph()
    graph.delete_all()

    # Uncomment on the first run!
    #graph.schema.create_uniqueness_constraint("Borjnuk", "id")
    #graph.schema.create_uniqueness_constraint("Obtaj", "id")
    #graph.schema.create_uniqueness_constraint("Property", "id")

    obtajenna = get_objects('obtaj')

    for api_obtaj in obtajenna:

        node_obtaj= graph.merge_one("Obtaj", "id", api_obtaj["id"])
        node_obtaj["reason_doc"] = api_obtaj["reason_doc"]
        node_obtaj["cost_size"] = api_obtaj["cost_size"]

        for api_author in api_obtaj["borjnuku"]:
            node_borjnuk = graph.merge_one("Borjnuk", "id", api_author["id"])
            node_borjnuk["name"] = api_author["name"]
            node_borjnuk["tel_number"] = api_author["tel_number"]
            node_borjnuk.push()
            graph.create_unique(Relationship(node_borjnuk, "obtajuetsa", node_obtaj))

        for api_property in api_obtaj["properties"]:
            node_property = graph.merge_one("Property", "id", api_property["id"])
            node_property["name"] = api_property["name_property"]
            node_property["ser_number"] = api_property["ser_number"]
            node_property.push()
            graph.create_unique(Relationship(node_property, "zakladena", node_obtaj))

        #api_category = api_obtaj["property"]
        #node_category = graph.merge_one("Category", "id", api_category["id"])
        #node_category["name"] = api_category["name"]
        #node_category.push()
        #graph.create_unique(Relationship(node_category, "CONTAINS", node_obtaj))
        node_obtaj.push()

def import_api2_data():
    """
    imports data from second register (experts and all adjacent)

    """

    graph = Graph()
    # Uncomment on first run!
    graph.schema.create_uniqueness_constraint("Expert", "id")
    graph.schema.create_uniqueness_constraint("Document", "id")
    graph.schema.create_uniqueness_constraint("Comission_order", "id")
    graph.schema.create_uniqueness_constraint("Legal_issue", "id")
    graph.schema.create_uniqueness_constraint("Expertise", "id")

    experts = get_objects2("experts")

    for api_expert in experts:
        node_expert = graph.merge_one("Expert", "id", api_expert["id"])
        node_expert["name"] = api_expert["name"]
        node_expert["workplace"] = api_expert["workplace"]
        node_expert["address"] = api_expert["address"]
        node_expert["phone"] = api_expert["phone"]

        for api_document in api_expert["documents"]:
            node_document = graph.merge_one("Document", "id", api_document["id"])
            node_document["id_doc"] = api_document["id_doc"]
            node_document["release_date"] = api_document["release_date"]
            node_document["expiry_date"] = api_document["expiry_date"]
            node_document["document_type"] = api_document["document_type"]
            node_document.push()
            graph.create_unique(Relationship(node_expert, "SIGNED", node_document))

        for api_order in api_expert["commission_orders"]:
            node_order = graph.merge_one("Comission_order", "id", api_order["id"])
            node_order["commission_name"] = api_order["commission_name"]
            node_order["order_number"] = api_order["order_number"]
            node_order["order_date"] = api_order["order_date"]
            node_order.push()
            graph.create_unique(Relationship(node_order, "APPOINTED", node_expert))

            for api_expertise in api_order["expertises"]:
                node_expertise = graph.merge_one("Category", "id", api_expertise["id"])
                node_expertise["name"] = node_expertise["name"]
                node_expertise.push()
                graph.create_unique(Relationship(node_order, "INCLUDES", node_expertise))



        for api_issue in api_expert["legal_issues"]:
            node_issue = graph.merge_one("Legal_issue", "id", api_issue["id"])
            node_issue["description"] = api_issue["description"]
            node_issue["date"] = api_issue["date"]
            node_issue.push()
            graph.create_unique(Relationship(node_expert, "WORKED_ON", node_issue))



        node_expert.push()


def import_api3_data():

    from py2neo import Graph, Path
    authenticate("localhost:7474", "neo4j", "1111")
    graph = Graph()

    tx = graph.cypher.begin()
    for name in ["Alice", "Bob", "Carol"]:
        tx.append("CREATE (person:Person {name:{name}}) RETURN person", name=name)
    alice, bob, carol = [result.one for result in tx.commit()]

    friends = Path(alice, "KNOWS", bob, "KNOWS", carol)
    graph.create(friends)


if __name__ == "__main__":
    # graph = Graph()
    # graph.delete_all()
    #import_api_data()
    import_api_data()
