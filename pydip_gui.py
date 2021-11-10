'''


Pydip's primary aim is to have an easy way to generate random geological data to practice the interpretation of stereoplots.

As a secondary objective I want to create a similar software as "Stereonet" with additional functions such as simple 3d rendering of structures. 


todos:

[]: Faults
[]: Better selection options
[]: Better import functions
[]: Statistics module
[]: 3D viewer
  
'''

# ============= IMPORTS ===================


import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import mplstereonet


import utils as ut

matplotlib.use('Qt5Agg')

# ============= FUNCTIONS ===================


# Function used to quickly construct a multipart widget (e.g button+label)

def widget_constructor(orientation,widget_list):

	if orientation == 'vertical':
		layout = QVBoxLayout()
	elif orientation == 'horizontal':
		layout = QHBoxLayout()
	
	main_widget = QWidget()
	main_widget.setLayout(layout)
	
	for widget in widget_list:
		layout.addWidget(widget)
		layout.setSpacing(0)
		layout.addStretch(1)
		
	return main_widget



# Function used to update the data table

def update_table(self,plane_data):
	
	self.table.setColumnCount(3)
	self.table.setHorizontalHeaderLabels(["Dip direction","Dip","Set"])
	c = 0
	for sets in plane_data:
		s_data = plane_data[sets]['s'].flatten()
		d_data = plane_data[sets]['d'].flatten()
		self.table.setRowCount(len(s_data))
		for i,s in enumerate(s_data):
			#print(i,s)
			self.table.setItem(i,0,QTableWidgetItem(str(s)))
			self.table.setItem(i,1,QTableWidgetItem(str(d_data[i])))
			self.table.setItem(i,2,QTableWidgetItem(str(sets)))	
				

# ============= CLASSES ===================

# Main canvas plot class
class pltCanvas(FigureCanvasQTAgg):

	def __init__(self,parent=None):
	
		self.fig,self.ax = mplstereonet.subplots(projection="equal_area_stereonet")
		self.ax.grid()

		
		super(pltCanvas,self).__init__(self.fig)

# Main widget class
class MWidget(QMainWindow):

	def __init__(self):
		super().__init__()
		
		self.main_layout = QGridLayout()
		plt_layout = QVBoxLayout()
		self.main_widget = QWidget()
		plt_widget = QWidget()
		
# ============= Main plot ===================

		self.plot = pltCanvas(self)
		toolbar = NavigationToolbar(self.plot,self)
		
		self.plt_widget = widget_constructor('vertical',[toolbar,self.plot])
		
		self.main_layout.addWidget(self.plt_widget,0,1)
		self.main_widget.setLayout(self.main_layout)
		
		self.setCentralWidget(self.main_widget)
		
# ============= Setup data table widget ===================

		self.table = QTableWidget()
		self.table.itemSelectionChanged.connect(self.on_click)
		self.opt_widget = QWidget()
		self.init_UI()


# Init function
	def init_UI(self):

		self.setGeometry(2100,550,950,500) #x,y,l,h
		self.setWindowTitle('pydip')
		self.setWindowIcon(QIcon('icon/pydip.png'))


# ============== Menubar ================
		
		menubar = self.menuBar()
		
		#Actions (plane gen, clear etcetc)
		
		actions = menubar.addMenu('Actions') #create action button in menu
		gen = QMenu('Generate',self) #create a Generate submenu
		actions.addMenu(gen)
		
		#create Generate submenus
		
		planePlot = QAction('Plot data',self)
		gen.addAction(planePlot)
		
		randomPlanes = QAction('Random planes', self)
		gen.addAction(randomPlanes)
		randomPlanes.triggered.connect(self.rand_plane_options)
		
		randomFolds = QAction('Random folds', self)
		gen.addAction(randomFolds)
		randomFolds.triggered.connect(self.rand_folds_options)
		
		randomFocal = QAction('Random focal mechanism', self)
		gen.addAction(randomFocal)
		randomFocal.triggered.connect(self.rand_focal_options)
		
		#Clear action
		cl = QAction('Clear', self)
		actions.addAction(cl)
		cl.triggered.connect(self.clear_data)

		
		
		# Import data
		imp = menubar.addMenu('Import')
		imp_csv = QAction('Import CSV',self)
		imp.addAction(imp_csv)
		imp_csv.triggered.connect(self.import_options)
		
		# View options
		view = menubar.addMenu('View')
		dataT = QAction('Data table',self)
		view.addAction(dataT)
		dataT.triggered.connect(self.view_data_table)
		
		self.show()




#================== Table selector ==================


	def on_click(self):
	
		sel_data = self.table.selectedItems()
		dd = [float(item.text()) for item in sel_data if item.column() == 0]
		d = [float(item.text()) for item in sel_data if item.column() == 1]
		if dd and d:
			if self.planesCheck.isChecked():
				self.plot.ax.plane(dd,d,'y-')
			if self.polesCheck.isChecked():
				self.plot.ax.pole(dd,d,'yo')
			self.plot.draw()
		elif self.gen_mode == 'planes':
			ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked()) #plot data with options to plot pole and/or planes
		elif self.gen_mode == 'folds':
			ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked(),
			              self.axialCheck.isChecked(),self.hingeCheck.isChecked()) #plot fold data with options to plot pole and/or planes and hinge/axial surface



