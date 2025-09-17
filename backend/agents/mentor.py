
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize 

def search_mentors(uid, db):
    # Fetch mentor list from Firestore
    mentor_list = db.collection("mentors")
    mentor_dict = {doc.id: doc.to_dict() for doc in mentor_list.stream()}
    
    # Fetch the user's document
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()  # This will fetch the entire document
    
    # Fetch the mentorScore from the user's document
    mentor_target = user_doc.to_dict().get("mentorScore", None)

    # Debug: Check mentor target data
    

    target_array = np.array([mentor_target[skill] for skill in sorted(mentor_target)])

    # Convert target vector into numpy array and reshape it to 2D (1 row, multiple columns)
    target_array = normalize(target_array.reshape(1, -1), norm='l2')  # Normalize target vector
    
    # Prepare mentor vectors from mentor dictionary
    mentor_vectors = []
    mentor_names = []

    for mentor_name, mentor_data in mentor_dict.items():
        mentor_scores = mentor_data['mentorScore']
        mentor_vector = np.array([mentor_scores.get(skill, 0) for skill in sorted(mentor_target)])  # Ensure the order of skills matches the target
        
        # Normalize the mentor vector (make it a unit vector)
        mentor_vector = normalize(mentor_vector.reshape(1, -1), norm='l2')  # Normalize mentor vector

        mentor_vectors.append(mentor_vector.flatten())  # Flatten it back into a 1D array
        mentor_names.append(mentor_name)

    # Debug: Check mentor vectors
    

    # Convert mentor vectors into a NumPy array
    mentor_vectors = np.array(mentor_vectors)

    # Calculate cosine similarity
    similarity_scores = cosine_similarity(target_array, mentor_vectors)

    # Debug: Check similarity scores before flattening

    # Flatten similarity_scores (since cosine_similarity returns a 2D array)
    similarity_scores = similarity_scores.flatten()

    # Combine mentor names and similarity scores into a list of tuples
    mentor_similarity_list = list(zip(mentor_names, similarity_scores))

    # Sort by similarity in descending order
    sorted_mentors = sorted(mentor_similarity_list, key=lambda x: x[1], reverse=True)

    
    
    # Optional: store just the mentor names in order
    sorted_mentor_names = [mentor for mentor, score in sorted_mentors]
    

    # Save sorted mentor names to Firestore under the user's document
    
    user_ref.update({
        "sortedMentors": sorted_mentor_names  # This will create or update the field "sortedMentors"
    })
    

    return sorted_mentor_names
