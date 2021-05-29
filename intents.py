import random 
import json 
from py2neo import Graph


graph = Graph(
    uri="neo4j+s://3670dede.databases.neo4j.io",
    user="neo4j", 
    password="4Pd1FlT3AOHxIlf6AoUKQYN09ajnrBOD7_l7mzO0tow"
    )


def return_fulfillment(data): 
    intent = data["queryResult"]["intent"]["displayName"]
    choices = []

    if intent == "EmployeeSkill": 
        # Who knows java? 
        skill_name = data["queryResult"]["parameters"]["skills"][0]
        cypher_query = f"MATCH (emp:Employee)-[:POSSESS]->(skill) WHERE skill.skill = '{skill_name}' RETURN (emp);"
        all_employee = graph.run(cypher_query).data()
        employee = random.choice(all_employee)["emp"]
        choices = [
            f"{employee['EmployeeName']} knows {skill_name}", 
            f"{employee['EmployeeName']} is experienced with {skill_name}"
        ]
    elif intent == "ProjectExperience": 
        # Have we worked with python before?
        skill_name = data["queryResult"]["parameters"]["skills"]
        cypher_query = f"MATCH (proj:Project)-[:REQUIRES]->(sk:Skill) WHERE sk.skill = '{skill_name}' return (proj)"
        all_project = graph.run(cypher_query).data()
        project = random.choice(all_project)['proj']
        print(project)
        choices = [
            f"{project['ProjectName']} involves some skill with {skill_name}", 
            f"{project['ProjectName']} requires personnel with experience in {skill_name}"
        ]
    

    if choices: 
        data = {
            'fulfillmentText' : random.choice(choices), 
            'source' : 'webhookdata'
        }
        return json.dumps(data)