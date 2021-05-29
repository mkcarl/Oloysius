import random 
import json 
from py2neo import Graph, Node, Relationship, cypher


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
        skill_name = data["queryResult"]["parameters"]["Skill"][0]
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
        cypher_query = f"MATCH (comp:Company)-[:ORGANISE]->(proj:Project)-[:LEAD_BY]->(emp:Employee) WHERE comp.CompanyName =~ '(?i){company_name}' RETURN emp, proj"
        all_employee_project = graph.run(cypher_query).data()
        employee_project = random.choice(all_employee_project)
        choices = [
            f"The tech lead of {employee_project['proj']['ProjectName']} is {employee_project['emp']['EmployeeName']}", 
            f"{employee_project['emp']['EmployeeName']} leaded the project {employee_project['proj']['ProjectName']}"
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
        if all_skill_list: 
            choices = [
                f"The skills required in {project_name} is {', '.join(all_skill_list)}"
            ]
        else: 
            return data
    elif intent == "help": 
        # if the user needs help 
        query_examples = [
            "Who knows java?",  
            "What projects did we do in the past involved C?",  
            "Do you know who is the tech lead of our las project with Singtel?",  
            "What is used in Berjaya Fitness System?", 
            "Did we had any affiliations with a company in Thailand?"
        ]    

        final_output =  f"These are some examples of what you can do : "\
                        f"\n - {random.choice(query_examples)}"\
                        f"\n - {random.choice(query_examples)}"\
                        f"\n - {random.choice(query_examples)}"\
        
        choices = [final_output]
    elif intent == "NewData.Project": 
        new_project_name = ""
        cypher_query = f"MATCH ()"

    elif intent == "NewData.Company": 
        new_company_name = data["queryResult"]["parameters"]["compName"]
        new_company_industry = data["queryResult"]["parameters"]["industry"]
        new_company_region  = data["queryResult"]["parameters"]["region"]["country"]
        cypher_query_check = f"MATCH (c:Company) WHERE c.CompanyName =~ '(?i){new_company_name}' RETURN c"
        exist = len(list(graph.run(cypher_query_check))) > 1
        
        if not exist: 
            cypher_query = f"MERGE (c:Company {{compName: '{new_company_name}', industry: '{new_company_industry}', region: '{new_company_region}'}})"
            graph.run(cypher_query)
            choices = [
                "Created new company entry!", 
                f"Success! {new_company_name} created."
            ]
        else: 
            choices = [
                "This entry already exist."
            ]
    elif intent == "NewData.Skill":
        new_skill = data["queryResult"]["parameters"]["skill"]
        cypher_query_check = f"MATCH (s:Skill) WHERE s.skill =~ '(?i){new_skill}' RETURN s"
        exist = len(list(graph.run(cypher_query_check))) > 0 

        if not exist: 
            cypher_query = f"MERGE (s:Skill {{skill: '{new_skill}'}})"
            graph.run(cypher_query)
            choices = [
                f"{new_skill} have been added!", 
                f"New skill acquired!", 
                f"Mastery level increase!"
            ]
        else: 
            choices = [
                f"Skill already exist!", 
                f"Existing skills cannot be added again. :("
            ] 
    elif intent == "NewData.Employee": 
        first_name = data["queryResult"]["parameters"]["emp_fame"]
        last_name = data["queryResult"]["parameters"]["emp_lname"]
        new_employee_name = f"{first_name} {last_name}"
        cypher_query_check = f"MATCH (e:Employee) WHERE e.EmployeeName =~ '(?i){new_employee_name}' RETURN e"
        exist = len(list(graph.run(cypher_query_check))) > 0

        if not exist: 
            cypher_query = f"CREATE (e:Employee {{ EmployeeName: '{new_employee_name}' }})"
            graph.run(cypher_query)
            choices = [
                f"{new_employee_name} has joined your party!", 
                f"You've got a new character! Welcome {new_employee_name} to the party!"
            ]
        else: 
            choices = [
                f"Warning! {new_employee_name} is already in the party!", 
                f"Employee was already in the team..."
            ]
    elif intent == "testCardResponse": 
        custom_card = {
                        "fulfillmentMessages": [
                            {
                            "card": {
                                "title": "LMAO card",
                                "subtitle": "ayeee",
                                "imageUri": "https://cdn.discordapp.com/attachments/846742521983664128/848250432127893565/unknown.png",
                                "buttons": [
                                {
                                    "text": "button text",
                                    "postback": "https://example.com/path/for/end-user/to/follow"
                                }
                                ]
                            }
                            }
                        ]
                        }
        return json.dumps(custom_card)
    else: 
        return data
    

    if choices: 
        output = {
            'fulfillmentText' : random.choice(choices), 
            'source' : 'webhookdata'
        }
        return json.dumps(output)

# TODO : ProjectPeople.Lead intent 