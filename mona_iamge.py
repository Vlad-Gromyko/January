import matplotlib.pyplot as plt


if __name__ == '__main__':
    for i in range(1, 11):
        plt.figure(figsize=(10, 10))
        plt.imshow(plt.imread(fr'C:\Users\vgrom\Desktop\mona2.png'), cmap='gray')
        plt.axis('off')
        plt.show()