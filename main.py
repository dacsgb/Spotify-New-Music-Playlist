import os
from dotenv import load_dotenv
from src.data_structures import UserCredentials
from src.NewMusicPlaylistFiller import NewMusicPlaylistFiller

def main():

    load_dotenv()

    user  = UserCredentials(client_id = os.getenv("CLIENT_ID"),
                            client_secret = os.getenv("CLIENT_SECRET"),
                            playlist_id = os.getenv("PLAYLIST_ID"))  

    app = NewMusicPlaylistFiller(user = user,
                                    redirect_uri = os.getenv("REDIRECT_URI"),
                                    app_scope = os.getenv("APP_SCOPE"))
    app.run()

if __name__ == "__main__":
    main()