#================== RANDOM GENERATORS OPTIONS ==================

#------------------ Planes options ------------------

	def rand_plane_options(self):

		self.nset=1
		self.nplane=1
		
		self.opt_widget.setParent(None) #remove existing widgets
		#Title
		
		title = QLabel()
		title.setText("Random planes generator options")
		title.setAlignment(Qt.AlignCenter)
		
		#set number Spinbox

		nset_spb_label = QLabel()
		nset_spb_label.setText("Number of sets")
		
		
		self.nset_spb = QSpinBox()
		self.nset_spb.setMinimum(1)
		self.nset_spb.valueChanged.connect(self.value_change_set)
		
		nset_spinbox = widget_constructor('vertical',[nset_spb_label,self.nset_spb])
		
		#Plane number Spinbox
		
		nplane_spb_label = QLabel()
		nplane_spb_label.setText("Number of planes")
		
		
		self.nplane_spb = QSpinBox()
		self.nplane_spb.setMinimum(1)
		self.nplane_spb.valueChanged.connect(self.value_change_planes)
		
		nplane_spinbox = widget_constructor('vertical',[nplane_spb_label,self.nplane_spb])
		
		# Check boxes
		
		self.planesCheck = QCheckBox("View planes")
		self.planesCheck.setChecked(True)
		self.planesCheck.clicked.connect(self.show_poles_planes) #function used to update plot based on the choice made
		self.polesCheck = QCheckBox("View poles")
		self.polesCheck.setChecked(True)
		self.polesCheck.clicked.connect(self.show_poles_planes) #function used to update plot based on the choice made (it's the same)
		
		
		
		
		checkBoxes = widget_constructor('horizontal',[self.planesCheck,self.polesCheck]) #put checkboxes in one widget
		
		
		genButton = QPushButton('Generate planes')
		self.gen_mode = 'planes'
		genButton.clicked.connect(self.rand_planes)
		
		self.opt_widget = widget_constructor('vertical',[title, nset_spinbox,nplane_spinbox,checkBoxes,genButton]) #put every option widget in one big widget
		self.main_layout.addWidget(self.opt_widget,0,0)
		
	
	#Show poles and/or planes in plot
	def show_poles_planes(self):
	
		try:
			ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked())
			self.on_click()
		except AttributeError:
			print('No data')
			
	#Show axial plane and/or hinge in folds plot		
	def show_axial_hinge(self):
	
		try:
			ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked(),
			              self.axialCheck.isChecked(),self.hingeCheck.isChecked()) #plot fold data with options to plot pole and/or planes and hinge/axial surface
			self.on_click()
		except AttributeError:
			print('No data')
			
	#Change value of set and plane numbers based on the spinbox
	def value_change_set(self):
	
		self.nset = self.nset_spb.value()
		
	def value_change_planes(self):
	
		self.nplane = self.nplane_spb.value()
	
	#View data table
	def view_data_table(self):
	
		self.main_layout.addWidget(self.table,0,2)

#------------------ Folds options ------------------

	def rand_folds_options(self):

		self.nset=1
		self.nplane=1
		
		self.opt_widget.setParent(None) #remove existing widgets
		#Title
		
		title = QLabel()
		title.setText("Random folds generator options")
		title.setAlignment(Qt.AlignCenter)
		
		#set number Spinbox

		nset_spb_label = QLabel()
		nset_spb_label.setText("Number of sets")
		
		
		self.nset_spb = QSpinBox()
		self.nset_spb.setMinimum(1)
		self.nset_spb.valueChanged.connect(self.value_change_set)
		
		nset_spinbox = widget_constructor('vertical',[nset_spb_label,self.nset_spb])
		
		#Plane number Spinbox
		
		nplane_spb_label = QLabel()
		nplane_spb_label.setText("Number of planes")
		
		
		self.nplane_spb = QSpinBox()
		self.nplane_spb.setMinimum(1)
		self.nplane_spb.valueChanged.connect(self.value_change_planes)
		
		nplane_spinbox = widget_constructor('vertical',[nplane_spb_label,self.nplane_spb])
		
		# Check boxes
		
		self.planesCheck = QCheckBox("View planes")
		self.planesCheck.setChecked(True)
		self.planesCheck.clicked.connect(self.show_poles_planes) #function used to update plot based on the choice made
		self.polesCheck = QCheckBox("View poles")
		self.polesCheck.setChecked(True)
		self.polesCheck.clicked.connect(self.show_poles_planes) #function used to update plot based on the choice made (it's the same)
		self.axialCheck = QCheckBox("View axial plane")
		self.axialCheck.setChecked(False)
		self.axialCheck.clicked.connect(self.show_axial_hinge)
		self.hingeCheck = QCheckBox("View hinge line")
		self.hingeCheck.setChecked(False)
		#self.axialCheck.clicked.connect(self.show_poles_planes)
		
		
		checkBoxes = widget_constructor('horizontal',[self.planesCheck,self.polesCheck,self.axialCheck,self.hingeCheck]) #put checkboxes in one widget
		
		
		genButton = QPushButton('Generate fold')
		self.gen_mode = 'folds'
		genButton.clicked.connect(self.rand_planes)
		
		self.opt_widget = widget_constructor('vertical',[title, nset_spinbox,nplane_spinbox,checkBoxes,genButton]) #put every option widget in one big widget
		self.main_layout.addWidget(self.opt_widget,0,0)
		

