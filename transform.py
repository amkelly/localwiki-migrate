# transform saved localwiki data for ingest into Wikimeda instance
import json
from bs4 import BeautifulSoup
from html_convert import parse_and_convert

sample_localwiki_data = {
    'url': 'https://localwiki.org/api/v4/pages/232046/', 
    'name': 'Indian Carry Road', 
    'slug': 'indian carry road', 
    'content': '<p>\n\t<span class="image_frame image_frame_border image_left"><img src="_files/Swenson.jpg" style="width: 450px; height: 248px;"><span style="width: 450px;" class="image_caption">Originally a part of the Swenson Camp, this building was moved onto Indian Carry Road in the early 1980s.</span></span><span class="image_frame image_frame_border image_right"><img src="_files/Guide%20House.jpg" style="width: 450px; height: 280px;"><span style="width: 450px;" class="image_caption">The guide house, built in the late 1880s, is the last remaining building in its original location from the <a href="Rustic%20Lodge">Rustic Lodge</a> era. Photograph by Herbert MacArthur</span></span><a href="Indian%20Carry%20Road">Indian Carry Road</a> is a private road which runs north from <a href="New%20York%20Route%203">New York Route 3</a> , directly across from <a href="Corey\'s%20Road">Corey\'s Road</a> it leads past the <a href="Swenson%20Camp%20">Indian Carry Chapel</a> , the <a href="Rustic%20Lodge%20Guide%20House">Rustic Lodge guide house</a> , the <a href="Swenson%20Camp">Swenson Camp</a> and other homes which were built after the Swenson Camp era.<span class="image_frame image_frame_border"><img src="_files/Indian%20Carry%20Chapel.jpg" style="width: 450px; height: 338px;"><span style="width: 450px;" class="image_caption">Indian Carry Chapel</span></span></p>',
    'region': 'https://localwiki.org/api/v4/regions/23/', 
    'tags': []
    }



def transform_content(html_content):
    """
    Transforms HTML content to wikimarkup.
    """
    try:
        # Convert HTML to wikimarkup
        #print(html_content)
        wikimarkup = parse_and_convert(html_content)
        print(wikimarkup)
        return wikimarkup
    except Exception as e:
        print(f"Error converting HTML to wikimarkup: {e}")
        return None

# Function to load JSON data from a file
def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

# Function to write JSON data to a new file
def write_json_data(data, output_file_path):
    try:
        with open(output_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data written to {output_file_path}")
    except Exception as e:
        print(f"Error writing JSON file: {e}")

# Main function to process the JSON data
def process_json_data(input_file_path, output_file_path):
    # Load JSON data from the input file
    data = load_json_data(input_file_path)
    
    if data:
        # Extract and transform 'content'
        #need a for loop in here to iterate through each entry in large json files with multiple entries and multiple 'content' fields for transformation.
        original_content = data.get('content', '')
        print(original_content)
        transformed_content = transform_content(original_content)
        
        if transformed_content:
            # Replace the original 'content' with the transformed content
            data['content'] = transformed_content
            
            # Write the transformed data to a new JSON file
            write_json_data(data, output_file_path)
        else:
            print("Content transformation failed.")
    else:
        print("Failed to load JSON data.")


# Example usage
if __name__ == "__main__":
    input_file_path = 'sample_in.json'
    output_file_path = 'sample_out.json'
    
    process_json_data(input_file_path, output_file_path)


#transform_content(sample_localwiki_data['content'])