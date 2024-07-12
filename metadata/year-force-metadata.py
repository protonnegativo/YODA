from mutagen.easyid3 import EasyID3
import mutagen
import os

def change_year_multiple_files(directory_path, new_year):
    for filename in os.listdir(directory_path):
        if filename.endswith(".mp3"):
            file_path = os.path.join(directory_path, filename)
            try:
                audio = EasyID3(file_path)
                audio['date'] = str(new_year)
                audio.save()
                print(f"O ano do arquivo '{file_path}' foi alterado para {new_year}.")
            except mutagen.id3.ID3NoHeaderError:
                audio = mutagen.File(file_path, easy=True)
                audio.add_tags()
                audio['date'] = str(new_year)
                audio.save()
                print(f"ID3 tag adicionada e o ano do arquivo '{file_path}' foi alterado para {new_year}.")

if __name__ == "__main__":
    directory_path = input("Por favor, insira o caminho do diretório onde os arquivos MP3 estão localizados: ")
    new_year = input("Por favor, insira o ano que você deseja colocar: ")
    change_year_multiple_files(directory_path, new_year)
