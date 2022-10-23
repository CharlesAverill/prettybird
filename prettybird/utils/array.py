import copy


def arange(start, stop, step):
    current = start
    while current < stop:
        yield round(current, 5)
        current += step


class Array:
    def __init__(self, data):
        self.type = type(data)

        if self.type == Array:
            self.type = copy.deepcopy(data.type)
            self.data = copy.deepcopy(data.data)
            return

        if self.type not in (int, float, list, tuple):
            raise TypeError(
                f"Arrays only support number and list types, not {self.type}"
            )

        self.data = None
        if self.type in (list, tuple):
            self.data = [Array(d) for d in data]
        else:
            self.data = data

    @staticmethod
    def _get_shape(data):
        if type(data) in (int, float):
            return ()
        out = [len(data)]
        if out[0] > 0:
            out.extend(data[0].shape)
        return tuple(out)

    @staticmethod
    def _get_size(data):
        if type(data) in (int, float):
            return 1
        return sum(d.size for d in data)

    @property
    def shape(self):
        return Array._get_shape(self.data)

    @property
    def size(self):
        return Array._get_size(self.data)

    def __repr__(self):
        if self.type in (list, tuple):
            return f"array({[d for d in self.data]})"
        else:
            return str(self.data)

    def __add__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(other.data + self.data)
        elif other.shape == () or other.size == 1:
            return Array([d + other.data for d in self.data])
        elif other.shape == self.shape:
            return Array([other.data[i] + self.data[i] for i in range(self.shape[0])])
        elif self.shape == () or self.size == 1:
            return Array([d + self.data for d in other.data])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-1 * other)

    def __rsub__(self, other):
        return other + (-1 * self)

    def __mul__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(other.data * self.data)
        elif other.shape == () or other.size == 1:
            return Array([d * other.data for d in self.data])
        elif other.shape == self.shape:
            return Array([other.data[i] * self.data[i] for i in range(self.shape[0])])
        elif self.shape == () or self.size == 1:
            return Array([d * self.data for d in other.data])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(other.data**self.data)
        elif other.shape == () or other.size == 1:
            return Array([d**other.data for d in self.data])
        elif other.shape == self.shape:
            return Array([other.data[i] ** self.data[i] for i in range(self.shape[0])])
        elif self.shape == () or self.size == 1:
            return Array([d**self.data for d in other.data])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __rpow__(self, other):
        return self**other

    def __mod__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(other.data % self.data)
        elif other.shape == () or other.size == 1:
            return Array([d % other.data for d in self.data])
        elif other.shape == self.shape:
            return Array([other.data[i] % self.data[i] for i in range(self.shape[0])])
        elif self.shape == () or self.size == 1:
            return Array([d % self.data for d in other.data])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    """
    def __rmod__(self, other):
        return self * other
    """

    def __rtruediv__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(other.data / self.data)
        elif other.shape == () or other.size == 1:
            return Array([d / other.data for d in self.data])
        elif other.shape == self.shape:
            return Array([other.data[i] / self.data[i] for i in range(self.shape[0])])
        elif self.shape == () or self.size == 1:
            return Array([d / self.data for d in other.data])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __truediv__(self, other):
        return self * (1 / other)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __float__(self):
        return float(self.data)

    def __int__(self):
        return int(self.data)

    def __lt__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return self.data < other.data
        elif other.shape == () or other.size == 1:
            return all([d < other.data for d in self.data])
        elif self.shape == () or self.size == 1:
            return all([self.data < d for d in other.data])
        elif other.shape == self.shape:
            return all([self.data[i] < other.data[i] for i in range(self.shape[0])])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __gt__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return self.data > other.data
        elif other.shape == () or other.size == 1:
            return all([d > other.data for d in self.data])
        elif self.shape == () or self.size == 1:
            return all([self.data > d for d in other.data])
        elif other.shape == self.shape:
            return all([self.data[i] > other.data[i] for i in range(self.shape[0])])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __eq__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return self.data == other.data
        elif other.shape == () or other.size == 1:
            return all([d == other.data for d in self.data])
        elif self.shape == () or self.size == 1:
            return all([self.data == d for d in other.data])
        elif other.shape == self.shape:
            return all([self.data[i] == other.data[i] for i in range(self.shape[0])])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not self == other

    def __abs__(self):
        return abs(self.data)

    def __and__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(int(other.data) & int(self.data))
        elif other.shape == () or other.size == 1:
            return Array([d & int(other.data) for d in int(self.data)])
        elif other.shape == self.shape:
            return Array(
                [int(other.data)[i] & int(self.data)[i]
                 for i in range(self.shape[0])]
            )
        elif self.shape == () or self.size == 1:
            return Array([d & int(self.data) for d in int(other.data)])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __xor__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(int(other.data) ^ int(self.data))
        elif other.shape == () or other.size == 1:
            return Array([d ^ int(other.data) for d in int(self.data)])
        elif other.shape == self.shape:
            return Array(
                [int(other.data)[i] ^ int(self.data)[i]
                 for i in range(self.shape[0])]
            )
        elif self.shape == () or self.size == 1:
            return Array([d ^ int(self.data) for d in int(other.data)])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __or__(self, other):
        other = Array(other)
        if other.shape == () and self.shape == ():
            return Array(int(other.data) | int(self.data))
        elif other.shape == () or other.size == 1:
            return Array([d | int(other.data) for d in int(self.data)])
        elif other.shape == self.shape:
            return Array(
                [int(other.data)[i] | int(self.data)[i]
                 for i in range(self.shape[0])]
            )
        elif self.shape == () or self.size == 1:
            return Array([d | int(self.data) for d in int(other.data)])
        else:
            raise ValueError(
                f"Cannot operate on Arrays of different sizes: {self.size}, {other.size}"
            )

    def __getitem__(self, item):
        return self.data[item]

    def __round__(self, digits):
        return round(self.data, digits)
