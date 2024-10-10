import multiprocessing
import requests
import cProfile

API_ENDPOINT = "http://pip-oceanus/zeafrost/api/v1"  # Replace with your API endpoint URL

# List of entities to query
entities = ["shot", "sequence", "version", "task", "publishedfile"]

def query_entity_data(entity):
    url = f"{API_ENDPOINT}/{entity}/search"
    response = requests.get(url, params={'project': "pnty", "episode": "201"})
    data = response.json()
    return data

def main():
    with multiprocessing.Pool() as pool:
        results = pool.map(query_entity_data, entities)

        # for entity, data in zip(entities, results):
        #     print(f"Data for {entity}")

if __name__ == "__main__":
    cProfile.run('main()')

