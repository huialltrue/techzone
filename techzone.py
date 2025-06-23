import json
import time
import requests


# Change the following variables to suit the user
user_name = 'Hui'  # Replace this with your name. This is an optional variable used for only for naming projects and resources
user_email = 'ciwino1722@ihnpo.com'  # Replace with user's email or a random email from https://temp-mail.org/en/ for dev/testing

# Leave the following variables unchanged
using_backup_owner_auth0_id = True  # Auth0 ID is a user ID required for creating projects in the AllTrue platform.
# This script provides a backup Auth0 ID to execute certain steps.
# Alternatively, the user can accept the invite sent by this script and use the Auth0 ID of their newly created account.
owner_auth0_id = 'auth0|6855a4d63e97a60d03df8d0b'  # This is a backup Auth0 ID that corresponds to alltrue608@gmail.com
alltrue_api_key = '2leJcrFlSPTwJCeHYNCveVocV6Z0tsva'  # This is an AllTrue API key given auditor, security analyst roles, and custom IBM training roles
customer_id = '42072582-95f4-46ef-be06-bb7aa2cdcff8'  # Default customer ID of the IBM Demos Environment
org_id = '9d59fd41-32e5-411d-923b-a5680855c6ae' # This corresponds to the "IBM GAIS Training" project in IBM Demos.

# To prevent duplicate project names, we use a count variable stored in count.txt. If the count.txt doesn't exist, it's created.
try:
    with open('../count.txt', 'r') as f:
        count = int(f.read())
except:
    count = 1

with open('../count.txt', 'w') as f:
    f.write(str(count + 1))  # Increment count in count.txt

new_project_name = f'{user_name}_Proj_{count}'  # New AllTrue project name with count to avoid duplication
ibm_cloud_account_identifier = f'{user_name}_IBM_Cloud_Account_{count}'  # This is an arbitrary string used to identify the IBM Cloud account to be linked
ibm_api_key = ''  # The ibm_api_key is required for running the following parts of the script
# 1) Linking the IBM Cloud account
# 2) Moving the cloud account to the correct project

# The following variables can also be set to arbitrary strings.
watsonx_assistant_endpoint_identifier = f'{user_name}_Watsonx_Assistant_{count}'
watsonx_ai_service_endpoint_identifier = f'{user_name}_Watsonx_AI_Service_{count}'
watsonx_foundation_model_endpoint_identifier = f'{user_name}_Watsonx_Foundation_Model_{count}'

print(f'New project name: {new_project_name}')
print(f'IBM project name: {ibm_cloud_account_identifier}', '\n')


def get_jwt_token(api_key):
    endpoint = f'https://api.demos.alltrue-be.com/v1/auth/issue-jwt-token'
    headers = {'X-API-Key': f'{api_key}'}
    response = requests.post(endpoint, headers=headers)
    try:
        print(endpoint, '\n' + json.dumps(response.json(), indent=4), '\n')
        return response.json()['access_token']
    except:
        print(endpoint, '\n' + str(response), '\n')

print('# Getting JWT token...')
JWT_TOKEN = get_jwt_token(alltrue_api_key)


def make_api_request(endpoint, method='GET', data=None, params=None, files=None):
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
    }
    response = requests.request(method, endpoint, headers=headers, params=params, json=data, files=files)
    try:
        print(endpoint, '\n' + json.dumps(response.json(), indent=4), '\n')
        return response.json()
    except:
        print(endpoint, '\n' + str(response), '\n')
        return response


# Get connection ID
print('# Getting connection ID...')
endpoint = f'https://api.demos.alltrue-be.com/v1/admin/connections'
method = 'GET'
connection_id = make_api_request(endpoint=endpoint, method=method)[0]['id']


# Invite User
print(f'# Inviting user {user_email}...')
endpoint = f'https://api.demos.alltrue-be.com/v1/admin/invitations'
method = 'POST'
data = {
    'connection_id': connection_id,
    'email': user_email,
    'role_ids': [
        "e6a08923-ce53-4c00-8148-65bad1c6eb61",  # Auditor
        "b6fde60f-a767-45b6-85d9-c94cccfd9ae8",  # Security Analyst
    ]
}
make_api_request(endpoint, method=method, data=data)


# Wait until user has accepted the invited and completed 2FA setup
# If user
while True:
    answer = input('# Have you created a new user account? (y/n): ').strip().lower()
    if answer == 'y':
        print('# Great! Moving on...\n')
        break
    print('# Waiting 30 seconds before asking again...\n')
    time.sleep(30)


# After creating a new user account
# Fetch all users to find the Auth0 ID needed for project creation
print(f'# Getting all users...')
endpoint = f'https://api.demos.alltrue-be.com/v1/admin/auth0-customer/{customer_id}/users'
method = 'GET'
data = {
    'customer_id': customer_id,
}
for user in make_api_request(endpoint, method=method, data=data):
    if user['email'] == user_email:
        print(f'# Found user {user_email} in {customer_id}...\n')
        owner_auth0_id = user['user_id']
        using_backup_owner_auth0_id = False
