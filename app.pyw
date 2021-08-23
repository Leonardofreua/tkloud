from dataclasses import dataclass, field
from os import path
from tkinter import Button, Frame, Label, Spinbox, StringVar, Text, Tk, filedialog, messagebox
from tkinter.colorchooser import askcolor
from tkinter.constants import BOTH, END, LEFT, X
from tkinter.ttk import Combobox
from enum import Enum
from typing import Optional, Tuple, Union, Set

from wordcloud import WordCloud

WINDOW_WIDTH = 50
WINDOW_HEIGHT = 50

# fmt: off
colormap_values = ["Accent", "Accent_r", "Blues", "Blues_r", "BrBG", "BrBG_r", "BuGn", "BuGn_r", "BuPu", "BuPu_r", "CMRmap", "CMRmap_r", "Dark2", "Dark2_r", "GnBu", "GnBu_r", "Greens", "Greens_r", "Greys", "Greys_r", "OrRd", "OrRd_r", "Oranges", "Oranges_r", "PRGn", "PRGn_r", "Paired", "Paired_r", "Pastel1", "Pastel1_r", "Pastel2", "Pastel2_r", "PiYG", "PiYG_r", "PuBu", "PuBuGn", "PuBuGn_r", "PuBu_r", "PuOr", "PuOr_r", "PuRd", "PuRd_r", "Purples", "Purples_r", "RdBu", "RdBu_r", "RdGy", "RdGy_r", "RdPu", "RdPu_r", "RdYlBu", "RdYlBu_r", "RdYlGn", "RdYlGn_r", "Reds", "Reds_r", "Set1", "Set1_r", "Set2", "Set2_r", "Set3", "Set3_r", "Spectral", "Spectral_r", "Wistia", "Wistia_r", "YlGn", "YlGnBu", "YlGnBu_r", "YlGn_r", "YlOrBr", "YlOrBr_r", "YlOrRd", "YlOrRd_r", "afmhot", "afmhot_r", "autumn", "autumn_r", "binary", "binary_r", "bone", "bone_r", "brg", "brg_r", "bwr", "bwr_r", "cividis", "cividis_r", "cool", "cool_r", "coolwarm", "coolwarm_r", "copper", "copper_r", "cubehelix", "cubehelix_r", "flag", "flag_r", "gist_earth", "gist_earth_r", "gist_gray", "gist_gray_r", "gist_heat", "gist_heat_r", "gist_ncar", "gist_ncar_r", "gist_rainbow", "gist_rainbow_r", "gist_stern", "gist_stern_r", "gist_yarg", "gist_yarg_r", "gnuplot", "gnuplot2", "gnuplot2_r", "gnuplot_r", "gray", "gray_r", "hot", "hot_r", "hsv", "hsv_r", "inferno", "inferno_r", "jet", "jet_r", "magma", "magma_r", "nipy_spectral", "nipy_spectral_r", "ocean", "ocean_r", "pink", "pink_r", "plasma", "plasma_r", "prism", "prism_r", "rainbow", "rainbow_r", "seismic", "seismic_r", "spring", "spring_r", "summer", "summer_r", "tab10", "tab10_r", "tab20", "tab20_r", "tab20b", "tab20b_r", "tab20c", "tab20c_r", "terrain", "terrain_r", "turbo", "turbo_r", "twilight", "twilight_r", "twilight_shifted", "twilight_shifted_r", "viridis", "viridis_r", "winter", "winter_r"]


