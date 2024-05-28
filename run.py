import os
import sys
from pytube import Playlist
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
import datetime
import re
from pydub import AudioSegment

# Variável global para controlar se o spotify.py já foi executado
spotify_executado = False

# Adiciona o diretório ao caminho de pesquisa do Python
sys.path.append(os.path.join(os.getcwd(), 'metadata'))

# Função para obter a data de publicação de um vídeo do YouTube
def obter_data_publicacao(video):
    return video.publish_date

# Função para baixar uma playlist do YouTube, converter os vídeos para MP3, adicionar o número sequencial como metadados e salvar em uma pasta
def baixar_playlist_converter_com_metadados_e_salvar():
    global spotify_executado
    try:
        # Solicitar a URL da playlist do usuário
        link_playlist = input("Insira a URL da playlist do YouTube: ")

        # Obtendo a playlist
        playlist = Playlist(link_playlist)
        playlist_title = playlist.title
        download_folder = f"downloads/"

        # Criando a pasta de download se não existir
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Criando subpastas para mp3 e mp4
        mp3_folder = os.path.join(download_folder, "mp3")
        mp4_folder = os.path.join(download_folder, "mp4")

        if not os.path.exists(mp3_folder):
            os.makedirs(mp3_folder)

        if not os.path.exists(mp4_folder):
            os.makedirs(mp4_folder)
        
        print(f"Baixando playlist: {playlist_title}")
        
        # Iterar sobre os vídeos na playlist
        for idx, video in enumerate(tqdm(playlist.videos, desc="Baixando vídeos"), start=1):
            # Baixar o vídeo com o nome original
            video.streams.get_highest_resolution().download(output_path=mp4_folder)
            # Obter o nome original do arquivo baixado
            original_file_name = video.streams.get_highest_resolution().default_filename
            # Renomear o arquivo MP4
            mp4_path = os.path.join(mp4_folder, original_file_name)
            os.rename(os.path.join(mp4_folder, original_file_name), mp4_path)

            # Converter para MP3
            mp3_path = os.path.join(mp3_folder, original_file_name[:-4] + ".mp3")  # Remove a extensão .mp4 e substitui por .mp3
            # Utilizando pydub para conversão de áudio
            audio = AudioSegment.from_file(mp4_path)
            audio.export(mp3_path, format="mp3")

            # Obter a data de publicação do vídeo
            data_publicacao = obter_data_publicacao(video)
            if data_publicacao:
                ano_publicacao = data_publicacao.year
            else:
                ano_publicacao = datetime.datetime.now().year
            
            # Adicionar número sequencial como metadado
            #audiofile = EasyID3(mp3_path)
            #audiofile['tracknumber'] = str(idx)
            # Adicionar o nome do vídeo como título
            #audiofile['title'] = video.title
            # Adicionar o nome do canal como artista participante
            #audiofile['artist'] = video.author
            # Adicionar "Powered by Proton Negativo." como metadado de artista no álbum
           # audiofile['albumartist'] = "Powered by Proton Negativo."
            # Adicionar o link do vídeo como a URL do autor, incluindo o ano de publicação
           # audiofile['website'] = f"{video.watch_url}?year={ano_publicacao}"
            # Adicionar o nome da playlist como metadado de álbum
            #audiofile['album'] = playlist_title
            # Adicionar o ano de publicação como metadado
            #audiofile['date'] = str(ano_publicacao)
            #audiofile.save()
        
        print("Download, conversão para MP3, adição de metadados e salvamento na pasta concluídos!")
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
    finally:
        # Se o spotify.py ainda não foi executado, chame-o
        if not spotify_executado:
            # Importar e chamar a função do spotify.py
            import spotify
            spotify.executar_funcao()
            # Definir a variável como True para indicar que o spotify.py foi executado
            spotify_executado = True
            print("A função do Spotify foi executada!")

# Chamar a função para baixar e converter a playlist com metadados
baixar_playlist_converter_com_metadados_e_salvar()

# Muda o diretório de trabalho para o diretório atual de run.py
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import os

def read_keys_file(file_path):
    # Obter o caminho absoluto para o arquivo key_spotify.txt
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navegue até o diretório pai (metadata) e depois para o diretório secret
    abs_file_path = os.path.join(current_dir, "secret", file_path)
    # Ler as chaves do arquivo
    with open(abs_file_path, 'r') as file:
        keys = file.read().strip()
    return keys

def executar_funcao():
    # Código para executar a função do Spotify
    print("Executando função do Spotify...")