import os
import glob
import csv

def selectFileImport(title, dir, ext):
    print(title)
    files = [f for f in os.listdir(dir) if f.endswith('.'+ext)]
    for idx, file in enumerate(files):
        print(idx, '-', file)
    selectedIdx = int(input('Enter a number: '))
    return files[selectedIdx]