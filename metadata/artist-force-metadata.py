from mutagen.easyid3 import EasyID3
import mutagen
import os

def change_artist_multiple_files(directory_path, artist):
    for filename in os.listdir(directory_path):
        if filename.endswith(".mp3"):
            file_path = os.path.join(directory_path, filename)
            try:
                audio = EasyID3(file_path)
                audio['artist'] = artist
                audio.save()
                print(f"O artista do arquivo '{file_path}' foi alterado para '{artist}'.")
            except mutagen.id3.ID3NoHeaderError:
                audio = mutagen.File(file_path, easy=True)
                audio.add_tags()
                audio['artist'] = artist
                audio.save()
                print(f"ID3 tag adicionada e o artista do arquivo '{file_path}' foi alterado para '{artist}'.")

if __name__ == "__main__":
    directory_path = input("Por favor, insira o caminho do diretório onde os arquivos MP3 estão localizados: ")
    artist = input("Por favor, insira o nome do artista participante: ")
    change_artist_multiple_files(directory_path, artist)