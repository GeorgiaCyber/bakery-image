import os
from tqdm import tqdm
import requests
from minio import Minio
import subprocess as sp
from minio.error import ResponseError
import hashlib


class DownloadImage:
    def __init__(self, image_url):
        self.image_url = image_url

    def download_image(self):
        # Downloads image from url passed from download_url() if available
        file = self.image_url.split('/')[-1]
        # file = file.replace("img", "qcow2")
        r = requests.get(self.image_url, stream=True, allow_redirects=True)
        total_size = int(r.headers.get('content-length'))
        initial_pos = 0

        print('\nDownloading image from ({}):'.format(self.image_url))
        with open(file, 'wb') as f:
            with tqdm(total=total_size, unit='it', unit_scale=True, desc=file, initial=initial_pos, ascii=True) as pbar:
                for ch in r.iter_content(chunk_size=1024):
                    if ch:
                        f.write(ch)
                        pbar.update(len(ch))

    def hash_download_image(self):
        # Create hash value for image downloaded with download_image()
        file = self.image_url.split('/')[-1]
        with open(file, 'rb') as file:
            content = file.read()
        sha = hashlib.sha256()
        sha.update(content)
        hash_file = sha.hexdigest()
        print('\nImage SHA256 Hash: {}'.format(hash_file))


def hash_image(image_name):
    # Create hash value for image
    file = image_name
    with open(file, 'rb') as file:
        content = file.read()
    sha = hashlib.sha256()
    sha.update(content)
    hash_file = sha.hexdigest()
    print('\nSHA256 Hash: {}'.format(hash_file))

class CompressImage:
    def __init__(self, image_name, compression, compressed_name):
        self.image_name = image_name
        self.compression = compression
        self.compressed_name = compressed_name
        print('\nCompressing image using {} method...'.format(self.compression))

    def compress(self):
        if self.compression == "xz":
            sp.call("xz -vzT 0 {}".format(self.image_name), shell=True)
            sp.call("xz -l {}".format(self.compressed_name), shell=True)
        elif self.compression == "gz":
            sp.call("gzip -v {}".format(self.image_name), shell=True)
            sp.call("gzip -l {}".format(self.compressed_name), shell=True)
        elif self.compression == "bz2":
            sp.call("bzip2 -v {}".format(self.image_name), shell=True)


class UploadImage:
    def __init__(self, compressed_name, minioclientaddr, minioaccesskey, miniosecretkey, miniobucket):
        self.compressed_name = compressed_name
        self.minioclientaddr = minioclientaddr
        self.minioaccesskey = minioaccesskey
        self.miniosecretkey = miniosecretkey
        self.miniobucket = miniobucket

    def uploadimagefile(self):
        print('\nUploading {} to minio object store at {}...'.format(self.compressed_name, self.minioclientaddr))
        client = Minio(self.minioclientaddr, access_key=self.minioaccesskey,
                       secret_key=self.miniosecretkey, secure=False)
        try:
            with open(self.compressed_name, 'rb') as file_data:
                file_stat = os.stat(self.compressed_name)
                client.put_object(self.miniobucket, self.compressed_name, file_data, file_stat.st_size)
        except ResponseError as err:
            print(err)
        sp.call('rm {}'.format(self.compressed_name))