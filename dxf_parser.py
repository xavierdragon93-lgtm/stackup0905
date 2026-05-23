import ezdxf
import re

# DXF unit conversion table to millimeters
UNIT_TO_MM = {
    0: 1.0,
    1: 25.4,      # Inches -> mm
    2: 304.8,
    4: 1.0,       # Millimeters
    5: 10.0,
    6: 1000.0,
}

def extract_number(text):
    """
    Extract numeric value from text.
    Example:
        '80±2' -> 80
        '100 ±3' -> 100
    """
    match = re.search(r"[-+]?\d*\.?\d+", text)
    
    if match:
        return float(match.group())
    
    return None


def get_dimension_text_from_block(doc, dim):
    """
    Extract visible dimension text from DXF dimension block.
    """

    try:
        block_name = dim.dxf.geometry

        if not block_name:
            return ""

        block = doc.blocks.get(block_name)

        for entity in block:

            if entity.dxftype() == "MTEXT":
                return entity.text

            if entity.dxftype() == "TEXT":
                return entity.dxf.text

    except Exception:
        pass

    return ""


def extract_dimensions(file_path):

    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    results = []

    # Detect drawing units
    units = doc.header.get("$INSUNITS", 0)
    conversion_factor = UNIT_TO_MM.get(units, 1.0)

    print("INSUNITS =", units)
    print("Conversion Factor =", conversion_factor)

    for dim in msp.query("DIMENSION"):

        measurement = None

        # -----------------------------------
        # Try geometric measurement
        # -----------------------------------
        try:
            raw_measurement = dim.get_measurement()

            if raw_measurement is not None:
                measurement = round(
                    raw_measurement * conversion_factor,
                    3
                )

        except Exception:
            pass

        # -----------------------------------
        # Get visible dimension text
        # -----------------------------------
        text = dim.dxf.text

        if text == "<>" or not text:
            text = get_dimension_text_from_block(doc, dim)

        # Clean formatting
        if text:
            text = text.replace("\\A1;", "")
            text = text.strip()

        # -----------------------------------
        # Fallback measurement from text
        # -----------------------------------
        if measurement is None and text:
            measurement = extract_number(text)

        # -----------------------------------
        # Set units label
        # -----------------------------------
        text = "mm"

        # -----------------------------------
        # Tolerances
        # -----------------------------------
        tol_upper = None
        tol_lower = None

        try:
            dimstyle = doc.dimstyles.get(dim.dxf.dimstyle)

            if dimstyle and dimstyle.dxf.dimtol:
                tol_upper = dimstyle.dxf.dimtp
                tol_lower = dimstyle.dxf.dimtm

        except Exception:
            pass

        results.append({
            "measurement_mm": measurement,
            "text": text,
            "tolerance_upper": tol_upper,
            "tolerance_lower": tol_lower
        })

    return results