from lxml import etree
from io import StringIO
from pathlib import Path
import pytest
import re
import requests
import time


@pytest.fixture(scope="session")
def temp_directory(tmp_path_factory):
    fn = tmp_path_factory.mktemp("i2d_test")
    return fn


def get_links(session, url):
    print("Getting links from: " + url)
    page = session.get(url)
    html = page.content.decode("utf-8")
    tree = etree.parse(StringIO(html), parser=etree.HTMLParser())
    refs = tree.xpath("//a")
    return list(set([link.get('href', '') for link in refs]))

def is_in_category(test_path):
    test_list = ['ct', 'pt']
    return any(el in test_path for el in test_list)
    
def has_extension(l):
    ext = ['.dcm', '.hdr', '.img']
    return any([l.lower().endswith(e.lower()) for e in ext])

def download_file(
    out_folder,
    base_url='http://sphinx.if.uj.edu.pl/~rakoczy/FormatConverterTests/inputs'
):
    for url in [
        f'{base_url}/dicoms/example_pt', f'{base_url}/dicoms/reference_pt', f'{base_url}/interfiles'
    ]:
        print(url)
        session = requests.Session()

        match = re.search(base_url, url)
        basedir = match.string[match.end()+1:] if match else ''

        links = get_links(session, url)
        lext = [l for l in links if has_extension(l)]
        for fext in lext:
            folder = out_folder / basedir
            filepath = folder / fext
            if Path(filepath).is_file():
                print("File exists: " + str(filepath))
            else:
                print("File doesn't exist: " + str(filepath))
                print("Downloading... " + f'{url}/{fext}')
                f = session.get(f'{url}/{fext}')
                time.sleep(0.05)
                Path(folder).mkdir(parents=True, exist_ok=True)
                open(filepath, 'wb').write(f.content)

@pytest.fixture
def data_directory(pytestconfig):
    out_folder = Path('tests/inputs')
    download_file(out_folder=out_folder)
    return out_folder
