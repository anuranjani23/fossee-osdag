from design_type.connection.shear_connection import ShearConnection
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from utils.common.component import Bolt, Plate, Weld
# from gui.ui_summary_popup import Ui_Dialog
from utils.common.component import *
from utils.common.material import *
from Common import *
from utils.common.load import Load
import yaml
from design_report.reportGenerator import save_html
import os
import shutil
import logging
from PyQt5.QtCore import QFile, pyqtSignal, QTextStream, Qt, QIODevice
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPixmap, QPalette
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow, QDialog, QFontDialog, QApplication, QFileDialog, QColorDialog,QMessageBox
import pickle
import pdfkit
import configparser
import cairosvg
from io import StringIO
import logging




#from ...gui.newnew import Ui_Form
#newnew_object = Ui_Form()

connectivity = "column_flange_beam_web"
supporting_member_section = "HB 400"
supported_member_section = "MB 300"
fy = 250.0
fu = 410.0
shear_force = 100.0
axial_force=100.0
bolt_diameter = 24.0
bolt_type = "friction_grip"
bolt_grade = 8.8
plate_thickness = 10.0
weld_size = 6
material_grade = "E 250 (Fe 410 W)B"
material = Material(material_grade)


def desired_location(self, filename, base_type):
    if base_type == ".svg":
        cairosvg.svg2png(file_obj=filename, write_to=os.path.join(str(self.maincontroller.folder), "images_html",
                                                                  "cmpylogoExtendEndplate.svg"))
    else:
        shutil.copyfile(filename,
                        os.path.join(str(self.maincontroller.folder), "images_html", "cmpylogoExtendEndplate.png"))

def saveUserProfile(self):
    inputData = self.get_report_summary()
    filename, _ = QFileDialog.getSaveFileName(self, 'Save Files',
                                              os.path.join(str(self.maincontroller.folder), "Profile"), '*.txt')
    if filename == '':
        flag = False
        return flag
    else:
        infile = open(filename, 'w')
        pickle.dump(inputData, infile)
        infile.close()


def getPopUpInputs(self):
    input_summary = {}
    input_summary["ProfileSummary"] = {}
    input_summary["ProfileSummary"]["CompanyName"] = str(self.ui.lineEdit_companyName.text())
    input_summary["ProfileSummary"]["CompanyLogo"] = str(self.ui.lbl_browse.text())
    input_summary["ProfileSummary"]["Group/TeamName"] = str(self.ui.lineEdit_groupName.text())
    input_summary["ProfileSummary"]["Designer"] = str(self.ui.lineEdit_designer.text())

    input_summary["ProjectTitle"] = str(self.ui.lineEdit_projectTitle.text())
    input_summary["Subtitle"] = str(self.ui.lineEdit_subtitle.text())
    input_summary["JobNumber"] = str(self.ui.lineEdit_jobNumber.text())
    input_summary["AdditionalComments"] = str(self.ui.txt_additionalComments.toPlainText())
    input_summary["Client"] = str(self.ui.lineEdit_client.text())


def useUserProfile(self):
    filename, _ = QFileDialog.getOpenFileName(self, 'Open Files',
                                              os.path.join(str(self.maincontroller.folder), "Profile"),
                                              "All Files (*)")
    if os.path.isfile(filename):
        outfile = open(filename, 'r')
        reportsummary = pickle.load(outfile)
        self.ui.lineEdit_companyName.setText(reportsummary["ProfileSummary"]['CompanyName'])
        self.ui.lbl_browse.setText(reportsummary["ProfileSummary"]['CompanyLogo'])
        self.ui.lineEdit_groupName.setText(reportsummary["ProfileSummary"]['Group/TeamName'])
        self.ui.lineEdit_designer.setText(reportsummary["ProfileSummary"]['Designer'])
    else:
        pass


