import hashlib
import subprocess as sp


class QemuImgConvert:
    def __init__(self, image_name, image_url, output_format, input_format):
        #  Set all common variables for the class
        self.image_name = image_name
        self.image_url = image_url
        self.output_format = output_format
        self.input_format = input_format

    def qemu_convert(self):
        #  Perform qemu image conversion for format type specified
        file = self.image_url.split('/')[-1]
        # new_filename = '{}.qcow2'.format(self.image_name)
        print('\nConverting {} to {} format with qemu-img utility...'.format(file, self.output_format))
        sp.call('qemu-img convert -f {} -O {} {} {} && rm {}'.format(self.input_format,
                self.output_format, file, self.image_name, file), shell=True)


class ImageCustomization:
        # Add custom packages
    def __init__(self, image_name, packages, customization):
        self.image_name = image_name
        self.packages = packages
        self.customization = customization

    def package_install(self):
        # update package cache
        sp.call('virt-customize -a {} --update'.format(self.image_name), shell=True)
        # iterate through items in package list and perform install
        for package in self.packages:
            sp.call('virt-customize -a {} --install {}'.format(self.image_name, package), shell=True)

    def custom_config(self):
        # run user scripts
        for item in self.customization:
            sp.call("virt-customize -a {} --run-command '{}'".format(self.image_name, item), shell=True)


def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))
