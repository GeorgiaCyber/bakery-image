from os import scandir
import sys
from image_baker._yamlparse import YamlLoad, YamlParse, print_config
from image_baker._imagemod import (ImageConvert, ImageCustomize,
                                   ImageCompress, hash_image)
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
        image_size = config_item.image_size()

        # Sets compressed name from compression format and image name variables
        compressed_name = "{}.{}".format(image_name, compression)
        file_name = '{}.{}'.format(image_name, output_format)

        # Minio variables
        minioclientaddr = sys.argv[1]
        minioaccesskey = sys.argv[2]
        miniosecretkey = sys.argv[3]
        miniobucket = 'images'
        miniofilepath = '.'

        # '172.17.0.3:9000'
        # 'ITSJUSTANEXAMPLE'
        # 'EXAMPLEKEY'

        # Assigns configuration item variables for each class method used.
        convert_image = ImageConvert(image_name, image_url,
                                     input_format, output_format, file_name)
        customize_image = ImageCustomize(image_name, packages,
                                         customization, method,
                                         output_format, file_name, image_size)
        compress_image = ImageCompress(compression, compressed_name, file_name)
        upload_image = ImageUpload(image_name, compressed_name,
                                   minioclientaddr, minioaccesskey,
                                   miniosecretkey, miniobucket, file_name, compression)

        if image_url:
            # Download image from url specified
            ImageDownload(image_url, image_name).download_image()
            ImageDownload(image_url, image_name).hash_download_image()

        if convert is True and method == 'virt-builder':
            # Determines if image needs to be converted to
            #  different format with virt-builder utility(raw, qcow2, etc.)
            customize_image.build_method()
        elif method == 'virt-builder':
            customize_image.build_method()

        if convert is True and method == 'virt-customize':
            # Determines if image needs to be converted to
            #  different format with qemu-img utility(raw, qcow2, etc.)
            convert_image.qemu_convert()         
            if image_size:
                # Determines if image needs to be resized
                customize_image.image_resize()
                customize_image.build_method()
            else:
                customize_image.build_method()
        elif method == 'virt-customize':
            customize_image.build_method()

        if compression:
            # Determinese if image needs to
            #  be compressed based on format specified (xz, gz, bz2)
            compress_image.compress()
            hash_image(compressed_name)

        # Uploads image to minio
        upload_image.uploadimagefile()

        # Print hashes for image original download,
        #  modification, and compression.
