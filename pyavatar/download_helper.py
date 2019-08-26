import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import os


class Extractor:
    def distribution_links(self, *args, **kwargs):
        """Crawl the given pypi page url to get all the distribution links"""
        page = requests.get(args[0])
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            l = {link.get_text(strip=True):link['href'] for link in soup.select('table.table--downloads tr th a') if not link.has_attr('class')}
            # print(l)
            return l
        else:
            raise IOError('Could not fetch from url - {}'.format(args[0]))

class BasicExtractor(Extractor):
    def distribution_links(self, *args, **kwargs):   
        # print(args)     
        return super().distribution_links(*args, **kwargs)

class Avatar:
    def download_dependency(self, depn_version, download_path):
        """Downloads the given dependency name into the given folder."""  
        # depn_version = 'attrs<=18.1.0'  
        # download_path = 'E:\\PyWorkspace\\PyAvatar\\tdwn'
        base_pypi_url = 'https://pypi.org/project/'
        url_components = [base_pypi_url]       
        non_word_regex = re.compile(r'[=><~]+')    
        depn_nm, version = non_word_regex.split(depn_version)
        # TODO : Logic for finding the version when >= or <=  or ~= is given needs to be found out.
        url_components.extend([depn_nm, version])
        url_components.append('#files')
        url = '/'.join(s.strip('/') for s in url_components)
        # print(url)
        # TODO: Further filters for setting platform type, python version and architecture in future
        extractor = BasicExtractor()
        distrib_links = extractor.distribution_links(url)
        for k, url in distrib_links.items():
            # TODO: Log the name of the file being downloaded
            response = requests.get(url, stream=True)
            path_ = os.path.join(download_path, k)
            with open(path_, "wb") as fh:
                for data in tqdm(response.iter_content()):
                    fh.write(data)

    def _clean_folder(self, download_path):
        for the_file in os.listdir(download_path):
            file_path = os.path.join(download_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def download(self, req_file_path, download_path):
        """Download each requirement from req_file_path and store it in download_path."""
        with open(req_file_path, 'r') as rh:
            content = rh.readlines()
        content = [c.strip() for c in content]
        # Clean the download path before downloading new files.
        self._clean_folder(download_path)
        for depn_version in content:
            self.download_dependency(depn_version, download_path)

if __name__ == "__main__":
    Avatar().download('E:\\PyWorkspace\\PyAvatar\\requirements.txt', 'E:\\PyWorkspace\\PyAvatar\\tdwn')            