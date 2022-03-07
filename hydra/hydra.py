from PyQt5 import QtWidgets, uic, QtCore, QtGui
from pyqtgraph import PlotWidget, TextItem
import pyqtgraph as pg
import sys, os
import numpy as np
import errormodel as em
import json
from scipy.interpolate import griddata, interp1d


QtWidgets.QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)  # DPI unaware window
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"     # adapts window to 4k screens

VERSION = '1.2'

KHZ = 2*np.pi*1e3
MHZ = 2*np.pi*1e6

SLDR_ID_NUCOM = 0
SLDR_ID_GRADIENT = 1
SLDR_ID_POWER = 2
SLDR_ID_ENOISE = 3
SLDR_ID_BAMBIENT = 4
SLDR_ID_VNOISE = 5
SLDR_ID_NUXY = 6
SLDR_ID_NBAR = 7
SLDR_ID_PHI = 8
SLDR_ID_CHI = 9
SLDR_ID_SA = 10
SLDR_ID_SYMFLUC = 11

CBOX_ARCH_ID_CHIP = 0
CBOX_ARCH_ID_MACRO = 1

CBOX_VNOISE_ID_CORR = 0
CBOX_VNOISE_ID_UNCORR = 1

C1 = '#00478F'
C2 = '#C34242'
C3 = '#FF9912'
C4 = '#3CAEA3'
COLORS = [C1, C2, C3, C4, 'k']

def resource_path(relative_path):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path_to_dat = os.path.abspath(os.path.join(bundle_dir, relative_path))
    return path_to_dat

#CHIP_PRESET_FILE = resource_path("presets\\chip_preset.json")
CHIP_PRESET_FILE = resource_path("presets\\chip_preset2.json")
MACRO_PRESET_FILE = resource_path("presets\\macro_preset.json")

with open(CHIP_PRESET_FILE) as json_file:
    CHIP_PRESET_DATA = json.load(json_file)
with open(MACRO_PRESET_FILE) as json_file:
    MACRO_PRESET_DATA = json.load(json_file)

WINDOW_UI_FILE = resource_path('window.ui')

class Trace:

    curves = []
    errors = []
    hide = False
    update = False
    active = False
    point = None
    table = {"tgate" : 0, "varmin" : 0, "errmin" : 1, "T2" : 0, "ndot" : 0}

    params = {}

    def __init__(self):
        return None

    def updateErrors(self, errors):
        self.errors = errors

    def updateTable(self, tgate = 0, varmin = 0, errmin = 1, T2 = 0, ndot = 0) :
        if self.update :
            self.table = {"tgate" : tgate, "varmin" : varmin, "errmin" : errmin, "T2" : T2, "ndot" : ndot}

    def plotTrace(self, data_list, units) :
        if self.hide :
            for curve in self.curves :
                curve.setData([300], [1])
            self.point.setData([300], [1])
        elif self.update :
            for curve, err in zip(self.curves, self.errors) :
                #curve.setData(self.NU_C_LIST/KHZ, err)
                curve.setData(data_list/units, err)
            self.point.setData([self.table["varmin"]/units], [self.table["errmin"]])


