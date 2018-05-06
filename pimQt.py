#!/usr/bin/env python
from __future__ import unicode_literals
import sys
# from PySide2.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PySide2 import QtWidgets, QtCore
from pim_calc import PIMCalc
import logging
from itertools import cycle

# try to import plotting
plt = None
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    plt.style.use('bmh')
    import numpy as np
    import scipy.stats as stats
except ImportError:
    print "no plotting.. :/"
    raise


class PIMCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # self.fig, self.axes = plt.subplots()

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        plt.style.use('bmh')


	def plot_beta_hist(ax, a, b):
            from numpy.random import beta
            ax.hist(beta(a, b, size=10000), histtype="stepfilled",
            bins=25, alpha=0.8, density=True)


        ax = self.axes
        # fig, ax = plt.subplots()
        plot_beta_hist(ax, 10, 10)
        plot_beta_hist(ax, 4, 12)
        plot_beta_hist(ax, 50, 12)
        plot_beta_hist(ax, 6, 55)
        ax.set_title("'bmh' style sheet")
        # plt.show()

    def update_figure(self, data):
        self.axes.cla()
        # TODO: clean 
        shape_im = np.array([0.2, 0.4, 0.50, 0.55, 0.6, 0.6, 0.55, 0.50, 0.4, 0.2])
        if isinstance(data[0], tuple):
            rx_present = []
            for rx, im_hits in data:
                x = np.arange(im_hits[0], im_hits[1])
                x_cf = im_hits[0] + (im_hits[1] - im_hits[0]) / 2
                # make pseudo PIM shape with edges lower than middle
                y = np.outer(shape_im, np.ones(len(x))).ravel()
                y = y[::len(y)/len(x)]
                # y = 0.6*np.ones(len(x))

                self.axes.bar(x, y,
                              label="IM Cf={0}".format(x_cf), alpha=0.60,
                              lw="3")
                rx_cf = rx[0] + (rx[1] - rx[0]) / 2
                if rx_cf not in rx_present:
                    rx = np.arange(rx[0], rx[1])
                    self.axes.bar(rx, np.ones(len(rx)),
                                  label="RX Cf={0}".format(rx_cf), alpha=0.8,
                                  lw="3")
                    rx_present.append(rx_cf)
                self.axes.legend()
            self.draw()
            return

        data = [np.arange(x[0], x[1], 0.1) for x in data]
        # y = [np.ones(len(x)) for x in data]
        poi = stats.poisson
        lambda_ = [1.5, 4.25]
        colours = ["#348ABD", "#A60628"]
        for x in data:
            # self.axes.bar(x, y.pop(), alpha=0.6, lw="3")
            y = np.ones(len(x))
            self.axes.bar(x, y,
                          label="Cf={0}".format(x[0]+(x[-1]-x[0])/2),
                          # alpha=0.60,
                          lw="3")
        # self.axes.plot(data, y, alpha=0.8)
        # self.axes.hist(data, histtype="stepfilled", bins=100, alpha=0.8, density=True)
        """y_pos = np.ar
        self.axes.barh(np.arange(, data, align='center', alpha=0.8,
                       ecolor='black')
    def newwindow(self):
        self.wid = QtGui.QWidget()
        self.wid.resize(250, 150)
        self.wid.setWindowTitle('NewWindow')
        self.wid.show()
        self.wid = QtGui.QWidget()
        self.wid.resize(250, 150)
        self.wid.setWindowTitle('NewWindow')
        self.wid.show()
        """
        # self.xticks(a + 0.4, a)
        self.axes.legend()
        # self.fig.ylabel("Power")
        # self.axes.xlabel("Frequency [MHz]")
        # self.axes.title("Probability mass function of a Poisson random variable; differing \
        #         $\lambda$ values");
        self.draw()


class PIMPlot(QtWidgets.QWidget):
    def __init__(self, item):
        QtWidgets.QWidget.__init__(self)

    def paintEvent(self, e):
        dc = QtWidgets.QPainter(self)
        dc.drawLine(0, 0, 100, 100)
        dc.drawLine(100, 0, 0, 100)


