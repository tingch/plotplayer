import matplotlib
import matplotlib.pylab as pylab

import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from matplotlib.figure import Figure
import tkinter.constants as Tkinter

WINDOW_SIZE=(8, 4.5)  # Aspect ratio (ie. 4:3, 16:9, 21:9) in relation to DPI; default is half 16:9 (8:4.5)
IMAGE_AXES_RECT = [0, 0.03, 1, 0.97]  # [ x, y, width, height ] in percentage of window size
SLIDER_AXES_RECT = [0, 0, 1, 0.03]  # [ x, y, width, height ] in percentage of window size
SLIDER_BACKGROUND_COLOR = 'lightgoldenrodyellow'

ANIMATION_NAME = 'PlotPlayer'

SKIP_BACK_BUTTON = 'left'
SKIP_AHEAD_BUTTON = 'right'
JUMP_BACK_BUTTON = 'down'
JUMP_AHEAD_BUTTON = 'up'
TOGGLE_PLAY_BUTTON = [ ' ', 'enter' ]
GOTO_BEGINNING_BUTTON = 'home'
GOTO_END_BUTTON = 'end'
TOGGLE_TOOLBAR_BUTTON = 't'
SAVE_BUTTON = 's'
SAVE_VIDEO_BUTTON = 'v'
SAVE_HTML_BUTTON = 'h'
SAVE_JAVASCRIPT_BUTTON = 'j'

KEYS_TRIGGER_STOP = [ SKIP_BACK_BUTTON, SKIP_AHEAD_BUTTON, JUMP_BACK_BUTTON, JUMP_AHEAD_BUTTON,
                     GOTO_BEGINNING_BUTTON, GOTO_END_BUTTON ]

VIDEO_SUFFIX = '.mp4'
HTML_SUFFIX = '.html'
JAVASCRIPT_SUFFIX = '-js.html'

SKIP_SIZE = 1
JUMP_SIZE = 10

pylab.plt.rcParams['keymap.save'].remove(SAVE_BUTTON)

def saveFile(fileName, data):
    file = open(fileName, 'w')
    file.write(data)
    file.close()

def assertIsFigure(value, variableName):
    assert isinstance(value, Figure), variableName + ' must be an instance of ' + str(Figure)

def assertIsInt(value, variableName):
    assert isinstance(value, int), variableName + ' must be an instance of ' + str(int) 

def assertIsFunction(value, variableName):
    assert callable(value), name + ' must be a callable function'

