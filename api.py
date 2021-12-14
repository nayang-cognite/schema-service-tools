#!/usr/bin/env python3

import requests
import json
import logging
import  pprint 

HOST_NAME = "localhost:8080"
PROJECT = "test"

def printDataApi(raw): 
    print(raw)

def api(operationName, query, variables, data_api=False):
    if not data_api:
        url = "http://%s/api/v1/projects/%s/schema/graphql" % (HOST_NAME, PROJECT)
    else :
        url = "http://%s/api/v1/projects/%s/schema/app/graphql" % (HOST_NAME, PROJECT)
    headers = {
        'auth-ticket': "test-ticket",
        'Content-Type': 'application/json'
    }
    json_body = {
        "operationName": operationName,
        "query": query,
        "variables": variables
    }
    try:
        res = requests.post(url, headers=headers, json=json_body, verify=False)
        pp = pprint.PrettyPrinter(indent=2)
        print("---") 
        pp.pprint(res.status_code)
        pp.pprint(res.reason)
        data = res.json()['data']
        print("---") 
        pp.pprint(data)
        if "listSchemas" in data:
            print(data["listSchemas"]["edges"][0]["node"]["versions"][0]["_generatedAPI"])
    except Exception as e:
        logging.error("exception:")
        logging.error(e)

def data_api_list(graphqlType):
    operationName = "TestDataQuery"
    query = """
        query {
            list%s {
                edges { 
                    node {
                        Id
                    }
                }
            }
        }
    """%(graphqlType+"s")
    api(operationName, query, {}, True)

def list_schemas():
    operationName = "TestQuery"
    select = """ {
        externalId
            versions {
                version
                types {
                    name
                    fields {
                        name
                        type
                    }
                }
                graphqlRepresentation
            }
        }
    """
    query = """
        query %s (
            $after: String
            $first: Int
        ){
        listSchemas(after: $after, first: $first) {
               edges {
                   cursor
                   node %s
               }
               pageInfo {
                   hasNextPage
                   hasPreviousPage
                   startCursor
                   endCursor
               }
            }
        }
    """ % (operationName, select)
    variables = {
        "after": None,
        "first": None,
    }
    print("list_schemas")
    api(operationName, query, {})

def introspection_query():
    operationName = "IntrospectionQuery"
    select = """
        description
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
            ...FullType
        }   
    """
    fragments = """
    fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args(includeDeprecated: true) {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields(includeDeprecated: true) {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }
        fragment InputValue on __InputValue {
          name
          description
          type {
            ...TypeRef
          }
          defaultValue
          isDeprecated
          deprecationReason
        }
        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """ 
    query = """
        query %s {
            __schema {
                %s
            }
        }
        %s
    """ % (operationName, select, fragments)
    print("introspection_query")
    api(operationName, query, {})

def introspection_query_type(typeName):
    operationName = "IntrospectionQueryOnType"
    select = """
      __type(name: "%s") {
        fields {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
    """ % (typeName)
    query = """
        query %s {
            %s
        }
    """ % (operationName, select)
    print("introspection_query_on_type")
    print(query)
    api(operationName, query, {})

def create_one_schema(schemaExternalId):
    operationName = "CreateSchema"
    query = """
        mutation %s (
            $schemaExternalId: String!
            $schema: String!
        ){
            createSchemaFromGQL(externalId: $schemaExternalId, schema: $schema) {
                externalId
            }
        }
    """ % (operationName)
    variables = {
        "schemaExternalId": schemaExternalId,
        "schema": "type Equipment @view {Id: Int!}" 
    }
    print("create_one_schema")
    api(operationName, query, variables)

def update_schemas(schemaExternalId):
    operationName = "UpdateSchema"
    query = """
        mutation %s (
            $schemaExternalId: String!
            $schema: String!
        ){
            updateSchemaFromGQL(externalId: $schemaExternalId, schema: $schema) {
                externalId
            }
        }
    """ % (operationName)
    variables = {
        "schemaExternalId": schemaExternalId,
        "schema": "type Equipment {Id: Int!}" 
    }
    print("update_schemas")
    api(operationName, query, variables)

def delete_schemas(schemaExternalId):
    operationName = "DeleteSchema"
    query = """
        mutation %s (
            $schemaExternalId: String!
        ){
            deleteSchemaById(externalId: $schemaExternalId) {
                externalId
            }
        }
    """ % (operationName)
    variables = {
        "schemaExternalId": schemaExternalId,
    }
    api(operationName, query, variables)

if __name__=="__main__":
    schemaExternalId = "Test"
    text = input("Test schema api? [y|n]")
    if (text=="y"):
        text = input("Create schema \"%s\"? [y|n]" % schemaExternalId)
        if (text=="y") :
            create_one_schema(schemaExternalId)
        text = input("Create multiple schemas for \"%s\", enter a number " % schemaExternalId)
        try:
            numSchemas = int(text)
            if (numSchemas>0) :
                for x in range(0,numSchemas):
                    create_one_schema("%s%d" % (schemaExternalId, x))
        except ValueError:
            pass
        text = input("Update schema \"%s\"? [y|n]" % schemaExternalId)
        if (text=="y") :
            update_schemas(schemaExternalId)
        text = input("Delete schema \"%s\"? [y|n]" % schemaExternalId)
        if (text=="y") :
            delete_schemas(schemaExternalId)
        text = input("Create 50 schema versions for \"%s\"? [y|n]" % schemaExternalId)
        if (text=="y") :
            for x in range(0,50):
                update_schemas(schemaExternalId)
        text = input("Run introspection query [y|n]") 
        if (text=="y") :
            introspection_query()
        text = input("Show schemas [y|n]") 
        if (text=="y") :
            list_schemas()
    text = input("Test data api? [y|n]")
    if (text=="y"):
        data_api_list("Equipment")
