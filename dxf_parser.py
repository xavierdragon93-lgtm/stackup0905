import ezdxf

def extract_dimensions(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    results = []

    for dim in msp.query("DIMENSION"):
        try:
            measurement = dim.get_measurement()
        except Exception:
            measurement = None

        dimstyle_name = dim.dxf.dimstyle
        dimstyle = doc.dimstyles.get(dimstyle_name)

        tol_upper = None
        tol_lower = None

        if dimstyle and dimstyle.dxf.dimtol:
            tol_upper = dimstyle.dxf.dimtp
            tol_lower = dimstyle.dxf.dimtm

        # Sometimes tolerance is embedded in text
        text = dim.dxf.text

        results.append({
            "measurement": measurement,
            "text": text,
            "tolerance_upper": tol_upper,
            "tolerance_lower": tol_lower
        })

    return results