class FormException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Application(Frame):
    def __init__(self, root: Tk) -> None:
        Frame.__init__(self, root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self._root = root
        self._setup_window()
        Form(self._root).build()

    def _setup_window(self) -> None:
        self._root.title("Cloud Words Generator")
        self._root.resizable(False, False)

class FieldUtils:
    @staticmethod
    def get_text_value(field: Text) -> str:
        return field.get("1.0", END).strip()

    @staticmethod
    def get_box_value(field: Union[Spinbox, Combobox]) -> str:
        return field.get().strip()


FONT = "Helvetica 11 bold"

MIN_WIDTH_IMAGE = 400
MAX_WIDTH_IMAGE = 3000
MIN_HEIGHT_IMAGE = 200
MAX_HEIGHT_IMAGE = 1500
MIN_NUM_WORDS = 200
MAX_NUM_WORDS = 400

LIGHT_GREEN = "#40d971"
LIGHT_BLUE = "#84c3be"


class FieldsValidator:
    @staticmethod
    def validate_text_content(textual_content: str) -> None:
        if not textual_content or textual_content == "\n":
            raise FormException("Textual content cannot be empty.")

    @staticmethod
    def validate_width(width: str) -> None:
        if not width:
            raise FormException("Width cannot be empty.")
        
        width = int(width)
        if width <= 0:
            raise FormException("Width cannot be less equal to zero.")

        if width < MIN_WIDTH_IMAGE or width > MAX_WIDTH_IMAGE:
            raise FormException(f"Width needs to be between {MIN_WIDTH_IMAGE} and {MAX_WIDTH_IMAGE}.")

    @staticmethod
    def validate_height(height: str) -> None:
        if not height:
            raise FormException("Height cannot be empty.")

        height = int(height)
        if height <= 0:
            raise FormException("Height cannot be less equal to zero.")

        if height < MIN_HEIGHT_IMAGE or height > MAX_HEIGHT_IMAGE:
            raise FormException(f"Height needs to be between {MIN_HEIGHT_IMAGE} and {MAX_HEIGHT_IMAGE}.")

    @staticmethod
    def validate_max_words(max_words: str) -> None:
        if not max_words:
            raise FormException("Max Words cannot be empty.")

        max_words = int(max_words)
        if max_words <= 0:
            raise FormException("Max Words cannot be less equal to zero.")

        if max_words < MIN_NUM_WORDS or max_words > MAX_NUM_WORDS:
            raise FormException(f"Max words needs to be between {MIN_NUM_WORDS} and {MAX_NUM_WORDS}.")

    @staticmethod
    def validate_file_path(file_path: str) -> None:
        if not file_path or path.basename(file_path).split(".")[0].isspace():
            raise FormException("File name cannot be empty.")


class ImageExtensions(Enum):
    PNG = ".png"
    JPEG = ".jpg"


@dataclass
class Image:
    textual_content: str
    width: int
    height: int
    max_words: int
    background_color: str
    colormap: str = field(default_factory="Accent")
    stopwords: Set[str] = field(default_factory=set)
    file_path: str = ""

    def __post_init__(self):
        if self.background_color is None:
            self.background_color = "black"


class Form:
    def __init__(self, root: Tk) -> None:
        self._main_frame = Frame(root)
        self._main_frame.pack(fill=BOTH, expand=1)

        self._textual_content_frame = Frame(self._main_frame)
        self._textual_content_frame.pack(fill=BOTH, expand=1, ipadx=10, ipady=10)

        self._left_frame = Frame(self._main_frame)
        self._left_frame.pack(side=LEFT, fill=BOTH, expand=1, padx=50)

        self._right_frame = Frame(self._main_frame)
        self._right_frame.pack(fill=BOTH, expand=1, padx=10)

        self._center_frame = Frame(root)
        self._center_frame.pack(fill=X, expand=1, ipadx=15, padx=15)

        self._textual_content_field: Text
        self._width_field: Spinbox
        self._height_field: Spinbox
        self._max_words_field: Spinbox
        self._background_color_field: str = ""
        self._colormap_field: Combobox
        self._stopwords_field: Text
        self._file_path_field: StringVar = StringVar()

    def build(self) -> None:
        self._add_textual_content_field()
        self._add_width_image_field()
        self._add_height_image_field()
        self._add_max_words_field()
        self._add_background_color_button()
        self._add_select_colormap_combobox()
        self._add_stopwords_field()
        self._add_location_save_file_button()
        self._add_submit_button()

    def _add_textual_content_field(self) -> None:
        Label(self._textual_content_frame, text="Text", font=FONT).pack(ipady=5)
        self._textual_content_field = Text(self._textual_content_frame, width=90, height=15)
        self._textual_content_field.pack()

    def _add_width_image_field(self) -> None:
        Label(
            self._left_frame,
            text="Width",
            font=FONT).pack(fill=X, ipady=5)
        self._width_field = Spinbox(self._left_frame, from_=MIN_WIDTH_IMAGE, to=MAX_WIDTH_IMAGE)
        self._width_field.pack(pady=5)

    def _add_height_image_field(self) -> None:
        Label(
            self._left_frame,
            text="Height",
            font=FONT).pack(fill=X, ipady=5)
        self._height_field = Spinbox(self._left_frame, from_=MIN_HEIGHT_IMAGE, to=MAX_HEIGHT_IMAGE)
        self._height_field.pack(pady=5)

    def _add_max_words_field(self) -> None:
        Label(
            self._left_frame,
            text="Max Words",
            justify=LEFT,
            font=FONT).pack(fill=X, ipady=5)
        self._max_words_field = Spinbox(self._left_frame, from_=MIN_NUM_WORDS, to=MAX_NUM_WORDS)
        self._max_words_field.pack(pady=5)

    def _add_background_color_button(self) -> None:
        Label(
            self._right_frame,
            text="Default: Black",
            font=FONT).pack(fill=X, ipady=5)
        Button(
            self._right_frame,
            text="Select image background color",
            bg=LIGHT_BLUE,
            activebackground=LIGHT_BLUE,
            command=self._background_colorpicker).pack(pady=5)

    def _background_colorpicker(self) -> None:
        colors = askcolor(title="Image background selector")
        self._background_color_field = colors[1]

    def _add_select_colormap_combobox(self) -> None:
        Label(
            self._right_frame,
            text="Colormap (Font)",
            font=FONT).pack(fill=X, ipady=5)
        self._colormap_field = Combobox(
            self._right_frame,
            values=colormap_values,
            textvariable=StringVar(),
            state="readonly",
            width=20)
        self._colormap_field.current(0)
        self._colormap_field.pack(pady=5)

    def _add_stopwords_field(self) -> None:
        Label(
            self._right_frame,
            text="Words you want to exclude (Separete with comma)",
            font=FONT).pack(fill=X, ipady=5)
        self._stopwords_field = Text(self._right_frame, width=45, height=3)
        self._stopwords_field.pack(pady=5)

    def _add_location_save_file_button(self) -> None:
        Button(
            self._center_frame,
            text="Where to save?",
            bg=LIGHT_BLUE,
            activebackground=LIGHT_BLUE,
            command=self._ask_saveas_file_name).pack(pady=50)

    def _ask_saveas_file_name(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Where to save your word cloud?",
            confirmoverwrite=False,
            filetypes=self._get_image_extensions())
        self._file_path_field.set(path)

    def _add_submit_button(self) -> None:
        Button(
            self._center_frame,
            text="Generate",
            command=self._generate_word_cloud_image,
            width=12,
            height=2,
            font=FONT,
            activebackground=LIGHT_GREEN,
            bg=LIGHT_GREEN).pack(pady=30)

    def _get_textual_content(self) -> str:
        textual_content = FieldUtils.get_text_value(self._textual_content_field)
        FieldsValidator.validate_text_content(textual_content)
        return textual_content

    def _get_dimensions(self) -> Tuple[int, int]:
        width = FieldUtils.get_box_value(self._width_field)
        height = FieldUtils.get_box_value(self._height_field)
        FieldsValidator.validate_width(width)
        FieldsValidator.validate_height(height)
        return int(width), int(height)

    def _get_max_words(self) -> int:
        max_words = FieldUtils.get_box_value(self._max_words_field)
        FieldsValidator.validate_max_words(max_words)
        return int(max_words)

    def _get_background_color(self) -> Optional[str]:
        if self._background_color_field:
            return self._background_color_field
        return None

    def _get_colormap(self) -> str:
        return FieldUtils.get_box_value(self._colormap_field)

    def _get_stopwords(self) -> Optional[Set[str]]:
        stopword_values = FieldUtils.get_text_value(self._stopwords_field)
        if stopword_values:
            return set(filter(None, [word.strip() for word in stopword_values.split(",")]))
        return None

    def _get_file_path(self) -> str:
        file_path = self._file_path_field.get()
        FieldsValidator.validate_file_path(file_path)
        return file_path

    @staticmethod
    def _get_image_extensions():
        return tuple([(extension.name, extension.value) for extension in ImageExtensions])

    def _build_image_object(self) -> Image:
        textual_content = self._get_textual_content()
        width, height = self._get_dimensions()
        max_words = self._get_max_words()
        background_color = self._get_background_color()
        colormap = self._get_colormap()
        stopwords = self._get_stopwords()
        file_path = self._get_file_path()
        
        return Image(
            textual_content, 
            width, height,
            max_words, 
            background_color,
            colormap,
            stopwords,
            file_path
        )

    def _reset_file_path(self) -> None:
        self._file_path_field = StringVar()

    def _generate_word_cloud_image(self) -> None:
        try:
            image = self._build_image_object()
            wordcloud = WordCloud(
                    width=image.width,
                    height=image.height,
                    random_state=1,
                    background_color=image.background_color,
                    colormap=image.colormap,
                    collocations=False,
                    max_words=image.max_words,
                    stopwords=image.stopwords).generate(image.textual_content)

            file_path = image.file_path

            wordcloud.to_file(file_path)
            self._reset_file_path()
            
            success_message = (
                "Your Word Cloud has been successfully generated."
                " You can find it on the path below:\n\n"
                f"{file_path}"
            )
            messagebox.showinfo("Success", success_message)
        except FormException as e:
            messagebox.showerror("error", e)


def main() -> None:
    root = Tk()
    Application(root).pack(fill=BOTH, expand=1)
    root.mainloop()

if __name__ == "__main__":
    main()
