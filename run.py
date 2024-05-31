import os
import sys
from pytube import Playlist
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
import datetime
from pydub import AudioSegment
from urllib.error import HTTPError
import time

# Global variable to control if spotify.py has been executed
spotify_executado = False

# Add the directory to the Python search path
sys.path.append(os.path.join(os.getcwd(), 'metadata'))

def obter_data_publicacao(video):
    return video.publish_date

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_and_convert_video(video, idx, mp4_folder, mp3_folder, playlist_title, max_retries=3):
    for attempt in range(max_retries):
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
            break
        except (HTTPError, OSError, Exception) as e:
            print(f"Erro ao processar vídeo {video.title} (tentativa {attempt + 1} de {max_retries}): {e}")
            if attempt + 1 == max_retries:
                print(f"Falha ao baixar o vídeo {video.title} após {max_retries} tentativas.")
            else:
                time.sleep(5)  # Aguardar um tempo antes de tentar novamente

def list_mp3_files(directory):
    mp3_files = [f for f in os.listdir(directory) if f.endswith('.mp3')]
    if mp3_files:
        print("Arquivos MP3 encontrados:")
        for idx, file in enumerate(mp3_files, start=1):
            print(f"{idx}. {file}")
    else:
        print("Nenhum arquivo MP3 encontrado.")
    return mp3_files

def clean_file_names(directory, text_to_remove):
    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            new_name = filename.replace(text_to_remove, '')
            if new_name != filename:
                os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))

def baixar_playlist():
    link_playlist = input("Insira a URL da playlist do YouTube (ou deixe em branco para pular): ").strip()
    if not link_playlist:
        print("Pulo da etapa de download.")
        return None

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
    return mp3_folder

def renomear_arquivos(mp3_folder):
    while True:
        mp3_files = list_mp3_files(mp3_folder)
        if not mp3_files:
            break

        limpar = input("Você quer limpar algo dos nomes dos arquivos? (s/n): ").strip().lower()
        if limpar == 's':
            texto_a_remover = input("Digite o texto a ser removido dos nomes dos arquivos: ").strip()
            clean_file_names(mp3_folder, texto_a_remover)
            print("Renomeação concluída!")
        else:
            break

def executar_spotify():
    global spotify_executado
    if not spotify_executado:
        import spotify
        spotify.executar_funcao()
        spotify_executado = True
        print("A função do Spotify foi executada!")

def main():
    try:
        mp3_folder = baixar_playlist()
        if mp3_folder or os.path.exists("downloads/mp3"):
            renomear_arquivos(mp3_folder or "downloads/mp3")
        executar_spotify()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

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