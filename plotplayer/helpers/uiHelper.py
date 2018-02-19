from tkinter import filedialog
import matplotlib.pylab as pylab

ALL_FILES_EXTENSION = '*.*'
ALL_FILES_TYPE = [ 'All Files', ALL_FILES_EXTENSION ]

def getSaveDialogResult(title, defaultFileName, fileTypes=[ ALL_FILES_TYPE ], defaultExtension=ALL_FILES_EXTENSION):
    saveFileName = filedialog.asksaveasfilename(title=title, filetypes=fileTypes,
                                               defaultextension=defaultExtension, initialfile=defaultFileName)
    return saveFileName

def showPlayers(blocking=True):
    try:
        pylab.plt.show(blocking)
    except AttributeError:
        print('Plotplayer encountered a playback error.')
        print('This is usually due to a plotplayer window getting closed during animation playback...')
        print('This causes all open plotplayer windows to malfunction.')
        print('Closing all plotplayer windows...')
        pylab.plt.close('all')
        pass