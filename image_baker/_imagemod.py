from os import remove
from subprocess import call
import hashlib



class ImageConvert:
    def __init__(self, image_name, image_url, input_format, output_format):
        #  Set all common variables for the ImageConvert class
        self.image_name = image_name
        self.image_url = image_url
        self.input_format = input_format        
        self.output_format = output_format


    def qemu_convert(self):
        #  Perform qemu image conversion for format type specified
        file = self.image_url.split('/')[-1]
        print('\nConverting {} to {} format with qemu-img utility...'.format(file, self.output_format))
        call('qemu-img convert -f {} -O {} {} {}'.format(self.input_format,
                self.output_format, file, self.image_name), shell=True)
        remove(file)


class ImageCustomize():
    def __init__(self, image_name, packages, customization):
         # Set all common variables for the ImageCustomizatoin class
        self.image_name = image_name
        self.packages = packages
        self.customization = customization

    def virt_customize(self):
        # update package cache for image
        call('virt-customize -a {} --update'.format(self.image_name), shell=True)
        # iterate through items in package list and perform install
        for package in self.packages:
            call('virt-customize -a {} --install {}'.format(self.image_name, package), shell=True)
        # iterate through items in customization script and execute via CLI on the image
        for command in self.customization:
            call("virt-customize -a {} --run-command '{}'".format(self.image_name, command), shell=True)

    def virt_builder(self):
        #  Perform qemu image customization with virt-builder for image specified
        print('\nCustomizing {} image with virt-builder utility...'.format(self.image_name))
        call('virt-builder {} --install {} --output {} --run-command {}'.format(self.image_name, self.customization), shell=True)      

class ImageCompress:
    def __init__(self, image_name, compression, compressed_name):
        self.image_name = image_name
        self.compression = compression
        self.compressed_name = compressed_name
        print('\nCompressing image using {} method...'.format(self.compression))

    def compress(self):
        if self.compression == "xz":
            call("xz -vzT 0 {}".format(self.image_name), shell=True)
            call("xz -l {}".format(self.compressed_name), shell=True)
        elif self.compression == "gz":
            call("gzip -v {}".format(self.image_name), shell=True)
            call("gzip -l {}".format(self.compressed_name), shell=True)
        elif self.compression == "bz2":
            call("bzip2 -v {}".format(self.image_name), shell=True)

def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))
