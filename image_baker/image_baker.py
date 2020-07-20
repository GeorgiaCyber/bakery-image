from _parseyaml import LoadYaml, ParseYaml, print_config
from _imagemod import QemuImgConvert, ImageCustomization, hash_image
from _imagetransfer import DownloadImage, CompressImage, UploadImage


# Specify template dir/file and load with yaml parser
template_file = '../templates/ubuntu.yaml'
image_config = LoadYaml(template_file).load_yaml()

# Minio variables
minioclientaddr = '172.17.0.2:9000'
minioaccesskey = 'ITSJUSTANEXAMPLE'
miniosecretkey = 'EXAMPLEKEY'
miniobucket = 'images'
miniofilepath = '.'

# Associate keys with item variables
config_item = ParseYaml(image_config)

# Prints build specification
print_config(image_config)

# Parses YAML configuration and sets variables for each item
image_name = config_item.image_name()
method = config_item.method()
image_url = config_item.image_url()
input_format = config_item.input_format()
output_format = config_item.output_format()
compressed = config_item.compressed()
convert = config_item.convert()
packages = config_item.packages()
customization = config_item.customization()
compression = config_item.compression()

qemubuild = QemuImgConvert(image_name, image_url, output_format, input_format)
customize_image = ImageCustomization(image_name, packages, customization)
compressed_name = "{}.{}".format(image_name, compression)
imageupload = UploadImage(compressed_name, minioclientaddr, minioaccesskey, miniosecretkey, miniobucket)


if convert is True:
    DownloadImage(image_url).download_image()
    DownloadImage(image_url).hash_download_image()
    qemubuild.qemu_convert()

if customization:
    customize_image.package_install()
    customize_image.custom_config()

if compression is not None:
    CompressImage(image_name, compression, compressed_name).compress()
    hash_image(compressed_name)

imageupload.uploadimagefile()

