""" Image Baker """
import os
import sys
import argparse
import hashlib
import lzma
import gzip
import bz2
from re import search, split
from subprocess import call
from shutil import copyfileobj, copy, move
from tqdm import tqdm
from requests import get
from yaml import safe_load


def hash_file(*args):
    """Create SHA256 hash for a given file"""
    with open(*args, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    sha256_hash = sha.hexdigest()
    return sha256_hash

def load_dir(dir_path):
    """Load template directory"""
    template_list = [f'{dir_path}/{item}' for item in os.listdir(dir_path)\
                     if item.endswith('.yaml') or item.endswith('.yml') or item.endswith('.sls')]
    return template_list

def hash_images(output_path):
    """Calculate sha256sum of images and output to file"""
    image_list = [f'{output_path}/{image}' for image in os.listdir(output_path)]
    if os.path.isfile(f'{output_path}/image_hashes'):
        write_hash = open(f'{output_path}/image_hashes', 'a')
    else:
        write_hash = open(f'{output_path}/image_hashes', 'x')
    for image in image_list:
        write_hash.write(f'{image}, {hash_file(image)}\n')

def bake(template, output_path, verbose):
    BuildImage(template).download()
    BuildImage(template).convert()
    BuildImage(template).resize()
    BuildImage(template).build_method(verbose)
    BuildImage(template).compress()
    BuildImage(template).store_image(output_path)


class BuildImage:
    def __init__(self, template):
        self.template = template
        with open(self.template, 'r') as fd:
            template_data = safe_load(fd)
        self.image_name = template_data.get("image_name")
        self.image_size = template_data.get("image_size")
        self.image_url = template_data.get("image_url")
        self.method = template_data.get("method")
        self.customization = template_data.get("customization")
        self.input_format = template_data.get("input_format")
        self.output_format = template_data.get("output_format")
        self.downloadimage_size = template_data.get("image_size")
        self.conversion = template_data.get("conversion")
        self.compression = template_data.get("compression")
        self.packages = template_data.get("packages")
        if self.packages:
            self.packages = ",".join(self.packages)
        self.output_name = f'{self.image_name}.{self.output_format}'

    def download(self):
        if self.image_url is None:
            pass
        else:
            file = self.image_url.split('/')[-1]
            file_request = get(self.image_url, stream=True, allow_redirects=True)
            total_size = int(file_request.headers.get('content-length'))
            initial_pos = 0
            print(f'\nDownloading image from ({self.image_url}):')
            with open(file, 'wb') as file_download:
                with tqdm(total=total_size, unit='it', unit_scale=True,
                          desc=file, initial=initial_pos,
                          ascii=True) as progress_bar:
                    for chunk in file_request.iter_content(chunk_size=1024):
                        if chunk:
                            file_download.write(chunk)
                            progress_bar.update(len(chunk))
            os.rename(file, self.image_name)
            print(f'\nImage download finished.\n')
            print(f'{self.image_name}\nSHA256 Hash: {hash_file(self.image_name)}')

    def convert(self):
        if self.convert is None:
            pass
        elif self.convert and self.method == 'virt-customize':
            """Perform qemu image conversion for format type specified"""
            print(f'\nConverting {self.image_name} to {self.output_format}\
                  format with qemu-img utility...')
            call(f'qemu-img convert -f {self.input_format} -O {self.output_format}\
                 {self.image_name} {self.output_name}', shell=True)
            os.rename(f'{self.output_name}', f'{self.image_name}')
        else:
            pass

    def resize(self):
        print(self.image_size)
        print(self.method)
        if self.image_size is None:
            pass
        elif self.image_size and self.method == 'virt-customize':
            """Resize image partition to specification in template file"""
            new_image = f'{self.image_name}_new'
            if search('G', self.image_size):
                image_size_b = int(split('G', self.image_size)[0]) * (1024**3)
            if search('M', self.image_size):
                image_size_b = int(split('M', self.image_size)[0]) * (1024**2)
            with open(new_image, 'wb') as fh:
                os.truncate(new_image, image_size_b)
            call(f'virt-resize --expand /dev/sda1 {self.image_name} {new_image}', shell=True)
            copy(new_image, self.image_name)
            os.remove(new_image)
            print('\nImage finished resizing using virt-resize\n')
            print(f'{self.image_name}\nSHA256 Hash: {hash_file(self.image_name)}')
        else:
            pass

    def build_method(self, verbose):
        """Determine build method and execute build"""
        create_script = open('user_script.sh', 'w')
        create_script.write(self.customization)
        create_script.close()

        if self.method == 'virt-customize' and verbose:
            print(f'\n{self.image_name} image is being created with virt-customize in VERBOSE mode')
            if self.packages:
                call(f'virt-customize -v -x -a {self.image_name} -update\
                     --install {self.packages} --run user_script.sh', shell=True)
            else:
                call(f'virt-customize -v -x -a {self.image_name} -update\
                     --run user_script.sh', shell=True)
        elif self.method == 'virt-builder' and verbose:
            print(f'\n{self.image_name} image is being created with virt-builder in VERBOSE mode')
            if self.packages:
                call(f'virt-builder -v -x {self.image_name} --update --run user_script.sh\
                     --format {self.output_format} --output {self.output_name}', shell=True)
            else:
                call(f'virt-builder -v -x {self.image_name} --update --install {self.packages}\
                      --run user_script.sh --format {self.output_format}\
                      --output {self.output_name}', shell=True)
            os.rename(f'{self.output_name}', f'{self.image_name}')
        elif self.method == 'virt-customize' and verbose is False:
            print(f'\n{self.image_name} image is being created with virt-customize')
            if self.packages:
                call(f'virt-customize -a {self.image_name} -update --install {self.packages}\
                      --run user_script.sh', shell=True)
            else:
                call(f'virt-customize -a {self.image_name} -update\
                     --run user_script.sh', shell=True)
        elif self.method == 'virt-builder' and verbose is False:
            print(f'\n{self.image_name} image is being created with virt-builder')
            if self.packages:
                call(f'virt-builder {self.image_name} --update --run user_script.sh\
                    --format {self.output_format} --output {self.output_name}', shell=True)
            else:
                call(f'virt-builder {self.image_name} --update --install {self.packages}\
                     --run user_script.sh --format {self.output_format}\
                     --output {self.output_name}', shell=True)
            os.rename(f'{self.output_name}', f'{self.image_name}')
        os.remove('user_script.sh')

    def compress(self):
        """Compress image to specification in template file (gz, bz2, xz)"""
        if self.compression is None:
            pass
        else:
            print(f'\nCompressing image using {self.compression} method....')
            if self.compression == "gz":
                with open(self.image_name, 'rb') as file_in, \
                    gzip.open(f'{self.image_name}.{self.compression}', 'wb') as file_out:
                    copyfileobj(file_in, file_out)
            elif self.compression == "bz2":
                with open(self.image_name, 'rb') as file_in, \
                    bz2.open(f'{self.image_name}.{self.compression}', 'wb') as file_out:
                    copyfileobj(file_in, file_out)
            else:
                with open(self.image_name, 'rb') as file_in, \
                    lzma.open(f'{self.image_name}.lzma', 'wb') as file_out:
                    copyfileobj(file_in, file_out)

    def store_image(self, output_path):
        """Create directory for image storage"""
        if not os.path.exists(f'{output_path}'):
            os.makedirs(f'{output_path}')
        move(f'{self.image_name}', f'{output_path}'f'/{self.image_name}')
        print(f'\nImage \'{self.image_name}\' stored at \'{output_path}\'')


def main():
    """CLI Parsing"""
    parser = argparse.ArgumentParser(prog='image_baker', description='Start baking an image.')
    parser.add_argument('-v', '--verbose', action='store_true',\
                        help='Verbose mode for troubleshooting image build')
    parser.add_argument('-t', '--template', action='store',\
                        help='Specifies template yaml file to build.')
    parser.add_argument('-d', '--dir_path', action='store', metavar=('./some/directory/'),\
                        help='Directory path for multiple template yaml files')
    parser.add_argument('-o', '--output_path', action='store', metavar=('./some/directory/'),\
                        help='Directory path to store image output', required=True)
    num_args = len(sys.argv)
    args = parser.parse_args()

    #Error Handling
    if num_args < 2:
        sys.stderr.write('ERROR: No options were present, refer to help (--help) if needed.\n')
    if args.template is None and args.dir_path is None and num_args > 2:
        sys.stderr.write('ERROR: Specify a directory path or template file.\
                         Refer to help (--help) if needed.\n')
    if args.output_path is None:
        sys.stderr.write('ERROR: Specify a directory path for image output.\
                         Refer to help (--help) if needed.\n')

    #Build using single template
    if args.template:
        bake(args.template, args.output_path, args.verbose)
    #Build using a template directory
    if args.dir_path:
        for template in load_dir(args.dir_path):
            bake(template, args.output_path, args.verbose)
    hash_images(args.output_path)

if __name__ == '__main__':
    sys.exit(main())
