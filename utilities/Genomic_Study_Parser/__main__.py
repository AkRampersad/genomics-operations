import argparse
import json
import sys

from .parser import GenomicStudyParser
from .pipeline import GenomicStudyPipeline


def main():
    parser = argparse.ArgumentParser(
        description='Parse FHIR R5 GenomicStudy resources'
    )
    parser.add_argument('input_file', help='Path to GenomicStudy JSON file')
    parser.add_argument('--fhir-url',
                        help='FHIR server base URL (required unless --dry-run)')
    parser.add_argument('--token', help='Bearer token for authentication')
    parser.add_argument('--output-dir',
                        default='./downloads', help='Download directory')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--pretty',
                        action='store_true', help='Pretty print output')
    parser.add_argument('--dry-run',
                        action='store_true', help='Parse only, no downloads')

    args = parser.parse_args()

    if not args.dry_run and not args.fhir_url:
        parser.error('--fhir-url is required unless --dry-run is specified')

    try:
        if args.dry_run:
            result = GenomicStudyParser(args.input_file).parse()
        else:
            pipeline = GenomicStudyPipeline(
                args.fhir_url,
                auth_token=args.token,
                output_dir=args.output_dir
            )
            processed = pipeline.process(args.input_file)
            result = pipeline.to_mongo_documents(processed)

    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    indent = 2 if args.pretty else None
    output = json.dumps(result, indent=indent)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
