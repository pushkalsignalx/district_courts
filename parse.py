from bs4 import BeautifulSoup
import json,re,os


def parse_file(file):
    data_dict = []
    file = json.loads(file)
    try:
        soup = BeautifulSoup(file['party_data'], 'html.parser')
        table = soup.find('tbody')
        rows = table.find_all('tr')
        data = []
        onclick_attrs = []

        for row in rows:
            if row.find('a'):
                onclick = row.find('a')['onclick']
                match = re.search(r"viewHistory\(\d+,'([\w]+)',", onclick)
                onclick_attrs.append(match.group(1))
                cols = [ele.text.strip() for ele in row.find_all(['td', 'th'])]
                data.append(cols) 
                data2 = {
                    'case_number' : cols[1],
                    'appellant_and_respondent' : cols[2],
                    'cnr': match.group(1)
                }
                data_dict.append(data2)
    except Exception as e:
        print(e)
    
    return data_dict

def main():
    base_dir = './2010_2023/andhra pradesh'
    all_data_dicts = []
    count = 1
    for filename in os.listdir(base_dir):
        print(f'Processing filename = {filename}, count = {count}')
        if filename.endswith('.txt'):
            file_path = os.path.join(base_dir, filename)
            
            with open(file_path, 'r') as file:
                file_content = file.read()
            
            data_dict = parse_file(file_content)
            all_data_dicts.extend(data_dict)
        count +=1
        
    return all_data_dicts

if __name__ == '__main__':

    data_dict =  main()
    print(len(data_dict))
    with open('2010_2023/andhra pradesh/data2.json', 'w') as f:
        json.dump(data_dict, f, indent=3)