class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi(WINDOW_UI_FILE, self)
        self.setWindowTitle("Hydra - v1.2")

        # Innitialize Traces
        self.active_trace = 0
        self.traces = [Trace(), Trace(), Trace(), Trace()]
        self.traces[self.active_trace].active = True
        self.traces[self.active_trace].update = True

        self.comboBoxTraceNum.currentIndexChanged.connect(lambda : self.toggle_traces())
        self.radioBtnTraceUpdate.toggled.connect(lambda : self.trace_update())
        self.radioBtnTraceHide.toggled.connect(lambda : self.trace_hide() )

        # Innitialize  Graph
        self.init_param_lists()
        self.init_graph()

        # Innitialize all slider and their labels        
        self.init_sliders()

        # Innitialize Radio buttons
        self.radioBtnShowOffRes.toggled.connect(lambda : self.update_offres_radio())
        self.radioBtnIncludeOffErr.toggled.connect(lambda : self.update_offres_radio())
        self.radioBtnPulseShaping.toggled.connect(lambda : self.update_offres_radio())
        self.radioBtnOptFid.toggled.connect(lambda : self.toggle_optfid_btn())
        self.radioBtnAmpNoise.toggled.connect(lambda : self.toggle_ampnoise_btn())
        self.radioBtnCCWNoise.toggled.connect(lambda : self.toggle_ccwnoise_btn())
        self.radioBtnSymFluc.toggled.connect(lambda : self.toggle_symfluc_btn())
        self.radioBtnMTMS.toggled.connect(lambda : self.toggle_MTMS())

        # Innitialize Table Info
        self.tableInfo.setRowCount(5)
        self.tableInfo.setColumnCount(2)
        self.tableInfo.setItem(0,0, QtWidgets.QTableWidgetItem("Fidelity"))
        self.tableInfo.setItem(1,0, QtWidgets.QTableWidgetItem("Optimal Frequency"))
        self.tableInfo.setItem(2,0, QtWidgets.QTableWidgetItem("Gate Time"))
        self.tableInfo.setItem(3,0, QtWidgets.QTableWidgetItem("Coherence Time"))
        self.tableInfo.setItem(4,0, QtWidgets.QTableWidgetItem("STR Heating Rate"))

        # Innitialize combo boxes
        self.comboBoxArchitecture.currentIndexChanged.connect(lambda : self.update_graph())
        self.comboBoxVNoise.currentIndexChanged.connect(lambda : self.update_graph())
        self.comboBoxVibMode.currentIndexChanged.connect(lambda : self.update_graph())
        self.comboBoxVarParam.currentIndexChanged.connect(lambda : self.update_graph())

        # Innitialize Menubar items
        self.actionLoadChip.triggered.connect(lambda : self.load_presets(CHIP_PRESET_DATA))
        self.actionLoadMacro.triggered.connect(lambda : self.load_presets(MACRO_PRESET_DATA))
        self.actionSavePresetFile.triggered.connect(lambda : self.save_preset_file())
        self.actionLoadPresetFile.triggered.connect(lambda : self.load_preset_file())

        # Initialize legend and update graph
        self.init_legend()
        self.update_graph()

    def get_pens(self, color) :
        return [pg.mkPen(color='r', width = 3, style=QtCore.Qt.CustomDashLine, dash=[1, 2]),
                pg.mkPen(color='k', width = 3, style=QtCore.Qt.CustomDashLine, dash=[3, 12]),
                pg.mkPen(color='m', width = 3, style=QtCore.Qt.CustomDashLine, dash=[6, 6]),
                pg.mkPen(color='c', width = 3, style=QtCore.Qt.CustomDashLine, dash=[25, 4]),
                pg.mkPen(color='g', width = 3, style=QtCore.Qt.DashDotLine),
                pg.mkPen(color='b', width = 3, style=QtCore.Qt.DashDotDotLine),
                pg.mkPen(color='y', width = 3)]

    def trace_hide(self) :
        self.traces[self.active_trace].hide = self.radioBtnTraceHide.isChecked()
        self.traces[self.active_trace].plotTrace(self.var_list, self.units)
        self.update_graph()

    def trace_update(self) :
        self.traces[self.active_trace].update = self.radioBtnTraceUpdate.isChecked()
        self.traces[self.active_trace].plotTrace(self.var_list, self.units)
        self.update_graph()

    def toggle_traces(self) :

        self.traces[self.active_trace].params = self.save_presets()

        self.active_trace = self.comboBoxTraceNum.currentIndex()
        self.radioBtnTraceUpdate.setChecked(self.traces[self.active_trace].update)
        self.radioBtnTraceHide.setChecked(self.traces[self.active_trace].hide)

        if not self.traces[self.active_trace].active :
            self.traces[self.active_trace].active = True
            self.traces[self.active_trace].curves = [self.graphWidget.plot([1], [1], pen=pen) for pen in self.get_pens(COLORS[self.active_trace])]
            self.traces[self.active_trace].point = self.graphWidget.plot([0], [1], pen= pg.mkPen(None), brush = 'k', symbol = 'o')

        else :
            params = self.traces[self.active_trace].params
            self.load_presets(params)


    def toggle_optfid_btn(self) :
        self.sliderFixNu.setEnabled(not self.radioBtnOptFid.isChecked())
        self.update_graph()

    def toggle_ampnoise_btn(self) :
        self.sliderChi.setEnabled(self.radioBtnAmpNoise.isChecked())
        self.update_graph()

    def toggle_ccwnoise_btn(self) :
        self.sliderSA.setEnabled(self.radioBtnCCWNoise.isChecked())
        self.update_graph()

    def toggle_symfluc_btn(self) :
        self.sliderSymFluc.setEnabled(self.radioBtnSymFluc.isChecked())
        self.update_graph()
        
    def toggle_MTMS(self) :
    
        if(self.radioBtnMTMS.isChecked()):
            self.label_17.setText('Tones :')
            self.var_name_list[8] = r'Tones'

        else:
            self.label_17.setText('Loops :')
            self.var_name_list[8] = r"Loops in phase space"
        
        if(self.graphXaxis == 8):
            self.change_var_param(8)
            
        self.update_graph()

    def save_preset_file(self) :

        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', '*.json')[0]

        try :
            preset_data = self.save_presets()

            with open(filename, 'w') as f:
                json.dump(preset_data, f)

        except :
            print('Error : Save presets to file failed')


    def load_preset_file(self) :
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Load File', '', '*.json')[0]

        try :
            with open(filename) as f:
                preset_data = json.load(f)

            self.load_presets(preset_data)

        except :
            print('Error : Load presets from file failed')


    def save_presets(self) :

        dzB = self.sliderGradient.value()
        Om = self.sliderPower.value()
        nuSE = (self.sliderENoise.value()/10)
        SBa = (self.sliderBAmbient.value()/10)
        SV = (self.sliderVNoise.value()/10)
        nuXY = self.sliderNuXY.value()/10
        chi = self.sliderChi.value()/10
        SA = self.sliderSA.value()/10
        nbar = self.sliderNbar.value()/10
        sym_fluc = self.sliderSymFluc.value()
        loops = self.sliderPhi.value()
        nu_c = self.sliderNuCOM.value()

        arch = self.comboBoxArchitecture.currentIndex()
        vnoise = self.comboBoxVNoise.currentIndex()
        vmode = self.comboBoxVibMode.currentIndex()

        toggle_amp_noise = self.radioBtnAmpNoise.isChecked()
        toggle_ccw_noise = self.radioBtnCCWNoise.isChecked()
        toggle_sym_fluc = self.radioBtnSymFluc.isChecked()
        toggle_MTMS = self.radioBtnMTMS.isChecked()

        return {"version" : VERSION,
                "slider" : { "dzB" : dzB, "Om" : Om, "nuSE" : nuSE, "SBa" : SBa,
                             "SV" : SV, "nuXY" : nuXY, 'chi' : chi, 'SA' : SA,
                             'nbar' : nbar, 'symfluc' : sym_fluc, 'phi' : loops, 'nuCOM' : nu_c},
                "toggles" : {'amp_noise' : toggle_amp_noise, 'ccw_noise' : toggle_ccw_noise, 
                             'sym_fluc' : toggle_sym_fluc, 'MTMS' : toggle_MTMS},
                "architecture" : arch,"vnoise" : vnoise,"vib_mode" : vmode}

    def load_presets(self, data) :

        self.sliderGradient.setValue(data['slider']['dzB'])
        self.labelGradient.setText(str(data['slider']['dzB']) + ' T/m')

        self.sliderPower.setValue(data['slider']['Om'])
        self.labelPower.setText(str(data['slider']['Om']) + ' kHz')

        self.sliderENoise.setValue(int(data['slider']['nuSE']*10))
        self.labelENoise.setText(str('%.2E'%(10**(data['slider']['nuSE']))))

        self.sliderBAmbient.setValue(int(data['slider']['SBa']*10))
        self.labelBAmbient.setText(str('%.2E'%(10**(data['slider']['SBa']))))

        self.sliderVNoise.setValue(int(data['slider']['SV']*10))
        self.labelVNoise.setText(str('%.2E'%(10**(data['slider']['SV']))))

        self.sliderNuXY.setValue(int(data['slider']['nuXY']*10))
        self.labelNuXY.setText(str(data['slider']['nuXY']) + ' MHz')

        self.sliderChi.setValue(int(data['slider']['chi']*10))
        self.labelChi.setText(str('%.2E'%(10**(data['slider']['chi']))))

        self.sliderSA.setValue(int(data['slider']['SA']*10))
        self.labelSA.setText(str('%.2E'%(10**(data['slider']['SA']))))

        self.sliderNbar.setValue(int(data['slider']['nbar']*10))
        self.labelNbar.setText(str('%.2f'%(10**(data['slider']['nbar']))))

        self.sliderPhi.setValue(data['slider']['phi'])
        self.labelPhi.setText(str(data['slider']['phi']))

        self.sliderNuCOM.setValue(data['slider']['nuCOM'])
        self.labelNuCOM.setText(str(data['slider']['nuCOM'])+ ' kHz')

        self.sliderSymFluc.setValue(int(data['slider']['symfluc']))
        self.labelSymFluc.setText(str(data['slider']['symfluc']))

        self.comboBoxArchitecture.setCurrentIndex(data['architecture'])
        self.comboBoxVNoise.setCurrentIndex(data['vnoise'])
        self.comboBoxVibMode.setCurrentIndex(data['vib_mode'])

        self.radioBtnAmpNoise.setChecked(data['toggles']['amp_noise'])
        self.radioBtnCCWNoise.setChecked(data['toggles']['ccw_noise'])
        self.radioBtnSymFluc.setChecked(data['toggles']['sym_fluc'])
        self.radioBtnMTMS.setChecked(data['toggles']['MTMS'])

        return 0

    def update_table(self, err_min, var_min, tgate, T2, ndot) :

        self.tableInfo.setItem(0,1, QtWidgets.QTableWidgetItem('%.3f'%((1 - err_min)*100) + ' %'))
        if(self.units==KHZ):
            self.tableInfo.setItem(1,1, QtWidgets.QTableWidgetItem('%.1f'%(var_min/KHZ) + ' kHz'))
        elif(self.units==MHZ):
            self.tableInfo.setItem(1,1, QtWidgets.QTableWidgetItem('%.1f'%(var_min/MHZ) + ' MHz'))
        else:
            self.tableInfo.setItem(1,1, QtWidgets.QTableWidgetItem('%.1f'%var_min))

        self.tableInfo.setItem(2,1, QtWidgets.QTableWidgetItem('%.3f'%(tgate*1e3) + ' ms'))
        self.tableInfo.setItem(3,1, QtWidgets.QTableWidgetItem('%.3f'%(T2)+ ' s'))
        self.tableInfo.setItem(4,1, QtWidgets.QTableWidgetItem('%.3f'%ndot + ' quanta/s'))

    def update_offres_radio(self) :

        show_offres = self.radioBtnShowOffRes.isChecked()
        inc_offres_err = self.radioBtnIncludeOffErr.isChecked()
        pulse_shaping = self.radioBtnPulseShaping.isChecked()

        if not show_offres :
            self.radioBtnIncludeOffErr.setChecked(False)

        self.update_graph()

    def init_legend(self) :

        self.legendWidget.setBackground(None)

        pos_list  = [[[0.5, 2], [8, 8]],
                     [[0.5, 2], [2, 2]],
                     [[4.5, 6], [8, 8]],
                     [[4.5, 6], [2, 2]],
                     [[8.8, 10.3], [2, 2]]]

        for pos, pen in zip(pos_list, self.get_pens(COLORS[0])) :
            self.legendWidget.plot(pos[0], pos[1], pen = pen)

        label_names = ['Heating', 'Decoherence', 'Trap frequency fluctuations', 'Off-res coupling', 'Amp noise']
        text_items = [pg.TextItem(name, (0, 0, 0), anchor = (0, 0.5)) for name in label_names]

        pos_list = [(2.3, 8), (2.3, 2),
                    (6.3, 8), (6.3, 2),
                    (10.5, 2), (10.3, 2)]

        for ti, pos in zip(text_items, pos_list) :
            ti.setPos(pos[0], pos[1])
            self.legendWidget.addItem(ti)

        self.legendWidget.setXRange(0, 12, padding = 0)
        self.legendWidget.setYRange(0, 10, padding = 0)

        self.legendWidget.getPlotItem().hideAxis('bottom')
        self.legendWidget.getPlotItem().hideAxis('left')

    def init_param_lists(self):

        nuCOM_list = np.linspace(100, 800, 101)*KHZ
        dzB_list = np.linspace(1, 150, 150)
        Om_list = np.linspace(1, 150, 151)*KHZ
        nuSE_list = np.logspace(-8, -3, 101)
        SBa_list = np.logspace(-25, -19, 101)
        SV_list = np.logspace(-19, -12, 101)
        nuXY_list = np.linspace(1, 5, 101)*MHZ
        nbar_list = np.linspace(0, 10, 101)
        phi_list = np.linspace(1, 10, 10)  # depends if MTMS or Multi-Loop
        chi_list = np.linspace(0, 1, 101)

        self.var_lists = [nuCOM_list, dzB_list, Om_list, nuSE_list, SBa_list, SV_list, nuXY_list,
             nbar_list, phi_list, chi_list]

        self.var_name_list = ["COM frequency (kHz)", "Magnetic field gradient (T/m)", "Gate Rabi frequency (kHz)",
                 r'Scaled Electric field noise (V/m)^2', "Ambient Magnetic field noise (T^2/ Hz)",
                 "Voltage noise (V^2/ Hz)", "Radial mode frequency (MHz)", r"Initial temperature nbar",
                 r"Loops in phase space", r"Amplitude Signal-to-Noise Ratio",
                 "CCW current noise (A^2/ Hz)", r"Variance from voltage noise ΔSV",
                 r"Geometric factor (m^-1)", "Pulse shaping",  "Vibrational mode (0 => Stretch, 1 => COM)"]


    def init_graph(self):

        self.graphWidget.setBackground(None)
        self.graphXaxis = self.comboBoxVarParam.currentIndex()

        self.var_list = self.var_lists[self.graphXaxis]

        if(self.graphXaxis==0 or self.graphXaxis==2):
            self.units = KHZ
        elif(self.graphXaxis==6):
            self.units = MHZ
        else:
            self.units = 1

