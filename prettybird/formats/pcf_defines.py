# Type
PCF_PROPERTIES = 1 << 0
PCF_ACCELERATORS = 1 << 1
PCF_METRICS = 1 << 2
PCF_BITMAPS = 1 << 3
PCF_INK_METRICS = 1 << 4
PCF_BDF_ENCODINGS = 1 << 5
PCF_SWIDTHS = 1 << 6
PCF_GLYPH_NAMES = 1 << 7
PCF_BDF_ACCELERATORS = 1 << 8

pcf_type_strings = {
    PCF_PROPERTIES: "PCF_PROPERTIES",
    PCF_ACCELERATORS: "PCF_ACCELERATORS",
    PCF_METRICS: "PCF_METRICS",
    PCF_BITMAPS: "PCF_BITMAPS",
    PCF_INK_METRICS: "PCF_INK_METRICS",
    PCF_BDF_ENCODINGS: "PCF_BDF_ENCODINGS",
    PCF_SWIDTHS: "PCF_SWIDTHS",
    PCF_GLYPH_NAMES: "PCF_GLYPH_NAMES",
    PCF_BDF_ACCELERATORS: "PCF_BDF_ACCELERATORS"
}

# Format
PCF_DEFAULT_FORMAT = 0
PCF_INKBOUNDS = 2
PCF_ACCEL_W_INKBOUNDS = 1
PCF_COMPRESSED_METRICS = 1

pcf_format_strings = {
    PCF_DEFAULT_FORMAT: "PCF_DEFAULT_FORMAT",
    PCF_INKBOUNDS: "PCF_INKBOUNDS",
    PCF_ACCEL_W_INKBOUNDS: "PCF_ACCEL_W_INKBOUNDS",
    PCF_COMPRESSED_METRICS: "PCF_COMPRESSED_METRICS"
}

# Format Modifiers
PCF_GLYPH_PAD_MASK = 3 << 0
PCF_BYTE_MASK = 1 << 2
PCF_BIT_MASK = 1 << 3
PCF_SCAN_UNIT_MASK = 3 << 4
