import os
from PIL import Image


def create_gif_from_png(folder_path, output_gif, duration=200, loop=0):

    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]


    png_files.sort(key=lambda x: int(os.path.splitext(x)[0]))


    images = []
    for png_file in png_files:
        file_path = os.path.join(folder_path, png_file)
        images.append(Image.open(file_path))


    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop
    )
    print(f"GIF успешно создан: {output_gif}")

if __name__ == '__main__':
    folder_path = r'C:\Users\vgrom\OneDrive\Рабочий стол\для гиф'
    output_gif = r'C:\Users\vgrom\OneDrive\Рабочий стол\gif\3.gif'
    create_gif_from_png(folder_path, output_gif, duration=200, loop=0)