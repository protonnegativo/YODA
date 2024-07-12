import os
import sys
import yt_dlp as youtube_dl
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
import datetime
from pydub import AudioSegment
import time
import re
import subprocess

# Global variable to control if spotify.py has been executed
spotify_executado = False

# Add the directory to the Python search path
sys.path.append(os.path.join(os.getcwd(), 'metadata'))

def obter_data_publicacao(video):
    return video['upload_date']

def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_video(video_url, folder):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        original_file_name = ydl.prepare_filename(info_dict)
    return original_file_name, info_dict

def convert_to_mp3(mp4_path, mp3_folder, idx, video, playlist_title):
    try:
        mp3_path = os.path.join(mp3_folder, os.path.basename(mp4_path)[:-4] + ".mp3")
        audio = AudioSegment.from_file(mp4_path)
        audio.export(mp3_path, format="mp3")

        data_publicacao = obter_data_publicacao(video)
        ano_publicacao = data_publicacao[:4] if data_publicacao else datetime.datetime.now().year

        audiofile = EasyID3(mp3_path)
        audiofile['tracknumber'] = str(idx)
        audiofile['title'] = video['title']
        audiofile['artist'] = video['uploader']
        audiofile['albumartist'] = "Powered by Proton Negativo."
        audiofile['website'] = f"{video['webpage_url']}?year={ano_publicacao}"
        audiofile['album'] = playlist_title
        audiofile['date'] = str(ano_publicacao)
        audiofile.save()
    except Exception as e:
        print(f"Erro ao converter vídeo {video['title']} para MP3: {e}")

def download_and_convert_video(video_url, idx, mp4_folder, mp3_folder, playlist_title, download_choice, max_retries=3):
    for attempt in range(max_retries):
        try:
            mp4_path = None
            video_info = None
            if download_choice in ['mp4', 'both']:
                mp4_path, video_info = download_video(video_url, mp4_folder)
                print(f"Vídeo {video_info['title']} baixado como MP4.")
            if download_choice in ['mp3', 'both']:
                if not mp4_path:
                    mp4_path, video_info = download_video(video_url, mp4_folder)
                convert_to_mp3(mp4_path, mp3_folder, idx, video_info, playlist_title)
                if download_choice == 'mp3':
                    os.remove(mp4_path)
                print(f"Vídeo {video_info['title']} convertido e baixado como MP3.")
            break
        except Exception as e:
            print(f"Erro ao processar vídeo {video_url} (tentativa {attempt + 1} de {max_retries}): {e}")
            if attempt + 1 == max_retries:
                print(f"Falha ao baixar o vídeo {video_url} após {max_retries} tentativas.")
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

def list_mp3_metadata(directory):
    metadata_list = []
    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            file_path = os.path.join(directory, filename)
            audiofile = EasyID3(file_path)
            metadata = {
                'filename': filename,
                'title': audiofile.get('title', [''])[0],
                'artist': audiofile.get('artist', [''])[0],
                'album': audiofile.get('album', [''])[0],
                'date': audiofile.get('date', [''])[0]
            }
            metadata_list.append(metadata)
    return metadata_list

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

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist = ydl.extract_info(link_playlist, download=False)
    playlist_title = sanitize_folder_name(playlist['title'])
    download_folder = "downloads"

    mp3_folder = os.path.join(download_folder, f"{playlist_title} mp3")
    mp4_folder = os.path.join(download_folder, f"{playlist_title} mp4")
    create_folder_if_not_exists(mp3_folder)
    create_folder_if_not_exists(mp4_folder)

    print(f"Baixando playlist: {playlist['title']}")
    for idx, video in enumerate(tqdm(playlist['entries'], desc="Baixando vídeos"), start=1):
        download_and_convert_video(video['webpage_url'], idx, mp4_folder, mp3_folder, playlist_title, download_choice)

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

def executar_spotify(playlist_title):
    global spotify_executado
    if not spotify_executado:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        spotify_script = os.path.join(script_directory, 'metadata', 'spotify.py')
        subprocess.run([sys.executable, spotify_script, playlist_title])
        spotify_executado = True
        print("A função do Spotify foi executada!")

if __name__ == "__main__":
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
