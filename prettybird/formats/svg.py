import svgwrite
import tempfile
import os
import subprocess
import json

from xml.dom import minidom
import xml.etree.ElementTree as ET

from prettybird.formats import Format

from pathlib import Path


class SVG(Format):
    def __init__(self, font_name: str, version: str, filename: str = None):
        super().__init__(filename, font_name, version)

    def compile(self):
        with Path(tempfile.TemporaryDirectory().name) as temp_dir:
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)
            json_data = {
                "props": {},
                "input": str(temp_dir.resolve()),
                "output": [str((Path.cwd() / (self.filename)).resolve()) + ".ttf"],
                "glyphs": {},
            }
            for symbol in self.symbols:
                svg_drawing = svgwrite.Drawing(
                    temp_dir / f"{symbol.identifier}.svg",
                    size=(f"{symbol.width}px", f"{symbol.height}px"),
                )
                for x in range(symbol.width):
                    for y in range(symbol.height):
                        if symbol.grid[symbol.point_to_index((x, y))] != ".":
                            svg_drawing.add(
                                svg_drawing.rect(insert=(x * 16, y * 16), size=("16px", "16px"))
                            )
                json_data["glyphs"][hex(ord(symbol.identifier[0]))] = Path(str(svg_drawing.filename)).name
                svg_drawing.save()
            temp_json = tempfile.NamedTemporaryFile(mode="w")
            json.dump(json_data, temp_json)
            temp_json.flush()
            subprocess.check_output(
                f"fontforge -lang=py -script {Path(__file__).parents[1] / 'fontforge_scripts' / 'svgs2ttf' / 'svgs2ttf'} {temp_json.name}",
                shell=True,
                stderr=subprocess.STDOUT
            )
            temp_json.close()