class FinPlateConnection(ShearConnection):


    def __init__(self):
        super(FinPlateConnection, self).__init__()

    def set_osdaglogger(key):
        global logger
        logger = logging.getLogger('osdag')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = OurLog(key)
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def input_values(self, existingvalues={}):

        options_list = []

        if KEY_CONN in existingvalues:
            existingvalue_key_conn = existingvalues[KEY_CONN]
        else:
            existingvalue_key_conn = ''

        if KEY_SUPTNGSEC in existingvalues:
           existingvalue_key_suptngsec = existingvalues[KEY_SUPTNGSEC]
        else:
            existingvalue_key_suptngsec = ''

        if KEY_SUPTDSEC in existingvalues:
            existingvalue_key_suptdsec = existingvalues[KEY_SUPTDSEC]
        else:
            existingvalue_key_suptdsec = ''

        if KEY_MATERIAL in existingvalues:
            existingvalue_key_mtrl = existingvalues[KEY_MATERIAL]
        else:
            existingvalue_key_mtrl = ''

        if KEY_SHEAR in existingvalues:
            existingvalue_key_versh = existingvalues[KEY_SHEAR]
        else:
            existingvalue_key_versh = ''

        if KEY_AXIAL in existingvalues:
            existingvalue_key_axial = existingvalues[KEY_AXIAL]
        else:
            existingvalue_key_axial = ''

        if KEY_D in existingvalues:
            existingvalue_key_d = existingvalues[KEY_D]
        else:
            existingvalue_key_d = ''

        if KEY_TYP in existingvalues:
            existingvalue_key_typ = existingvalues[KEY_TYP]
        else:
            existingvalue_key_typ = ''

        if KEY_GRD in existingvalues:
            existingvalue_key_grd = existingvalues[KEY_GRD]
        else:
            existingvalue_key_grd = ''

        if KEY_PLATETHK in existingvalues:
            existingvalue_key_platethk = existingvalues[KEY_PLATETHK]
        else:
            existingvalue_key_platethk = ''

        t16 = (KEY_MODULE, KEY_DISP_FINPLATE, TYPE_MODULE, None, None)
        options_list.append(t16)

        t1 = (None, DISP_TITLE_CM, TYPE_TITLE, None, None)
        options_list.append(t1)

        t2 = (KEY_CONN, KEY_DISP_CONN, TYPE_COMBOBOX, existingvalue_key_conn, VALUES_CONN)
        options_list.append(t2)

        t15 = (KEY_IMAGE, None, TYPE_IMAGE, None, None)
        options_list.append(t15)

        t3 = (KEY_SUPTNGSEC, KEY_DISP_COLSEC, TYPE_COMBOBOX, existingvalue_key_suptngsec, connectdb("Columns"))
        options_list.append(t3)

        t4 = (KEY_SUPTDSEC, KEY_DISP_BEAMSEC, TYPE_COMBOBOX, existingvalue_key_suptdsec, connectdb("Beams"))
        options_list.append(t4)

        t5 = (KEY_MATERIAL, KEY_DISP_MATERIAL, TYPE_COMBOBOX, existingvalue_key_mtrl, VALUES_MATERIAL)
        options_list.append(t5)

        t6 = (None, DISP_TITLE_FSL, TYPE_TITLE, None, None)
        options_list.append(t6)

        t7 = (KEY_SHEAR, KEY_DISP_SHEAR, TYPE_TEXTBOX, existingvalue_key_versh, None)
        options_list.append(t7)

        t8 = (KEY_AXIAL, KEY_DISP_AXIAL, TYPE_TEXTBOX, existingvalue_key_axial, None)
        options_list.append(t8)

        t9 = (None, DISP_TITLE_BOLT, TYPE_TITLE, None, None)
        options_list.append(t9)

        t10 = (KEY_D, KEY_DISP_D, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_d, VALUES_D)
        options_list.append(t10)

        t11 = (KEY_TYP, KEY_DISP_TYP, TYPE_COMBOBOX, existingvalue_key_typ, VALUES_TYP)
        options_list.append(t11)

        t12 = (KEY_GRD, KEY_DISP_GRD, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_grd, VALUES_GRD)
        options_list.append(t12)

        t13 = (None, DISP_TITLE_PLATE, TYPE_TITLE, None, None)
        options_list.append(t13)

        t14 = (KEY_PLATETHK, KEY_DISP_PLATETHK, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_platethk, VALUES_PLATETHK)
        options_list.append(t14)

        return options_list

    def output_values(self, flag):

        out_list = []

        t1 = (None, DISP_TITLE_BOLT, TYPE_TITLE, None)
        out_list.append(t1)

        t2 = (KEY_OUT_D_PROVIDED, KEY_DISP_OUT_D_PROVIDED, TYPE_TEXTBOX,  self.bolt.bolt_diameter_provided if flag == 'True' and self.design_flag else '')
        out_list.append(t2)

        t3 = (KEY_OUT_GRD_PROVIDED, KEY_DISP_OUT_GRD_PROVIDED, TYPE_TEXTBOX, self.bolt.bolt_grade_provided if flag == 'True' and self.design_flag else '')
        out_list.append(t3)

        t4 = (None, DISP_TITLE_PLATE, TYPE_TITLE, None)
        out_list.append(t4)

        t5 = (KEY_OUT_PLATETHK, KEY_DISP_OUT_PLATETHK, TYPE_TEXTBOX, self.plate.thickness if flag == 'True' and self.design_flag else '')
        out_list.append(t5)

        t6 = (KEY_OUT_PLATE_HEIGHT, KEY_DISP_OUT_PLATE_HEIGHT, TYPE_TEXTBOX, self.plate.height if flag == 'True' and self.design_flag else '')
        out_list.append(t6)

        t7 = (KEY_OUT_PLATE_LENGTH, KEY_DISP_OUT_PLATE_LENGTH, TYPE_TEXTBOX, self.plate.length if flag == 'True' and self.design_flag else '')
        out_list.append(t7)

        return out_list

    def set_input_values(self, design_dictionary, window):

        self.design_flag = self.func_for_validation(self, window, design_dictionary)
        if self.design_flag:
            super(FinPlateConnection, self).set_input_values(self, design_dictionary)
            self.plate = Plate(thickness=design_dictionary.get(KEY_PLATETHK, None),
                               material_grade=design_dictionary[KEY_MATERIAL],
                               gap=design_dictionary[KEY_DP_DETAILING_GAP])

            self.warn_text(self)
            self.get_bolt_details(self)

    def func_for_validation(self, window, design_dictionary):
        flag = False
        flag1 = True
        option_list = self.input_values(self)
        missing_fields_list = []
        for option in option_list:
            if option[2] == TYPE_TEXTBOX:
                if design_dictionary[option[0]] == '':
                    missing_fields_list.append(option[1])
            elif option[2] == TYPE_COMBOBOX and option[0] != KEY_CONN:
                val = option[4]
                if design_dictionary[option[0]] == val[0]:
                    missing_fields_list.append(option[1])

        if design_dictionary[KEY_CONN] == 'Beam-Beam':
            primary = design_dictionary[KEY_SUPTNGSEC]
            secondary = design_dictionary[KEY_SUPTDSEC]
            conn = sqlite3.connect(PATH_TO_DATABASE)
            cursor = conn.execute("SELECT D FROM BEAMS WHERE Designation = ( ? ) ", (primary,))
            lst = []
            rows = cursor.fetchall()
            for row in rows:
                lst.append(row)
            p_val = lst[0][0]
            cursor2 = conn.execute("SELECT D FROM BEAMS WHERE Designation = ( ? )", (secondary,))
            lst1 = []
            rows1 = cursor2.fetchall()
            for row1 in rows1:
                lst1.append(row1)
            s_val = lst1[0][0]
            if p_val <= s_val:
                QMessageBox.about(window, 'Information',
                                  "Secondary beam depth is higher than clear depth of primary beam web "
                                  "(No provision in Osdag till now)")
                flag1 = False

        if len(missing_fields_list) > 0:
            QMessageBox.information(window, "Information",
                                    self.generate_missing_fields_error_string(self, missing_fields_list))
            flag = False
        else:
            flag = True
        if flag and flag1:
            return True
        else:
            return False

        # for option in option_list:
        #     if option[0] == KEY_CONN:
        #         continue
        #     s = p.findChild(QtWidgets.QWidget, option[0])
        #
        #     if option[2] == TYPE_COMBOBOX:
        #         if option[0] in [KEY_D, KEY_GRD, KEY_PLATETHK]:
        #             continue
        #         if s.currentIndex() == 0:
        #             missing_fields_list.append(option[1])
        #
        #
        #     elif option[2] == TYPE_TEXTBOX:
        #         if s.text() == '':
        #             missing_fields_list.append(option[1])
        #     else:
        #         pass



    def generate_missing_fields_error_string(self, missing_fields_list):
        """
        Args:
            missing_fields_list: list of fields that are not selected or entered
        Returns:
            error string that has to be displayed
        """
        # The base string which should be displayed
        information = "Please input the following required field"
        if len(missing_fields_list) > 1:
            # Adds 's' to the above sentence if there are multiple missing input fields
            information += "s"
        information += ": "
        # Loops through the list of the missing fields and adds each field to the above sentence with a comma

        for item in missing_fields_list:
            information = information + item + ", "

        # Removes the last comma
        information = information[:-2]
        information += "."

        return information

    def warn_text(self):
        # old_col_section = get_oldcolumncombolist()
        # old_beam_section = get_oldbeamcombolist()
        red_list = red_list_function()

        if self.supported_section.designation in red_list or self.supporting_section.designation in red_list:
            logger.warning(
                " : You are using a section (in red color) that is not available in latest version of IS 808")
            logger.debug(
                " : You are using a section (in red color) that is not available in latest version of IS 808")


    def get_bolt_details(self):
        print(self)
        self.bolt.calculate_bolt_spacing_limits(bolt_diameter_provided=self.bolt.bolt_diameter[0],
                                                connecting_plates_tk=[self.plate.thickness[0],
                                                                      self.supported_section.web_thickness],bolt_hole_type=self.bolt.bolt_hole_type)
        self.bolt.calculate_bolt_capacity(bolt_diameter_provided=self.bolt.bolt_diameter[0],
                                          bolt_grade_provided=self.bolt.bolt_grade[0],
                                          connecting_plates_tk=[self.plate.thickness[0],
                                                                self.supported_section.web_thickness],
                                          n_planes=1)

        min_plate_height = self.supported_section.min_plate_height()
        max_plate_height = self.supported_section.max_plate_height()

        self.plate.get_web_plate_details(bolt_dia=self.bolt.bolt_diameter[0], web_plate_h_min=min_plate_height,
                                         web_plate_h_max=max_plate_height, bolt_capacity=self.bolt.bolt_capacity,
                                         connecting_plates_tk=[self.plate.thickness[0],
                                                               self.supported_section.web_thickness],
                                         bolt_hole_type=self.bolt.bolt_hole_type,
                                         bolt_line_limit=2, shear_load=self.load.shear_force*1000, gap=self.plate.gap,
                                         shear_ecc=True)

        block_shear_capacity = 0
        moment_capacity = 0
        edge_dist_rem = self.plate.edge_dist_provided+self.plate.gap

        self.plate.blockshear(numrow=self.plate.bolts_one_line, numcol=self.plate.bolt_line, pitch=self.plate.pitch_provided,
                              gauge=self.plate.gauge_provided, thk=self.plate.thickness[0], end_dist=self.plate.end_dist_provided,
                              edge_dist=edge_dist_rem, dia_hole=self.bolt.dia_hole,
                              fy=self.supported_section.fy, fu=self.supported_section.fu)

        self.plate.shear_yielding_b(self.plate.height, self.plate.thickness[0], self.plate.fy)

        self.plate.shear_rupture_b(self.plate.height, self.plate.thickness[0], self.plate.bolts_one_line,
                                       self.bolt.dia_hole, self.plate.fu)

        plate_shear_capacity = min(self.plate.block_shear_capacity, self.plate.shear_rupture_capacity,
                                   self.plate.shear_yielding_capacity)

        # if self.load.shear_force > plate_shear_capacity:
        #     design_status = False
        #     logger.error(":shear capacity of the plate is less than the applied shear force, %2.2f kN [cl. 6.4.1]"
        #                  % self.load.shear_force)
        #     logger.warning(":Shear capacity of plate is %2.2f kN" % plate_shear_capacity)
        #     logger.info(": Increase the plate thickness")

        self.plate.get_moment_cacacity(self.plate.fy, self.plate.thickness[0], self.plate.height)

        # if self.plate.moment_capacity < self.plate.moment_demand:
        #     design_status = False
        #     logger.error(": Plate moment capacity is less than the moment demand [cl. 8.2.1.2]")
        #     logger.warning(": Re-design with increased plate dimensions")

        print(self.connectivity)
        print(self.supporting_section)
        print(self.supported_section)
        print(self.load)

#        print(Plate.design_status)
        if self.plate.design_status == False:
            # del_data = open('logging_text.log', 'w')
            # del_data.truncate()
            # del_data.close()
            # logging.basicConfig(format='%(asctime)s %(message)s', filename='logging_text.log',level=logging.DEBUG)
            logger.warning(" : The connection cannot be designed with given loads")
            # with open('logging_text.log') as file:
            #     data = file.read()
            #     print(data)
            #     file.close()
            # file = open('logging_text.log', 'r')
            # # This will print every line one by one in the file
            # for each in file:
            #     print(each)
            #key.setText(data)
        else:        
            print(self.bolt)
            print(self.plate)



#
# with open("filename", 'w') as out_file:
#     yaml.dump(fin_plate_input, out_file)

