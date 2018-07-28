import logging
import sys
import os
import time

from modules.subscene import Subscene
from modules.utilities import Utilities
from daemon_thread.daemon import DaemonBase
from daemon_thread.daemon import DaemonControl

logging.getLogger().setLevel(logging.INFO)


class App:
    
    """ Class that contains the main program to be executed
    """

    @staticmethod
    def main(language, movieMainDirectoryPath):

        logging.info("MAIN PROGRAM EXECUTION STARTED")
        logging.info('Language Selected: ' + language)
        logging.info('Main Movies Directory Path: ' + movieMainDirectoryPath)

        # Get a list of the name of the movie folders found inside the main directory
        movieFolderNames = Utilities.readMovieFolderNamesFromMainDirectory(movieMainDirectoryPath)

        # Log a warning message if no folders are found
        if len(movieFolderNames) == 0:
            logging.warn('No folders found')

        # Download subtitle for each folder found in the main directory
        for movieFolderName in movieFolderNames:

            logging.info('Processing folder: ' + movieFolderName)

            # Split the movieFolderName into different parts (movie name, year, quality, encoding, uploader)
            movieFolderNameParts = Utilities.splitMovieFolderName(movieFolderName)

            # Get the search URL with information about the year of release
            urlWithYear = Subscene.generateSearchSubtitleUrlWithYear(movieFolderNameParts[0], movieFolderNameParts[1], language)
            logging.info('URL with year info: ' + urlWithYear)

            # Get the search URL without the year of release
            urlWithoutYear = Subscene.generateSearchSubtitleUrlWithoutYear(movieFolderNameParts[0], language)
            logging.info('URL without year info: ' +  urlWithoutYear)

            # Get the required subtitle download link from the webpage obtained from the URLS
            # If one URL returns 404 error (page not found) or does not have the required subtitle, the other URLS are tried
            logging.info('Fetching subtitle download link for: ' + movieFolderName)
            downloadUrl = Subscene.getSubtitleDownloadLink([urlWithoutYear, urlWithYear], movieFolderName)

            # Check if the required subtitle download link was obtained
            if downloadUrl is not None:
                logging.info('Download link fetched: ' + downloadUrl)

                # Get Confirmation download link
                confirmationDownloadLink = Subscene.getSubtitleConfirmationDownloadLink(downloadUrl)
                logging.info('Confirmation Download Link: ' + confirmationDownloadLink)

                # Download the subtitle
                if Subscene.downloadSubtitle(confirmationDownloadLink, movieMainDirectoryPath, movieFolderName):
                    logging.info('Subtitle successfully downloaded for: ' + movieFolderName)
                else:
                    logging.warn('Fail to download subtitle for: ' + movieFolderName)
            else:
                logging.warn('No download links found for ' + movieFolderName)


        logging.info('MAIN PROGRAM COMPLETED SUCCESSFULLY')





class Daemon(DaemonBase):
    
    """ Inheriting from the Daemon Thread and overriding the run method to execute the main program
    """
    def run(self):
        while True:
            # The main methods takes as argument the language and the path to the movie main directory
            App.main(sys.argv[2], sys.argv[3])
            time.sleep(2)



# Start the program
if __name__ == '__main__':
    
    logging.info("To launch application use: python3 app.py start language path_to_movies_main_directory")
    logging.info("To stop the application use: python3 app.py stop")

    if len(sys.argv) < 4:
        if (sys.argv[1] == 'start' and len(sys.argv) < 4) or (len(sys.argv) == 1):
            logging.error('Wrong command line arguments, use: python3 app.py start|stop language movieMainDirectoryPath\n')
            sys.exit()


    daemonThread = DaemonControl(Daemon, '/tmp/test_daemon.pid', os.getcwd())

    if sys.argv[1] == 'start':
        # Check if path_to_movies_main_directory is valid
        if not os.path.isdir(sys.argv[3]):
            logging.error("Directory does not exists")
            sys.exit()
            
        logging.warn('Daemon Thread Started')
        daemonThread.start()
        
    elif sys.argv[1] == 'stop':
        daemonThread.stop()
        logging.warn('Daemon Thread Stopped')
