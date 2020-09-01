'''
mkcourses.py

Make the courses/chapters list for OpenRevise.

Can be imported as a library. Refer to docs/mkchapters.html

Copyright (C) 2020-present jkelol111
'''

__author__ = 'jkelol111'
__copyright__ = 'Copyright (C) 2020-present jkelol111'
__license__ = 'Public Domain'
__version__ = '1.0.1'

import os
import shutil
import json
import threading
import pprint
import argparse
import logging

class Courses:
    '''
    Utilities to scan for chapters.

    ...

    Attributes:
    -----------
    directory : str
        The path to the notes folder.
    dryrun : bool
        Perform real writes or test writes.
    everything : list
        List of courses and their associated chapters.

    Methods
    -------
    To be added.

    '''
    def __init__(self, directory, dryrun):
        '''
        Initialize the class by scanning for courses.

        Parameters
        ----------
        directory : str
            The path to the notes folder.
        dryrun : bool
            Perform real writes or test writes.
        '''
        self.dryrun = dryrun
        self.directory = directory
        self.everything = {}
        self.refresh_courses()

    def start_thread(self, function):
        '''
        Starts a new Thread for moar performance.

        Parameters
        ----------
        function : func
            A function to run in the new thread.

        Returns
        -------
        None
        '''
        t = threading.Thread(target=function)
        t.start()

    def refresh_courses(self, threaded=False):
        '''
        Refreshes this list of courses and their associated files into this class's self.everything list.

        If the argument 'threaded' is not passed, we will assume single-threaded mode.

        Parameters
        ----------
        threaded : bool
            Chooses the threading model.

        Returns
        -------
        None
        '''
        def task_refresh_courses():
            total_files = 0
            # Scan for the courses in the supplied notes directory
            for course in os.scandir(self.directory):
                # Check if the course is a directory or not, or is meant to be non-indexed.
                if not course.name.startswith('.') and course.is_dir():
                    logging.debug('Found course: ' + course.name)
                    # Set up the course list.
                    self.everything[course.name] = {}
                    # Scan for the chapters inside the course.
                    for chapter in os.scandir(os.path.join(self.directory, course.name)):
                        # Check if the chapter is a directory or not, or is meant to be non-indexed.
                        if not chapter.name.startswith('.') and chapter.is_dir():
                            logging.debug('--- Found chapter: ' + chapter.name)
                            # Set up the chapters list
                            self.everything[course.name][chapter.name] = {}
                            # Scan for chapter files of whatever format.
                            for file in os.scandir(os.path.join(self.directory, course.name, chapter)):
                                # Check if the chapter file is a file or not, or is meant to be non-indexed.
                                if not file.name.startswith('.') and file.is_file():
                                    logging.debug('------ Found file: ' + file.name)
                                    # Get the extension of the file.
                                    file_extension = os.path.splitext(file.name)[1].split('.')[1]
                                    # Fix for KeyError, creates an empty array for file type if not present yet.
                                    if not file_extension in self.everything[course.name][chapter.name]:
                                        self.everything[course.name][chapter.name][file_extension] = []
                                    if not self.everything[course.name][chapter.name][file_extension]:
                                        self.everything[course.name][chapter.name][file_extension] = []
                                    # Add the file into the file type array for the chapter and course.
                                    self.everything[course.name][chapter.name][file_extension].append(file.name)
                                    # Tally up the total files found (useless informational thing).
                                    total_files += 1
            logging.info('Found {0} files!'.format(total_files))
        # Check if the function is to be executed under a new thread (useful for GUI apps).
        if threaded:
            self.start_thread(task_refresh_courses)
        elif not threaded:
            task_refresh_courses()

    def get_courses(self, threaded=False):
        '''
        Returns the list of courses.

        If the argument 'threaded' is not passed, we will assume single-threaded mode.

        Parameters
        ----------
        threaded : bool
            Chooses the threading model.

        Returns
        -------
        If courses is not []: ['course0', 'course1', ...]
        else []

        Returns an empty array if there are no courses.
        '''
        def task_get_courses():
            courses = []
            for course in self.everything:
                courses.append(str(course))
            return courses
        # Check if the function is to be executed under a new thread (useful for GUI apps).
        if threaded:
            self.start_thread(task_get_courses)
        elif not threaded:
            task_get_courses()

    def get_course_chapters(self, course):
        '''
        Returns the list of chapters in a particular course.

        Parameters
        ----------
        None

        Returns
        -------
        If course exists in everything: list {}
        else: TypeError

        Throws a TypeError if the course doesn't exist.
        '''
        if course in self.everything:
            return self.everything[course]
        else:
            raise TypeError('"{0}" is not in the courses list!'.format(course))

    def write_courses(self, threaded=False):
        '''
        Writes the list of courses to notes directory/courses.json

        If the argument 'threaded' is not passed, we will assume single-threaded mode.

        Parameters
        ----------
        threaded : bool
            Chooses the threading model.

        Returns
        -------
        None
        '''
        if not self.dryrun:
            def task_write_courses():
                with open(os.path.join(self.directory, 'index.json'), 'w') as courses:
                    json.dump(self.everything, courses)
            # Check if the function is to be executed under a new thread (useful for GUI apps).
            if threaded:
                self.start_thread(task_write_courses)
            elif not threaded:
                task_write_courses()
        else:
            logging.warning('Dry-run enabled, not writing to disk.')


