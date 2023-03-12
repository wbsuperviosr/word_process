from pydantic import BaseModel
from argparse import ArgumentParser

from typing import Optional


class DocXConfig(BaseModel):
    type: str
    title: Optional[str]
    cache: bool
    output_dir: str
    image_dir: str


def make_parseargs(args: Optional[list[str]] = None):
    parser = ArgumentParser(description="word2json conversion program")

    parser.add_argument(
        "-t",
        "--type",
        help="the document type",
        required=True,
        choices=["casefile", "about", "media", "voice", "post", "timeline", "rumor"],
    )
    parser.add_argument(
        "-n",
        "--title",
        help="the document title. If missed, process the entire document type",
        required=False,
    )

    parser.add_argument(
        "-c",
        "--no_cache",
        action="store_true",
        default=False,
        help="If provide, don't use image cache foder, directly downlaod from web",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default="mswords",
        help="the output directory of the word files",
    )
    parser.add_argument(
        "-i",
        "--image_dir",
        default="images",
        help="the image directory containing the cached images",
    )

    if args is not None:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    return DocXConfig(
        type=args.type,
        title=args.title,
        cache=not args.no_cache,
        output_dir=args.output_dir,
        image_dir=args.image_dir,
    )
