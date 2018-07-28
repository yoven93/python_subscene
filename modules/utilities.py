import os
import re
from enums.regex_enums import RegexEnums



class Utilities:
    
    @staticmethod
    def readMovieFolderNamesFromMainDirectory(pathToMainDirectory):
    
        """Read the name of movie folders inside of a main directory
        Only valid movie folder names are added to the output list
        
        @param pathToMainDirectory: The path to the main directory containing the movie folders which names need to be read
        
        @return: A list of movie folder names
        """
        
        movies = []
        for root, movieFolders, files in os.walk(pathToMainDirectory, topdown=False):
            
            for moviefolderName in movieFolders:
                
                # Checks if movie folder name is valid before adding it to the list
                # Skip the folder if the folder name is invalid
                if Utilities.checkMovieFolderNameValidity(moviefolderName) is not None:
                    movies.append(moviefolderName)
            
        return movies


    @staticmethod
    def checkMovieFolderNameValidity(movieFolderName):
        
        """ Check if the movie folder name is valid (Has the appropriate naming format)
        
        @param movieFolderName: The name of the movie folder that needs to be validated
        
        @return: A match object if the movie folder name is valid else return None
        """
    
        return re.match(RegexEnums.VALID_MOVIE_FOLDER_NAME_REGEX.value, movieFolderName)
    
    
    @staticmethod
    def splitMovieFolderName(movieFolderName):
        
        """  Analyze a movie folder name and split it into 5 parts
        part1: movie name
        part2: year
        part3: quality
        part4: encoding
        part5: uploader
        
        @param movieFolderName:  The name of the movie folder to be analyzed and split
        
        @return: A tuple containing all 5 parts in order (part1 to part5)
        """
        
        parts = re.search(RegexEnums.VALID_MOVIE_FOLDER_NAME_GROUP_REGEX.value, movieFolderName)
        
        return (parts.group(1), parts.group(2), parts.group(3), parts.group(4), parts.group(5))