# Run only if the file isn't imported
if __name__ == '__main__':
    # Prints standard copyright stuff.
    print('{file} (version: {version})'.format(
        file=__file__,
        version=__version__
    ))
    print(__copyright__)
    print('-----------------------------------------------')
    # Scan for command line arguments
    CMD_PARSER = argparse.ArgumentParser(
        description='Generate the chapters.json and courses.json database for OpenRevise.'
    )
    CMD_PARSER.add_argument(
        'command',
        action='store',
        help='The command to run (generate, list)')

    CMD_PARSER.add_argument(
        '--force-directory',
        action='store',
        dest='forced_directory',
        help='The directory the notes folder. If this is not provided, the "notes" folder in the\
              same directory will be used.')
    CMD_PARSER.add_argument(
        '-d', '--dryrun',
        action="store_true",
        default=False,
        help='Dry run / perform the command without actually changing anything.')
    CMD_PARSER.add_argument(
        '-D', '--debug',
        action="store_true",
        default=False,
        help='Activates enhanced logging.')
    CMD_PARSED = CMD_PARSER.parse_args()
    print('Command parsed: ' + CMD_PARSED.command)
    if CMD_PARSED.forced_directory is not None:
        print('Forced directory parsed: ' + CMD_PARSED.forced_directory)
    else:
        print('Forced directory not specified, skipping.')
    print('Dry run parsed: ' + str(CMD_PARSED.dryrun))
    print('Debug logging: ' + str(CMD_PARSED.debug))
    print('-----------------------------------------------')
    if CMD_PARSED.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    logging.info('Selected task: {0}\n'.format(CMD_PARSED.command))
    if CMD_PARSED.command in ['generate', 'list']:
        if CMD_PARSED.forced_directory is not None:
            logging.info('0/x: Scanning forced directory: ' + CMD_PARSED.forced_directory)
            SCANNER = Courses(CMD_PARSED.forced_directory, CMD_PARSED.dryrun)
        else:
            logging.info('0/x: Scanning notes/ directory...')
            SCANNER = Courses(os.path.join(os.getcwd(), 'notes'), CMD_PARSED.dryrun)
    if CMD_PARSED.command == 'generate':
        print('')
        logging.info('1/2: Compiling the JSON...\n')
        if CMD_PARSED.forced_directory is not None:
            logging.info('2/2: Writing {0}/courses.json...'.format(CMD_PARSED.forced_directory))
        else:
            logging.info('2/2: Writing notes/courses.json...')
        SCANNER.write_courses()
    elif CMD_PARSED.command == 'list':
        print()
        logging.info('1/1: Listing courses and associated files...')
        pprint.pprint(SCANNER.everything)
    print('')
    logging.info('All done!')
