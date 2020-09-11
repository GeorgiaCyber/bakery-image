import os
import sys
import argparse
from yaml import safe_load
# from image_baker._yamlparse import YamlLoad, YamlParse, print_config



def load_yaml(template):
    with open(template, 'r') as fd:
        template_data = safe_load(fd)
    return template_data


def main():
    parser = argparse.ArgumentParser(prog='image_baker', description='Start baking an image.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode for troubleshooting image build')
    parser.add_argument('-a', '--all', default='NONE', action='store_true', help='Runs image baker on all template files in the specified directory')
    parser.add_argument('-T', '--type', default='NONE', action='store', choices=['vm', 'docker'], help='Specifies the type of image to build', )
    parser.add_argument('-t', '--template', default='NONE', action='store', help='Specifies template yaml file to build.')
    parser.add_argument('-d', '--dir_path', default='NONE', action='store', metavar=('./some/directory/'), help='Directory path for multiple template yaml files')
    parser.add_argument('-f', '--format', nargs=2, action='store', metavar=('input_format', 'output_format'), help='specifies the input and output format for image conversion')
    parser.add_argument('-o', '--output_name', action='store', help='Specifies the output file name for the image.')
    parser.add_argument('-r', '--resize', action='store', help='Specifies the the output image size')
    parser.add_argument('-b', '--builder', default='virt-customize', action='store', choices=['virt-customize', 'virt-builder'], help='Specifies the builder to use.')
    parser.add_argument('-c', '--compress', default='NONE', action='store', choices=['gz', 'bz2', 'lzma'], help='Specifies compression and type')
    parser.add_argument('-p', '--packages', action='store', help='Packages to install on the image')

    num_args = len(sys.argv)

    args = parser.parse_args()

    if num_args < 2:
        sys.stderr.write('ERROR: No options were present, refer to help (--help) if needed.\n')
    
    if args.all == 'NONE' and args.template == 'NONE' and args.dir_path == 'NONE' and num_args > 2:
        sys.stderr.write('ERROR: Specify a directory path, template file, or all. Refer to help (--help) if needed.\n')

    if args.dir_path != 'NONE' and args.all:
        #Bake images for all templates in a given dir path
        template_list = []
        templates = os.listdir(args.dir_path)
        for template in templates:
            #Creates list of templates in dir path provided
            template_list.append(f'{args.dir_path}{template}')
            print(template_list)
        for template in template_list:
            #Loads params specified in yaml template for each image
            loaded_template = load_yaml(template)
            for k, v in loaded_template.items():
                print(k, v)
'''
break point, kwargs needs to be implemented for parsing through the templates loaded by load_yaml.
'''
        
    if args.template != 'NONE':
        #Bake images for a specifc yaml template
        template = args.template
        print(load_yaml(template))
        print(type(template))




            # YamlParse.load_yaml(dir_path, template)
            # print(template_data)
        
        # with os.scandir(args.dir_path) as templates:
        #     for template in templates:
        #         print(template)
                # print(templates)
                # image_template = load_yaml(template)
            # print(image_template)


    # args = parser.parse_args()

    # template_name = args.template

    if args.template == 'NONE' and not args.dir_path:
        sys.stderr.write(f'Missing template name or directory:\n {args.template}')
        parser.usage()
        sys.exit(1)
    
    # if template_name not in dirs:
    #     sys.stderr.write(f'ERROR: Image named {template_name} not found.')
    #     sys.stderr.write('Make sure you spelled the template name correctly.')
    #     sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