if using_backup_owner_auth0_id:
    print(f'# {user_email} not found in {customer_id}. Proceeding with backup user...\n')


# Create project API
print(f'# Creating AllTrue project {new_project_name}...')
endpoint = f'https://api.demos.alltrue-be.com/v1/admin/projects'
method = 'POST'
data = {
    'organization_id': org_id,
    'project_name': new_project_name,
    'owner_auth0_id': owner_auth0_id
}
new_project_id = make_api_request(endpoint=endpoint, method=method, data=data)['project_id']


# ibm_api_key is required for the following two functions to work.
# # Link IBM cloud account
# print('# Linking IBM cloud account...')
# endpoint = f'https://api.demos.alltrue-be.com/v1/admin/cloud-accounts/'
# method = 'POST'
# data = {
#   'cloud_accounts': [
#       {
#           'cloud_provider': 'IBM',
#           'ibm_credentials': json.dumps({
#               'apikey': ibm_api_key,
#               'project_id': ibm_cloud_account_identifier
#           })
#       }
#   ]
# }
# make_api_request(endpoint=endpoint, method=method, data=data)  # Though response is None, project_id be listed under All Organizations > AI Inventory > Configuration > Cloud Accounts
# print(f'# {ibm_cloud_account_identifier} should be listed under All Organizations > AI Inventory > Configuration > Cloud Accounts.')
#
#
# # Move cloud account to correct project
# print(f'# Assigning IBM project {ibm_cloud_account_identifier} to AllTrue project {new_project_name}...')
# endpoint = f'https://api.demos.alltrue-be.com/v1/admin/cloud-accounts/projects'
# method = 'PUT'
# data = {
#     'cloud_accounts_projects': [
#         {
#             'cloud_provider_account_id': ibm_cloud_account_identifier,
#             'project_id': new_project_id
#         }
#     ]
# }
# make_api_request(endpoint=endpoint, method=method, data=data)  # IBM Cloud project should appear in AllTrue Project > AI Inventory > Configuration > Cloud Accounts
# print(f'# {ibm_cloud_account_identifier} should be listed under {new_project_name} > AI Inventory > Configuration > Cloud Accounts.\n')


# Adding Hugging Face Model
print(f'# Adding Hugging face Models to {new_project_name}...')
endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources'
method = 'POST'
data = {'resources': []}
huggingface_models = [
    ['ibm-granite/granite-3.1-8b-instruct', '', 'ibm-granite/granite-speech-3.3-8b'],
    ['stable-diffusion-v1-5-ML-Model', 'stable-diffusion-v1-5-ML-Model', 'stable-diffusion-v1-5/stable-diffusion-v1-5'],
    ['Whisper-large-v3-ml-model', 'OpenAI-ml-model', 'openai/whisper-large-v3'],
    ['Llama-3.1-405B-Meta-AI-Model', 'MetaAI-ml-model', 'meta-llama/Llama-3.3-70B-Instruct'],
    ['Meta-Llama-3-70B-Instruct-ml-model', 'MetaAI-ml-model', 'meta-llama/Meta-Llama-3-70B'],
    ['BERT-base-Chinese-ml-model', 'Google-Bert-ml-model', 'google-bert/bert-base-chinese']
]
for resource_type, technology_type, hugging_face_model_id in huggingface_models:
    data['resources'].append({
        'resource_type': resource_type,
        'technology_types': [
            technology_type
        ] if technology_type else [],
        'resource_data': {
            'hugging_face_model_id': hugging_face_model_id,
            'hugging_face_model_revision': 'main',
            'storage_source': 'hugging-face-hub',
        },
        'project_ids': [
            new_project_id
        ],
    })
make_api_request(endpoint=endpoint, method=method, data=data)


# Adding Python Library
print(f'# Adding Python Libraries to {new_project_name}...')
endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources'
method = 'POST'
data = {'resources': []}
python_packages = [
    ['Matplotlib', '3.4.3'],
    ['numpy', '1.19.5'],
    ['pandas', '1.3.3'],
    ['scipy', '1.7.1'],
    ['scikit-learn', '1.0.0'],
    ['xgboost', '1.4.2'],
    ['transformers', '4.11.3'],
    ['tensorflow', '2.6.0'],
    ['tensorboard', '2.7.0'],
    ['TensorFlow-Datasets', '4.4.0'],
    ['tensorflow-hub', '0.12.0'],
    ['tensorflow-probability', '0.14.1'],
    ['TFX', '1.3.0'],
    ['TF-Agents', '0.10.0'],
    ['Pillow', '8.4.0'],
    ['Graphviz', '0.17'],
    ['opencv-python', '4.5.3.56'],
    ['joblib', '0.14.1'],
    ['nltk', '3.6.5'],
    ['ftfy', '6.0.3'],
    ['spacy', '3.8.7']
]
for package, version in python_packages:
    data['resources'].append({
        'resource_type': package,
        'resource_data': {
            'library_name': package,
            'programming_language': 'python',
            'version': version,
        },
        'technology_types': [
            package
        ],
        'project_ids': [
            new_project_id
        ],
    })
make_api_request(endpoint=endpoint, method=method, data=data)


