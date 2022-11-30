import os
import hubspot
import re
from hubspot import HubSpot
from hubspot.crm.tickets import ApiException

import requests

def main(event):

  # How to use secrets
  # Secrets are a way for you to save API keys or private apps and set them as a variable to use anywhere in your code
  # Each secret needs to be defined like the example below
  

  hubspot = HubSpot(access_token=os.getenv('PRIVATEKEY'))
  
  #Getting the email attached to this ticket
  try:
    ApiResponse = hubspot.crm.tickets.associations_api.get_all(ticket_id=event.get('inputFields').get('hs_ticket_id'), to_object_type="email")
    result = ApiResponse.results
    size = len(result)
  
    associated_email= result[0]
    email_id = associated_email.id
    #print(email_id)
    
  except ApiException as e:
    print(e)
    # We will automatically retry when the code fails because of a rate limiting error from the HubSpot API.
    raise
    
  url = "https://api.hubapi.com/crm/v3/objects/emails/"+email_id
  querystring = {"properties":["hs_email_text"],"archived":"false"}
  headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(os.getenv('PRIVATEKEY'))}
  response = requests.request("GET", url, headers=headers, params=querystring)

  email = response.json()
  #print(email)
  email_body=email["properties"]["hs_email_text"]
  print(email_body)
   
  #Checking if email body contains a Soacial Security Number
  ptn=re.compile(r'\d\d\d-\d\d-\d\d\d\d')
  sensitive = re.search(ptn, email_body)
  is_sensitive = bool(sensitive)
  #print(is_sensitive)
  
  #Removing the Sensitive Content if it exists
  if sensitive:
    start = sensitive.span()[0]
    end = sensitive.span()[1]
    modified_content= "".join((email_body[:start],"*SENSITIVE CONTENT REMOVED*",email_body[end:]))
    print (modified_content)
    properties = { "properties":
          { "hs_email_html": modified_content,
          "hs_email_text": modified_content
          } 
         }
    requests.request("PATCH", url, json=properties, headers=headers)
