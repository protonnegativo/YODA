from mutagen.id3 import ID3, APIC
import mutagen
import os

def add_cover_to_mp3(directory_path, cover_image_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".mp3"):
            file_path = os.path.join(directory_path, filename)
            try:
                audio = ID3(file_path)
                with open(cover_image_path, 'rb') as albumart:
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',  # ou 'image/png'
                        type=3,  # 3 é para a imagem de capa (frontal)
                        desc=u'Cover',
                        data=albumart.read()
                    )
                audio.save()
                print(f"A imagem de capa foi adicionada ao arquivo '{file_path}'.")
            except mutagen.id3.ID3NoHeaderError:
                audio = mutagen.File(file_path, easy=True)
                audio.add_tags()
                audio.save()

                audio = ID3(file_path)
                with open(cover_image_path, 'rb') as albumart:
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',  # ou 'image/png'
                        type=3,  # 3 é para a imagem de capa (frontal)
                        desc=u'Cover',
                        data=albumart.read()
                    )
                audio.save()
                print(f"ID3 tag adicionada e a imagem de capa foi adicionada ao arquivo '{file_path}'.")

# Uso
directory_path = r"C:\Users\Computer\Documents\Estudos\git\Public\YODA\downloads\Taylor Swift - Speak Now (Taylor's Version) mp3"
cover_image_path = r"C:\Users\Computer\Documents\Estudos\git\Public\YODA\downloads\Cover.jpg"
add_cover_to_mp3(directory_path, cover_image_path)
