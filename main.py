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

Window.clearcolor = (0.95, 0.95, 0.97, 1)

class BookletApp(App):
    def build(self):
        self.title = "6-Up Duplex Booklet Studio"
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)

        title_lbl = Label(text="[b]6-Up Duplex Booklet Studio[/b]", markup=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=0.08, font_size='20sp')
        root.add_widget(title_lbl)

        self.status = Label(text="கீழே ஒரு PDF-ஐத் தேர்ந்தெடுக்கவும்", color=(0.3, 0.3, 0.3, 1), size_hint_y=0.06, font_size='14sp')
        root.add_widget(self.status)

        download_path = "/storage/emulated/0/Download" if os.path.exists("/storage/emulated/0/Download") else os.path.expanduser("~")
        self.chooser = FileChooserListView(path=download_path, filters=['*.pdf', '*.PDF'], size_hint_y=0.65)
        root.add_widget(self.chooser)

        slider_box = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        slider_lbl = Label(text="Margin: 10pt", color=(0.2, 0.2, 0.2, 1), size_hint_x=0.4)
        self.margin_slider = Slider(min=5, max=25, value=10, step=1, size_hint_x=0.6)
        def on_slider_val(instance, val):
            slider_lbl.text = f"Margin: {int(val)}pt"
        self.margin_slider.bind(value=on_slider_val)
        slider_box.add_widget(slider_lbl)
        slider_box.add_widget(self.margin_slider)
        root.add_widget(slider_box)

        self.btn = Button(text="🚀 Convert to 6-Up Booklet PDF", size_hint_y=0.13, background_color=(0.0, 0.47, 0.89, 1), font_size='16sp', bold=True)
        self.btn.bind(on_press=self.process_pdf)
        root.add_widget(self.btn)

        return root

    def process_pdf(self, instance):
        selection = self.chooser.selection
        if not selection:
            self.status.text = "⚠️ ஒரு PDF கோப்பைத் தேர்ந்தெடுக்கவும்!"
            return

        input_file = selection[0]
        self.status.text = "வேலை நடக்கிறது, காத்திருக்கவும்..."

        try:
            src_doc = fitz.open(input_file)
            total_pages = len(src_doc)

            A4_W, A4_H = 841.89, 595.28
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

                        out_page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=(0.15, 0.15, 0.15), width=0.8)
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

            self.status.text = "✅ வெற்றி! புதிய PDF உருவாக்கப்பட்டது!"
        except Exception as e:
            self.status.text = f"பிழை: {str(e)}"

if __name__ == '__main__':
    BookletApp().run()
