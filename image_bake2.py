import os
import sys
import argparse
import time
import hashlib
from tqdm import tqdm
from requests import get
from yaml import safe_load
from subprocess import call


def load_yaml(template):
    with open(template, 'r') as fd:
        template_data = safe_load(fd)
    return template_data

def parse_template(loaded_template):
    global image_name, image_url, method, image_url, compression, input_format, output_format, compressed, convert, packages, customization, image_size
    image_name = loaded_template.get("image_name")
    method = loaded_template.get("method")
    image_url = loaded_template.get("image_url")
    compression = loaded_template.get("compression")
    input_format = loaded_template.get("input_format")
    output_format = loaded_template.get("output_format")
    compressed = loaded_template.get("compressed")
    convert = loaded_template.get("convert")
    packages = loaded_template.get("packages")
    customization = loaded_template.get("customization")
    image_size = loaded_template.get("image_size")

def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))

def download_image(image_url):
    # Downloads image from url passed from download_url() if available
    file = image_url.split('/')[-1]
    file_request = get(image_url, stream=True, allow_redirects=True)
    total_size = int(file_request.headers.get('content-length'))
    initial_pos = 0

    print(f'\nDownloading image from ({image_url}):')
    with open(file, 'wb') as file_download:
        with tqdm(total=total_size, unit='it', unit_scale=True,
                    desc=file, initial=initial_pos,
                    ascii=True) as progress_bar:
            for chunk in file_request.iter_content(chunk_size=1024):
                if chunk:
                    file_download.write(chunk)
                    progress_bar.update(len(chunk))
    os.rename(file, image_name)

def qemu_convert(image_name, input_format, output_format):
    # Perform qemu image conversion for format type specified
    if method == 'virt-customize':
        print(f'\nConverting {image_name} to {output_format} format with qemu-img utility...')
        call(f'qemu-img convert -f {input_format} -O {output_format} {image_name} {image_name}.{output_format}', shell=True)
        os.remove(image_name)

def main():
    parser = argparse.ArgumentParser(prog='image_baker', description='Start baking an image.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode for troubleshooting image build')
    parser.add_argument('-a', '--all', default='NONE', action='store_true', help='Runs image baker on all template files in the specified directory')
    parser.add_argument('-T', '--type', default='NONE', action='store', choices=['vm', 'docker'], help='Specifies the type of image to build', )
    parser.add_argument('-t', '--template', default='NONE', action='store', help='Specifies template yaml file to build.')
    parser.add_argument('-d', '--dir_path', default='NONE', action='store', metavar=('./some/directory/'), help='Directory path for multiple template yaml files')
    parser.add_argument('-f', '--format', nargs=2, action='store', metavar=('input_format', 'output_format'), help='specifies the input and output format for image conversion')
    parser.add_argument('-o', '--output_name', action='store', help='Specifies the output file name for the image.')
    parser.add_argument('-r', '--resize', action='store', help='Specifies the the output image size')
    parser.add_argument('-b', '--builder', default='virt-customize', action='store', choices=['virt-customize', 'virt-builder'], help='Specifies the builder to use.')
    parser.add_argument('-c', '--compress', default='NONE', action='store', choices=['gz', 'bz2', 'lzma'], help='Specifies compression and type')
    parser.add_argument('-p', '--packages', action='store', help='Packages to install on the image')

    num_args = len(sys.argv)

    args = parser.parse_args()

    if num_args < 2:
        sys.stderr.write('ERROR: No options were present, refer to help (--help) if needed.\n')
    
    if args.all == 'NONE' and args.template == 'NONE' and args.dir_path == 'NONE' and num_args > 2:
        sys.stderr.write('ERROR: Specify a directory path, template file, or all. Refer to help (--help) if needed.\n')

    if args.dir_path != 'NONE' and args.all:
        #Bake images for all templates in a given dir path
        template_list = []
        templates = os.listdir(args.dir_path)
        for item in templates:
            if item.endswith('.yaml') or item.endswith('.yml'):
                item = f'{args.dir_path}{item}'
                template_list.append(item) 
        for template in template_list:
            loaded_template = load_yaml(template)
            parse_template(loaded_template)
            download_image(image_url)
            hash_image(image_name)
            if convert is True and method == 'virt-customize':
                qemu_convert(image_name, input_format, output_format)


'''
break point, kwargs needs to be implemented for parsing through the templates loaded by load_yaml.
'''
        
    # if args.template != 'NONE':
    #     #Bake images for a specifc yaml template
    #     template = args.template
    #     print(load_yaml(template))
    #     print(type(template))




            # YamlParse.load_yaml(dir_path, template)
            # print(template_data)
        
        # with os.scandir(args.dir_path) as templates:
        #     for template in templates:
        #         print(template)
                # print(templates)
                # image_template = load_yaml(template)
            # print(image_template)


    # args = parser.parse_args()

    # template_name = args.template

    # if args.template == 'NONE' and not args.dir_path:
    #     sys.stderr.write(f'Missing template name or directory:\n {args.template}')
    #     parser.usage()
    #     sys.exit(1)
    
    # if template_name not in dirs:
    #     sys.stderr.write(f'ERROR: Image named {template_name} not found.')
    #     sys.stderr.write('Make sure you spelled the template name correctly.')
    #     sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
