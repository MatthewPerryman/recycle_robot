import click
import json
import hashlib
import glob
import os

def get_hash(path):
    """
    Return the hash of the input path
    """
    return hashlib.md5(path.encode('utf-8')).hexdigest()

@click.argument('source', type=click.Path(exists=True, file_okay=False,\
            resolve_path=True, readable=True), required=True)
@click.argument('directory', type=click.Path(exists=True, file_okay=False,\
            resolve_path=True, readable=True), required=True)
@click.command()
def main(directory, source):
    for path in glob.glob(directory + '\*.json'):
        name = ""
        with open(path, 'r+') as f:
            image_dict = json.load(f)
            
            image_dict["asset"]["path"] = "file:" + source.replace("\\", "/") + "/" + image_dict["asset"]["name"]
            image_dict["asset"]["id"] = get_hash(image_dict["asset"]["path"])
            name = image_dict["asset"]["id"]
                
            f.seek(0)  # rewind
            json.dump(image_dict, f, indent=4)
            f.truncate()
        
        os.rename(path, directory + '\\' + name + '-asset.json')
    
    
if __name__ == '__main__':
    main()