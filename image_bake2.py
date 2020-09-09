import os
import sys
import argparse
from yaml import safe_load
from image_baker._yamlparse import YamlLoad, YamlParse, print_config


# def load_yaml(template):
#     with open(template, 'r') as fd:
#         data = safe_load(fd)
#     return data


def main():
    parser = argparse.ArgumentParser(prog='image_baker', description='Start baking an image.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode for troubleshooting image_build')
    parser.add_argument('-a', '--all', default='NONE', action='store_true', help='Runs image baker on all template files in the specified directory')
    parser.add_argument('-T', '--type', default='NONE', action='store', choices=['vm', 'docker'], help='Specifies the type of image to build', )
    parser.add_argument('-t', '--template', default='NONE', action='store', help='Specifies template yaml file to build.')
    parser.add_argument('-d', '--dir_path', default='NONE', action='store', help='Directory path for multiple template yaml files')
    parser.add_argument('-i', '--input_name', action='store', help='Specifies the input file name for the image.')
    parser.add_argument('-o', '--output_name', action='store', help='Specifies the output file name for the image.')
    parser.add_argument('-r', '--resize', action='store', help='Specifies the the output image size')
    parser.add_argument('-f', '--output_format', action='store', help='Output format for image (raw, qcow2, etc.)')
    parser.add_argument('-b', '--builder', default='virt-customize', action='store', choices=['virt-customize', 'virt-builder'], help='Specifies the builder to use.')
    parser.add_argument('-c', '--compress', default='NONE', action='store', choices=['gz', 'bz2', 'lzma'], help='Specifies compression and type')
    parser.add_argument('-p', '--packages', action='store', help='Packages to install on the image')

    num_args = len(sys.argv)

    args = parser.parse_args()

    if num_args < 2:
        sys.stderr.write('ERROR: No options were present, refer to help (--help) if needed.\n')
    
    if args.all == 'NONE' and args.template == 'NONE' and args.dir_path == 'NONE' and num_args > 2:
        sys.stderr.write('ERROR: Specify a directory path, template file, or all. Refer to help (--help) if needed.\n')



    # args = parser.parse_args()

    # template_name = args.template

    # if template_name == 'NONE' and not args.dir_path:
    #     sys.stderr.write(f'Missing template name or directory:\n {template_name}')
    #     parser.usage()
    #     sys.exit(1)
    
    # if template_name not in dirs:
    #     sys.stderr.write(f'ERROR: Image named {template_name} not found.')
    #     sys.stderr.write('Make sure you spelled the template name correctly.')
    #     sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