#         self.graphWidget.plot([self.NU_C_LIST[0]/KHZ, self.NU_C_LIST[-1]/KHZ], [1e-2, 1e-2], pen=pg.mkPen('#666666', width=1, style=QtCore.Qt.DashLine))
#         self.graphWidget.plot([self.NU_C_LIST[0]/KHZ, self.NU_C_LIST[-1]/KHZ], [1e-4, 1e-4], pen=pg.mkPen('#666666', width=1, style=QtCore.Qt.DashLine))

        self.graphWidget.plot([self.var_list[0]/self.units, self.var_list[-1]/self.units], [1e-2, 1e-2], pen=pg.mkPen('#666666', width=1, style=QtCore.Qt.DashLine))
        self.graphWidget.plot([self.var_list[0]/self.units, self.var_list[-1]/self.units], [1e-3, 1e-3], pen=pg.mkPen('#666666', width=1, style=QtCore.Qt.DashLine))


        self.traces[0].curves = [self.graphWidget.plot([0], [0], pen=pen) for pen in self.get_pens(COLORS[0])]
        self.traces[0].errors = [[0], [0], [0], [0], [0], [0], [0]]
        self.traces[0].point = self.graphWidget.plot([0], [1], pen= pg.mkPen(None), brush = 'k', symbol = 'o')

        self.graphWidget.plot([300], [2e-1])    # Purpose?
        self.graphWidget.plot([300], [1e-5])    # Purpose?

        if(self.graphXaxis>=3 and self.graphXaxis<=5 or self.graphXaxis==10):
            self.graphWidget.setLogMode(True, True)
            exponents = np.log10(self.var_list)
            self.graphWidget.setXRange(min(exponents), max(exponents), padding=0)
        else:
            self.graphWidget.setLogMode(False, True)
            self.graphWidget.setXRange(min(self.var_list/self.units), max(self.var_list/self.units)*1.03, padding=0)

        self.graphWidget.setLabel('left', 'Infidelity')
        #self.graphWidget.setLabel('bottom', 'COM Secular Frequency', 'kHz')
        self.graphWidget.setLabel('bottom', self.var_name_list[self.graphXaxis])
        #self.graphWidget.setXRange(100, 820, padding=0)
        self.graphWidget.setYRange(-4, 0, padding=0.02)
    
    def change_var_param(self, varParam):
        
        self.graphXaxis = varParam
        #print("VarParam changed to " + str(varParam))
        print("Variable Parameter changed to " + str(self.var_name_list[self.graphXaxis]))
        self.tableInfo.setItem(1,0, QtWidgets.QTableWidgetItem("Optimal " +
            str(self.var_name_list[self.graphXaxis])))
        self.graphWidget.clear()
        self.init_graph()
        

    def update_graph(self) :
        
        varParam = self.comboBoxVarParam.currentIndex()
        if(varParam!=self.graphXaxis):
            self.change_var_param(varParam)

        architecture = self.comboBoxArchitecture.currentIndex()

        if architecture is CBOX_ARCH_ID_CHIP :
            g_factor = em.G_FACTOR_CHIP
        elif architecture is CBOX_ARCH_ID_MACRO :
            g_factor = em.G_FACTOR_MACRO

        if self.comboBoxVNoise.currentIndex() == CBOX_VNOISE_ID_CORR :
            # g_factor *= np.sqrt(12)  # eqn 4.22 Christophe's thesis (this is WITHOUT electrode pairing)
            '''
            The effect of electrode pairing (numerically simulated by Alex to reduce g by ~20)
            '''
            g_factor *= 1/20

        elif self.comboBoxVNoise.currentIndex() == CBOX_VNOISE_ID_UNCORR:
            # if electrode noise is uncorrelated, pairing has no effect
            pass

        vib_mode = self.comboBoxVibMode.currentIndex()
        include_amp_noise = self.radioBtnAmpNoise.isChecked()
        include_ccw_noise = self.radioBtnCCWNoise.isChecked()
        include_symfluc_noise = self.radioBtnSymFluc.isChecked()
        
        show_offres = self.radioBtnShowOffRes.isChecked()
        inc_offres_err = self.radioBtnIncludeOffErr.isChecked()
        pulse_shaping = self.radioBtnPulseShaping.isChecked() and show_offres
        MTMS = self.radioBtnMTMS.isChecked()

        dzB = self.sliderGradient.value()
        Om = self.sliderPower.value() * KHZ
        nuSE = 10**(self.sliderENoise.value()/10)
        SBa = 10**(self.sliderBAmbient.value()/10)
        SV = 10**(self.sliderVNoise.value()/10)
        NuXY = self.sliderNuXY.value()/10*MHZ
        nbar = 10**(self.sliderNbar.value()/10)
        loops = self.sliderPhi.value()
        nu_c = self.sliderNuCOM.value() * KHZ

        if include_amp_noise :
            chi = 10**(self.sliderChi.value()/10)
        else : chi = 0

        if include_ccw_noise :
            SA = 10**(self.sliderSA.value()/10)
        else : SA = 0

        if include_symfluc_noise :
            sym_fluc = 2*np.pi* self.sliderSymFluc.value()
        else : sym_fluc = 0
                
        params = [nu_c, dzB, Om, nuSE, SBa, SV, NuXY, nbar, loops, chi, SA, sym_fluc,
             g_factor, pulse_shaping, vib_mode, MTMS]

        params[varParam] = self.var_lists[varParam]

        err_h, err_d, err_t, err_o, err_a = em.compute_total_errors(*params)
        err_tot = err_h + err_d + err_t + err_a

        if inc_offres_err and show_offres: err_tot += err_o
        elif not show_offres : err_o = [0]*len(err_o)

        '''
        Optimise the variable parameter for maximum fidelity (minimum error)
        and calculate the new optimised heating rate, gate time and coherence time
        '''

        if self.radioBtnOptFid.isChecked() :
            err_min, var_min = em.optimizeFidelity(self.var_list, err_tot)
        else :
            interp_func = interp1d(self.var_list, err_tot, kind='linear')
            var_min = self.get_slider_value(self.graphXaxis)
            #print("VarMin = " + str(var_min))
            err_min = interp_func(var_min)

        ''' confirm that these work?'''
        if varParam==0:
            nu_c = var_min
        elif varParam==1:
            dzB = var_min
        elif varParam==2:
            Om = var_min
        elif varParam==3:
            nuSE = var_min
        elif varParam==4:
            SBa = var_min
        elif varParam==5:
            SV = var_min
        elif varParam==6:
            NuXY = var_min
        elif varParam==7:
            nbar = var_min
        elif varParam==8:
            loops = var_min

        gate_cost = np.sqrt(loops)

        if vib_mode is em.VIB_MODE_AXIAL_STR :
            ndot = em.ndot_STR(nu_c, nu_c*np.sqrt(3), em.DIST_ELECTRODE, nuSE)
            tgate = em.compute_tgate(nu_c*np.sqrt(3), dzB, Om, gate_cost)

        elif vib_mode is em.VIB_MODE_AXIAL_COM :
            ndot = em.ndot_COM(nu_c, nuSE)
            tgate = em.compute_tgate(nu_c, dzB, Om, gate_cost)

        SBtot = em.SB(nu_c, dzB, g_factor, nuSE, SBa, SV, SA)

        T2 = em.compute_T2(SBtot)

        self.update_table(err_min, var_min, tgate, T2, ndot)

        self.traces[self.active_trace].updateTable(tgate = tgate, varmin = var_min, errmin = err_min, T2 = T2, ndot = ndot)
        self.traces[self.active_trace].updateErrors([err_h, err_d, err_t, err_o, err_a, err_tot])
        self.traces[self.active_trace].plotTrace(self.var_list, self.units)
        
        #print("At this optimum, Lamb-Dicke ^2 = " + str(em.compute_eta(nu_c, dzB)**2) )


    def init_sliders(self) :


        self.sliderGradient.setMinimum(25)
        self.sliderGradient.setMaximum(200)

        self.sliderPower.setMinimum(25)
        self.sliderPower.setMaximum(150)

        self.sliderENoise.setMinimum(-80)
        self.sliderENoise.setMaximum(-30)

        self.sliderBAmbient.setMinimum(-260)
        self.sliderBAmbient.setMaximum(-200)

        self.sliderVNoise.setMinimum(-200)
        self.sliderVNoise.setMaximum(-120)

        self.sliderNuXY.setMinimum(10)
        self.sliderNuXY.setMaximum(50)

        self.sliderFixNu.setMinimum(100)
        self.sliderFixNu.setMaximum(500)
        self.sliderFixNu.setValue(300)

        self.sliderChi.setMinimum(-40)
        self.sliderChi.setMaximum(-10)
        self.sliderChi.setValue(-20)

        self.sliderSA.setMinimum(-180)
        self.sliderSA.setMaximum(-60)

        self.sliderNbar.setMinimum(-10)
        self.sliderNbar.setMaximum(10)

        self.sliderSymFluc.setMinimum(0)
        self.sliderSymFluc.setMaximum(100)

        self.sliderPhi.setMinimum(1)
        self.sliderPhi.setMaximum(10)

        self.sliderNuCOM.setMinimum(100)
        self.sliderNuCOM.setMaximum(800)

        self.sliderGradient.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_GRADIENT))
        self.sliderPower.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_POWER))
        self.sliderENoise.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_ENOISE))
        self.sliderBAmbient.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_BAMBIENT))
        self.sliderVNoise.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_VNOISE))
        self.sliderNuXY.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_NUXY))
        self.sliderChi.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_CHI))
        self.sliderSA.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_SA))
        self.sliderNbar.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_NBAR))
        self.sliderSymFluc.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_SYMFLUC))
        self.sliderPhi.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_PHI))
        self.sliderNuCOM.valueChanged.connect(lambda : self.update_sldr_label(SLDR_ID_NUCOM))

        self.sliderFixNu.valueChanged.connect(lambda : self.update_graph())

        with open(CHIP_PRESET_FILE) as json_file:
            data = json.load(json_file)

        self.load_presets(data)

    def update_sldr_label(self, sldr_id = 0) :

        if sldr_id is SLDR_ID_GRADIENT :
            dzB = self.sliderGradient.value()
            self.labelGradient.setText(str(dzB) + ' T/m')

        elif sldr_id is SLDR_ID_POWER :
            Om = self.sliderPower.value()
            self.labelPower.setText(str(Om) + ' kHz')

        elif sldr_id is SLDR_ID_ENOISE :
            nuSE = self.sliderENoise.value()
            self.labelENoise.setText(str('%.2E'%(10**(nuSE/10))))

        elif sldr_id is SLDR_ID_BAMBIENT :
            SBa = self.sliderBAmbient.value()
            self.labelBAmbient.setText(str('%.2E'%(10**(SBa/10))))

        elif sldr_id is SLDR_ID_VNOISE :
            SV = self.sliderVNoise.value()
            self.labelVNoise.setText(str('%.2E'%(10**(SV/10))))

        elif sldr_id is SLDR_ID_NUXY :
            NuXY = self.sliderNuXY.value()
            self.labelNuXY.setText(str(NuXY/10) + ' MHz')

        elif sldr_id is SLDR_ID_CHI :
            chi = self.sliderChi.value()
            self.labelChi.setText(str('%.2E'%(10**(chi/10))))

        elif sldr_id is SLDR_ID_SA :
            SA = self.sliderSA.value()
            self.labelSA.setText(str('%.2E'%(10**(SA/10))))

        elif sldr_id is SLDR_ID_NBAR :
            nbar = self.sliderNbar.value()
            self.labelNbar.setText(str('%.2f'%(10**(nbar/10))))

        elif sldr_id is SLDR_ID_SYMFLUC :
            symfluc = self.sliderSymFluc.value()
            self.labelSymFluc.setText(str(symfluc))

        elif sldr_id is SLDR_ID_PHI :
            phi = self.sliderPhi.value()
            self.labelPhi.setText(str(phi))

        elif sldr_id is SLDR_ID_NUCOM :
            nuCOM = self.sliderNuCOM.value()
            self.labelNuCOM.setText(str(nuCOM) + ' kHz')

        self.update_graph()

    def get_slider_value(self, sldr_id = 0) :

        if sldr_id is SLDR_ID_GRADIENT :
            value = self.sliderGradient.value()

        elif sldr_id is SLDR_ID_POWER :
            value = self.sliderPower.value() *KHZ

        elif sldr_id is SLDR_ID_ENOISE :
            value = 10**(self.sliderENoise.value()/10)

        elif sldr_id is SLDR_ID_BAMBIENT :
            value = 10**(self.sliderBAmbient.value()/10)

        elif sldr_id is SLDR_ID_VNOISE :
            value = 10**(self.sliderVNoise.value()/10)

        elif sldr_id is SLDR_ID_NUXY :
            value = self.sliderNuXY.value()/10 *MHZ

        elif sldr_id is SLDR_ID_CHI :
            value = 10**(self.sliderChi.value()/10)

        elif sldr_id is SLDR_ID_SA :
            value = 10**(self.sliderSA.value()/10)

        elif sldr_id is SLDR_ID_NBAR :
            value = 10**(self.sliderNbar.value()/10)

        elif sldr_id is SLDR_ID_SYMFLUC :
            value = self.sliderSymFluc.value()

        elif sldr_id is SLDR_ID_PHI :
            value = self.sliderPhi.value()

        elif sldr_id is SLDR_ID_NUCOM :
            value = self.sliderNuCOM.value() *KHZ

        return value

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
