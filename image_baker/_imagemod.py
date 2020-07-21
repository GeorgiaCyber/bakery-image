from os import remove
from subprocess import call
import hashlib



class QemuImgConvert:
    def __init__(self, image_name, image_url, input_format, output_format):
        #  Set all common variables for the QemuImgConvert class
        self.image_name = image_name
        self.image_url = image_url
        self.input_format = input_format        
        self.output_format = output_format


    def qemu_convert(self):
        #  Perform qemu image conversion for format type specified
        file = self.image_url.split('/')[-1]
        # new_filename = '{}.qcow2'.format(self.image_name)
        print('\nConverting {} to {} format with qemu-img utility...'.format(file, self.output_format))
        call('qemu-img convert -f {} -O {} {} {}'.format(self.input_format,
                self.output_format, file, self.image_name), shell=True)
        remove(file)


# class VirtBuild:
#     def __init__(self, image_name, input_format, output_format, packages, customization):
#         #  Set all common variables for the VirtBuild class
#         self.image_name = image_name
#         self.input_format = input_format
#         self.output_format = output_format
#         self.packages = packages
#         self.customization = customization

#     def virt_build(self):
#         #  Perform qemu image customization with virt-builder for image specified
#         print('\nCustomizing {} image with virt-builder utility...'.format(image_name))
#         call('virt-builder {} --install {} --output {} --run-command {}'.format(self.image_name, self.customization), shell=True)

class ImageCustomization:
        # Add custom packages
    def __init__(self, image_name, packages, customization):
        self.image_name = image_name
        self.packages = packages
        self.customization = customization

    def package_install(self):
        # update package cache
        call('virt-customize -a {} --update'.format(self.image_name), shell=True)
        # iterate through items in package list and perform install
        for package in self.packages:
            call('virt-customize -a {} --install {}'.format(self.image_name, package), shell=True)

    def custom_config(self):
        # run user scripts
        for item in self.customization:
            call("virt-customize -a {} --run-command '{}'".format(self.image_name, item), shell=True)


def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))
