from configparser import ConfigParser
from argparse import ArgumentParser
import time
from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
from database import DataBase

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)

    DataBase.load_blacklist()
    DataBase.load_stop_words()

    DataBase.start_timer()
    start_time = time.time()
    crawler.start()
    end_time = time.time() 

    DataBase.save_blacklist()
    DataBase.print_summary() 



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
