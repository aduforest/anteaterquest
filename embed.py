import csv
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    embedding = model.encode(text)
    return embedding

# Open the CSV file and create a new one with embeddings
with open('courses.csv', 'r') as csvinput:
    with open('courses_with_embeddings.csv', 'w', newline='') as csvoutput:
        reader = csv.reader(csvinput)
        writer = csv.writer(csvoutput)

        # Read the header and append 'embedding' to it
        row = next(reader)
        row.append('embedding')
        writer.writerow(row)

        # Iterate over the rows to get course descriptions and embeddings
        for row in reader:
            # Assume course description is in the second column
            description = row[4]
            embedding = get_embedding(description)

            # Convert embedding from numpy array to string
            embedding_str = ' '.join(map(str, embedding))

            row.append(embedding_str)

            # Write the row into the new CSV file
            writer.writerow(row)
