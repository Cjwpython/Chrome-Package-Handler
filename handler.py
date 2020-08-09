# coding: utf-8
import json
import os
import logging
import argparse
from settings import ColoredLogger, base_dir
import urlparse

logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger("hanler")
logger.setLevel(logging.DEBUG)

url_list = []
base_data = {
}


def handler(choices, dir_path):
    """
    :param choice:  list ['header']
    :return:
    """
    file_list = os.listdir(dir_path)
    if ".keepgit" in file_list:
        file_list.remove(".keepgit")
    if not file_list:
        logger.error("No files in current {} directory".format(dir_path))
    for file_name in file_list:
        try:
            with open(os.path.join(dir_path, file_name)) as f:
                data = json.loads(f.read())
                for i in data["log"]["entries"]:
                    if i.has_key("request"):
                        url = i["request"]["url"]
                        key = urlparse.urlparse(str(url)).netloc
                        if key not in base_data:
                            base_data[key] = {}
                        if url not in url_list:
                            url_list.append(url)
                            base_data[key][url] = {}
                        else:
                            continue
                        for choice in choices:
                            if choice == "url":
                                base_data[key][url]["url"] = i["request"]["url"]
                            if choice == "request":
                                headers = {}
                                for p in i["request"]["headers"]:
                                    headers[p["name"]] = p["value"]
                                base_data[key][url]["request"] = headers
                            if choice == "response":
                                base_data[key][url]["response"] = i["response"]
                return base_data
        except Exception as e:
            logger.error(e)


def save_result(data, svae_dir_path):
    for i in data:
        with open(os.path.join(svae_dir_path, i), "w") as f:
            json.dump(data[i], f, indent=4)


def parse():
    parser = argparse.ArgumentParser(description='Chrome-package-handler')
    parser.add_argument('-c', '--choice', dest='choice', nargs='+',
                        choices=["url", "header", "request", "response", "all"],
                        help=u'抓取的内容选择')
    parser.add_argument('-s', '--save', dest='save', default=os.path.join(base_dir, "results"),
                        help=u'结果保存的路径')
    parser.add_argument('-d', '--dir', dest='dir', default=os.path.join(base_dir, "urls"),
                        help=u'文件读取路径')
    args = parser.parse_args()
    if not any([args.choice]):
        parser.print_help()
        exit(1)
    if 'all' in args.choice:
        args.choice = ["url", "header", "request", "response"]

    if not os.path.exists(args.save):
        os.makedirs(args.save)
        logger.info("auto mkdir {}".format(args.save))
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
        logger.info("auto mkdir {}".format(args.dir))
    return args.choice, args.save, args.dir


if __name__ == '__main__':
    choice, save, dir = parse()
    data = handler(choice, dir)
    save_result(data, save)
