from pathlib import Path

import requests


class FHIRClient:
    """HTTP client for FHIR R5 server interactions."""

    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/fhir+json'
        if auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'

    def get_resource(self, reference):
        """Fetch a FHIR resource by reference."""
        url = f"{self.base_url}/{reference}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_document_reference(self, reference):
        """Fetch a DocumentReference and extract file info."""
        doc_ref = self.get_resource(reference)
        result = {
            'id': doc_ref.get('id'),
            'title': doc_ref.get('description') or doc_ref.get('id'),
            'file_url': None,
            'content_type': None
        }
        content = doc_ref.get('content', [])
        if content:
            attachment = content[0].get('attachment', {})
            result['file_url'] = attachment.get('url')
            result['content_type'] = attachment.get('contentType')
        return result

    def download_file(self, file_url, output_dir, filename=None):
        """Download a file from URL to the specified directory."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        if not filename:
            filename = file_url.split('/')[-1].split('?')[0]
        output_path = output_dir / filename
        response = self.session.get(file_url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path

    def get_patient(self, reference):
        """Fetch a Patient resource and extract key fields."""
        patient = self.get_resource(reference)
        name = ""
        if patient.get('name'):
            name_obj = patient['name'][0]
            given = ' '.join(name_obj.get('given', []))
            family = name_obj.get('family', '')
            name = f"{given} {family}".strip()
        return {
            'id': patient.get('id'),
            'name': name,
            'birthDate': patient.get('birthDate'),
            'gender': patient.get('gender'),
            'identifier': [
                {'system': i.get('system'), 'value': i.get('value')}
                for i in patient.get('identifier', [])
            ]
        }
