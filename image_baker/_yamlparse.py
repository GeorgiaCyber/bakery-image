from yaml import safe_load


class YamlLoad:
    def __init__(self, template):
        self.template = template

    def load_yaml(self):
        # Loads a yaml file
        with open(self.template, "r") as file_descriptor:
            data = safe_load(file_descriptor,)
        return data


class YamlParse:
    def __init__(self, image_config):
        self.image_config = image_config

    def image_name(self):
        # Parses yaml for image_name
        for item, value in list(self.image_config.items()):
            if item == 'image_name':
                return value

    def method(self):
        # Parses yaml for method
        for item, value in list(self.image_config.items()):
            if item == 'method':
                return value

    def image_url(self):
        # Parses yaml for image_url
        for item, value in list(self.image_config.items()):
            if item == 'image_url':
                return value

    def compression(self):
        # Parses yaml for compression type
        for item, value in list(self.image_config.items()):
            if item == 'compression':
                return value

    def input_format(self):
        # Parses yaml for input_format
        for item, value in list(self.image_config.items()):
            if item == 'input_format':
                return value

    def output_format(self):
        # Parses yaml for output_format
        for item, value in list(self.image_config.items()):
            if item == 'output_format':
                return value

    def compressed(self):
        # Parses yaml for ocompression
        for item, value in list(self.image_config.items()):
            if item == 'compressed':
                return value

    def convert(self):
        # Parses yaml for conversion
        for item, value in list(self.image_config.items()):
            if item == 'convert':
                return value

    def packages(self):
        # Parses yaml for packages
        for item, value in list(self.image_config.items()):
            if item == 'packages':
                return value

    def customization(self):
        # Parses yaml for customization
        for item, value in list(self.image_config.items()):
            if item == 'customization':
                return value

    def image_size(self):
        # Parses yaml for image size modification
        for item, value in list(self.image_config.items()):
            if item == 'image_size':
                return value


def print_config(image_config):
    print('\nYAML loaded with the following specification:\n')
    # Print YAML properties to terminal
    for key, value in image_config.items():
        print(str(key) + ': ' + str(value))
    return
