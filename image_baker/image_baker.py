import hashlib
import yaml
import requests
from tqdm import tqdm

def load_yaml(template_file):
# Loads a yaml file
    with open(template_file, "r") as file_descriptor:
        data = yaml.safe_load(file_descriptor,)
    return data

def print_config():
# Prints YAML properties to terminal
    print('\nYAML loaded with the following specfication:\n')
    for key, value in data.items():
        print(str(key)+': ' + str(value))

def build_method():
# Determines if build method is virt-builder, diskimage-builder, docker, or podman
    for item, value in list(data.items()):
        if item == 'method' and value == 'virt-builder':
            return value
        elif item == 'method' and value == 'diskimage-builder':
            return value
        elif item == 'method' and value == 'docker':
            return value
        elif item == 'method' and value == 'podman':
            return value
        else:
            

def compression():

def virt_build():

def diskimage_build():

def docker_build():

def podman_build():



def download_url():
# Parses yaml for image_url if provided
    for item, value in list(data.items()):
        if item == 'image_url':
            return value

def download_image():
# Downloads image from url passed from download_url() if available
    url = download_url()
    file = url.split('/')[-1]
    r = requests.get(url, stream=True, allow_redirects=True)
    total_size = int(r.headers.get('content-length'))
    initial_pos = 0

    print('\nDownloading image from ({}):'.format(url))
    with open(file, 'wb') as f:
        with tqdm(total=total_size, unit='it', unit_scale=True, desc=file, initial=initial_pos, ascii=True) as pbar:
            for ch in r.iter_content(chunk_size=1024):
                if ch:
                    f.write(ch)
                    pbar.update(len(ch))

def hash_download_image():
# Create hash value for image downloaded with download_image()
    url = download_url()
    file = url.split('/')[-1]
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nImage SHA256 Hash: {}'.format(hash_file))


#def hash_final_image():
# Create hash value final image product

# def virt_build():
# Use virt-build method to modify image


if __name__ == "__main__":
# Specify template dir/file and load with yaml parser
    template_file = '../templates/centos8.yaml'
    data = load_yaml(template_file)

    print_config()
# Print yaml template build summary

    if build_method() == 'virt-builder':
# Get build method
        print(build_method())
    elif build_method() == 'diskimage-builder':
        print(build_method())
    elif build_method() == 'docker':
        print(build_method())
    elif build_method() == 'podman':
        print(build_method())


    download_image()
# Download image if available

    hash_download_image()
# Hash downloaded image
