import json

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        # Use eval to parse the dictionary data
        return eval(data)

def list_fields_and_data(data):
    fields_and_data = []

    def extract_fields_and_data(data, prefix=''):
        if isinstance(data, dict):
            for key, value in data.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    extract_fields_and_data(value, new_prefix)
                else:
                    fields_and_data.append((new_prefix, value))
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_prefix = f"{prefix}[{index}]"
                if isinstance(item, (dict, list)):
                    extract_fields_and_data(item, new_prefix)
                else:
                    fields_and_data.append((new_prefix, item))

    extract_fields_and_data(data)
    return fields_and_data

# Load data from files
dir_start = './sample_data/'
file_paths = ['file_01.txt', 'file_02.txt', 'file_03.txt']
for file_path in file_paths:
    data = load_data(dir_start + file_path)
    fields_and_data = list_fields_and_data(data)
    print(f"Fields and Data for {file_path}:")
    for field, value in fields_and_data:
        print(f"{field}: {value}")
    print("\n")

"""
# Data Extractor

Extracts and lists all fields and their respective data from a nested dictionary 
or list structure stored in text files.

Reads data from text files, processes it to extract fields and their associated data, 
and then lists them in a structured format. It handles nested dictionaries and lists, 
ensuring all data points are captured with their full field paths.

# Sample out:
Fields and Data for file_01.txt:
metadata.name: {{input_LB-Name}}
metadata.namespace: {{input_namespace}}
metadata.disable: False
spec.domains[0]: {{input_FQDN}}
spec.https.http_redirect: True
spec.https.add_hsts: False
spec.https.port: 443
spec.https.connection_idle_timeout: 120000
spec.https.tls_cert_params.certificates[0].tenant: p-X
spec.https.tls_cert_params.certificates[0].namespace: {{input_namespace}}
spec.https.tls_cert_params.certificates[0].name: {{input_certificate_name}}
spec.https.tls_cert_params.certificates[0].kind: certificate
spec.default_route_pools[0].pool.tenant: p-X
spec.default_route_pools[0].pool.namespace: {{input_namespace}}
spec.default_route_pools[0].pool.name: {{input_backend_origin_pool_name}}
spec.default_route_pools[0].pool.kind: origin_pool
spec.default_route_pools[0].weight: 1
spec.default_route_pools[0].priority: 1
spec.routes[0].simple_route.http_method: ANY
spec.routes[0].simple_route.path.prefix: /
spec.routes[0].simple_route.headers[0].name: X-Content-Label
spec.routes[0].simple_route.headers[0].presence: True
spec.routes[0].simple_route.headers[0].invert_match: False
spec.routes[0].simple_route.origin_pools[0].pool.tenant: p-X
spec.routes[0].simple_route.origin_pools[0].pool.namespace: {{input_namespace}}
spec.routes[0].simple_route.origin_pools[0].pool.name: {{input_backend_origin_pool_name}}
spec.routes[0].simple_route.origin_pools[0].pool.kind: origin_pool
spec.routes[0].simple_route.origin_pools[0].weight: 1
spec.routes[0].simple_route.origin_pools[0].priority: 1
spec.routes[0].simple_route.advanced_options.priority: DEFAULT
spec.routes[0].simple_route.advanced_options.request_headers_to_remove[0]: X-Content-Label
spec.routes[0].simple_route.advanced_options.disable_location_add: False
spec.routes[0].simple_route.advanced_options.timeout: 30000
spec.routes[1].simple_route.http_method: {{input_request_method}}
spec.routes[1].simple_route.path.regex: (?i).*{{input_endpoint_path}}.*
spec.routes[1].simple_route.origin_pools[0].pool.tenant: p-X
spec.routes[1].simple_route.origin_pools[0].pool.namespace: {{input_namespace}}
spec.routes[1].simple_route.origin_pools[0].pool.name: botdefense-mobile-pre-prod
spec.routes[1].simple_route.origin_pools[0].pool.kind: origin_pool
spec.routes[1].simple_route.origin_pools[0].weight: 1
spec.routes[1].simple_route.origin_pools[0].priority: 1
spec.routes[1].simple_route.origin_pools[1].pool.tenant: p-X
spec.routes[1].simple_route.origin_pools[1].pool.namespace: {{input_namespace}}
spec.routes[1].simple_route.origin_pools[1].pool.name: {{input_backen_origin_pool_name}}
spec.routes[1].simple_route.origin_pools[1].pool.kind: origin_pool
spec.routes[1].simple_route.origin_pools[1].weight: 1
spec.routes[1].simple_route.origin_pools[1].priority: 0
spec.app_firewall.tenant: p-X
spec.app_firewall.namespace: shared
spec.app_firewall.name: app-firewall-monitoring-01
spec.app_firewall.kind: app_firewall
spec.add_location: True
spec.active_service_policies.policies[0].tenant: p-X
spec.active_service_policies.policies[0].namespace: shared
spec.active_service_policies.policies[0].name: p-X-bot-defense-restriction
spec.active_service_policies.policies[0].kind: service_policy
spec.active_service_policies.policies[1].tenant: v-io
spec.active_service_policies.policies[1].namespace: shared
spec.active_service_policies.policies[1].name: v-io-allow-all
spec.active_service_policies.policies[1].kind: service_policy


Fields and Data for file_02.txt:
pools[0].pool.node: v-b1
pools[0].pool.namespace: j-site
pools[0].pool.name: node-prod
pools[0].weight: 1
pools[0].priority: 1
pools[0].endpoint_subsets.part: 55
pools[1].pool.node: v-b2
pools[1].pool.namespace: x-site
pools[1].pool.name: v0-QA
pools[1].weight: 1
pools[1].priority: 0


Fields and Data for file_03.txt:
urls.path.regex: (?i).*example.*


"""