#------------------ Focal mechanisms options------------------

	def rand_focal_options(self):
	
		self.opt_widget.setParent(None) #remove existing option widgets
		
		#Title
		
		title = QLabel()
		title.setText("Random focal mechanisms generator")
		title.setAlignment(Qt.AlignCenter)
		
		'''
		#Grid dimension input
		
		focal_rows = QSpinBox()
		focal_rows.setMinimum(1)
		#self.nset_spb.valueChanged.connect(self.value_change_set)
		focal_cols = QSpinBox()
		focal_cols.setMinimum(1)
		times = QLabel()
		times.setText("x")
		'''
		#grid_dim = widget_constructor('horizontal',[focal_rows,times,focal_cols])
		
		
		genButton = QPushButton(f'Generate focal\nmechansims')
		genButton.clicked.connect(self.rand_focal)
		#self.opt_widget = widget_constructor('vertical',[title,grid_dim,genButton]) #put every option widget in one big widget
		self.opt_widget = widget_constructor('vertical',[title,genButton]) #put every option widget in one big widget
		self.main_layout.addWidget(self.opt_widget,0,0)
		


#================== GENERATORS ==================




#------------------ Random planes generator (planes, folds, faults)----------------



	def rand_planes(self):
	
		if self.gen_mode == 'planes':
			self.planes_dict = ut.random_plane_gen(self.nset,self.nplane) #generate planes with input variables (set and plane numbers)
			ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked()) #plot data with
		elif self.gen_mode == 'folds':
			self.planes_dict = ut.random_folds_gen(self.nset,self.nplane)
			ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked(),
			              self.axialCheck.isChecked(),self.hingeCheck.isChecked()) #plot fold data with options to plot pole and/or planes and hinge/axial surface
		update_table(self, self.planes_dict) #update data table
		
# Used to clear plot and table
	def clear_data(self):
	
		self.plot.ax.cla()
		self.plot.ax.grid()
		self.plot.draw()
		self.table.clearContents()



#------------------ Random focal mechansims generator ----------------
	def focal_grid_constr(text):
		print(text)

	def rand_focal(self):
		
		ut.random_focal_plot(self)
		
#================== Input and import options ==================

	
	# Function used to update planes dict form csv file
	def import_csv(self):
		
		self.file_path = self.path.text()
		self.planes_dict,nrows = ut.csv_convert(self.file_path)
		
		ut.plane_plot(self,self.planes_dict,self.planesCheck.isChecked(),self.polesCheck.isChecked())
		update_table(self, self.planes_dict, nrows) #update data table
		
	
	# Secondary function used when the user chooses to navigate with the file explorer
	
	def import_csv_nav(self):
	
		self.file_path_nav,_ = QFileDialog.getOpenFileName(self)
		self.path.setText(self.file_path_nav)
		self.path.setFocus()
	
	
	def import_options(self):
	
		self.opt_widget.setParent(None) #remove existing widgets
		
		#Title
		
		title = QLabel()
		title.setText("Plot options")
		title.setAlignment(Qt.AlignCenter)
		
		
		# Path input 
		
		path_title= QLabel()
		path_title.setText('Choose path: ')
		
		self.path = QLineEdit()
		self.path.setFixedWidth(230)
		
		nav_button = QPushButton('...')
		nav_button.setFixedWidth(25)
		nav_button.setFixedHeight(25)
		nav_button.clicked.connect(self.import_csv_nav)
		
		path_bar = widget_constructor('horizontal', [self.path, nav_button])
		
		path_widget = widget_constructor('vertical', [path_title, path_bar])
				
		# Check boxes
		
		self.planesCheck = QCheckBox("View planes")
		self.planesCheck.setChecked(True)
		self.planesCheck.clicked.connect(self.show_poles_planes) #function used to update plot based on the choice made
		self.polesCheck = QCheckBox("View poles")
		self.polesCheck.setChecked(True)
		self.polesCheck.clicked.connect(self.show_poles_planes) #function used to update plot based on the choice made (it's the same)
		
		checkBoxes = widget_constructor('horizontal',[self.planesCheck,self.polesCheck]) #put checkboxes in one widget
		

		
		# Show data button
		
		show_data = QPushButton('Plot data')
		
		show_data.clicked.connect(self.import_csv)
		
		
		self.opt_widget = widget_constructor('vertical',[title, path_widget, checkBoxes, show_data]) #put every option widget in one big widget
		self.main_layout.addWidget(self.opt_widget,0,0)
		


if __name__ == '__main__':
	app = QApplication(sys.argv)
	test = MWidget()
	app.exec_()
