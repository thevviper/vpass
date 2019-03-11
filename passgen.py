#!/usr/bin/env python
# coding: utf-8
import hashlib
import sys
from base64 import b64encode

import lyricsgenius
from Crypto.Cipher import AES

PUNCTUATIONS = "`~!@#$%^&*()-=_+[]{};:./<>?|"


class PseudoRNG(object):
    mod = int(1e9 + 9)
    init = int(1e9 + 7)
    a = 4385131
    b = 65536
    val = None

    def hash_string(self, s):
        h = 0
        x = 711
        for c in s:
            h = (h + x * ord(c)) % self.mod
        return h

    def next_alpha_string(self, length=100):
        res = ""
        for i in range(length):
            res += chr(ord('a') + self.next_int() % 26)
        return res

    def next_int(self):
        if self.val is None:
            self.val = self.init
        self.val = (self.val * self.a + self.b) % self.mod
        return self.val

    def next_boolean(self):
        return self.next_int() % 2 == 1

    def shuffle(self, l):
        n = len(l)
        if n < 2:
            return
        for i in reversed(range(1, n)):
            j = self.next_int() % (i + 1)
            if i == j:
                continue
            l[i], l[j] = l[j], l[i]

    def __init__(self, seed=811):
        if isinstance(seed, str):
            self.init = self.hash_string(seed)
        else:
            self.init = seed


def get_song(artist_name, song_name):
    artist = genius.search_artist(artist_name, max_songs=1, sort="title")
    song = genius.search_song(song_name, artist.name)
    lyrics = song.lyrics.replace(" ", "").replace("\n", "")
    br = False
    res = ""
    for c in lyrics:
        if c == "[":
            br = True
        elif c == "]":
            br = False
            continue
        if not br and c.isalpha():
            res += c.lower()
    return res


args = list(sys.argv)

offline = "--offline" in args
capital = "--lowercase" not in args
punc = "--no-puncs" not in args
passkey = args[1]
max_len = 32
for arg in args[2:]:
    try:
        int_arg = int(arg)
    except:
        continue
    max_len = int_arg
    break

passphrase = input("Enter passphrase: ").strip()
num = int(input("Enter pin: ").strip())

raw_songs = []

for i in range(5):
    raw_songs.append(input("Enter song name #{} ('artist, song' format): ".format(i + 1)).strip())

songs = [
    [song.split(',')[0].strip(), song.split(',')[1].strip()] for song in raw_songs
]

res = ""


genius = lyricsgenius.Genius("<YOUR GENIUS ACCESS TOKEN>")

if offline:
    for song in songs:
        for term in song:
            rand = PseudoRNG(term.replace(" ", "").lower())
            res += rand.next_alpha_string(500)
else:
    for song in songs:
        res += get_song(*song)


rand = PseudoRNG(num)

res = passkey + "$" + res
p = b64encode((passkey + passphrase).encode()).decode()
p = list(p)
rand.shuffle(p)
for kl in [32, 24, 16]:
    key = "".join(p)[:kl].encode()
    if len(key) == kl:
        break
rand.shuffle(p)
iv = "".join(p)[:16].encode()

aes = AES.new(key, AES.MODE_CBC, iv)

while len(res.encode()) % 16 != 0:
    res += "="
e = aes.encrypt(res)
x = num % 256
y = (num // 256) % len(e)
e = e[y:] + e[:y]
for b in e:
    b ^= x

pw = list(hashlib.sha512(e).hexdigest())
if len(pw) > max_len:
    ids = [i for i in range(len(pw))]
    rand.shuffle(ids)
    ids = ids[:max_len]
    res = []
    for i in ids:
        res.append(pw[i])
    pw = res
    
if punc:
    p = 1 + rand.next_int() % 4
    ids = [i for i in range(len(pw))]
    rand.shuffle(ids)
    ids = ids[:p]
    for i in ids:
        pw[i] = PUNCTUATIONS[rand.next_int() % len(PUNCTUATIONS)]
        
if capital:
    alphas = []
    for i in range(len(pw)):
        if pw[i].isalpha():
            alphas.append(i)
    rand.shuffle(alphas)
    caps = len(alphas) // 2
    alphas = alphas[:caps]
    for i in alphas:
        pw[i] = pw[i].upper()

print("".join(pw))
