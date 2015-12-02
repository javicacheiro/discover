"""Helper classes"""


class ToDictMixin(object):
    """Mixin to transform an object into a dict"""
    def to_dict(self):
        """Convert object to dictionary"""
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, dictionary):
        """Traverse the contents of the given dictionary"""
        output = {}
        for key, value in dictionary.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        """Traverse the given value"""
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, '__dict__'):
            return self._traverse_dict(value.__dict__)
        else:
            return value
