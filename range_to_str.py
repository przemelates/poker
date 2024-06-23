import re
import sys
import cv2
import json
from dataclasses import dataclass


@dataclass
class Color:
    r: int
    g: int
    b: int

    range_name: str = ""

    def __eq__(self, other):
        margin = 25
        return all([
            abs(self.r - other.r) < margin,
            abs(self.g - other.g) < margin,
            abs(self.b - other.b) < margin
        ])

    def __hash__(self):
        return self.r * 2 + self.g * 3 + self.b * 5

    def colored_square(self):
        return f"\033[38;2;{self.r};{self.g};{self.b}m■\033[39m"


@dataclass
class Cell:
    x: int
    y: int
    color: Color

    CARDS = "AKQJT98765432"

    def get_hand_str(self):
        card1 = Cell.CARDS[min(self.x, self.y)]
        card2 = Cell.CARDS[max(self.x, self.y)]
        s = card1 + card2
        match self.x - self.y:
            case d if d < 0:
                return s + "s"
            case d if d > 0:
                return s + "o"
        return s


def iterate_image(img, cs, start_x=5, start_y=5):
    for y in range(start_y, img.shape[1], cs):
        for x in range(start_x, img.shape[0], cs):
            yield Cell(x // cs, y // cs, Color(*(int(c) for c in img[x, y])))


if __name__ == '__main__':
    if not 2 <= len(sys.argv) <= 3:
        print("Usage: \npython range_to_str.py image_file [output_file]")
        exit(1)
    is_out_file = len(sys.argv) == 3

    filename = sys.argv[1]
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    (width, height, _) = image.shape
    cell_size = round((width + height) / 26)

    colors = []
    for cell in iterate_image(image, cell_size):
        if cell.color not in colors:
            colors.append(cell.color)

    print("Please define names of ranges, ex. 'raise' for red and 'fold' for white")
    for color in colors:
        print(color.colored_square(), end=" >")
        color.range_name = input()

    hands = {color.range_name: [] for color in colors}
    for cell in iterate_image(image, cell_size):
        best_color_match = colors[colors.index(cell.color)]
        hands[best_color_match.range_name].append(cell.get_hand_str())

    out = json.dumps(hands, indent=4)
    out = re.sub(r'": \[\s+', '": [', out)
    out = re.sub(r'",\s+', '", ', out)
    out = re.sub(r'"\s+\]', '"]', out)

    if is_out_file:
        with open(sys.argv[2], "w") as file:
            file.write(out)
        exit(0)


    try:
        out_loaded = json.loads(out)
        assert sum(len(arr) for arr in out_loaded.values()) == 169, "A hand might not have loaded correctly!"

        print("""
\033[32mConversion successful!\033[39m
Use
\033[33m
with open(file_path) as f:
    my_dict = json.loads(f.read())
\033[39m
to read the saved range into python code.
            """)
    except Exception as ex:
        print(f"""
Conversion resulted in an error!
\033[31m{ex}\033[39m
        """)

    print(out)

