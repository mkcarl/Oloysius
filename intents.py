import random 
import json 
from py2neo import Graph, cypher


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
    elif intent == "ProjectSkill": 
        # Have we worked with python before?
        skill_name = data["queryResult"]["parameters"]["Skill"]
        cypher_query = f"MATCH (proj:Project)-[:REQUIRES]->(sk:Skill) WHERE sk.skill =~ '(?i){skill_name}' return (proj)"
        all_project = graph.run(cypher_query).data()
        project = random.choice(all_project)['proj']
        choices = [
            f"{project['ProjectName']} involved some skill with {skill_name}", 
            f"Yes, {project['ProjectName']} had involved personnel with experience in {skill_name}", 
            f"Yes, {skill_name} was used in {project['ProjectName']}"
        ]
    elif intent == "CompanyPeople.Lead": 
        # who was the tech lead in our last project with singtel
        company_name = data["queryResult"]["parameters"]["company"]
        cypher_query = f"MATCH (comp:Company)-[:ORGANISE]->(proj:Project)-[:LEAD_BY]->(emp:Employee) WHERE comp.CompanyName =~ '(?i){company_name}' RETURN (emp)"
        all_employee = graph.run(cypher_query).data()
        employee = random.choice(all_employee)["emp"]
        choices = [
            f"The tech lead of {company_name} is {employee['EmployeeName']}", 
            f"{employee['EmployeeName']} leaded the project {company_name}"
        ]
    elif intent == "Company.Industry": 
        # were we involved in the healthcare industry? 
        industry = data["queryResult"]["parameters"]["industry"]
        cypher_query = f"MATCH (comp:Company) WHERE comp.Industry =~ '(?i){industry}' RETURN (comp) "
        all_comp = graph.run(cypher_query).data()
        comp = random.choice(all_comp)["comp"]
        choices = [
            f"Yes, we were affiliated in the {industry} industry with {comp['CompanyName']}", 
            f"Yup, we had some experience with {comp['CompanyName']} who is in the {industry} industry"
        ]
    elif intent == "Company.Region": 
        # Do we have a client from Singapore 
        region = data["queryResult"]["parameters"]["geo-country"]
        cypher_query = f"MATCH (comp:Company) WHERE comp.Region =~ '(?i){region}' RETURN (comp) "
        all_comp = graph.run(cypher_query).data()
        comp = random.choice(all_comp)["comp"]
        choices = [
            f"Yes, {comp['CompanyName']} is located in {region}", 
            f"Yup, {comp['CompanyName']} is from {region} "
        ]
    elif intent == "ProjectSkill.All": 
        # What is used in Berjaya fitness system? 
        project_name = data["queryResult"]["parameters"]["project-name"]
        cypher_query = f"MATCH (proj:Project)-[:REQUIRES]->(sk:Skill) WHERE proj.ProjectName =~ '(?i){project_name}' RETURN (sk)"
        all_skill = graph.run(cypher_query).data()
        all_skill_list = [skill["sk"]['skill'] for skill in all_skill]
        choices = [
            f"The skills required in {project_name} is {', '.join(all_skill_list)}"
        ]

    if choices: 
        data = {
            'fulfillmentText' : random.choice(choices), 
            'source' : 'webhookdata'
        }
        return json.dumps(data)