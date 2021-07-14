from asciimatics.renderers import FigletText
from tqdm import tqdm

class Terminal():
    def __init__(self):
        self.pbar = None

    def logo(self):
        renderer = FigletText("ONCOGERIATRICS\n SYNTHETIC\n DATA GENERATOR", font='small')
        print(renderer)

    def initialiseProgressBar(self, total=100):
        self.pbar = tqdm(ascii=True, total=total)

    def updateProgress(self):
        self.pbar.update()
    
    def closeProgressBar(self):
        self.pbar.close()
        self.pbar.clear()

    def print(self, s=""):
        print(f"\n{s}")
