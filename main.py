import os
import math
import fitz
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

# iOS Style Background (Light Neutral Gray)
Window.clearcolor = (0.94, 0.95, 0.96, 1)

class CardLayout(BoxLayout):
    """iOS-style rounded card container"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1) # Pure white card
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class BookletApp(App):
    def build(self):
        self.title = "Booklet Studio Pro"
        
        main_layout = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=16)

        # 1. Header Card
        header_card = CardLayout(orientation='vertical', size_hint_y=0.14, padding=[16, 12], spacing=4)
        title_lbl = Label(
            text="[b]Booklet Studio Pro[/b]", 
            markup=True, 
            color=(0.11, 0.11, 0.13, 1), 
            font_size='22sp'
        )
        self.status = Label(
            text="ஒரு PDF கோப்பை கீழே தேர்வு செய்யவும்", 
            color=(0.45, 0.45, 0.50, 1), 
            font_size='13sp'
        )
        header_card.add_widget(title_lbl)
        header_card.add_widget(self.status)
        main_layout.add_widget(header_card)

        # 2. File Chooser Card
        chooser_card = CardLayout(orientation='vertical', size_hint_y=0.60, padding=[10, 10])
        download_path = "/storage/emulated/0/Download" if os.path.exists("/storage/emulated/0/Download") else os.path.expanduser("~")
        self.chooser = FileChooserListView(
            path=download_path, 
            filters=['*.pdf', '*.PDF']
        )
        chooser_card.add_widget(self.chooser)
        main_layout.add_widget(chooser_card)

        # 3. Controls & Margin Card
        control_card = CardLayout(orientation='horizontal', size_hint_y=0.10, padding=[18, 10], spacing=12)
        self.margin_lbl = Label(
            text="Margin: [b]10 pt[/b]", 
            markup=True,
            color=(0.15, 0.15, 0.18, 1), 
            size_hint_x=0.45,
            font_size='14sp'
        )
        self.margin_slider = Slider(min=5, max=25, value=10, step=1, size_hint_x=0.55)
        
        def on_slider_change(instance, val):
            self.margin_lbl.text = f"Margin: [b]{int(val)} pt[/b]"
        self.margin_slider.bind(value=on_slider_change)

        control_card.add_widget(self.margin_lbl)
        control_card.add_widget(self.margin_slider)
        main_layout.add_widget(control_card)

        # 4. Action Button (iOS Accent Blue)
        self.btn = Button(
            text="🚀 Convert to 6-Up Booklet", 
            size_hint_y=0.12, 
            background_normal='',
            background_color=(0.0, 0.48, 1.0, 1), 
            font_size='16sp', 
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.btn.bind(on_press=self.process_pdf)
        main_layout.add_widget(self.btn)

        return main_layout

    def process_pdf(self, instance):
        selection = self.chooser.selection
        if not selection:
            self.status.text = "⚠️ தயவுசெய்து PDF கோப்பைத் தேர்ந்தெடுக்கவும்"
            return

        input_file = selection[0]
        self.status.text = "மாற்றப்படுகிறது... சிறிது நேரம் காத்திருக்கவும்"

        try:
            src_doc = fitz.open(input_file)
            total_pages = len(src_doc)

            A4_W, A4_H = 841.89, 595.28  # Landscape A4
            COLS, ROWS, CHUNK = 3, 2, 12
            margin_pt = int(self.margin_slider.value)

            padded_total = math.ceil(total_pages / CHUNK) * CHUNK
            out_doc = fitz.open()

            for base in range(0, padded_total, CHUNK):
                front_map = [base + 0, base + 2, base + 4, base + 6, base + 8, base + 10]
                back_map = [base + 5, base + 3, base + 1, base + 11, base + 9, base + 7]

                for page_mapping in [front_map, back_map]:
                    out_page = out_doc.new_page(width=A4_W, height=A4_H)
                    cell_w = (A4_W - (2 * margin_pt)) / COLS
                    cell_h = (A4_H - (2 * margin_pt)) / ROWS

                    for idx, pno in enumerate(page_mapping):
                        r, c = idx // COLS, idx % COLS
                        x0 = margin_pt + (c * cell_w) + 2
                        y0 = margin_pt + (r * cell_h) + 2
                        x1 = margin_pt + ((c + 1) * cell_w) - 2
                        y1 = margin_pt + ((r + 1) * cell_h) - 2

                        out_page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=(0.2, 0.2, 0.2), width=0.8)
                        content_rect = fitz.Rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3)

                        if pno < total_pages:
                            src_p = src_doc[pno]
                            pix = src_p.get_pixmap(dpi=250, alpha=False)
                            out_page.insert_image(content_rect, stream=pix.tobytes("jpeg"), keep_proportion=True)
                            out_page.insert_text(fitz.Point(x0 + 6, y1 - 6), f"Pg {pno + 1}", fontsize=6.5, color=(0, 0, 0))

            output_dir = os.path.dirname(input_file)
            output_file = os.path.join(output_dir, "OUTPUT_6UP_BOOKLET.pdf")
            out_doc.save(output_file, deflate=True)
            out_doc.close()
            src_doc.close()

            self.status.text = "✅ புதிய PDF வெற்றிகரமாக உருவானது!"
        except Exception as e:
            self.status.text = f"பிழை: {str(e)}"

if __name__ == '__main__':
    BookletApp().run()
