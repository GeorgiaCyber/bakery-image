from os import scandir
from image_baker._yamlparse import YamlLoad, YamlParse, print_config
from image_baker._imagemod import ImageConvert, ImageCustomize, ImageCompress, hash_image, create_user_script
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
        minioclientaddr = '172.17.0.3:9000'
        minioaccesskey = 'ITSJUSTANEXAMPLE'
        miniosecretkey = 'EXAMPLEKEY'
        miniobucket = 'images'
        miniofilepath = '.'

        # Assigns configuration item variables for each class method used.
        convert_image = ImageConvert(image_name, image_url, input_format, output_format)
        customize_image = ImageCustomize(image_name, packages, customization, method, output_format)
        compress_image = ImageCompress(image_name, compression, compressed_name)
        upload_image = ImageUpload(image_name, compressed_name, minioclientaddr, minioaccesskey, miniosecretkey, miniobucket)


        if image_url:
            ImageDownload(image_url).download_image()
            ImageDownload(image_url).hash_download_image()

        if convert is True and method == 'virt-builder':
            # Determines if image needs to be converted to different format with virt-builder utility(raw, qcow2, etc.)
            customize_image.build_method()

        if convert is True and method == 'virt-customize':
            # Determines if image needs to be converted to different format with qemu-img utility(raw, qcow2, etc.)
            convert_image.qemu_convert()
            customize_image.build_method()

        if compression:
            # Determinese if image needs to be compressed based on format specified (xz, gz, bz2)
            compress_image.compress()
            hash_image(compressed_name)

        # Uploads image to minio
        upload_image.uploadimagefile()

        # Print hashes for image original download, modification, and compression.
