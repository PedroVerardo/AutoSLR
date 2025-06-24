import pandas as pd
import re
import numpy as np

def parse_log_to_dataframe(log_data: str) -> pd.DataFrame:
    """
    Parses the provided log data string into a pandas DataFrame.

    Args:
        log_data: A string containing the log output.

    Returns:
        A pandas DataFrame with columns 'reference', 'input_text',
        and separate columns for each embedding model's result.
    """

    data = []
    current_reference = None
    current_input_text = None
    temp_results = {}

    lines = log_data.strip().split('\n')

    for line in lines:
        # Ignore lines related to networkx warnings or irrelevant info
        if "networkx" in line or "RuntimeWarning" in line or line.strip() == "":
            continue

        # Extract Processing reference
        ref_match = re.search(r'Processing reference: (\S+)', line)
        if ref_match:
            # If we were processing a previous entry, save it before starting a new one
            if current_reference and current_input_text and temp_results:
                row = {
                    'reference': current_reference,
                    'input_text': current_input_text
                }
                row.update(temp_results)
                data.append(row)
                temp_results = {} # Reset for the next input_text

            current_reference = ref_match.group(1)
            # Reset input_text and temp_results when a new reference starts
            current_input_text = None
            temp_results = {}
            continue

        # Extract Input text
        input_text_match = re.search(r'Input text: (.+)', line)
        if input_text_match:
            # If there are accumulated results for the previous input_text, save them
            if current_input_text and temp_results:
                row = {
                    'reference': current_reference,
                    'input_text': current_input_text
                }
                row.update(temp_results)
                data.append(row)
            current_input_text = input_text_match.group(1).strip()
            temp_results = {} # Reset for the new input_text
            continue

        # Extract embedding model results
        # This regex captures the model name (e.g., Word2Vec, BERT) and the result string
        result_match = re.search(r'(\w+) (.+) Result: (.+)', line)
        if result_match:
            model_name = result_match.group(1)
            # We are ignoring the 'input' part of the '{embedding_model} {imput} Result: {string}'
            # as it's already captured by 'Input text: {string}'
            result_value = result_match.group(3)
            if current_reference and current_input_text:
                temp_results[f'{model_name}_Result'] = result_value
            continue

    # After the loop, add any remaining data
    if current_reference and current_input_text and temp_results:
        row = {
            'reference': current_reference,
            'input_text': current_input_text
        }
        row.update(temp_results)
        data.append(row)

    df = pd.DataFrame(data)

    # Reorder columns to have reference and input_text first
    if not df.empty:
        cols = ['reference', 'input_text'] + [col for col in df.columns if col not in ['reference', 'input_text']]
        df = df[cols]

    return df

# Your provided log data
with open('/home/pramos/Documents/AutoSLR/analysis/result.txt', 'r') as file:
    log_data = file.read()

# Parse the log data
df = parse_log_to_dataframe(log_data)

# Display the DataFrame
#print(df)

# You can save it to a CSV file if needed:
# df.to_csv('parsed_results.csv', index=False)
import matplotlib.pyplot as plt

# Provided vectors
word2vec = [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0]
sbert = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0]
scibert = [1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
gemini = [1, 1, 1, 0, 1, 0, 1 , 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1 ,0, 1]

print(len(word2vec), len(sbert), len(scibert), len(gemini))

models = {
    'word2vec': word2vec,
    'sbert': sbert,
    'scibert': scibert,
    'gemini': gemini
}

# Separate into even and odd indices
even_indices = slice(0, None, 2)
odd_indices = slice(1, None, 2)

# Bar plot for the total of each one (doubled for 54)
totals = [sum(word2vec), sum(sbert), sum(scibert), sum(gemini)]
model_names = list(models.keys())

plt.figure(figsize=(6, 4))
plt.bar(model_names, totals)
plt.ylabel('Total (out of 27)')
plt.title('Total for Each Model')
plt.ylim(0, 27)  # Set y-axis upper limit to 54
plt.savefig('model_totals_bar.png')