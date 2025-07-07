import json
import time
import requests


# Change the following variables to suit the user
first_name = 'first_name'  # Please change me
last_name = 'last_name'  # Please change me
user_password = 'csF7MNZsjVrvn9Mx4WxN'  # Please change me
full_name = username = f'{first_name} {last_name}'
user_id = f'{full_name} {time.time()}'
user_email = 'syfipy@forexzig.com'  # Replace with user's email or a random email from https://tempmailo.com/ for dev/testing

# Leave the following variables unchanged please
auth0_id = 'auth0|68235f5459f6c9965c15aad1'  # To be populated after user creation
alltrue_api_key = '2leJcrFlSPTwJCeHYNCveVocV6Z0tsva'  # API key given auditor, security analyst, and custom IBM training roles
customer_id = '42072582-95f4-46ef-be06-bb7aa2cdcff8'  # IBM Demos default customer ID
project_id = 'b0fd57c4-6941-4583-a805-dbc8a2502d59' # z_IBM_Enablement > IBM_Enablement


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


# Creating user
print('# Creating user...')
endpoint = f'https://api.demos.alltrue-be.com/v1/admin/auth0-customer/{customer_id}/users'
method = 'POST'
data = {
    'user': {
        'name': full_name,
        'user_id': user_id,
        'given_name': first_name,
        'family_name': last_name,
        'email': user_email,  # Temporary email addresses available at https://adguard.com/en/adguard-temp-mail/overview.html
        'password': user_password,
        'connection': 'Username-Password-Authentication',  # Do not change this please
  },
  'roles': [
      '5625e45c-8f5e-414e-ad8f-093864e58c2e',  # Limited User
      'b6fde60f-a767-45b6-85d9-c94cccfd9ae8',  # Security Analyst
      '679e4f70-54b1-4936-a5ca-c341c65714ba'   # IBM_Training
  ]
}
response = make_api_request(endpoint=endpoint, method=method, data=data)
if 'already exists' in str(response):
    print('# User already exists')
else:
    auth0_id = response['user']['user_id']


if auth0_id:
    print(f'# Assigning user {auth0_id} to project {project_id}')
    endpoint = f'https://api.demos.alltrue-be.com/v1/admin/customers/{customer_id}/users/{auth0_id}/projects'
    method = 'POST'
    data = {
        'projects': [
            {
                'project_id': 'b0fd57c4-6941-4583-a805-dbc8a2502d59'  # z_IBM_Enablement > IBM_Enablement
            }
        ]
    }
    make_api_request(endpoint=endpoint, method=method, data=data)


# Adding Hugging Face Model
print(f'# Adding Hugging face Models to project {project_id}...')
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
            project_id
        ],
    })
make_api_request(endpoint=endpoint, method=method, data=data)


# Adding Python Library
print(f'# Adding Python Libraries to project {project_id}...')
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
            project_id
        ],
    })
make_api_request(endpoint=endpoint, method=method, data=data)


# Adding Dependency File
print(f'# Adding Dependency File...')
dependency_file_identifier = f'{full_name}_requirements.txt'
file_path = 'sample-requirements.txt'
endpoint = f'https://api.demos.alltrue-be.com/v1/inventory/customer/{customer_id}/resources/dependency-file'
method = 'POST'
params = {
    'project_id': project_id,
    'dependency_file_identifier': dependency_file_identifier,
    'language_and_file': 'Python: requirements.txt',
    'display_name': dependency_file_identifier
}
files = {
    'file': (file_path, open(file_path, 'rb'))  # Replace with your actual file path
}
make_api_request(endpoint=endpoint, method=method, params=params, files=files) # Check for dependency file at AI Inventory > Configuration > Dependency File


# Fetch all users to find the Auth0 ID needed for user deletion
if input('Delete newly created user? (y/n): ') == 'y':
    print(f'# Getting all users...')
    endpoint = f'https://api.demos.alltrue-be.com/v1/admin/auth0-customer/{customer_id}/users'
    method = 'GET'
    data = {
        'customer_id': customer_id,
    }
    for user in make_api_request(endpoint, method=method, data=data):
        if user['email'] == user_email:
            print(f'# Found user {user_email} in {customer_id}...\n')
            auth0_id = user['user_id']
            # Delete User
            # Only required once training is complete or expired.
            # Can be triggered immediately after training or scheduled to run periodically in the background.
            print(f'# Deleting user {auth0_id}...')
            endpoint = f'https://api.demos.alltrue-be.com/v1/admin/auth0-customer/{customer_id}/users/{auth0_id}'
            method = 'DELETE'
            data = {
                'customer_id': customer_id,
                'owner_auth0_id': auth0_id
            }
            make_api_request(endpoint=endpoint, method=method, data=data)
