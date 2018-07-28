import io
import os
import re
import time
import urllib.error
import urllib.request
import zipfile
import logging

from bs4 import BeautifulSoup

from enums.regex_enums import RegexEnums
from enums.subscene_enums import SubsceneEnums


logging.getLogger().setLevel(logging.INFO)


class Subscene:
    
    @staticmethod
    def generateSearchSubtitleUrlWithYear(movieName, yearOfRelease, language):
        
        """ Generate a URL based on the movie name, year of release and language
        
        @param    movieName:    The name of the movie which subtitle needs to be downloaded
        @param    yearOfRelease:    The year that the movie was released 
        @param    language:    The language of choice
        
        @return:    A URL required to make the search     
        """
        
        # Replace any . in the movie name with -
        movieName = movieName.replace('.', '-')
        
        # Generate URL with year
        urlWitYear = SubsceneEnums.SUBSCENE_DOWNLOAD_URL.value + "/" + movieName + '-' + yearOfRelease + "/" + language.lower()
        
        return urlWitYear
    
    
    
    @staticmethod
    def generateSearchSubtitleUrlWithoutYear(movieName, language):
        
        """ Generate a URL based on the movie name and language
        
        @param    movieName:    The name of the movie which subtitle needs to be downloaded
        @param    language:    The language of choice
        
        @return:    A URL required to make the search     
        """
        
        # Replace any . in the movie name with -
        movieName = movieName.replace('.', '-')
        
        # Generate URL without year
        urlWithoutYear = SubsceneEnums.SUBSCENE_DOWNLOAD_URL.value + "/" + movieName + "/" + language.lower()
        
        return urlWithoutYear
    
    
    
    @staticmethod
    def getWebPage(url):
        
        """ Retrieve the webpage of the URL provided
        
        @param    url:    The URL of the page to be searched
        
        @return    The webpage
        """
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req)
        return resp.read()
        
    
    
    @staticmethod
    def generateRegexToGetDownloadLink(movieFolderName):
        
        """ Generate a regular expression to match patterns of a download link from the subscene webpage
        
        @param    movieFolderName: The movie folder name for which the subtitle needs to be downloaded
        
        @return    A regular expression to match the required patterns
        """
        
        return RegexEnums.MATCH_DOWNLOAD_LINK_REGEX.value + movieFolderName
    
    
    
    @staticmethod
    def getSubtitleDownloadLink(urls, movieFolderName):
        
        """ Tries URLs provided and extract the required subtitle download link for the specified movie folder name if a webpage is obtained
        
        @param    urls:    A list of urls of the webpage to be tried
        @param    movieFolderName:    The movie folder name for which the subtitle needs to be downloaded
        
        @return    The subtitle download link for the specified movie folder name if found,
                   else return None if page or link is not found
        """
            
        index = 0
        
        while True:
            
            try:
                # Try to get webpage from url
                webpage = Subscene.getWebPage(urls[index])
                
                soup = BeautifulSoup(webpage, "html.parser")
                links = re.search(Subscene.generateRegexToGetDownloadLink(movieFolderName), str(soup))
                
                # If no links is found, try with another URL
                if links is None:
                    if index < len(urls):
                        index += 1
                else:
                    return SubsceneEnums.SUBSCENE_URL.value + links.group(1)
                
            except urllib.error.HTTPError as e:
                
                # If page is not found
                if str(e) == 'HTTP Error 404: Not Found':
                    logging.warn('No page found at: ' + urls[index])
                    index += 1
                    
                # If too many request is sent and an error occurs, try again
                if str(e) == 'HTTP Error 409: Conflict':
                    logging.warn('Too many request to ' + urls[index])
                
                # Add a timer to minimize the chance of having to many requests error
                time.sleep(1.5)
                
            
            # Return None if all the links returns 404 error or does not contain any links
            if index == len(urls):
                return None

    
    
    @staticmethod
    def getSubtitleConfirmationDownloadLink(downloadUrl):
        
        """ Go to the confirmation download link page and extract the confirmation download link
        
        @param    downloadUrl:    The url that leads to the confirmation download page
        
        @return:    The confirmation download link if found else return None
        """
        
        while True:
            
            try:
                webpage = BeautifulSoup(Subscene.getWebPage(downloadUrl), "html5lib")
                
                # Search for the confirmation download link
                for link in webpage.find_all("a"):
                    if "download" in str(link):
                        return SubsceneEnums.SUBSCENE_URL.value + link['href']
                
                # Return None if no confirmation download link is found
                return None
            
            except urllib.error.HTTPError as e:  
                 
                # If page is not found, return None
                if str(e) == 'HTTP Error 404: Not Found':
                    logging.warn('No page found at: ' + downloadUrl)
                    return None
                    
                # If too many request is sent and an error occurs, try again
                if str(e) == 'HTTP Error 409: Conflict':
                    logging.warn('Too many request to ' + downloadUrl)
                
                # Add a timer to minimize the chance of having to many requests error
                time.sleep(1.5)
            
        
        
    @staticmethod
    def downloadSubtitle(confirmationDownloadLink, outputDirPath, movieFolderName):
        
        """ Download the subtitle, extract it and store it in the desired file location
        
        @param    confirmationDownloadLink:    The confirmation link to download the subtitle
        @param    outputDirPath:    The path to the main directory containing the movie folders
        @param    movieFolderName:    The name of the movie folder which subtitle needs to be downloaded
        
        @return:    True if subtitle is downloaded and extracted successfully else return False
        """
        
        # The download location
        # os.path was used to make the path platform independent
        downloadLocation = os.path.join(outputDirPath, movieFolderName)
        
        # Download the subtitle
        while True:
            try:
                downloadContent = Subscene.getWebPage(confirmationDownloadLink)
                
                # Extract the downloadContent and store in the download location provided
                z = zipfile.ZipFile(io.BytesIO(downloadContent))
                z.extractall(downloadLocation)
                return True
            
            except urllib.error.HTTPError as e:  
                     
                # If page is not found, return None
                if str(e) == 'HTTP Error 404: Not Found':
                    logging.warn('Invalid Confirmation Download Link')
                    return False
                    
                # If too many request is sent and an error occurs, try again
                if str(e) == 'HTTP Error 409: Conflict':
                    logging.warn('Too many request')
                
                # Add a timer to minimize the chance of having to many requests error
                time.sleep(1.5)
                    
            except Exception as e:
                logging.error('An error occurred')
                return False
        
    