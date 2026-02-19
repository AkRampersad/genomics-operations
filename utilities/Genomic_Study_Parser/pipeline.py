from pathlib import Path
from .parser import GenomicStudyParser
from .fhir_client import FHIRClient


class GenomicStudyPipeline:
    """Orchestrates parsing, fetching, and downloading of GenomicStudy data."""

    def __init__(self,
                 fhir_base_url,
                 auth_token=None,
                 output_dir='./downloads'):
        self.fhir_client = FHIRClient(fhir_base_url, auth_token)
        self.output_dir = Path(output_dir)

    def process(self, genomic_study_path):
        """Parse GenomicStudy, fetch resources, and download files."""
        parsed = GenomicStudyParser(genomic_study_path).parse()

        result = {
            'patient': None,
            'analyses': [],
            'downloaded_files': []
        }

        # Fetch patient info from first analysis
        if parsed['analyses']:
            patient_ref = parsed['analyses'][0]['patientID']
            if patient_ref:
                try:
                    patient = self.fhir_client.get_patient(patient_ref)
                    result['patient'] = patient
                except Exception as e:
                    result['patient'] = {'error': str(e),
                                         'reference': patient_ref}

        # Process each analysis
        for analysis in parsed['analyses']:
            analysis_result = {
                'metadata': analysis,
                'vcf_files': []
            }

            # Fetch and download VCF files
            for vcf_ref in analysis.get('vcfFiles', []):
                try:
                    doc_info = self.fhir_client.get_document_reference(vcf_ref)
                    local_path = None
                    if doc_info['file_url']:
                        local_path = self.fhir_client.download_file(
                            doc_info['file_url'],
                            self.output_dir / analysis['analysisID']
                        )
                    analysis_result['vcf_files'].append({
                        'reference': vcf_ref,
                        'doc_info': doc_info,
                        'local_path': str(local_path) if local_path else None
                    })
                    if local_path:
                        result['downloaded_files'].append(str(local_path))
                except Exception as e:
                    analysis_result['vcf_files'].append({
                        'reference': vcf_ref,
                        'error': str(e)
                    })

            result['analyses'].append(analysis_result)

        return result

    def to_mongo_documents(self, processed_result):
        """Convert processed result to MongoDB-ready documents."""
        mongo_docs = {
            'patient': processed_result.get('patient'),
            'analyses': []
        }

        for analysis in processed_result['analyses']:
            meta = analysis['metadata']
            patient_id = (
                meta['patientID'].split('/')[-1] if meta['patientID'] else None
            )
            specimen_ids = [
                s.split('/')[-1] for s in meta.get('specimenID', [])
            ]
            studied_regions = [
                r.split('/')[-1] for r in meta.get('studiedRegion', [])
            ]
            mongo_analysis = {
                'patientID': patient_id,
                'analysisID': meta['analysisID'],
                'analysisDate': meta['analysisDate'],
                'specimenID': specimen_ids,
                'genomicBuild': meta['genomicBuild'],
                'studiedRegion': studied_regions,
                'dnaChangeType': meta.get('dnaChangeType', []),
                'vcfFiles': [
                    {
                        'documentReference': f['reference'].split('/')[-1],
                        'localPath': f.get('local_path'),
                        'contentType': f.get('doc_info', {}).get(
                            'content_type'
                        )
                    }
                    for f in analysis['vcf_files']
                    if 'error' not in f
                ]
            }
            mongo_docs['analyses'].append(mongo_analysis)

        return mongo_docs
