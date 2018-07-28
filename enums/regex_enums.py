'''
Regular Expressions
'''

from enum import Enum

class RegexEnums(Enum):
    
    # valid movie folder name regular expression
    VALID_MOVIE_FOLDER_NAME_REGEX = '[a-zA-Z0-9\.]+\.\d{4}\.[0-9]+p\.[a-zA-Z0-9\.-]+-[a-zA-Z0-9\[\]\.]+'
    
    # valid movie folder name grouping regular expression
    VALID_MOVIE_FOLDER_NAME_GROUP_REGEX = '([a-zA-Z0-9\.]+)\.(\d{4})\.([0-9]+p)\.([a-zA-Z0-9\.-]+)-([a-zA-Z0-9\[\]\.]+)'
    
    # regular expression to match the pattern of a subtitle download link and group the download hyperlink
    MATCH_DOWNLOAD_LINK_REGEX = '<a href="([a-zA-Z0-9-/]+)">\s+<span[ \sa-zA-Z"=\'-]+>[ \sa-zA-Z]+</span>\s+<span>\s+'