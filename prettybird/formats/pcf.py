# Derived from https://fontforge.org/docs/techref/pcf-format.html
# https://github.com/ganaware/pcf2bdf/blob/main/pcf2bdf.cc

import sys

from .pcf_defines import *


def int_to_8bit_int(number: int, signed=True):
    return number.to_bytes(1, sys.byteorder, signed=signed)

def int_to_16bit_int(number: int, signed=True):
    return number.to_bytes(2, sys.byteorder, signed=signed)

def int_to_32bit_int(number: int, signed=True):
    return number.to_bytes(4, sys.byteorder, signed=signed)

def int_to_little_endian_32bit_int(number: int, signed=True):
    return number.to_bytes(4, "little", signed=signed)


class PCFProperty:
    def __init__(self, _name: str, _is_str_prop: bool, _value_or_str_offset: int):
        self.name = _name
        self.is_str_prop = _is_str_prop
        self.value_or_str_offset = _value_or_str_offset

class PCFMetric:
    def __init__(self, _left_sided_bearing: int, _right_side_bearing: int, _character_width: int, _character_ascent: int, _character_descent: int, _character_attributes: int):
        self.left_sided_bearing = _left_sided_bearing
        self.right_side_bearing = _right_side_bearing
        self.character_width = _character_width
        self.character_ascent = _character_ascent
        self.character_descent = _character_descent
        self.character_attributes = _character_attributes


class PCFTable:
    def __init__(self, _type: int, _format: int, _properties: list[PCFProperty] = [], _metrics: list[PCFMetric] = []):
        self.type = _type
        self.format = _format
        self.size = 0
        self.offset = 0

        # Properties table
        self.num_properties = len(_properties)
        self.props = _properties

        # Metrics table
        self.num_metrics = len(_metrics)
        self.mets = _metrics

        self.function_map = {
            PCF_PROPERTIES: self.properties,
            PCF_ACCELERATORS: self.accelerators,
            PCF_METRICS: self.metrics,
            PCF_BITMAPS: self.bitmaps,
            PCF_INK_METRICS: self.ink_metrics,
            PCF_BDF_ENCODINGS: self.bdf_encodings,
            PCF_SWIDTHS: self.swidths,
            PCF_GLYPH_NAMES: self.glyph_names,
            PCF_BDF_ACCELERATORS: self.bdf_accelerators,
        }

    def get_toc_entry(self):
        out = b""
        out += int_to_little_endian_32bit_int(self.type)
        out += int_to_little_endian_32bit_int(self.format)
        out += int_to_little_endian_32bit_int(self.size)
        out += int_to_little_endian_32bit_int(self.offset)
        return out

    def toc_entry_str(self):
        out = "struct toc_entry {\n"
        out += f"\tlsbint32 type={pcf_type_strings[self.type]};\n"
        out += f"\tlsbint32 format={self.format};\n"
        out += f"\tlsbint32 size={self.size};\n"
        out += f"\tlsbint32 offset={self.offset};\n"
        out += "};"
        return out

    def get_table(self):
        return self.function_map[self.type]()

    def properties(self):
        out = b""
        # format
        if self.format != PCF_DEFAULT_FORMAT:
            raise UserWarning(
                "PCF_PROPERTIES should have the PCF Default Format, this one has",
                pcf_format_strings[self.format],
            )
        out += int_to_little_endian_32bit_int(self.format)
        # num_properties
        if self.num_properties < 1:
            raise UserWarning(
                "PCF_PROPERTIES should have at least one property, this one has",
                self.num_properties,
            )
        out += int_to_32bit_int(self.num_properties)
        # properties
        properties_name_size = 0
        strings = b""
        for property in self.props:
            out += int_to_32bit_int(properties_name_size)
            properties_name_size += len(property.name) + 1  # Add 1 for null terminator
            strings += str.encode(property.name) + b"\0"
            out += int_to_8bit_int(property.is_str_prop)
            out += int_to_32bit_int(property.value_or_str_offset)
        # padding
        padding = 3 - (((4 + 1 + 4) * self.num_properties + 3) % 4)
        out += int(0).to_bytes(padding, byteorder=sys.byteorder, signed=True)
        # string_size
        out += int_to_32bit_int(properties_name_size + 1)
        # strings
        out += strings

        return out
    
    def accelerators(self):
        out = b""

        return out
    
    def metrics(self):
        out = b""

        # format
        if self.format not in (PCF_DEFAULT_FORMAT, PCF_COMPRESSED_METRICS):
            raise UserWarning(
                "PCF_BITMAPS should have the PCF Default Format or the PCF Compressed Metrics Format, this one has",
                pcf_format_strings[self.format],
            )
        out += int_to_little_endian_32bit_int(self.format)

        # metrics
        if self.format == PCF_DEFAULT_FORMAT:
            # Uncompressed metrics
            out += int_to_32bit_int(self.num_metrics)
            for metric in self.mets:
                out += int_to_16bit_int(metric.left_sided_bearing)
                out += int_to_16bit_int(metric.right_side_bearing)
                out += int_to_16bit_int(metric.character_width)
                out += int_to_16bit_int(metric.character_ascent)
                out += int_to_16bit_int(metric.character_descent)
                out += int_to_16bit_int(metric.character_attributes, signed=False)
        else: 
            # Compressed metrics
            raise NotImplementedError("PCF_COMPRESSED_METRICS is not yet supported")

        return out

    def bitmaps(self):
        out = b""

        return out

    def ink_metrics(self):
        out = b""

        return out

    def bdf_encodings(self):
        out = b""

        return out

    def swidths(self):
        out = b""

        return out

    def glyph_names(self):
        out = b""

        return out

    def bdf_accelerators(self):
        out = b""

        return out


class PCF:

    required_tables = [
        PCF_PROPERTIES,
        PCF_ACCELERATORS,
        PCF_METRICS,
        PCF_BITMAPS,
        PCF_BDF_ENCODINGS,
    ]

    def __init__(self, _filename: str, _tables: list[PCFTable]):
        if not _filename.endswith(".pcf"):
            raise UserWarning("PCF files should end with a .pcf suffix")
        self.filename = _filename
        self.file = None

        self.table_count = len(_tables)
        # Sort tables by type
        self.tables = sorted(_tables, key=lambda x: x.type, reverse=False)

    def write_little_endian_32bit_int(self, number: int):
        self.file.write(int_to_little_endian_32bit_int(number))

    def write_header(self):
        # Constant file header
        self.file.write(b"\1fcp")
        # table_count (i32)
        self.write_little_endian_32bit_int(self.table_count)
        # Write table of contents
        for table in self.tables:
            self.file.write(table.get_toc_entry())

    def write(self):
        self.file = open(self.filename, "wb")
        # Write header
        self.write_header()
        # Write tables themselves
        for table in self.tables:
            self.file.write(table.get_table())
        self.file.close()


if __name__ == "__main__":
    tables = [
        PCFTable(PCF_PROPERTIES, PCF_DEFAULT_FORMAT, _properties=[
            PCFProperty("DEFAULT_CHAR", False, 0),
            PCFProperty("FONT_ASCENT", False, 16),
            PCFProperty("FONT_DESCENT", False, 2)
        ]),
        PCFTable(PCF_ACCELERATORS, PCF_DEFAULT_FORMAT),
        PCFTable(PCF_METRICS, PCF_DEFAULT_FORMAT),
        PCFTable(PCF_BITMAPS, PCF_DEFAULT_FORMAT),
        PCFTable(PCF_BDF_ENCODINGS, PCF_DEFAULT_FORMAT),
    ]
    pcf = PCF("test.pcf", tables)
    pcf.write()
