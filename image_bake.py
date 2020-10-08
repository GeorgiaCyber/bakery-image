#! /usr/bin/env python3

import os, sys, argparse, time, hashlib, lzma, gzip, bz2
from tqdm import tqdm
from requests import get
from yaml import safe_load
from subprocess import call
from re import search, split
from shutil import copyfileobj, copy, move


def load_yaml(template):
    """Load template and associate key words with variables globally"""
    with open(template, 'r') as fd:
        template_data = safe_load(fd)
    global image_name, image_url, method, image_url, compression, input_format, output_format, compressed, conversion, packages, customization, image_size, output_name
    image_name = template_data.get("image_name")
    method = template_data.get("method")
    image_url = template_data.get("image_url")
    compression = template_data.get("compression")
    input_format = template_data.get("input_format")
    output_format = template_data.get("output_format")
    compressed = template_data.get("compressed")
    conversion = template_data.get("conversion")
    packages = template_data.get("packages")
    customization = template_data.get("customization")
    image_size = template_data.get("image_size")
    output_name = f'{image_name}.{output_format}'

def hash_file(*args):
    """Create SHA256 hash for a given file"""
    with open(*args, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    sha256_hash = sha.hexdigest()
    return sha256_hash
    # print(f'{image_name},  SHA256 Hash: {sha256_hash}')

def build(verbose, output_path):
    if image_url is not None:
        ImageTransfer().download_image(image_name, image_url)
    if conversion is True:
        BuildImage().convert(input_format, output_format, image_name, output_name)
    if image_size is not None:
        BuildImage().resize(image_size, image_name)
    if verbose is True:
        BuildImage().build_method_v(packages, method, image_name, customization)
    elif verbose is False:
        BuildImage().build_method(packages, method, output_name, customization)
    if compression is not None:
        BuildImage().compress(compression, output_name)
    if output_path is not None:
        ImageTransfer().store_image(image_name, output_path)

class ImageTransfer:
    def __init__(self, *args):
        self.image_name = image_name
        self.image_url = image_url

    def download_image(self, image_name, image_url):
        """Download image from url"""
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

    def store_image(self, image_name, output_path):
        """Create directory for image storage"""
        if not os.path.exists(f'{output_path}'):
            os.makedirs(f'{output_path}')
        move(f'{self.image_name}', f'{output_path}'f'/{self.image_name}')
        print(f'\nImage \'{self.image_name}\' stored at \'{output_path}\'')


    '''Placeholder for upload functions (glance, amazon s3, minio, dockerhub, etc.'''
    # def upload_glance(self):


class BuildImage:
    def __init__(self, *args):
        self.image_name = image_name
        self.output_name = output_name
        self.method = method
        self.input_format = input_format
        self.output_format = output_format
        self.image_size = image_size
        self.conversion = conversion
        self.compression = compression
        self.packages = packages
        if self.packages is not None:
            self.packages = ",".join(self.packages)
        self.customization = customization

    def create_user_script(self, customization):
        """Create custom user script file"""
        create_script = open('user_script.sh', 'w')
        create_script.write(self.customization)
        create_script.close()

    def convert(self, input_format, output_format, image_name, output_name):
        """Perform qemu image conversion for format type specified"""
        print(f'\nConverting {self.image_name} to {self.output_format} format with qemu-img utility...')
        call(f'qemu-img convert -f {self.input_format} -O {self.output_format} {self.image_name} {self.output_name}', shell=True)
        os.rename(f'{self.output_name}',f'{self.image_name}')

    def resize(self, image_name, image_size):
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
        print(f'\nImage finished resizing using virt-resize\n')
        print(f'{self.image_name}\nSHA256 Hash: {hash_file(self.image_name)}')

    def build_method(self, packages, method, image_name, customization):
        """Determine build method and execute build"""
        BuildImage().create_user_script(self.customization)
        if self.method == 'virt-customize':
            print(f'\n{self.image_name} image is being created with virt-customize')
            if self.packages is not None:
                call(f'virt-customize -a {self.image_name} -update --install {self.packages} --run user_script.sh', shell=True)
            else:
                call(f'virt-customize -a {self.image_name} -update --run user_script.sh', shell=True)
        else:
            print(f'\n{self.image_name} image is being created with virt-builder')
            if self.packages is not None:
                call(f'virt-builder {self.image_name} --update --run user_script.sh\
                    --format {self.output_format} --output {self.output_name}', shell=True)
            else:
                call(f'virt-builder {self.image_name} --update --install {self.packages} --run user_script.sh\
                    --format {self.output_format} --output {self.output_name}', shell=True)
            os.rename(f'{self.output_name}',f'{self.image_name}')
        os.remove('user_script.sh')

    def build_method_v(self, packages, method, image_name, customization):
        """Determine build method and execute build in verbose mode"""
        BuildImage().create_user_script(self.customization)
        if self.method == 'virt-customize':
            print(f'\n{self.image_name} image is being created with virt-customize in VERBOSE mode')
            if self.packages is not None:
                call(f'virt-customize -v -x -a {self.image_name} -update --install {self.packages} --run user_script.sh', shell=True)
            else:
                call(f'virt-customize -v -x -a {self.image_name} -update --run user_script.sh', shell=True)
        else:
            print(f'\n{self.image_name} image is being created with virt-builder in VERBOSE mode')
            if self.packages is not None:
                call(f'virt-builder -v -x {self.image_name} --update --run user_script.sh\
                    --format {self.output_format} --output {self.output_name}', shell=True)
            else:
                call(f'virt-builder -v -x {self.image_name} --update --install {self.packages} --run user_script.sh\
                    --format {self.output_format} --output {self.output_name}', shell=True)
            # os.remove(self.image_name)
            os.rename(f'{self.output_name}',f'{self.image_name}')
        os.remove('user_script.sh')

    def compress(self, compression, image_name):
        """Compress image to specification in template file (gz, bz2, xz)"""
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


def main():
    """CLI Parsing"""
    parser = argparse.ArgumentParser(prog='image_baker', description='Start baking an image.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode for troubleshooting image build')
    parser.add_argument('-t', '--template', action='store', help='Specifies template yaml file to build.')
    parser.add_argument('-d', '--dir_path', action='store', metavar=('./some/directory/'), help='Directory path for multiple template yaml files')
    parser.add_argument('-o', '--output_path', action='store', metavar=('./some/directory/'), help='Directory path to store image output')
    num_args = len(sys.argv)
    args = parser.parse_args()

    """Error Handling"""
    if num_args < 2:
        sys.stderr.write('ERROR: No options were present, refer to help (--help) if needed.\n')
    if args.template is None and args.dir_path is None and num_args > 2:
        sys.stderr.write('ERROR: Specify a directory path or template file. Refer to help (--help) if needed.\n')

    """Build using a template directory:"""
    if args.dir_path is not None:
        template_list = []
        for item in os.listdir(args.dir_path):
            if item.endswith('.yaml') or item.endswith('.yml'):
                item = f'{args.dir_path}/{item}'
                template_list.append(item)
        for template in template_list:
            load_yaml(template)
            build(args.verbose, args.output_path)

    """Build using a single template"""
    if args.template is not None:
        load_yaml(args.template)
        build(args.verbose, args.output_path)
    
    """Calculate sha256sum of images and output to file"""
    if args.output_path is not None:
        image_list = []
        for image in os.listdir(args.output_path):
            image = f'{args.output_path}/{image}'
            image_list.append(image)
        if os.path.exists(f'{args.output_path}/image_hashes'):
            print('exists')
            write_hash = open(f'{args.output_path}/image_hashes', 'a')
        else:
            write_hash = open(f'{args.output_path}/image_hashes', 'x')
        for image in image_list:
                write_hash.write(f'{image_name}, {hash_file(image)}')

if __name__ == '__main__':
    sys.exit(main())
