# util
# s/anilist_api.py
import requests
class AniListAPI:
    def __init__(self):
        self.url = 'https://graphql.anilist.co'

    def fetch_anime_info(self, anime_id):
        query = '''
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            description
            averageScore
            episodes
            coverImage {
              large
            }
          }
        }
        '''
        variables = {'id': anime_id}

        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            return response.json()['data']['Media']
        else:
            raise Exception(f"Query failed with status code {response.status_code}.")
        

    def search_anime(self, name, page=1, per_page=10):
        query = '''
        query ($search: String, $page: Int, $perPage: Int) {
          Page(page: $page, perPage: $perPage) {
            media(search: $search, type: ANIME, sort: POPULARITY_DESC) {
              id
              title {
                romaji
                english
                native
              }
              description
              averageScore
              episodes
              coverImage {
                large
              }
            }
          }
        }
        '''
        variables = {
            'search': name,
            'page': page,
            'perPage': per_page
        }

        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            return response.json()['data']['Page']['media']
        else:
            raise Exception(f"Query failed with status code {response.status_code}.")


anilist = AniListAPI()
