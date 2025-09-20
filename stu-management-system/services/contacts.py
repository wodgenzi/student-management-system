from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

# CREDENTIALS_PATH = os.path.join(settings.BASE_DIR, 'utils/credentials.json')
CREDENTIALS_PATH = '/credentials.json'
# TOKEN_PATH = os.path.join(settings.BASE_DIR, 'utils/token.json')
TOKEN_PATH = '/token.json'
SCOPES = ['https://www.googleapis.com/auth/contacts']

def get_contact_group(service, name: str):
    """
    Return contact group resourceName for given name. Optionally create if missing.
    """
    try:
        resp = service.contactGroups().list(pageSize=200, groupFields='name,groupType').execute()
        for grp in resp.get('contactGroups', []):
            if grp.get('name') == name:
                return grp.get('resourceName')
    except HttpError as e:
        print(f"Group lookup/create failed: {e}")
    return None

def get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            from google.auth.exceptions import RefreshError
            try:
                creds.refresh(Request())
            except RefreshError:
                # If refresh fails, get a new token through the flow
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('people', 'v1', credentials=creds)

def create_contact(service, user_data: dict, group_name: str, group_resource: str = None):
    """
    Create a new contact in Google Contacts.
    :param service:
    :param user_data: {
            'name': 'John Doe', 'email': 'johndeo@gmail.com',
            'phone': '+1234567890', 'phone_type': 'mobile',
            'relation_type': 'friend', 'relation_value': 'Jane Doe'
            }
    :return:
    """
    new_contact = {}
    if name:= user_data.get('name', None):
        new_contact['names'] = [{'givenName': name}]
    if email:= user_data.get('email', None):
        new_contact['emailAddresses'] = [{'value': email}]
    if phone:= user_data.get('phone', None):
        new_contact['phoneNumbers'] = [{'value': phone, 'type': user_data.get('phone_type', 'mobile')}]
    if relation_type:=  user_data.get('relation_type', None):
        new_contact['relations'] = [{'type': relation_type, 'person': user_data.get('relation_value', 'Unknown')}]

    group_res = group_resource
    if not group_res and group_name:
        group_res = get_contact_group(service, group_name)

    if group_res:
        new_contact['memberships'] = [{
            'contactGroupMembership': {
                'contactGroupResourceName': group_res
            }
        }]

    try:
        return service.people().createContact(body=new_contact).execute()
    except Exception as e:
        print(f"Error creating contact: {e}")
        return None

def _chunk(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def get_numbers_in_group(service, group_name: str = None, group_resource: str = None,
                          person_fields: str = 'phoneNumbers'):
    """
    Return full person objects for all contacts in the specified group.
    Provide either group_resource (contactGroups/XXX) or group_name.
    """
    if not group_resource:
        if not group_name:
            raise ValueError("Provide group_name or group_resource")
        group_resource = get_contact_group(service, group_name)
        if not group_resource:
            return []

    try:
        members_resp = service.contactGroups().get(resourceName=group_resource, maxMembers=1000).execute()
        member_ids = members_resp.get('memberResourceNames', [])
        if not member_ids:
            return []

        res = []
        for batch in _chunk(member_ids, 200):  # API limit
            resp = service.people().getBatchGet(resourceNames=batch, personFields=person_fields).execute()
            for r in resp.get('responses', []):
                if 'person' in r:
                    res.append(r['person']['phoneNumbers'][0]['value'])
        return res
    except HttpError as e:
        print(f"Error fetching group contacts: {e}")
        return []
