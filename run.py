import os
import sys
from pytube import Playlist
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
import datetime
from pydub import AudioSegment

# Global variable to control if spotify.py has been executed
spotify_executado = False

# Add the directory to the Python search path
sys.path.append(os.path.join(os.getcwd(), 'metadata'))

def obter_data_publicacao(video):
    return video.publish_date

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_and_convert_video(video, idx, mp4_folder, mp3_folder, playlist_title):
    try:
        # Download video
        video.streams.get_highest_resolution().download(output_path=mp4_folder)
        original_file_name = video.streams.get_highest_resolution().default_filename
        mp4_path = os.path.join(mp4_folder, original_file_name)
        os.rename(os.path.join(mp4_folder, original_file_name), mp4_path)

        # Convert to MP3
        mp3_path = os.path.join(mp3_folder, original_file_name[:-4] + ".mp3")
        audio = AudioSegment.from_file(mp4_path)
        audio.export(mp3_path, format="mp3")

        # Add metadata
        data_publicacao = obter_data_publicacao(video)
        ano_publicacao = data_publicacao.year if data_publicacao else datetime.datetime.now().year

        audiofile = EasyID3(mp3_path)
        audiofile['tracknumber'] = str(idx)
        audiofile['title'] = video.title
        audiofile['artist'] = video.author
        audiofile['albumartist'] = "Powered by Proton Negativo."
        audiofile['website'] = f"{video.watch_url}?year={ano_publicacao}"
        audiofile['album'] = playlist_title
        audiofile['date'] = str(ano_publicacao)
        audiofile.save()
    except Exception as e:
        print(f"Erro ao processar vídeo {video.title}: {e}")

def main():
    global spotify_executado
    try:
        link_playlist = input("Insira a URL da playlist do YouTube: ")
        playlist = Playlist(link_playlist)
        playlist_title = playlist.title
        download_folder = "downloads"

        create_folder_if_not_exists(download_folder)
        mp3_folder = os.path.join(download_folder, "mp3")
        mp4_folder = os.path.join(download_folder, "mp4")
        create_folder_if_not_exists(mp3_folder)
        create_folder_if_not_exists(mp4_folder)

        print(f"Baixando playlist: {playlist_title}")
        for idx, video in enumerate(tqdm(playlist.videos, desc="Baixando vídeos"), start=1):
            download_and_convert_video(video, idx, mp4_folder, mp3_folder, playlist_title)

        print("Download, conversão para MP3, adição de metadados e salvamento na pasta concluídos!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        if not spotify_executado:
            import spotify
            spotify.executar_funcao()
            spotify_executado = True
            print("A função do Spotify foi executada!")

def read_keys_file(file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    abs_file_path = os.path.join(current_dir, "secret", file_path)
    with open(abs_file_path, 'r') as file:
        keys = file.read().strip()
    return keys

def executar_funcao():
    print("Executando função do Spotify...")

if __name__ == "__main__":
    main()