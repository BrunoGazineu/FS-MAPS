import ast
from shapely.geometry import Polygon

# Selecionar estilos de mapa aqui:
#https://developers.arcgis.com/rest/basemap-styles/
#teste

def string_to_coords(lot__string_coords):
  try:
        # Safely evaluate the string input as a Python literal
        polygon_coords = ast.literal_eval(lot__string_coords)

        # Ensure the input evaluates to a nested list structure
        if (
            not isinstance(polygon_coords, list)
            or len(polygon_coords) != 1
            or not all(isinstance(coord, (list, tuple)) and len(coord) == 2 for coord in polygon_coords[0])
        ):
            raise ValueError("Input must be a string representation of a nested list with [x, y] coordinate pairs.")

        # Extract the inner list of coordinates
        polygon_coords = polygon_coords[0]

        # Create a Shapely polygon from the coordinates
        polygon = Polygon(polygon_coords)
        return polygon
  except (ValueError, SyntaxError) as e:
        print(f"Error parsing lot coordinates: {e}")