class ScrollMessageBox(QtWidgets.QMessageBox):

    def __init__(self, widgets, *args, **kwargs):
        QtWidgets.QMessageBox.__init__(self, *args, **kwargs)

        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setGeometry(100,100,100,100)
        self.content = QtWidgets.QWidget()
        scroll.setWidget(self.content)
        lay = QtWidgets.QVBoxLayout(self.content)

        if not isinstance(widgets, list):
            widgets = [widgets]

        for item in widgets:
            lay.addWidget(item)

        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        self.setStyleSheet("QScrollArea{min-width:640 px; min-height: 480px}")


class MainWindow(QtWidgets.QMainWindow):
    # elements
    labels = []
    fields = []
    chk_box = []
    windows = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # super(MainWindow, self).__init__()
        self.initUI()

    def fileQuit(self):
        for wind in self.windows:
            wind.close()
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def initUI(self):
        self.setWindowTitle('-- PIM Calculator --')

        # MENUS
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        # Go! btn
        self.chk_box.append(QtWidgets.QCheckBox("Plot Results"))
        self.chk_box[-1].setChecked(False)
        self.chk_box.append(QtWidgets.QCheckBox("Plot IM Separately"))
        self.chk_box[-1].setChecked(False)
        calculate_btn = QtWidgets.QPushButton('Calculate', self)
        calculate_btn.setToolTip('<b>Click to calculate</b>')
        calculate_btn.resize(calculate_btn.sizeHint())
        calculate_btn.clicked.connect(self.on_calculate_click)

        # validators
        # validator_number = QtGui.QIntValidator(0,1, self)

        # Labels and text forms
        self.labels.append(QtWidgets.QLabel("<b>TX Carriers</b>", self))
        self.labels.append(QtWidgets.QLabel("Frequency [MHz]", self))
        self.labels.append(QtWidgets.QLabel("Bandwidth [MHz]", self))
        self.labels.append(QtWidgets.QLabel("<b>RX Carriers</b>", self))
        self.labels.append(QtWidgets.QLabel("Frequency [MHz]", self))
        self.labels.append(QtWidgets.QLabel("Bandwidth [MHz]", self))

        self.fields.append(QtWidgets.QLineEdit("1980,1940", self))
        self.fields.append(QtWidgets.QLineEdit("5,5", self))
        self.fields.append(QtWidgets.QLineEdit("1900,1880", self))
        self.fields.append(QtWidgets.QLineEdit("5,5", self))

        # set validators later..
        # for field in self.fields:
        #    field.setValidator(validator_number)

        # Grid
        grid_main = QtWidgets.QGridLayout(self.main_widget)
        grid_main.setSpacing(5)
        grid = QtWidgets.QGridLayout()

        grid_main.addLayout(grid, 0, 0, 1, 4)
        grid.setSpacing(5)

        yPos = 0
        xPos = 0
        # Add labels to grid
        for l in range(0, len(self.labels)):
            if (yPos == 0) or (yPos == 3) or (yPos == 6):
                x = 1
            else:
                x = 0
            grid.addWidget(self.labels[l], l, x)
            yPos += 1
        # Add edit fields
        yPos = 1
        for l in self.fields:
            grid.addWidget(l, yPos, 1)
            if yPos == 2 or yPos == 5:
                yPos += 1
            yPos += 1

        grid.addWidget(calculate_btn, 1, 4)
        grid.addWidget(self.chk_box[0], 2, 4)
        grid.addWidget(self.chk_box[1], 3, 4)

        # Set up logging to use your widget as a handler
        # log_handler = QPlainTextEditLogger()
        # logging.getLogger().addHandler(log_handler)

        self.setGeometry(500, 300, 400, 150)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.show()

    @staticmethod
    def _convert_list(items):
        """ Convert string params into lists """

        if not isinstance(items, str):
            items = str(items)

        print items
        if "," in items:
            items = [float(x) for x in items.strip().split(",")]
        else:
            items = [float(items)]

        return items

    def show_results(self, results, plot_results, im_data=None, rx_data=None):
        # box = QtWidgets.QMessageBox()
        items = []
        text_obj = QtWidgets.QTextBrowser(self)
        text_obj.setText(results)
        # items.append(text_obj)
        if plt and plot_results:
            for im, im_full in im_data:
                pim_plots = PIMCanvas()
                pim_plots.update_figure(im_full)
                items.append(pim_plots)

            for im, im_full in rx_data:
                pim_plots = PIMCanvas()
                pim_plots.update_figure(im_full)
                items.append(pim_plots)

            for w in items:
                # wind = PIMPlot(w)
                # wind.show()
                self.result_window(w)

        box = ScrollMessageBox(text_obj)
        box.setWindowTitle('PIM Calculator Results')
        result = box.exec_()

        # self.w.setGeometry(QtGui.QRect(100, 100, 400, 200))
        # self.w.show()

    def result_window(self, item, item_name="Results"):
        # QtGui.QWidget()
        # self.wid.resize(250, 150)
        item.setWindowTitle(item_name)
        item.show()
        self.windows.append(item)

    def on_calculate_click(self):
        """ Method to call on calculate click """

        tx_list = self._convert_list(self.fields[0].text())
        tx_size = self._convert_list(self.fields[1].text())
        rx_list = self._convert_list(self.fields[2].text())
        rx_size = self._convert_list(self.fields[3].text())

        plot_results = self.chk_box[0].isChecked()
        plot_im = self.chk_box[1].isChecked()
        pimc = PIMCalc()

        # get IM results
        im_result = pimc.calculate(tx_list, tx_bandwith=tx_size)
        text_result = []
        im_name = cycle(["IM3", "IM5"]).next
        rx_result = []
        for im, im_full in im_result:
            name = im_name()
            pimc.logger.info(48*"=")
            pimc.logger.info(im)
            pimc.logger.info("==== {0}:fmin, fmax ====".format(name))
            pimc.logger.info(im_full)
            pimc.logger.info(48*"=")
            text_result.append(48*"=")
            text_result.append("==== {0} ====".format(name))
            text_result.append(str(im))
            text_result.append("==== {0}:fmin, fmax ====".format(name))
            text_result.append(str(im_full))
            text_result.append(48*"=")
            if rx_list is not None:
                pimc.logger.info("==== RX check ===")
                im_hits = pimc.check_rx(rx_list, im_full, rx_bandwith=rx_size)
                if len(im_hits) > 0:
                    pimc.logger.warning("yey, we've got some {0} PIM".format(name))
                rx_result.append((name, im_hits))
                text_result.append(48*"=")
                pimc.logger.info(48*"=")

        if rx_list is None:
            sys.exit()

        for rx_res in rx_result:
            im_type = rx_res[0]
            pimc.logger.warning("===== {0} =====".format(im_type))
            text_result.append("===== {0} =====".format(im_type))
            for pim in rx_res[1]:
                pimc.logger.warning("{0} is inside: {1}".format(pim[0], pim[1]))
                text_result.append("{0} is inside: {1}".format(pim[0], pim[1]))
        text_result = "\n".join(text_result)
        self.show_results(text_result, plot_results, im_data=im_result, rx_data=rx_result)

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """PIM Calculator
This program is a simple GUI hello world of a Qt5 application embedding matplotlib canvases.

"""                                )


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()

        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.textCursor().appendPlainText(msg)

    def write(self, m):
        pass


if __name__ == "__main__":
    # setup logger
    console = logging.StreamHandler()
    console.setLevel("DEBUG")
    logger = logging.getLogger("test_executor")
    logger.addHandler(console)
    logger.setLevel("DEBUG")

    # Allow the taking of command line arguements
    app = QtWidgets.QApplication(sys.argv)
    # label = QLabel("<font color=red size=40>Hello World!</font>")
    # label.show()

    main = MainWindow()
    # Ensure the execution stops correctly
    sys.exit(app.exec_())