# Adding Dependency File
print(f'# Adding Dependency File to {new_project_name}...')
dependency_file_identifier = f'{new_project_name}_requirements.txt'
file_path = 'sample-requirements.txt'
endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources/dependency-file'
method = 'POST'
params = {
    'project_id': new_project_id,
    'dependency_file_identifier': dependency_file_identifier,
    'language_and_file': 'Python: requirements.txt',
    'display_name': dependency_file_identifier
}
files = {
    'file': (file_path, open(file_path, 'rb'))  # Replace with your actual file path
}
make_api_request(endpoint=endpoint, method=method, params=params, files=files) # Check for dependency file at AI Inventory > Configuration > Dependency File


# # The following Watsonx resources are disabled and therefore cannot be added to AllTrue.
# # Adding IBM Watsonx Assistant
# print(f'# Adding {watsonx_assistant_endpoint_identifier} to {new_project_name}...')
# endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources'
# method = 'POST'
# data = {
#     'resources': [
#         {
#             'display_name': None,
#             'cloud_provider_account_id': None,
#             'resource_type': 'IBMWatsonxAssistantEndpoint',
#             'resource_data': {
#                 'type': 'IBMWatsonxAssistantEndpoint',
#                 'endpoint_identifier': watsonx_assistant_endpoint_identifier,
#                 'api_key': ibm_api_key,
#                 'pentest_connection_details': {
#                     'assistant_id': '9be6f9d0-6a5c-46c2-b2d3-3d7dfde6e783',
#                     'instance_id': '17b285ef-d647-4062-b216-7efab114d43d',
#                     'pentest_api_key': ibm_api_key,
#                     'service_url': 'https://api.us-south.assistant.watson.cloud.ibm.com/',
#                     'initial_messages': ['Tell me a joke please.']
#                 }
#             },
#             'technology_types': [
#                 'ibmwatsonx-assistant'
#             ],
#             'project_ids': [
#                 new_project_id
#             ],
#             'reviewed': None
#         }
#     ],
#     'cloud_provider_account_id': None,
#     'region': None
# }
# make_api_request(endpoint=endpoint, method=method, data=data)


# # Adding IBM Watsonx Foundation Model
# print(f'# Adding {watsonx_foundation_model_endpoint_identifier} to {new_project_name}...')
# endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources'
# method = 'POST'
# data = {
#     'resources': [
#         {
#             'display_name': None,
#             'cloud_provider_account_id': None,
#             'resource_type': 'IBMWatsonxEndpoint',
#             'resource_data': {
#                 'type': 'ibm',
#                 'endpoint_identifier': watsonx_foundation_model_endpoint_identifier,
#                 'api_key': ibm_api_key,
#                 'pentest_connection_details': {
#                     'project_id': '09b2dd6b-c08d-4082-bf28-a7b24019414c',
#                     'pentest_api_key': ibm_api_key
#                 }
#             },
#             'technology_types': [
#                 'ibmwatsonx-api-key'
#             ],
#             'project_ids': [
#                 new_project_id
#             ],
#             'reviewed': None
#         }
#     ],
#     'cloud_provider_account_id': None,
#     'region': None
# }
# make_api_request(endpoint=endpoint, method=method, data=data)


# # Adding IBM WatsonX AI Service
# print(f'# Adding {watsonx_ai_service_endpoint_identifier} to {new_project_name}...')
# endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources'
# method = 'POST'
# data = {
#     'resources': [
#         {
#             'display_name': None,
#             'cloud_provider_account_id': None,
#             'resource_type': 'IBMWatsonxDeployedAIServiceEndpoint',
#             'resource_data': {
#                 'type': 'IBMWatsonxDeployedAIServiceEndpoint',
#                 'endpoint_identifier': watsonx_ai_service_endpoint_identifier,
#                 'api_key': ibm_api_key,
#                 'pentest_connection_details': {
#                     'service_url': 'https://us-south.ml.cloud.ibm.com/',
#                     'deployment_id': '674e8f98-6e37-4782-8c40-7cba4790e36a'
#                 }
#             },
#             'technology_types': [
#                 'ibmwatsonx-api-key'
#             ],
#             'project_ids': [
#                 new_project_id
#             ],
#             'reviewed': None
#         }
#     ],
#     'cloud_provider_account_id': None,
#     'region': None
# }
# make_api_request(endpoint=endpoint, method=method, data=data)


# Delete User
# Only required once training is complete or expired.
# Can be triggered immediately after training or scheduled to run periodically in the background.
if not using_backup_owner_auth0_id:
    while True:
        answer = input(f'# Are you ready to delete the {user_email}? (y/n): ').strip().lower()
        if answer == 'y':
            print(f'# Deleting {user_email}...')
            endpoint = f'https://api.demos.alltrue-be.com/v1/admin/auth0-customer/{customer_id}/users/{owner_auth0_id}'
            method = 'DELETE'
            data = {
                'customer_id': customer_id,
                'owner_auth0_id': owner_auth0_id
            }
            make_api_request(endpoint=endpoint, method=method, data=data)
            break

        print('# Waiting 1 minute before asking again...\n')
        time.sleep(60)