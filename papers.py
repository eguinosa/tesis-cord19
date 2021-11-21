# Gelin Eguinosa Rosique

import csv
import pickle
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
    papers_index_file = 'papers_index.pickle'

    def __init__(self):
        """
        Loads the metadata.csv to create the index and save the information of
        interest.
        """
        # Create the metadata path
        metadata_path = join(self.cord19_data_folder, self.current_dataset, self.metadata_file)

        # Dictionary where the information of the papers will be saved.
        self.papers_index = defaultdict(dict)

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
                current_paper = self.papers_index[cord_uid]
                current_paper['cord_uid'] = cord_uid
                current_paper['title'] = title
                current_paper['abstract'] = abstract
                current_paper['publish_time'] = publish_time
                current_paper['authors'] = authors
                if pdf_json_files != ['']:
                    current_paper['pdf_json_files'] = pdf_json_files
                if pmc_json_files != ['']:
                    current_paper['pmc_json_files'] = pmc_json_files

        # Transform the papers' index from a defaultdict to a normal dictionary.
        self.papers_index = dict(self.papers_index)

        # Save the Papers' Index
        papers_index_path = join(self.project_data_folder, self.papers_index_file)
        with open(papers_index_path, 'wb') as file:
            pickle.dump(self.papers_index, file)

        # Load the Papers' Index
        with open(papers_index_path, 'rb') as file:
            self.papers_index = pickle.load(file)

    def paper_embedding(self, cord_uid):
        """
        Find the precomputed SPECTER Document Embedding for the specified Paper
        (cord_uid) inside the csv embeddings file.
        :param cord_uid: The Unique Identifier of the CORD-19 paper.
        :return: A 768-dimensional document embedding
        """
        # Create the path for the CSV file containing the embeddings.
        embeddings_path = join(self.cord19_data_folder, self.current_dataset, self.embeddings_file)

        # Load the file
        with open(embeddings_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Search for the embedding of cord_uid Paper
            for row in csv_reader:
                if row[0] == cord_uid:
                    # We found the embedding. Transform the dimensions of the
                    # embedding from string to float.
                    paper_embedding = list(map(float, row[1:]))

                    # Return the SPECTER Document Embedding
                    return paper_embedding

        # Raise an exception if we can't find the embedding for the 'cord_uid' Paper
        raise Exception("Paper not found in the list of embeddings.")

    def create_embeddings_index(self):
        """
        Scan the csv embedding file, to load and save all the vectors of the
        documents to access them more easily.
        """


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
