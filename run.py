import os
import sys
from pytube import Playlist # type: ignore
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
import datetime
from pydub import AudioSegment # type: ignore
from urllib.error import HTTPError
import time
import subprocess
import re

# Global variable to control if spotify.py has been executed
spotify_executado = False

# Add the directory to the Python search path
sys.path.append(os.path.join(os.getcwd(), 'metadata'))

def obter_data_publicacao(video):
    return video.publish_date

def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_video(video, folder):
    video.streams.get_highest_resolution().download(output_path=folder)
    original_file_name = video.streams.get_highest_resolution().default_filename
    return os.path.join(folder, original_file_name)

def convert_to_mp3(mp4_path, mp3_folder, idx, video, playlist_title):
    try:
        mp3_path = os.path.join(mp3_folder, os.path.basename(mp4_path)[:-4] + ".mp3")
        audio = AudioSegment.from_file(mp4_path)
        audio.export(mp3_path, format="mp3")

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
        print(f"Erro ao converter vídeo {video.title} para MP3: {e}")

def download_and_convert_video(video, idx, mp4_folder, mp3_folder, playlist_title, download_choice, max_retries=3):
    for attempt in range(max_retries):
        try:
            mp4_path = None
            if download_choice in ['mp4', 'both']:
                mp4_path = download_video(video, mp4_folder)
                print(f"Vídeo {video.title} baixado como MP4.")
            if download_choice in ['mp3', 'both']:
                if not mp4_path:
                    mp4_path = download_video(video, mp4_folder)
                convert_to_mp3(mp4_path, mp3_folder, idx, video, playlist_title)
                if download_choice == 'mp3':
                    os.remove(mp4_path)
                print(f"Vídeo {video.title} convertido e baixado como MP3.")
            break
        except (HTTPError, OSError, Exception) as e:
            print(f"Erro ao processar vídeo {video.title} (tentativa {attempt + 1} de {max_retries}): {e}")
            if attempt + 1 == max_retries:
                print(f"Falha ao baixar o vídeo {video.title} após {max_retries} tentativas.")
            else:
                time.sleep(5)

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

def is_valid_youtube_playlist(url):
    pattern = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/playlist\?list=.*')
    return pattern.match(url)

def baixar_playlist(download_choice, link_playlist=None):
    attempts = 0
    while not link_playlist or not is_valid_youtube_playlist(link_playlist):
        if attempts >= 3:
            print("URL inválida inserida 3 vezes. Pulando a etapa de download.")
            return None, None

        if not link_playlist:
            link_playlist = input("Insira a URL da playlist do YouTube (ou deixe em branco para pular): ").strip()
        if not link_playlist:
            print("Pulo da etapa de download.")
            return None, None
        if not is_valid_youtube_playlist(link_playlist):
            print("URL inválida. Por favor, insira uma URL válida da playlist do YouTube.")
            link_playlist = None
            attempts += 1

    playlist = Playlist(link_playlist)
    playlist_title = sanitize_folder_name(playlist.title)
    download_folder = "downloads"

    mp3_folder = os.path.join(download_folder, f"{playlist_title} mp3")
    mp4_folder = os.path.join(download_folder, f"{playlist_title} mp4")
    create_folder_if_not_exists(mp3_folder)
    create_folder_if_not_exists(mp4_folder)

    print(f"Baixando playlist: {playlist.title}")
    for idx, video in enumerate(tqdm(playlist.videos, desc="Baixando vídeos"), start=1):
        download_and_convert_video(video, idx, mp4_folder, mp3_folder, playlist_title, download_choice)

    if download_choice == 'mp3':
        if os.path.exists(mp4_folder):
            for file in os.listdir(mp4_folder):
                file_path = os.path.join(mp4_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(mp4_folder)
    elif download_choice == 'mp4':
        if os.path.exists(mp3_folder):
            for file in os.listdir(mp3_folder):
                file_path = os.path.join(mp3_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(mp3_folder)

    print("Download e conversão concluídos!")
    return mp3_folder, playlist_title

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

def executar_spotify(playlist_title):
    global spotify_executado
    if not spotify_executado:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        spotify_script = os.path.join(script_directory, 'metadata', 'spotify.py')
        subprocess.run([sys.executable, spotify_script, playlist_title])
        spotify_executado = True
        print("A função do Spotify foi executada!")

def main():
    try:
        print("Escolha uma opção de download:")
        print("1. Apenas MP3")
        print("2. Apenas MP4")
        print("3. Ambos MP3 e MP4")
        choice = input("Digite o número da sua escolha: ").strip()

        if choice == '1':
            download_choice = 'mp3'
            link_playlist = None
        elif choice == '2':
            download_choice = 'mp4'
            link_playlist = None
        elif choice == '3':
            download_choice = 'both'
            link_playlist = None
        else:
            print("Escolha inválida. Usando a opção padrão: Apenas MP3.")
            download_choice = 'mp3'
            link_playlist = choice

        mp3_folder, playlist_title = baixar_playlist(download_choice, link_playlist)
        if mp3_folder:
            renomear_arquivos(mp3_folder)
        executar_spotify(playlist_title or "default_playlist")
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