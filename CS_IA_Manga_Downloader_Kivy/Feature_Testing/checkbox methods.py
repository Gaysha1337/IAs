import time
from tqdm import tqdm

pbar = tqdm(total=21)
for i in range(21):
    time.sleep(.1)
    pbar.update(1)