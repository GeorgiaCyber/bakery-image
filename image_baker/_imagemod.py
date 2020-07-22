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
        self.packages = ",".join(packages)
        self.customization = customization

    def virt_customize(self):
        print('\nCustomizing {} image with virt-customize utility...\n'.format(self.image_name))
        print('\nInstalling the following packages: {}\n'.format(self.packages))
        # creates custom user script ran via CLI in virtcustomize
        create_user_script(self.customization)
        user_script = open('user_script.sh', 'r')
        print('\nApplying the following user script:\n {}'.format(print(user_script.read())))
        # update package cache and install packages
        call('virt-customize -a {} -update --install {} --run user_script.sh'.format(self.image_name, self.packages), shell=True)
        remove('user_script.sh')

 
    # def virt_builder(self):
    #     # update package cache and install packages
    #     print('\nCustomizing {} image with virt-builder utility...'.format(self.image_name))
    #     call('virt-builder {} --update --install {} --output {} --run-command {}'.format(self.image_name, self.packages, self.customization), shell=True)      

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

def create_user_script(customization):
    # creates custom user script file
    create_script = open('user_script.sh', 'w')
    create_script.write(customization)
    create_script.close()
