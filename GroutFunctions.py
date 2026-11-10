# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    FamilySymbol,
    Material,
    BuiltInParameter,
    BuiltInCategory,
    Transaction,
    UnitUtils,
    UnitTypeId,
    ElementTransformUtils,
    Line,
    XYZ,
)

from Autodesk.Revit.DB.Structure import (
    StructuralType
)

from Autodesk.Revit.UI.Selection import (
    ObjectType
)

from Autodesk.Revit.DB import LocationPoint

from SelectionFilters import (
    ColumnSelectionFilter
)


# =========================================================
# PARAMETROS
# =========================================================

PARAMS = {

    # Parametros seccion columna
    "column_width": "b",
    "column_height": "h",

    # Parametros grout
    "grout_width": "G_Width",
    "grout_height": "G_Height",
    "grout_thickness": "G_Thickness",

}

# =========================================================
# CONVERSION MM
# =========================================================
def mm_to_internal(value):
    return UnitUtils.ConvertToInternalUnits(
        value,
        UnitTypeId.Millimeters
    )

# =========================================================
# SET PARAMETER
# =========================================================
def set_parameter_if_exists(element, name, value):

    param = element.LookupParameter(name)

    if param and not param.IsReadOnly:
        param.Set(value)
        return True

    return False


class FamilyItem(object):

    def __init__(
            self,
            name,
            symbol):

        self.name = name
        self.symbol = symbol

    def __str__(self):

        return self.name

class MaterialItem(object):

    def __init__(
            self,
            name,
            material):

        self.name = name
        self.material = material

    def __str__(self):

        return self.name

def get_grout_families(doc):

    items = []
    symbols = (
        FilteredElementCollector(doc)
        .OfClass(FamilySymbol)
        .ToElements()
    )

    for symbol in symbols:

        try:

            if (
                symbol.Category
                and
                symbol.Category.Id.IntegerValue
                ==
                int(
                    BuiltInCategory.OST_StructuralColumns
                )
            ):

                items.append(
                    FamilyItem(
                        symbol.Family.Name,
                        symbol
                    )
                )

        except:
            pass

    items.sort(
        key=lambda x:x.name
    )

    return items

def get_materials(doc):
    materials = []
    for mat in (
        FilteredElementCollector(doc)
        .OfClass(Material)
    ):
        materials.append(

            MaterialItem(
                mat.Name,
                mat
            )

        )

    materials.sort(
        key=lambda x:x.name
    )

    return materials

# =========================================================
# CREAR GROUT
# =========================================================
def create_grout(
        doc,
        uidoc,
        data):

    # -----------------------------------------------------
    # SELECCIONAR COLUMNAS
    # -----------------------------------------------------

    refs = uidoc.Selection.PickObjects(
        ObjectType.Element,
        ColumnSelectionFilter(),
        "Seleccione columnas estructurales"
    )

    if not refs:
        return (
            "No se seleccionaron columnas."
        )

    # -----------------------------------------------------
    # OBTENER FAMILIA
    # -----------------------------------------------------
    symbol = doc.GetElement(
        data["family_id"]
    )

    if not symbol:

        return (
            "No se encontro la familia."
        )

    if not symbol.IsActive:
        symbol.Activate()
        doc.Regenerate()

    # -----------------------------------------------------
    # MATERIAL
    # -----------------------------------------------------
    material = doc.GetElement(
        data["material_id"]
    )

    # -----------------------------------------------------
    # ESPESOR
    # -----------------------------------------------------
    thickness = mm_to_internal(
        data["thickness_mm"]
    )
    created = 0

    # -----------------------------------------------------
    # TRANSACTION
    # -----------------------------------------------------
    t = Transaction(
        doc,
        "Crear grout"
    )
    t.Start()

    try:
        for ref in refs:
            column = doc.GetElement(ref)
            if column is None:
                continue
            location = column.Location
            if not isinstance(location, LocationPoint):
                continue
            point = location.Point

            # -----------------------------------------
            # OBTENER TIPO
            # -----------------------------------------
            column_symbol = doc.GetElement(
                column.GetTypeId()
            )

            # -----------------------------------------
            # ANCHO
            # -----------------------------------------
            width = 0
            param = column_symbol.LookupParameter(
                PARAMS["column_width"]
            )
            if param:
                width = param.AsDouble()

            # -----------------------------------------
            # ALTO
            # -----------------------------------------
            height = 0
            param = column_symbol.LookupParameter(
                PARAMS["column_height"]
            )

            if param:
                height = param.AsDouble()

            # -----------------------------------------
            # NIVEL SUPERIOR
            # -----------------------------------------
            top_level = doc.GetElement(
                column.get_Parameter(
                    BuiltInParameter.FAMILY_TOP_LEVEL_PARAM
                ).AsElementId()
            )

            offset = column.get_Parameter(
                BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM
            ).AsDouble()

            top_point = XYZ(
                point.X,
                point.Y,
                top_level.Elevation + offset
            )

            # -----------------------------------------
            # CREAR FAMILIA
            # -----------------------------------------
            grout = doc.Create.NewFamilyInstance(
                top_point,
                symbol,
                top_level,
                StructuralType.Column
            )

            
            # -----------------------------------------
            # PARAMETROS
            # -----------------------------------------
            if data["assign_parameters"]:

                set_parameter_if_exists(
                    grout,
                    PARAMS["grout_width"],
                    width
                )

                set_parameter_if_exists(
                    grout,
                    PARAMS["grout_height"],
                    height
                )

                set_parameter_if_exists(
                    grout,
                    PARAMS["grout_thickness"],
                    thickness
                )

                # -------------------------------------
                # COMENTARIO DE INSTANCIA
                # -------------------------------------

                comment_param = grout.get_Parameter(
                    BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS
                )

                if comment_param and not comment_param.IsReadOnly:
                    comment_param.Set(
                        str(data["comment"] or "")
                    )

                
            # -----------------------------------------
            # ROTACION
            # -----------------------------------------
            axis = Line.CreateBound(
                top_point,
                top_point + XYZ.BasisZ
            )

            ElementTransformUtils.RotateElement(
                doc,
                grout.Id,
                axis,
                location.Rotation
            )
            # -----------------------------------------
            # MATERIAL
            # -----------------------------------------
            if material:
                mat_param = grout.get_Parameter(
                    BuiltInParameter.STRUCTURAL_MATERIAL_PARAM
                )

                if mat_param:
                    mat_param.Set(
                        material.Id
                    )
            created += 1
        t.Commit()

    except Exception as ex:

        t.RollBack()

        return (
            "Error creando grout:\n{}".format(ex)
        )

    return (
        "{} familias insertadas correctamente."
        .format(created)
    )