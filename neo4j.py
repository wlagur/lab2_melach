__author__ = 'vlad'
import py2neo
from py2neo import Graph, Node, Relationship, authenticate
import json
import requests
authenticate("localhost:7474", "neo4j", "1111")


def get_objects(name):
    """
    fetches objects from my register

    name: method, author, category
    returns: dictionary
    """
    request = requests.get('http://127.0.0.1:5010/api/' + str(name))
    api_data = json.loads(request.text)
    #print(request.text)
    return api_data["objects"]

def get_objects_art(name):
    """
    fetches objects from my register

    name: method, author, category
    returns: dictionary
    """
    request = requests.get('http://127.0.0.1:5020/api/' + str(name))
    api_data = json.loads(request.text)
    #print(api_data)
    return api_data["objects"]

def get_object(name):
    """
    fetches objects from my register

    name: method, author, category
    returns: dictionary
    """
    request = requests.get('http://127.0.0.1:5010/api/' + str(name))
    api_object = json.loads(request.text)
    #print(request.text)
    return api_object

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
    """
    imports data from my register (method and all adjacent) into graph DB
    """

    graph = Graph()
    # graph.delete_all()
    # Uncomment on the first run!
    # graph.schema.create_uniqueness_constraint("Method", "id")
    # graph.schema.create_uniqueness_constraint("Author", "id")
    # graph.schema.create_uniqueness_constraint("Category", "id")

    obtajenna = get_objects_art('obtaj')

    for api_obtaj in obtajenna:

        node_demand= graph.merge_one("Demand", "id", api_obtaj["id"])
        node_demand["reason_doc"] = api_obtaj["reason_doc"]
        node_demand["cost_size"] = api_obtaj["cost_size"]

        for api_author in api_obtaj["borjnuku"]:
            node_borjnuk = graph.merge_one("Borjnuk", "id", api_author["id"])
            node_borjnuk["name"] = api_author["name"]
            node_borjnuk["tel_number"] = api_author["tel_number"]
            node_borjnuk.push()
            graph.create_unique(Relationship(node_borjnuk, "obtajuetsa", node_demand))

        for api_property in api_obtaj["properties"]:
            node_property = graph.merge_one("Property", "id", api_property["id"])
            node_property["name"] = api_property["name_property"]
            node_property["ser_number"] = api_property["ser_number"]
            node_property.push()
            graph.create_unique(Relationship(node_property, "zakladena", node_demand))
        node_demand.push()

    demands = get_objects('demand')

    for api_demand in demands:

        node_demand = graph.merge_one("Demand", "id", api_demand["id"])
        node_demand["sum"] = api_demand["sum"]

        api_debtor = api_demand["Debtor"]
        node_debtor = graph.merge_one("Debtor", "id", api_debtor["id"])
        node_debtor["name"] = api_debtor["name"]

        api_arbitration = get_object('arbitration/' + str(api_debtor["arbitration_id"]))
        #print(api_arbitration.text)
        node_arbitration = graph.merge_one("Arbitration", "id", api_arbitration["id"])
        node_arbitration["name"] = api_arbitration["name"]
        node_arbitration.push()
        graph.create_unique(Relationship(node_arbitration, "CONTAINS", node_debtor))

        node_debtor.push()
        graph.create_unique(Relationship(node_debtor, "CONTAINS", node_demand))

        api_creditor = api_demand["Creditor"]
        node_creditor = graph.merge_one("Creditor", "id", api_creditor["id"])
        node_creditor["name"] = api_creditor["name"]
        node_creditor.push()
        graph.create_unique(Relationship(node_creditor, "CONTAINS", node_demand))


        """
        for api_author in api_method["authors"]:
            node_author = graph.merge_one("Author", "id", api_author["id"])
            node_author["name"] = api_author["name"]
            node_author.push()
            graph.create_unique(Relationship(node_author, "WROTE", node_method))

        api_category = api_method["category"]
        node_category = graph.merge_one("Category", "id", api_category["id"])
        node_category["name"] = api_category["name"]
        node_category.push()
        graph.create_unique(Relationship(node_category, "CONTAINS", node_method))"""
        node_demand.push()
def import_api_data2():
    authenticate("localhost:7474", "neo4j", "1111")
    graph = Graph()
    #graph.delete_all()

    # Uncomment on the first run!
    #graph.schema.create_uniqueness_constraint("Borjnuk", "id")
    #graph.schema.create_uniqueness_constraint("Obtaj", "id")
    #graph.schema.create_uniqueness_constraint("Property", "id")

    obtajenna = get_objects_art('obtaj')

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
        node_obtaj.push()






if __name__ == "__main__":
    # graph = Graph()
    # graph.delete_all()
    import_api_data()
    #import_api_data2()