class PlotPlayer(object):
    '''Lightweight function based animation player for Matplotlib'''
    _figure = _animationName = None
    _animationAxes = _frameRate = None
    _sliderAxes = _slider = None
    _animation = _playing = None
    _drawFunc = _keyPressHandler = None
    _skipSize = _jumpSize = None
    _toolbarHidden = _playing = False
    _saveButtonPressed = False

    def __init__(self, windowTitle=None, figure=None, windowSize=WINDOW_SIZE, sliderBackgroundColor=SLIDER_BACKGROUND_COLOR, hideToolbar=True,
                keyPressHandler=None, skipSize=SKIP_SIZE, jumpSize=JUMP_SIZE):
        if figure == None:
            figure = pylab.plt.figure(figsize=windowSize)
        assertIsFigure(figure, 'figure')

        if not windowTitle == None:
            figure.canvas.set_window_title(windowTitle)
        else:
            figure.canvas.set_window_title(ANIMATION_NAME)

        if len(figure.axes) > 0:
            animationAxes = figure.gca()
        else:
            animationAxes = figure.add_axes(IMAGE_AXES_RECT)
            animationAxes.set_axis_off()

        sliderAxes = figure.add_axes(SLIDER_AXES_RECT, facecolor=sliderBackgroundColor)

        self._figure = figure
        self._animationAxes = animationAxes
        self._sliderAxes = sliderAxes
        self._keyPressHandler = keyPressHandler
        self._skipSize = skipSize
        self._jumpSize = jumpSize

        if hideToolbar:
            self.hideToolbar()

    def initializeAnimation(self, totalFrames, drawFunc, animationName=ANIMATION_NAME, frameRate=30):
        assertIsInt(totalFrames, 'totalFrames')
        assertIsFunction(drawFunc, 'drawFunc')
        assertIsInt(frameRate, 'frameRate')

        slider = Slider(self._sliderAxes, '', 0, totalFrames - 1, valinit=0.0)
        slider.on_changed(self.render)
        
        self._animationName = animationName
        self._figure.canvas.mpl_connect('button_press_event', self.handleMouseButtonDown)
        self._figure.canvas.mpl_connect('key_press_event', self.handleKeyPress)
        self._figure.canvas.mpl_connect('key_release_event', self.handleKeyRelease)

        self._playing = False
        self._drawFunc = drawFunc
        self._slider = slider
        self._frameRate = frameRate

    def render(self, frameNumber):
        frameNumber = min(max(0, int(frameNumber)), self._slider.valmax)
        self.renderSlider(frameNumber)
        self.renderImage(frameNumber)

    def renderImage(self, frameNumber):
        self._figure.sca(self._animationAxes)
        self._drawFunc(frameNumber, self._animationAxes)
        self._figure.canvas.draw_idle()

    def renderSlider(self, newFrameNumber):
        currentFrameNumber = int(self._slider.val)
        if currentFrameNumber != newFrameNumber:
            self._slider.set_val(newFrameNumber)

        if newFrameNumber == self._slider.valmax:
            self.stop()

    def play(self):
        if self._playing:
            return

        if self._slider.val == self._slider.valmax:
            self.render(0)

        framesToPlay = range(int(self._slider.val), self._slider.valmax + 1)
        animation = FuncAnimation(self._figure, self.render, framesToPlay, interval=1000 // self._frameRate, repeat=False)
        self._figure.canvas.draw()

        self._playing = True
        self._animation = animation

    def stop(self):
        if not self._playing:
            return

        self._animation.event_source.stop()
        self._playing = False

    def togglePlayback(self):
        if self._playing:
            self.stop()
        else:
            self.play()

    def hideToolbar(self):
        self._figure.canvas.toolbar.pack_forget()
        self._toolbarHidden = True

    def showToolbar(self):
        self._figure.canvas.toolbar.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        self._toolbarHidden = False

    def toggleToolbar(self):
        if self._toolbarHidden:
            self.showToolbar()
        else:
            self.hideToolbar()

    def handleKeyPress(self, eventData):
        if not self._keyPressHandler == None and self._keyPressHandler(eventData) == True:
            return
        
        key = eventData.key
        if self._saveButtonPressed:
            animationName = self._animationName
            if key == SAVE_VIDEO_BUTTON:
                self.saveVideo(animationName + VIDEO_SUFFIX)
            elif key == SAVE_HTML_BUTTON:
                self.saveHtml(animationName + HTML_SUFFIX)
            elif key == SAVE_JAVASCRIPT_BUTTON:
                self.saveJavascript(animationName + JAVASCRIPT_SUFFIX)

        if key in KEYS_TRIGGER_STOP:
            self.stop()

        currentFrame = int(self._slider.val)
        if key == SKIP_BACK_BUTTON:
            self.render(currentFrame - self._skipSize)
        elif key == SKIP_AHEAD_BUTTON:
            self.render(currentFrame + self._skipSize)
        elif key == JUMP_BACK_BUTTON:
            self.render(currentFrame - self._jumpSize)
        elif key == JUMP_AHEAD_BUTTON:
            self.render(currentFrame + self._jumpSize)
        elif key == GOTO_BEGINNING_BUTTON:
            self.render(0)
        elif key == GOTO_END_BUTTON:
            self.render(self._slider.valmax)
        elif key in TOGGLE_PLAY_BUTTON:
            self.togglePlayback()
        elif key == TOGGLE_TOOLBAR_BUTTON:
            self.toggleToolbar()
        elif key == SAVE_BUTTON:
            self._saveButtonPressed = True

    def handleKeyRelease(self, eventData):
        key = eventData.key

        if key == SAVE_BUTTON:
            self._saveButtonPressed = False

    def handleMouseButtonDown(self, eventData):
        if eventData.inaxes == self._sliderAxes:
            self.stop()

    def getHtml(self):
        html = self._animation.to_html5_video()
        return html

    def getJavascript(self):
        javascript = self._animation.to_jshtml()
        return javascript

    def saveVideo(self, fileName, writer=None):
        self._animation.save(fileName, writer)

    def saveHtml(self, fileName):
        videoHtml = self.getHtml()
        saveFile(fileName, videoHtml)

    def saveJavascript(self, fileName):
        videoJavascript = self.getJavascript()
        saveFile(fileName, videoJavascript)

    @staticmethod
    def showPlayers(blocking=True):
        try:
            pylab.plt.show(blocking)
        except AttributeError:
            print('Videofig encountered a playback error.')
            print('This is usually due to a videofig window getting closed during animation playback...')
            print('This causes all open videofig windows to malfunction.')
            print('Closing all videofig windows...')
            pylab.plt.close('all')
            pass