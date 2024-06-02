import os
import sys
import requests
import eyed3
from spotipy import SpotifyClientCredentials, Spotify
from typing import Dict, Optional

def read_keys_file(file_path: str) -> Dict[str, str]:
    keys = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            keys[key.strip()] = value.strip()
    return keys

def download_image(url: str, file_name: str) -> None:
    response = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(response.content)

def fill_metadata(file_path: str, song: 'SpotifySong', fixed_album_artist: Optional[str] = None) -> None:
    audiofile = eyed3.load(file_path)
    if audiofile.tag is None:
        audiofile.initTag()

    album_artist = fixed_album_artist if fixed_album_artist else song.artist_name

    audiofile.tag.title = song.track_name
    audiofile.tag.artist = song.artist_name
    audiofile.tag.album = song.collection_name
    audiofile.tag.band = song.artist_name
    audiofile.tag.album_artist = album_artist
    
    image_file_name = "Cover.jpg"
    image_file_path = os.path.join(os.path.dirname(file_path), image_file_name)
    download_image(song.artwork_url_100, image_file_path)
    
    with open(image_file_path, 'rb') as image_file:
        image_data = image_file.read()
    
    audiofile.tag.images.set(3, image_data, 'image/jpeg')
    audiofile.tag.save()

class SpotifySong:
    def __init__(self, song: Dict) -> None:
        self.track_name = song["name"]
        self.release_date = song["album"]["release_date"]
        self.artist_name = song["artists"][0]["name"]
        self.collection_name = song["album"]["name"]
        self.artwork_url_100 = song["album"]["images"][0]["url"]

def search_song_by_file_title(file_path: str, artist: Optional[str] = None, album: Optional[str] = None, country: str = "US", limit: int = 1) -> Optional[SpotifySong]:
    file_name = os.path.basename(file_path)
    title = os.path.splitext(file_name)[0]

    try:
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

def main():
    if len(sys.argv) != 2:
        print("Uso: python spotify.py <nome_da_playlist>")
        sys.exit(1)

    playlist_name = sys.argv[1]
    script_directory = os.path.dirname(os.path.abspath(__file__))
    mp3_folder = os.path.abspath(os.path.join(script_directory, f"../downloads/{playlist_name} mp3"))

    while not os.path.exists(mp3_folder):
        print(f"Erro: O caminho '{mp3_folder}' não foi encontrado.")
        mp3_folder = input("Por favor, insira o caminho correto para a pasta contendo os arquivos MP3: ").strip()

    artist = input("Digite o nome do artista (ou pressione Enter para pular): ").strip()
    album = input("Digite o nome do álbum (ou pressione Enter para pular): ").strip()
    fixed_album_artist = input("Digite o nome do artista do álbum fixo (ou pressione Enter para usar o nome do artista): ").strip()

    print("\nPreenchendo metadados dos arquivos MP3...")
    for file_name in os.listdir(mp3_folder):
        if file_name.lower().endswith(".mp3"):
            file_path = os.path.join(mp3_folder, file_name)
            resultado = search_song_by_file_title(file_path, artist=artist if artist else None, album=album if album else None)
            if resultado:
                fill_metadata(file_path, resultado, fixed_album_artist if fixed_album_artist else None)
                print(f"Metadados preenchidos para o arquivo: {file_name}")
            else:
                print(f"Não foi possível encontrar metadados para o arquivo: {file_name}")
    print("Metadados preenchidos com sucesso.")

if __name__ == "__main__":
    keys = read_keys_file(os.path.join(os.path.dirname(__file__), "..", "secret", "key_spotify.txt"))
    CLIENT_ID = keys.get("CLIENT_ID")
    CLIENT_SECRET = keys.get("CLIENT_SECRET")

    main()