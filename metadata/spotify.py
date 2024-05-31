import os
import requests
import eyed3
from spotipy import SpotifyClientCredentials, Spotify
from typing import Dict

# Função para ler as credenciais do arquivo key_spotify.txt
def read_keys_file(file_path: str) -> Dict[str, str]:
    keys = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            keys[key.strip()] = value.strip()
    return keys

# Caminho correto para o arquivo de chaves
keys = read_keys_file("secret/key_spotify.txt")
CLIENT_ID = keys.get("CLIENT_ID")
CLIENT_SECRET = keys.get("CLIENT_SECRET")

class SpotifySong:
    """
    Classe para armazenar dados sobre as músicas obtidas do Spotify.
    """

    def __init__(self, song: Dict) -> None:
        self.track_name = song["name"]
        self.release_date = song["album"]["release_date"]
        self.artist_name = song["artists"][0]["name"]
        self.collection_name = song["album"]["name"]
        self.artwork_url_100 = song["album"]["images"][0]["url"]

def search_song_by_file_title(file_path: str, artist: str = None, album: str = None, country: str = "US", limit: int = 1) -> SpotifySong:
    """
    Pesquisa a música usando o título do arquivo de música e, opcionalmente, o nome do artista e/ou nome do álbum,
    e retorna os resultados. Retorna None se não encontrar nenhum resultado.
    """
    # Extrai o título do arquivo (sem extensão)
    file_name = os.path.basename(file_path)
    title = os.path.splitext(file_name)[0]

    try:
        # Constrói a consulta de busca incluindo o título e, opcionalmente, o nome do artista e/ou nome do álbum
        query = f"track:{title}"
        if artist:
            query += f" artist:{artist}"
        if album:
            query += f" album:{album}"

        spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
        response = spotify.search(query, limit=limit, type="track", market=country)
        if response["tracks"]["items"]:
            return SpotifySong(response["tracks"]["items"][0])
        return None
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return None

def executar_funcao():
    print("...")

# Função para baixar a imagem a partir de uma URL e salvar como Cover.jpg
def download_image(url: str, file_name: str) -> None:
    response = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(response.content)

def fill_metadata(file_path: str, song: SpotifySong) -> None:
    # Construir o novo caminho do arquivo com a pasta "../downloads/mp3/"
    new_file_path = os.path.join("/downloads/mp3/", os.path.basename(file_path))
    
    audiofile = eyed3.load(file_path)
    if audiofile.tag is None:
        audiofile.initTag()

    audiofile.tag.title = song.track_name
    audiofile.tag.artist = song.artist_name
    audiofile.tag.album = song.collection_name
    audiofile.tag.band = song.artist_name  # Adicionando o metadado 'band'
    audiofile.tag.album_artist = song.artist_name  # Adicionando o metadado 'artista do álbum'
    
    # Salvando a imagem na mesma pasta dos arquivos MP3
    image_file_name = "Cover.jpg"  # Nome do arquivo de imagem
    image_file_path = os.path.join(os.path.dirname(file_path), image_file_name)
    download_image(song.artwork_url_100, image_file_path)
    
    # Carregando a imagem salva
    with open(image_file_path, 'rb') as image_file:
        image_data = image_file.read()
    
    # Adicionando a imagem aos metadados
    audiofile.tag.images.set(3, image_data, 'image/jpeg')
    
    # Salvando os metadados
    audiofile.tag.save()

# Exemplo de uso
script_directory = os.path.dirname(__file__)
mp3_folder = os.path.abspath(os.path.join(script_directory, "../downloads/mp3"))

# Solicitar o nome do artista e do álbum uma vez
artist = input("Digite o nome do artista (ou pressione Enter para pular): ").strip()
album = input("Digite o nome do álbum (ou pressione Enter para pular): ").strip()

print("\nPreenchendo metadados dos arquivos MP3...")
for file_name in os.listdir(mp3_folder):
    if file_name.lower().endswith(".mp3"):
        file_path = os.path.join(mp3_folder, file_name)
        resultado = search_song_by_file_title(file_path, artist=artist if artist else None, album=album if album else None)
        if resultado:
            fill_metadata(file_path, resultado)
            print(f"Metadados preenchidos para o arquivo: {file_name}")
        else:
            print(f"Não foi possível encontrar metadados para o arquivo: {file_name}")
print("Metadados preenchidos com sucesso.")