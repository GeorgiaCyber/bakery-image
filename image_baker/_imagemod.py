from os import remove
from subprocess import call
from shutil import copyfileobj
import hashlib
import lzma
import gzip
import bz2


def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))


def create_user_script(customization):
    # creates custom user script file
    create_script = open('user_script.sh', 'w')
    create_script.write(customization)
    create_script.close()


class ImageConvert:
    def __init__(self, image_name, image_url, input_format, output_format, file_name):
        # Set all common variables for the ImageConvert class
        self.image_name = image_name
        self.image_url = image_url
        self.input_format = input_format
        self.output_format = output_format
        self.file_name = file_name

    def qemu_convert(self):
        # Perform qemu image conversion for format type specified
        print('\nConverting {} to {} format with qemu-img utility...'
              .format(self.image_name, self.output_format))
        call('qemu-img convert -f {} -O {} {} {}'.format(self.input_format,
             self.output_format, self.image_name, self.file_name), shell=True)
        remove(self.image_name)


class ImageCustomize():
    def __init__(self, image_name, packages,
                 customization, method, output_format, file_name):
        # Set all common variables for the ImageCustomizatoin class
        self.image_name = image_name
        self.packages = ",".join(packages)
        self.customization = customization
        self.method = method
        self.output_format = output_format
        self.file_name = file_name

    def build_method(self):
        if self.method == 'virt-customize':
            print('\nCustomizing {} image with virt-customize\
                  utility...\n'.format(self.image_name))
            print('\nInstalling the following packages:{}\n'
                  .format(self.packages))
            # creates custom user script ran via CLI in virtcustomize
            create_user_script(self.customization)
            user_script = open('user_script.sh', 'r').read()
            print('\nApplying the following user script:\
                  \n {}'.format(user_script))
            # update package cache and install packages
            call('virt-customize -a {} -update --install {}\
                 --run user_script.sh'.format(self.file_name,
                 self.packages), shell=True)
            remove('user_script.sh')
        elif self.method == 'virt-builder':
            # update package cache and install packages
            print('\nCustomizing {} image with virt-builder utility'
                  .format(self.image_name))
            print('\nInstalling the following packages: {}\n'
                  .format(self.packages))
            # creates custom user script ran via CLI in virtcustomize
            create_user_script(self.customization)
            user_script = open('user_script.sh', 'r').read()
            print('\nApplying the following user script:\n {}'
                  .format(user_script))
            call('virt-builder -v {} --update --install {} --run user_script.sh\
                 --format {} --output {}'.format(self.image_name,
                 self.packages, self.output_format,
                 self.image_name), shell=True)


class ImageCompress:
    def __init__(self, compression, compressed_name, file_name):
        self.compression = compression
        self.compressed_name = compressed_name
        self.file_name = file_name

    def compress(self):
        print('\nCompressing image using {} method....'
              .format(self.compression))
        if self.compression == "gz":
            with open(self.file_name, 'rb') as file_in, \
                 gzip.open(self.compressed_name, 'wb') as file_out:
                copyfileobj(file_in, file_out)
        elif self.compression == "bz2":
            with open(self.file_name, 'rb') as file_in, \
                 bz2.open(self.compressed_name, 'wb') as file_out:
                copyfileobj(file_in, file_out)
        else:
            with open(self.file_name, 'rb') as file_in, \
                 lzma.open(self.compressed_name, 'wb') as file_out:
                copyfileobj(file_in, file_out)
