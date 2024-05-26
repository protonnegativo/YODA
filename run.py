import os
from pytube import Playlist
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
import datetime
import re
from pydub import AudioSegment

# Função para substituir caracteres inválidos em um nome de pasta ou arquivo
def substituir_caracteres_invalidos(nome):
    return re.sub(r'[<>:"/\\|?*]', '-', nome)

# Função para obter a data de publicação de um vídeo do YouTube
def obter_data_publicacao(video):
    return video.publish_date

# Função para baixar uma playlist do YouTube, converter os vídeos para MP3, adicionar o número sequencial como metadados e salvar em uma pasta
def baixar_playlist_converter_com_metadados_e_salvar():
    try:
        # Solicitar a URL da playlist do usuário
        link_playlist = input("Insira a URL da playlist do YouTube: ")

        # Obtendo o título da playlist
        playlist = Playlist(link_playlist)
        playlist_title = substituir_caracteres_invalidos(playlist.title)
        download_folder = f"downloads/{playlist_title}"

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
            # Baixar o vídeo
            video.streams.get_highest_resolution().download(output_path=mp4_folder, filename=f"{substituir_caracteres_invalidos(video.title)}.mp4")
            # Converter para MP3
            mp4_path = os.path.join(mp4_folder, f"{substituir_caracteres_invalidos(video.title)}.mp4")
            mp3_path = os.path.join(mp3_folder, f"{substituir_caracteres_invalidos(video.title)}.mp3")
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
            audiofile = EasyID3(mp3_path)
            audiofile['tracknumber'] = str(idx)
            # Adicionar o nome do vídeo como título
            audiofile['title'] = video.title
            # Adicionar o nome do canal como artista participante
            audiofile['artist'] = video.author
            # Adicionar "Powered by Proton Negativo." como metadado de artista no álbum
            audiofile['albumartist'] = "Powered by Proton Negativo."
            # Adicionar o link do vídeo como a URL do autor, incluindo o ano de publicação
            audiofile['website'] = f"{video.watch_url}?year={ano_publicacao}"
            # Adicionar o nome da playlist como metadado de álbum
            audiofile['album'] = playlist_title
            # Adicionar o ano de publicação como metadado
            audiofile['date'] = str(ano_publicacao)
            audiofile.save()
        
        print("Download, conversão para MP3, adição de metadados e salvamento na pasta concluídos!")
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")

# Chamar a função para baixar e converter a playlist com metadados
baixar_playlist_converter_com_metadados_e_salvar()
