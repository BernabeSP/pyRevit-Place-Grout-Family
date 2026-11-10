from Autodesk.Revit.UI.Selection import ISelectionFilter
from Autodesk.Revit.DB import BuiltInCategory


class ViewElementSelectionFilter(ISelectionFilter):

    ALLOWED_CATEGORIES = {

        int(BuiltInCategory.OST_StructuralFraming),
        int(BuiltInCategory.OST_StructuralColumns),
        int(BuiltInCategory.OST_Walls),
        int(BuiltInCategory.OST_Floors),
        int(BuiltInCategory.OST_StructConnections),
        int(BuiltInCategory.OST_StructuralFoundation),

    }

    def AllowElement(self, element):

        category = element.Category

        if category is None:
            return False

        return category.Id.IntegerValue in self.ALLOWED_CATEGORIES


    def AllowReference(self, reference, point):

        return False


# =========================================================
# SELECCIONAR VIGAS
# =========================================================
class BeamSelectionFilter(ISelectionFilter):
    def AllowElement(
            self,
            element):
        try:
            if not element.Category:
                return False

            return (
                element.Category.Id.IntegerValue
                ==
                int(
                    BuiltInCategory.OST_StructuralFraming
                )
            )

        except:
            return False

    def AllowReference(
            self,
            reference,
            point):
        return True

# =========================================================
# SELECCIONAR COLUMNAS
# =========================================================
class ColumnSelectionFilter(ISelectionFilter):
    def AllowElement(
            self,
            element):
        try:
            if not element.Category:
                return False

            return (
                element.Category.Id.IntegerValue
                ==
                int(
                    BuiltInCategory.OST_StructuralColumns
                )
            )

        except:
            return False

    def AllowReference(
            self,
            reference,
            point):
        return True