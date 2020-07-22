from os import scandir
from image_baker._yamlparse import YamlLoad, YamlParse, print_config
from image_baker._imagemod import ImageConvert, ImageCustomize, ImageCompress, hash_image
from image_baker._imagetransfer import ImageDownload, ImageUpload


# Creates list of files in template directory
with scandir('./templates/') as templates:
    for template in templates:
        # Loads YAML specification for template file
        image_config = YamlLoad(template).load_yaml()
        # Prints build specification
        print_config(image_config)

        # Parses YAML for configuration items
        config_item = YamlParse(image_config)

        # Assigns each configuration item to a variable
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

        # Sets compressed name from compression format and image name variables
        compressed_name = "{}.{}".format(image_name, compression)

        # Minio variables
        minioclientaddr = '172.17.0.2:9000'
        minioaccesskey = 'ITSJUSTANEXAMPLE'
        miniosecretkey = 'EXAMPLEKEY'
        miniobucket = 'images'
        miniofilepath = '.'

        # Assigns configuration item variables for each class method used.
        convert_image = ImageConvert(image_name, image_url, input_format, output_format)
        customize_image = ImageCustomize(image_name, packages, customization)
        upload_image = ImageUpload(compressed_name, minioclientaddr, minioaccesskey, miniosecretkey, miniobucket)


        if convert is True:
            # Determines if image needs to be converted to different format (raw, qcow2, etc.)
            ImageDownload(image_url).download_image()
            ImageDownload(image_url).hash_download_image()
            convert_image.qemu_convert()

        if customization:
            # Determines if image needs customization and what utility to use for customization (virt-customize if not virt-builder)
            customize_image.virt_customize()

        if compression:
            # Determinese if image needs to be compressed based on format specified (xz, gz, bz2)
            ImageCompress(image_name, compression, compressed_name).compress()
            hash_image(compressed_name)

        # Uploads image to minio
        upload_image.uploadimagefile()

        # Print hashes for image original download, modification, and compression.