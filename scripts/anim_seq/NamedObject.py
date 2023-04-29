
class NamedObject(object):
    """
    Must be named during init with a name='name'
    Class shows the name of it, instead of the memory
    address while inspecting, debugging.
    Also allows for name vs name compare behaviors
    """
    def __init__(self, **kwargs):
        """
        Setups up Ordered Dict() Details container,
        Populates Details and Default Values
        :param name: string to name ObjectAsset.name after
        """
        self.details = {}
        self.set(**self.details_core())
        self.set(**kwargs)

    def __repr__(self):
        """
        Adds self.name to standard return object
        """
        repr_string = f"{self.__class__.__module__,},{self.__class__.__name__}"
        if self.name:
            repr_string += f",{self.name}"
        return repr_string

    def __eq__(self, other):
        if hasattr(other, 'name'):
            return self.details['name'] == other.name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def set(self, **kwargs):
        """
        :keyword key=value: pairs to populate self.details with validation
        """
        for key, value in kwargs.items():
            self.details[key] = value

    def get(self, key):
        """
        Returns a value from a details key
        :param key: existing details key (Can use list to see dictionary keys)
        :return:
        """
        return self.details.get(key)

    @classmethod
    def details_core(cls):
        """
        base dictionary entries
        :return dictionary:
        """
        return {'name': None}

    @property
    def name(self):
        """
        :return String name of gameObject:
        """
        return self.details['name']

    def list_details(self):
        """
        Debug method to list detail values to Output
        """
        print('\n')
        print(('Item Details for {}:'.format(self.details['name'])))
        for key, value in list(self.details.items()):
            print(f'   {key: <24} = {value}')


