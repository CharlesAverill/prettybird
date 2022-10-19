# https://adobe-type-tools.github.io/font-tech-notes/pdfs/5005.BDF_Spec.pdf
# https://en.wikipedia.org/wiki/Glyph_Bitmap_Distribution_Format

from . import Format

class BDF(Format):
    def __init__(self, font_name: str, version: str, point_size: int = 16, bounding_box: tuple[int, int] = (6, 8), properties: list[tuple] = [], filename: str = ""):     
        super().__init__(filename, font_name, version)

        self.file = None
        self.point_size = point_size
        self.bounding_box = bounding_box
        self.properties = properties

        self.symbols = []

        self.compiled = False

    def compile(self, to_ttf=False):
        if to_ttf:
            raise NotImplementedError("BDF -> TTF conversion not supported")
        
        self.file = open(self.filename, "w")

        self.file.write(f"STARTFONT {str(self.version)}\n")
        self.file.write(f"FONT {self.font_name}\n")
        self.file.write(f"SIZE {self.point_size} 75 75\n")
        self.file.write(f"FONTBOUNDINGBOX {self.bounding_box[0]} {self.bounding_box[1]} 0 -1\n")
        self.file.write(f"COMMENT Compiled with prettybird, https://github.com/CharlesAverill/prettybird\n")

        if self.properties and len(self.properties):
            self.file.write(f"STARTPROPERTIES {len(self.properties)}\n")
            for property in self.properties:
                self.file.write(" ".join([str(p) for p in property]) + "\n")
            self.file.write("ENDPROPERTIES\n")
        
        if self.symbols and len(self.symbols):
            self.file.write(f"CHARS {len(self.symbols)}\n")

            for symbol in self.symbols:
                self.file.write(f"STARTCHAR {symbol.identifier}\n")
                self.file.write(f"ENCODING {symbol.encoding}\n")
                self.file.write(f"SWIDTH 500 0\n")
                self.file.write(f"DWIDTH {symbol.width} 0\n")
                self.file.write(f"BBX {symbol.width} {symbol.height} 0 0\n")
                self.file.write(f"BITMAP\n")
                self.file.write(symbol.grid_hex_repr())
                self.file.write("ENDCHAR\n")

        self.file.write("ENDFONT\n")

        self.file.close()

        self.compiled = True
    
    """
    def convert_to_ttf(self):
        if not self.compiled:
            raise RuntimeError("Can't convert BDF to TTF before compilation")
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".ini")
        tmpfile.write(f"Fontname = {self.font_name}\n".encode())
        tmpfile.close()

        bdf2ttf_path = Path(__file__).parents[2] / "lib" / "bdf2ttf" / "bdf2ttf"

        if "." not in self.filename:
            self.filename += "."

        cmd = f"{bdf2ttf_path.absolute()} {self.filename[:self.filename.rindex('.')]}.ttf {tmpfile.name} {self.filename}"
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        os.remove(tmpfile.name)
    """
