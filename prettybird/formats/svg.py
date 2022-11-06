import svgwrite  # type: ignore
import tempfile
import os
import subprocess
import json
import warnings

from . import Format

from ..utils import get_progressbar

from pathlib import Path

from progressbar import FormatLabel


class SVG(Format):
    def __init__(self, font_name: str, version: str, filename: str = ""):
        super().__init__(filename, font_name, version)

    def compile(self, to_ttf=False, bitmap=False):
        with tempfile.TemporaryDirectory() as temp_dir_obj:
            temp_dir = Path(temp_dir_obj)
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)

            json_data = {
                "props": {},
                "input": str(temp_dir.resolve()),
                "output": [
                    str(
                        (
                            Path.cwd()
                            / (Path(self.filename).stem if to_ttf else self.filename)
                        ).resolve()
                    )
                    + (".ttf" if to_ttf else "")
                ],
                "glyphs": {},
            }

            pbar = None
            if not all([symbol._is_function_call for symbol in self.symbols]):
                pbar, widgets = get_progressbar(len(self.symbols))

                pbar.start()
            for i, symbol in enumerate(self.symbols):
                if not symbol._is_function_call:
                    widgets[0] = FormatLabel('Symbol: {0}'.format(symbol.identifier))
                    pbar.update(i)

                svg_drawing = svgwrite.Drawing(
                    temp_dir / f"{symbol.identifier}.svg",
                    size=(f"{symbol.width * 16}px", f"{symbol.height * 16}px"),
                )

                if bitmap:
                    self.draw_bitmap_on_svg(symbol, svg_drawing)
                else:
                    self.draw_outline_on_svg(symbol, svg_drawing)

                json_data["glyphs"][hex(ord(symbol.identifier[0]))] = Path(
                    str(svg_drawing.filename)
                ).name
                svg_drawing.save()
            if pbar:
                pbar.finish()

            temp_json = tempfile.NamedTemporaryFile(mode="w")
            json.dump(json_data, temp_json)
            temp_json.flush()

            subprocess.check_output(
                f"fontforge -lang=py -script {Path(__file__).parents[1] / 'fontforge_scripts' / 'svgs2ttf' / 'svgs2ttf'} {temp_json.name}",
                shell=True,
                stderr=subprocess.STDOUT,
            )

            temp_json.close()

    @staticmethod
    def draw_bitmap_on_svg(symbol, svg_drawing):
        for x in range(symbol.width):
            for y in range(symbol.height):
                if symbol.grid[symbol.point_to_index((x, y))] != ".":
                    svg_drawing.add(
                        svg_drawing.rect(
                            insert=(x * 16, y * 16), size=("16px", "16px"))
                    )

    @staticmethod
    def _mul_tup(tup, multiplier):
        return tuple(map(lambda x: x * multiplier, tup))

    @staticmethod
    def draw_outline_on_svg(symbol, svg_drawing):
        for i, instruction in enumerate(symbol._instructions):
            instruction_name, draw_mode, filled, inputs = instruction

            if draw_mode == "draw":
                to_draw = svg_drawing
            else:
                clip_path = svg_drawing.defs.add(
                    svg_drawing.mask(id=f"{i}_{instruction_name}")
                )
                to_draw = clip_path
                to_draw.add(
                    svg_drawing.rect(insert=(0, 0), size=(
                        "100%", "100%"), fill="white")
                )

            if draw_mode == "erase":
                warnings.warn(
                    "The erase keyword is not stable with outline fonts, but may work as expected in some cases. Please check back later!",
                    UserWarning,
                )

            stroke = "black"
            stroke_width = "1px" if filled else "16px"
            fill = stroke if filled else "none"

            if instruction_name == "vector":
                to_draw.add(
                    svg_drawing.line(
                        start=SVG._mul_tup(inputs[0], 16),
                        end=SVG._mul_tup(inputs[1], 16),
                        stroke="black",
                        stroke_width="16px",
                    )
                )
            elif instruction_name == "ellipse":
                p1, p2 = SVG._mul_tup(
                    inputs[0], 16), SVG._mul_tup(inputs[1], 16)
                a = abs(p2[1] - p1[1]) / 2
                b = abs(p2[0] - p1[0]) / 2
                c = (p1[0] + b, p1[1] + a)

                to_draw.add(
                    svg_drawing.ellipse(
                        center=c,
                        r=(b, a),
                        stroke=stroke,
                        stroke_width=stroke_width,
                        fill=fill,
                    )
                )
            elif instruction_name == "rectangle":
                p1, p2 = inputs[0], inputs[1]
                w = abs(p2[0] - p1[0])
                h = abs(p2[1] - p1[1])
                to_draw.add(
                    svg_drawing.rect(
                        insert=SVG._mul_tup(p1, 16),
                        size=(w * 16, h * 16),
                        stroke=stroke,
                        stroke_width=stroke_width,
                        fill=fill,
                    )
                )
            elif instruction_name == "point":
                to_draw.add(
                    svg_drawing.circle(
                        center=SVG._mul_tup(inputs[0], 16),
                        r=16,
                        stroke=stroke,
                        stroke_width="1px",
                        fill="black",
                    )
                )
            elif instruction_name == "circle":
                to_draw.add(
                    svg_drawing.circle(
                        center=SVG._mul_tup(inputs[0], 16),
                        r=inputs[1] * 16,
                        stroke=stroke,
                        stroke_width=stroke_width,
                        fill=fill,
                    )
                )
            elif instruction_name == "square":
                to_draw.add(
                    svg_drawing.rect(
                        insert=SVG._mul_tup(inputs[0], 16),
                        size=(inputs[1] * 16, inputs[1] * 16),
                        stroke=stroke,
                        stroke_width=stroke_width,
                        fill=fill,
                    )
                )

            if draw_mode == "erase":
                for elem in svg_drawing.elements:
                    if type(elem) in (
                        svgwrite.shapes.Line,
                        svgwrite.shapes.Ellipse,
                        svgwrite.shapes.Rect,
                        svgwrite.shapes.Circle,
                    ):
                        elem["mask"] = f"url(#{i}_{instruction_name})"
