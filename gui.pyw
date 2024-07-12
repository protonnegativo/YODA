import os
import tkinter as tk
from tkinter import ttk, messagebox
from run import baixar_playlist, list_mp3_metadata
from mutagen.easyid3 import EasyID3, ID3
from mutagen import MutagenError

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("YODA - Youtube Online Download Assistant")
        self.create_widgets()
        self.update_frame = None

    def create_widgets(self):
        self.url_label = tk.Label(self.root, text="URL da Playlist do YouTube:", font=("Arial", 12))
        self.url_label.grid(row=0, column=0, padx=10, pady=10)

        self.url_entry = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        self.download_choice = tk.StringVar(value="mp3")
        self.mp3_radio = tk.Radiobutton(self.root, text="Apenas MP3", variable=self.download_choice, value="mp3", font=("Arial", 12))
        self.mp3_radio.grid(row=1, column=0, padx=10, pady=10)

        self.mp4_radio = tk.Radiobutton(self.root, text="Apenas MP4", variable=self.download_choice, value="mp4", font=("Arial", 12))
        self.mp4_radio.grid(row=1, column=1, padx=10, pady=10)

        self.both_radio = tk.Radiobutton(self.root, text="Ambos MP3 e MP4", variable=self.download_choice, value="both", font=("Arial", 12))
        self.both_radio.grid(row=1, column=2, padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Iniciar Download", command=self.start_download, font=("Arial", 12))
        self.start_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        self.files_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.files_label.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

        self.tree = ttk.Treeview(self.root, columns=("Select", "Filename", "Title", "Artist", "Album", "Album Artist", "Date"), show="headings", selectmode="none")
        self.tree.heading("Select", text="Select", command=self.toggle_all)
        self.tree.heading("Filename", text="Nome do Arquivo")
        self.tree.heading("Title", text="Título")
        self.tree.heading("Artist", text="Artista")
        self.tree.heading("Album", text="Álbum")
        self.tree.heading("Album Artist", text="Artistas do Álbum")
        self.tree.heading("Date", text="Data")
        self.tree.column("Select", width=50, anchor='center')
        self.tree.column("Filename", width=250)
        self.tree.column("Title", width=200)
        self.tree.column("Artist", width=150)
        self.tree.column("Album", width=150)
        self.tree.column("Album Artist", width=150)
        self.tree.column("Date", width=100)
        self.tree.grid(row=4, column=0, padx=10, pady=10, columnspan=3)

        self.tree.bind("<Button-1>", self.on_treeview_click)

    def start_download(self):
        url = self.url_entry.get().strip()
        download_choice = self.download_choice.get()

        if not url:
            messagebox.showerror("Erro", "Por favor, insira a URL da playlist do YouTube.")
            return

        try:
            self.mp3_folder, self.playlist_title = baixar_playlist(download_choice, url)
            if self.mp3_folder:
                self.mp3_metadata = list_mp3_metadata(self.mp3_folder)
                self.show_files()
                self.create_update_frame()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def show_files(self):
        self.files_label.config(text="Arquivos MP3 encontrados:")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for metadata in self.mp3_metadata:
            self.tree.insert("", tk.END, values=("☐", metadata['filename'], metadata['title'], metadata['artist'], metadata['album'], metadata.get('albumartist', ''), metadata['date']))

    def create_update_frame(self):
        if self.update_frame:
            self.update_frame.destroy()
        
        self.update_frame = tk.Frame(self.root)
        self.update_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.update_frame, text="Título:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.title_entry = tk.Entry(self.update_frame, width=20, font=("Arial", 12))
        self.title_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.update_frame, text="Artista:", font=("Arial", 12)).grid(row=0, column=2, padx=5)
        self.artist_entry = tk.Entry(self.update_frame, width=20, font=("Arial", 12))
        self.artist_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.update_frame, text="Álbum:", font=("Arial", 12)).grid(row=0, column=4, padx=5)
        self.album_entry = tk.Entry(self.update_frame, width=20, font=("Arial", 12))
        self.album_entry.grid(row=0, column=5, padx=5)

        tk.Label(self.update_frame, text="Artistas do Álbum:", font=("Arial", 12)).grid(row=0, column=6, padx=5)
        self.album_artist_entry = tk.Entry(self.update_frame, width=20, font=("Arial", 12))
        self.album_artist_entry.grid(row=0, column=7, padx=5)

        tk.Label(self.update_frame, text="Data:", font=("Arial", 12)).grid(row=1, column=0, padx=5)
        self.date_entry = tk.Entry(self.update_frame, width=10, font=("Arial", 12))
        self.date_entry.grid(row=1, column=1, padx=5)

        self.apply_button = tk.Button(self.update_frame, text="Aplicar", command=self.apply_changes, font=("Arial", 12))
        self.apply_button.grid(row=1, column=8, padx=10)

    def toggle_all(self):
        current_state = self.tree.heading("Select")["text"]
        new_state = "☑" if current_state == "☐" else "☐"
        self.tree.heading("Select", text=new_state)

        for item in self.tree.get_children():
            self.tree.set(item, column="Select", value=new_state)

    def on_treeview_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Column 1 is the 'Select' column
                item = self.tree.identify_row(event.y)
                current_value = self.tree.set(item, "Select")
                new_value = "☑" if current_value == "☐" else "☐"
                self.tree.set(item, column="Select", value=new_value)

    def apply_changes(self):
        selected_items = [item for item in self.tree.get_children() if self.tree.set(item, "Select") == "☑"]
        
        if not selected_items:
            messagebox.showerror("Erro", "Por favor, selecione pelo menos um arquivo para aplicar as mudanças.")
            return

        new_title = self.title_entry.get().strip()
        new_artist = self.artist_entry.get().strip()
        new_album = self.album_entry.get().strip()
        new_album_artist = self.album_artist_entry.get().strip()
        new_date = self.date_entry.get().strip()

        for item in selected_items:
            filename = self.tree.item(item, 'values')[1]
            file_path = os.path.join(self.mp3_folder, filename)

            # Debugging message to ensure file path is correct
            print(f"Updating file: {file_path}")

            try:
                audiofile = EasyID3(file_path)
            except ID3.NoHeaderError:
                audiofile = EasyID3()
                audiofile.save(file_path)

            try:
                if new_title:
                    audiofile['title'] = new_title
                if new_artist:
                    audiofile['artist'] = new_artist
                if new_album:
                    audiofile['album'] = new_album
                if new_album_artist:
                    audiofile['albumartist'] = new_album_artist
                if new_date:
                    audiofile['date'] = new_date

                audiofile.save()

                # Debugging message to confirm save
                print(f"Updated metadata for: {file_path}")

                metadata = {
                    'filename': filename,
                    'title': audiofile.get('title', [''])[0],
                    'artist': audiofile.get('artist', [''])[0],
                    'album': audiofile.get('album', [''])[0],
                    'albumartist': audiofile.get('albumartist', [''])[0],
                    'date': audiofile.get('date', [''])[0]
                }
                self.tree.item(item, values=("☑", metadata['filename'], metadata['title'], metadata['artist'], metadata['album'], metadata['albumartist'], metadata['date']))
            except MutagenError as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar os metadados: {e}")
                print(f"MutagenError: {e}")

        messagebox.showinfo("Sucesso", "Metadados atualizados com sucesso.")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
