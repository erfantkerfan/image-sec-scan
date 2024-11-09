import subprocess
from datetime import datetime
import logging
import argparse
from pathlib import Path
import os
import re
from functools import lru_cache


@lru_cache
def sanitize_docker_image_name(image_name: str):
    parts = image_name.split(':')
    if len(parts) > 2 or image_name.isspace() or image_name == '':
        logging.error(f"Found unsupported string: {image_name}")
        return False
    elif len(parts) == 1:
        logging.warning(f"Found image without tag, using latest: {image_name}")
        image_name = image_name + ':latest'
    sanitized = re.sub(r'\s+', '', image_name)
    sanitized = re.sub(r'[^\w\-\.]', '_', sanitized)
    return sanitized.strip('_')


def load_grype_db():
    logging.info('Loading grype DB')
    try:
        result = subprocess.run(
            ['grype', 'db', 'update'],
            env=os.environ,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)
        logging.info("Grype database updated successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to update Grype database. Exit code: {e.returncode}")
        logging.error(f"Error message: {e.stderr}")
        exit(1)


def remove_image(image_name: str):
    try:
        result = subprocess.run(
            ['docker', 'rmi', f'{image_name}'],
            env=os.environ,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)
        logging.info(f"Image removal successful: {image_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Image removal unsuccessful: {e.returncode}")
        logging.error(f"Error message: {e.stderr}")


def main(input_file: str, output_path: str, template_file: str):
    formated_date = datetime.now().strftime('%Y-%m-%d')
    path_tool = Path(f'{output_path}/{formated_date}/')
    path_tool.mkdir(exist_ok=True)

    with open(input_file, 'r') as file:
        for line in file:
            image = line.strip()
            logging.info(f"Processing image: {image}")
            try:
                if sanitize_docker_image_name(image):
                    result = subprocess.run(
                        ['grype', "--by-cve", "--output", "template", "-t", template_file, image],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    with open(f'{output_path}/{formated_date}/{sanitize_docker_image_name(image)}.html', 'w') as output_file:
                        output_file.write(result.stdout)
                    logging.info(f"Successfully processed image: {image}")
                    remove_image(image)
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to process image {image}: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # parsing input arguments
    parser = argparse.ArgumentParser(description='A wrapper for grype to generate html based output')
    parser.add_argument('-i', '--input', help='input to load image names', default='/mnt/reports/images.txt', type=str)
    parser.add_argument('-o', '--output', help='ou  tput dir to put reports', default='/mnt/reports/', type=str)
    parser.add_argument('-t', '--template', help='template to use with grype', default='/mnt/reports/html.tmpl', type=str)
    parser.add_argument('-v', '--verbose', help='run in verbose mode', default=False, action='store_true')
    args = parser.parse_args()

    load_grype_db()
    main(args.input, args.output, args.template)
