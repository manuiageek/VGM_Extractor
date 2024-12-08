import ctypes
import os
from ctypes import wintypes

user32 = ctypes.windll.user32

WM_WA_IPC = 1024  # WM_USER
IPC_DELETE = 101
IPC_GETLISTLENGTH = 124
IPC_SETPLAYLISTPOS = 121
IPC_PLAYFILE = 100
IPC_STARTPLAY = 102
WM_COPYDATA = 0x004A

class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ("dwData", wintypes.LPARAM),
        ("cbData", wintypes.DWORD),
        ("lpData", wintypes.LPVOID)
    ]

def find_winamp_window():
    hwnd = user32.FindWindowW("Winamp v1.x", None)
    if hwnd == 0:
        raise Exception("Winamp n'est pas ouvert ou introuvable.")
    return hwnd

def get_playlist_length(hwnd):
    return user32.SendMessageW(hwnd, WM_WA_IPC, 0, IPC_GETLISTLENGTH)

def set_playlist_pos(hwnd, pos):
    user32.SendMessageW(hwnd, WM_WA_IPC, pos, IPC_SETPLAYLISTPOS)

def delete_selected(hwnd):
    user32.SendMessageW(hwnd, WM_WA_IPC, 0, IPC_DELETE)

def clear_playlist(hwnd):
    length = get_playlist_length(hwnd)
    while length > 0:
        # Sélectionner la première piste
        set_playlist_pos(hwnd, 0)
        # Supprimer l'entrée sélectionnée
        delete_selected(hwnd)
        # Mettre à jour la longueur
        length = get_playlist_length(hwnd)
    print("Playlist vidée.")

def send_ipc_command(hwnd, ipc_code, path):
    data = path.encode('mbcs') + b'\0'
    buffer = ctypes.create_string_buffer(data)
    
    cds = COPYDATASTRUCT()
    cds.dwData = ipc_code
    cds.cbData = len(data)
    cds.lpData = ctypes.addressof(buffer)
    
    lParam = ctypes.c_void_p(ctypes.addressof(cds))
    return user32.SendMessageW(hwnd, WM_COPYDATA, 0, lParam)

def play_spc_file(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"Le fichier n'existe pas : {file_path}")
    
    hwnd = find_winamp_window()

    # Vider la playlist manuellement
    clear_playlist(hwnd)

    # Charger le fichier SPC via IPC_PLAYFILE
    res = send_ipc_command(hwnd, IPC_PLAYFILE, file_path)
    if res == 0:
        print("Échec de l'envoi du fichier à Winamp.")
    else:
        print(f"Fichier '{file_path}' chargé. Tentative de démarrage de la lecture...")
        # Envoyer le message pour démarrer la lecture
        user32.SendMessageW(hwnd, WM_WA_IPC, 0, IPC_STARTPLAY)
        print("Lecture démarrée.")

if __name__ == "__main__":
    SPC_FILE = r"E:\_MUSIC\VIDEO GAME MUSIC\SNES_Breath Of Fire 1\Blood Relation\EXTRACT\02 Blood Relation.spc"
    try:
        play_spc_file(SPC_FILE)
    except Exception as e:
        print(f"Erreur : {e}")
