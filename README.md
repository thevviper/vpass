# VPass

## Installing requirements

```bash
pip install lyricsgenius pycrypto
```



## Genius access token

Register at genius.com and get an access, token. Then, paste it at this line:

```python
genius = lyricsgenius.Genius("<YOUR GENIUS ACCESS TOKEN>")
```



## Usage

```bash
python passgen.py website_name (or key_name) max_length (optional) [options]
```

Options are: `--offline` for not using genius or in fact without connecting to the internet at all, 

`--lowercase` to not include uppercase letters, `--no-puncs` to not include any punctuations.



#### Examples

```bash
python passgen.py gmail 16
python passgen.py github 16 --offline --lowercase --no-puncs
```



