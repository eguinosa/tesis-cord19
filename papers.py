# Gelin Eguinosa Rosique

import csv
import json
from os import mkdir
from os.path import join, isfile, isdir
from collections import defaultdict

# To test the speed of the class
from time_keeper import TimeKeeper


class Papers:
    """
    Scans the CORD-19 dataset to create an index of it, saving all the relevant
    information for later use.
    """
    # CORD-19 Data Location
    cord19_data_folder = 'cord19_data'
    current_dataset = '2020-05-31'
    metadata_file = 'metadata.csv'
    embeddings_file = 'cord_19_embeddings_2020-05-31.csv'

    # Project Data Location
    project_data_folder = 'project_data'
    project_embeds_folder = 'embedding_dicts'
    papers_index_file = 'papers_index.json'
    embeds_index_file = 'embeddings_index.json'

    def __init__(self):
        """
        Load the metadata.csv to create the index of all the papers available in
        the current CORD-19 dataset and save all the information of interest.
        
        Also, load the cord_19_embeddings to create an index and save them in
        100 different dictionaries, so they are quickly loaded without
        occupying too much memory.
        """
        # Create a data folder if it doesn't exist.
        if not isdir(self.project_data_folder):
            mkdir(self.project_data_folder)
        # Form the papers index path.
        papers_index_path = join(self.project_data_folder, self.papers_index_file)
        # Check if the papers' index exists or not.
        if isfile(papers_index_path):
            # Load the Papers' Index.
            with open(papers_index_path, 'r') as file:
                self.papers_index = json.load(file)
        else:         
            # Create the index of the papers.
            self.papers_index = self._create_papers_index()
            # Save the Papers' Index
            with open(papers_index_path, 'w') as file:
                json.dump(self.papers_index, file)

        # Create the folder of the embedding dictionaries if it doesn't exist.
        proj_embeds_folder_path = join(self.project_data_folder, self.project_embeds_folder)
        if not isdir(proj_embeds_folder_path):
            mkdir(proj_embeds_folder_path)
        # Form the embeddings index path.
        embeds_index_path = join(self.project_data_folder, self.embeds_index_file)
        # Check if the embeddings' index exists or not.
        if isfile(embeds_index_path):
            # Load the embeddings' index.
            with open(embeds_index_path, 'r') as file:
                self.embeds_index = json.load(file)
        else:
            # Save the embeddings of the papers and create an index of their
            # location.
            self.embeds_index = self._create_embeddings_index()
            # Save the embeddings' index
            with open(embeds_index_path, 'w') as file:
                json.dump(self.embeds_index, file)

        # Create a Cache for the Embedding Dictionaries, the they work faster in
        # repetitive cases.
        self.cached_embed_dict = {}
        self.cached_dict_filename = ''

    def _create_papers_index(self):
        """
        Create an index of the papers available in the CORD-19 dataset specified
        in the data folders of the class.
        """
        # Create the metadata path
        metadata_path = join(self.cord19_data_folder, self.current_dataset, self.metadata_file)

        # Dictionary where the information of the papers will be saved.
        papers_index = defaultdict(dict)

        # Open the metadata file
        with open(metadata_path) as file:
            reader = csv.DictReader(file)
            # Go through the information of all the papers.
            for row in reader:
                # Get the fields of interest.
                cord_uid = row['cord_uid']
                title = row['title']
                abstract = row['abstract']
                publish_time = row['publish_time']
                authors = row['authors'].split('; ')
                pdf_json_files = row['pdf_json_files'].split('; ')
                pmc_json_files = row['pmc_json_files'].split('; ')

                # Save all the information of the current paper, or update it
                # if we have found this 'cord_uid' before. Also, check if the
                # are not empty.
                current_paper = papers_index[cord_uid]
                current_paper['cord_uid'] = cord_uid
                current_paper['title'] = title
                current_paper['abstract'] = abstract
                current_paper['publish_time'] = publish_time
                current_paper['authors'] = authors
                if pdf_json_files != ['']:
                    current_paper['pdf_json_files'] = pdf_json_files
                if pmc_json_files != ['']:
                    current_paper['pmc_json_files'] = pmc_json_files

        # Transform the papers' index from a 'defaultdict' to a normal dictionary.
        papers_index = dict(papers_index) 
        return papers_index

    def _create_embeddings_index(self, embed_dicts=100):
        """
        Load all the embeddings of the documents from the current CORD-19
        dataset and save them in several dictionaries so when needed they can
        be loaded quickly and without occupying to much space in memory.

        We create an index with the 'cord_uid' of the papers and the location of
        the dictionary that contains them.

        :param embed_dicts: The number of dictionaries that we are going to use
        to store all the embeddings of the papers (default: 100).
        :return: A dictionary (the index) containing the location of the
        dictionary that contains the embedding for a given paper.
        """
        # Get the amount of CORD-19 papers in the current dataset.
        total_papers = len(self.papers_index)
        # Amount of embeddings to be stored per dictionary
        embeds_per_dict = total_papers // 100 + 1

        # Index to store the papers' 'cord_uid' and the location of the dictionary
        # with their embedding.
        embeddings_index = {}

        # Create a temporary dictionary to store the embeddings of the papers.
        temp_embeds_dict = {}
        # Create counter for the amount of dictionaries we have created to store
        # the embeddings of the papers, starting with 1.
        dicts_count = 1
        # Create counter for the amount of embeddings we have stored in the
        # current temporary dictionary.
        dict_embeds_count = 0
        # Create the name of the file where the temporary dictionary will be
        # stored.
        temp_dict_file = f"embeddings_dict_{_number_to_3digits(dicts_count)}"

        # Create the path for the CSV file containing the embeddings.
        embeddings_path = join(self.cord19_data_folder, self.current_dataset, self.embeddings_file)
        # Load the file
        with open(embeddings_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            # Iterate through the embedding of all the papers
            for row in csv_reader:
                # Get the 'cord_uid' and check if we have seen it before.
                paper_cord_uid = row[0]
                if paper_cord_uid in embeddings_index:
                    continue
                # Get the embedding of the paper.
                paper_embedding = list(map(float, row[1:]))
                # Save the embedding in the temporary dictionary.
                temp_embeds_dict[paper_cord_uid] = paper_embedding
                # Save the file where the embedding of the current paper will be
                # saved.
                embeddings_index[paper_cord_uid] = temp_dict_file
                # Update the amount of embeddings stored.
                dict_embeds_count += 1

                # Check if we have reached the maximum amount of papers per dict.
                if dict_embeds_count >= embeds_per_dict:
                    # Save the current temporary dictionary
                    temp_dict_path = join(self.project_data_folder, self.project_embeds_folder, temp_dict_file)
                    with open(temp_dict_path, 'w') as file:
                        json.dump(temp_embeds_dict, file)

                    # Reset the temporary dictionary.
                    temp_embeds_dict = {}
                    dicts_count += 1
                    dict_embeds_count = 0
                    temp_dict_file = f"embeddings_dict_{_number_to_3digits(dicts_count)}"
        # Check if we have pending embeddings once we finish visiting all the papers in
        # the CSV file.
        if temp_embeds_dict:
            # Save the current temporary dictionary
            temp_dict_path = join(self.project_data_folder, self.project_embeds_folder, temp_dict_file)
            with open(temp_dict_path, 'w') as file:
                json.dump(temp_embeds_dict, file)

        # Once we have saved all the embeddings, return the index.
        return embeddings_index

    def paper_embedding(self, cord_uid):
        """
        Find the precomputed SPECTER Document Embedding for the specified Paper
        'cord_uid'.
        :param cord_uid: The Unique Identifier of the CORD-19 paper.
        :return: A 768-dimensional document embedding
        """
        # Get the dictionary where the embedding is saved.
        embed_dict_filename = self.embeds_index[cord_uid]
        # Check if this dictionary is already in memory.
        if embed_dict_filename != self.cached_dict_filename:
            # If the needed dict is not in memory, load it.
            embed_dict_path = join(self.project_data_folder, self.project_embeds_folder, embed_dict_filename)
            with open(embed_dict_path, 'r') as file:
                # Update the cached dictionary.
                self.cached_embed_dict = json.load(file)
                self.cached_dict_filename = embed_dict_filename
        # Return the embedding using the cached dictionary.
        return self.cached_embed_dict[cord_uid]


def _number_to_3digits(number):
    """
    Transform a number smaller than 1000 (0-999) to a string representation with
    three characters (000, 001, ..., 021, ..., 089, ..., 123, ..., 999).
    """
    # Make sure the value we transform is under 1000 and is positive.
    mod_number = number % 1000
    
    if mod_number < 10:
        return "00" + str(mod_number)
    elif mod_number < 100:
        return "0" + str(mod_number)
    else:
        return str(mod_number)


# Testing the Papers class
if __name__ == '__main__':
    # Record the Runtime of the Program
    stopwatch = TimeKeeper()

    # Load the CORD-19 Dataset
    print("Loading the CORD-19 Dataset...")
    cord19_papers = Papers()
    print("Done.")
    print(f"[{stopwatch.formatted_runtime()}]")

    # Get the amount of documents the dataset has.
    num_papers = len(cord19_papers.papers_index)
    print(f"\nThe current CORD-19 dataset has {num_papers} documents.")

    # Get the Embedding for one of the papers.
    cord19_uids = list(cord19_papers.papers_index.keys())
    random_cord_uid = cord19_uids[100000]
    print(f"\nGetting the Embedding for the Paper <{random_cord_uid}>...")
    result = cord19_papers.paper_embedding(random_cord_uid)
    print(f"The Embedding is:")
    print(result)
    print("Done.")
    print(f"[{stopwatch.formatted_runtime()}]")
