# -*- coding: utf-8 -*-

__title__ = "Grout"
__persistentengine__ = True

# =========================================================
# IMPORTS
# =========================================================

import os
import sys

from pyrevit import revit
from pyrevit import forms
from pyrevit.forms import WPFWindow

from Autodesk.Revit.UI import (
    IExternalEventHandler,
    ExternalEvent
)

# =========================================================
# DOCUMENT
# =========================================================
doc = revit.doc
uidoc = revit.uidoc

# ---------------------------------------------------
# PATH
# ---------------------------------------------------
xamlfile = xamlfile = os.path.join(os.path.dirname(__file__), "GroutView.xaml")

# =========================================================
# IMPORT FUNCTIONS
# =========================================================
from GroutFunctions import (
    create_grout,
    get_grout_families,
    get_materials
)

# =========================================================
# EVENT HANDLER
# =========================================================
class GroutEventHandler(
        IExternalEventHandler):

    def __init__(self):

        self.data = None

    def Execute(
            self,
            app):

        try:

            uidoc = app.ActiveUIDocument
            doc = uidoc.Document

            result = create_grout(

                doc,
                uidoc,
                self.data

            )

            forms.alert(
                result,
                title="Grout"
            )

        except Exception as ex:

            import traceback

            traceback.print_exc()

            forms.alert(
                str(ex),
                title="Error"
            )

    def GetName(self):

        return "Grout External Event"


# =========================================================
# WINDOW
# =========================================================
class GroutWindow(
        WPFWindow):

    def __init__(
            self,
            handler,
            external_event):

        WPFWindow.__init__(
            self,
            xamlfile
        )

        self.handler = handler
        self.external_event = external_event

        self.load_families()
        self.load_materials()

        self.btn_accept.Click += self.accept_click
        self.btn_cancel.Click += self.cancel_click

        self.Show()

    # =====================================================
    # FAMILIAS
    # =====================================================
    def load_families(self):
        self.family_items = get_grout_families(doc)
        self.cmb_family.ItemsSource = (
            self.family_items
        )
        if self.family_items:
            self.cmb_family.SelectedIndex = 0

    # =====================================================
    # MATERIALES
    # =====================================================
    def load_materials(self):
        self.material_items = get_materials(doc)
        self.cmb_material.ItemsSource = (
            self.material_items
        )
        if self.material_items:
            self.cmb_material.SelectedIndex = 0

    # =====================================================
    # OBTENER FAMILIA
    # =====================================================
    def get_selected_family(self):
        return self.cmb_family.SelectedItem

    # =====================================================
    # OBTENER MATERIAL
    # =====================================================
    def get_selected_material(self):
        return self.cmb_material.SelectedItem


    # =====================================================
    # ACEPTAR
    # =====================================================
    def accept_click(
            self,
            sender,
            args):

        family = self.get_selected_family()
        material = self.get_selected_material()

        if family is None:

            forms.alert(
                "Seleccione una familia."
            )

            return

        if material is None:

            forms.alert(
                "Seleccione un material."
            )

            return

        try:
            data = {
                # -----------------------------------
                # FAMILIA
                # -----------------------------------
                "family_name":
                    family.name,

                "family_id":
                    family.symbol.Id,
                # -----------------------------------
                # MATERIAL
                # -----------------------------------
                "material_name":
                    material.name,

                "material_id":
                    material.material.Id,
                # -----------------------------------
                # ESPESOR (mm)
                # -----------------------------------
                "thickness_mm":
                    float(
                        self.txt_thickness.Text
                    ),
                # -----------------------------------
                # OPCIONES
                # -----------------------------------
                "assign_parameters":
                    self.chk_parameters.IsChecked
                    == True,

                "comment":
                    self.txt_comment.Text
            }

        except Exception:
            forms.alert(
                "Revise los valores ingresados."
            )
            return

        # ==========================================
        # ENVIAR AL EXTERNAL EVENT
        # ==========================================
        self.handler.data = data
        self.external_event.Raise()
        self.Close()

    # =====================================================
    # CANCELAR
    # =====================================================
    def cancel_click(
            self,
            sender,
            args):

        self.Close()


# =========================================================
# CREAR EXTERNAL EVENT
# =========================================================
handler = GroutEventHandler()
external_event = ExternalEvent.Create(
    handler
)

# =========================================================
# MOSTRAR VENTANA
# =========================================================
GroutWindow(
    handler,
    external_event
)