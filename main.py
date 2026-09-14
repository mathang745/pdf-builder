import os
import math
from pypdf import PdfReader, PdfWriter, Transformation
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0.94, 0.95, 0.96, 1)

class CardLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class BookletApp(App):
    def build(self):
        self.title = "Booklet Studio Pro"
        main_layout = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=16)

        header_card = CardLayout(orientation='vertical', size_hint_y=0.14, padding=[16, 12], spacing=4)
        title_lbl = Label(text="[b]Booklet Studio Pro[/b]", markup=True, color=(0.11, 0.11, 0.13, 1), font_size='22sp')
        self.status = Label(text="ஒரு PDF கோப்பைத் தேர்ந்தெடுக்கவும்", color=(0.45, 0.45, 0.50, 1), font_size='13sp')
        header_card.add_widget(title_lbl)
        header_card.add_widget(self.status)
        main_layout.add_widget(header_card)

        chooser_card = CardLayout(orientation='vertical', size_hint_y=0.60, padding=[10, 10])
        dl_path = "/storage/emulated/0/Download" if os.path.exists("/storage/emulated/0/Download") else os.path.expanduser("~")
        self.chooser = FileChooserListView(path=dl_path, filters=['*.pdf', '*.PDF'])
        chooser_card.add_widget(self.chooser)
        main_layout.add_widget(chooser_card)

        control_card = CardLayout(orientation='horizontal', size_hint_y=0.10, padding=[18, 10], spacing=12)
        self.margin_lbl = Label(text="Margin: [b]10 pt[/b]", markup=True, color=(0.15, 0.15, 0.18, 1), size_hint_x=0.45, font_size='14sp')
        self.margin_slider = Slider(min=5, max=25, value=10, step=1, size_hint_x=0.55)
        self.margin_slider.bind(value=lambda inst, val: setattr(self.margin_lbl, 'text', f"Margin: [b]{int(val)} pt[/b]"))
        control_card.add_widget(self.margin_lbl)
        control_card.add_widget(self.margin_slider)
        main_layout.add_widget(control_card)

        self.btn = Button(text="🚀 Convert to 6-Up Booklet", size_hint_y=0.12, background_normal='', background_color=(0.0, 0.48, 1.0, 1), font_size='16sp', bold=True, color=(1, 1, 1, 1))
        self.btn.bind(on_press=self.process_pdf)
        main_layout.add_widget(self.btn)

        return main_layout

    def process_pdf(self, instance):
        if not self.chooser.selection:
            self.status.text = "⚠️ தயவுசெய்து ஒரு PDF கோப்பைத் தேர்வு செய்யவும்"
            return

        input_path = self.chooser.selection[0]
        self.status.text = "மாற்றப்படுகிறது... காத்திருக்கவும்"

        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            num_pages = len(reader.pages)

            A4_W, A4_H = 841.89, 595.28
            cols, rows, chunk = 3, 2, 12
            margin = int(self.margin_slider.value)
            cell_w = (A4_W - (2 * margin)) / cols
            cell_h = (A4_H - (2 * margin)) / rows

            padded = math.ceil(num_pages / chunk) * chunk

            for base in range(0, padded, chunk):
                front_seq = [base + 0, base + 2, base + 4, base + 6, base + 8, base + 10]
                back_seq = [base + 5, base + 3, base + 1, base + 11, base + 9, base + 7]

                for page_seq in [front_seq, back_seq]:
                    out_sheet = writer.add_blank_page(width=A4_W, height=A4_H)
                    for idx, p_idx in enumerate(page_seq):
                        if p_idx < num_pages:
                            r, c = idx // cols, idx % cols
                            x = margin + (c * cell_w)
                            y = A4_H - margin - ((r + 1) * cell_h)
                            
                            src_page = reader.pages[p_idx]
                            orig_w = float(src_page.mediabox.width)
                            orig_h = float(src_page.mediabox.height)
                            scale = min(cell_w / orig_w, cell_h / orig_h)
                            
                            tx = Transformation().scale(scale).translate(
                                tx=x + (cell_w - (orig_w * scale)) / 2,
                                ty=y + (cell_h - (orig_h * scale)) / 2
                            )
                            out_sheet.merge_transformed_page(src_page, tx)

            out_dir = os.path.dirname(input_path)
            out_file = os.path.join(out_dir, "OUTPUT_6UP_BOOKLET.pdf")
            with open(out_file, "wb") as f:
                writer.write(f)

            self.status.text = "✅ புதிய PDF வெற்றிகரமாக உருவானது!"
        except Exception as e:
            self.status.text = f"பிழை: {str(e)}"

if __name__ == '__main__':
    BookletApp().run()
