
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageEnhance

class WatermarkApp:
    def __init__(self, master):
        self.master = master
        master.title("Watermark Application")
        master.geometry("600x700")  # Set a fixed window size to ensure everything fits

        self.input_dir = ""
        self.output_dir = ""
        self.watermark_path = ""
        self.current_image = None
        self.watermarked_image = None
        self.preview_size = (400, 400)

        self.opacity = tk.DoubleVar(value=0.5)
        self.size_percent = tk.IntVar(value=25)
        self.position_x = tk.DoubleVar(value=0.5)
        self.position_y = tk.DoubleVar(value=0.5)
        self.tile_var = tk.BooleanVar(value=False)

        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):
        # Creating a frame to organize widgets vertically
        frame = ttk.Frame(self.master)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Buttons for selecting input directory, output directory, and watermark
        ttk.Button(frame, text="Select Input Directory", command=self.select_input_dir).pack(pady=5, fill='x')
        self.input_label = ttk.Label(frame, text="No input directory selected")
        self.input_label.pack(pady=5)

        ttk.Button(frame, text="Select Output Directory", command=self.select_output_dir).pack(pady=5, fill='x')
        self.output_label = ttk.Label(frame, text="No output directory selected")
        self.output_label.pack(pady=5)

        ttk.Button(frame, text="Select Watermark", command=self.select_watermark).pack(pady=5, fill='x')
        self.watermark_label = ttk.Label(frame, text="No watermark selected")
        self.watermark_label.pack(pady=5)

        self.create_slider(frame, "Opacity", self.opacity, 0, 1, 0.1)
        self.create_slider(frame, "Size (%)", self.size_percent, 1, 100, 1)
        self.create_slider(frame, "X Position", self.position_x, 0, 1, 0.01)
        self.create_slider(frame, "Y Position", self.position_y, 0, 1, 0.01)

        ttk.Checkbutton(frame, text="Tile Watermark", variable=self.tile_var, command=self.update_preview).pack(pady=5)

        self.preview_canvas = tk.Canvas(frame, width=self.preview_size[0], height=self.preview_size[1], bg='grey')
        self.preview_canvas.pack(pady=10)

    def create_slider(self, parent_frame, label, variable, from_, to, resolution):
        frame = ttk.Frame(parent_frame)
        frame.pack(pady=5, fill='x')
        ttk.Label(frame, text=label).pack(side='left')
        slider = ttk.Scale(frame, from_=from_, to=to, orient='horizontal', variable=variable, command=self.update_preview)
        slider.pack(side='right', expand=True, fill='x')
        slider.set(variable.get())

    def bind_keys(self):
        # Bind the keyboard shortcut Ctrl+S to save the image
        self.master.bind('<Control-s>', self.save_image_with_shortcut)

    def select_input_dir(self):
        self.input_dir = filedialog.askdirectory()
        self.input_label.config(text=f"Input: {self.input_dir}")
        self.load_first_image()

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        self.output_label.config(text=f"Output: {self.output_dir}")

    def select_watermark(self):
        self.watermark_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        self.watermark_label.config(text=f"Watermark: {os.path.basename(self.watermark_path)}")
        self.update_preview()

    def load_first_image(self):
        if self.input_dir:
            for filename in os.listdir(self.input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.current_image = Image.open(os.path.join(self.input_dir, filename))
                    self.update_preview()
                    break

    def update_preview(self, *args):
        if self.current_image and self.watermark_path:
            preview_image = self.current_image.copy()
            preview_image.thumbnail(self.preview_size)

            watermark = Image.open(self.watermark_path).convert('RGBA')

            watermark_size = (int(preview_image.width * self.size_percent.get() / 100),
                              int(preview_image.height * self.size_percent.get() / 100))
            watermark = watermark.resize(watermark_size, Image.LANCZOS)

            enhancer = ImageEnhance.Brightness(watermark.split()[3])
            alpha = enhancer.enhance(self.opacity.get())
            watermark.putalpha(alpha)

            if self.tile_var.get():
                tiled_watermark = Image.new('RGBA', preview_image.size)
                for y in range(0, preview_image.height, watermark.height):
                    for x in range(0, preview_image.width, watermark.width):
                        tiled_watermark.paste(watermark, (x, y))
                preview_watermarked = Image.alpha_composite(preview_image.convert('RGBA'), tiled_watermark)
            else:
                x = int((preview_image.width - watermark.width) * self.position_x.get())
                y = int((preview_image.height - watermark.height) * self.position_y.get())

                preview_watermarked = preview_image.copy().convert('RGBA')
                preview_watermarked.paste(watermark, (x, y), watermark)

            self.photo = ImageTk.PhotoImage(preview_watermarked)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

            # Store the watermarked image in case the user wants to save it later
            self.watermarked_image = preview_watermarked

    def save_image_with_shortcut(self, event=None):
        """Save the image when Ctrl+S is pressed."""
        if self.watermarked_image and self.output_dir:
            save_path = os.path.join(self.output_dir, "watermarked_image.png")
            self.watermarked_image.convert('RGB').save(save_path, 'PNG', quality=95)
            print(f"Saved watermarked image to {save_path}")
            messagebox.showinfo("Save", f"Watermarked image saved to {save_path}")
        else:
            messagebox.showwarning("No image", "No watermarked image to save.")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()




