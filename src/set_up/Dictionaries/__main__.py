import sys
import argparse
from .load_n4j_dictionary import load_dictionary
from .taxonomy_translations import create_translation_files, upload_translations
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up the taxonomy dictionaries.')
    parser.add_argument("-a", "--action", help="what action to perform", required=True,
                        choices=['load', 'create', 'translate', 'load_translate'])
    args = parser.parse_args()
    if args.action == "load":
        load_dictionary()
    elif args.action == "create":
        create_translation_files()
    elif args.action == "translate":
        upload_translations()
    elif args.action == "load_translate":
        load_dictionary()
        upload_translations()
