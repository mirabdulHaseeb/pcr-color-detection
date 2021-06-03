import cv2
import numpy as np
import webcolors
from scipy.spatial import KDTree

img = cv2.imread('pcr_colored.png', cv2.IMREAD_COLOR)

mapped_cell = {
    "well_name": "",
    "well_coordinates": None,
    "well_color": None
}
mapped_cells_list = []
sorted_outer_list = []
sorted_final_list = []
row_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Get Color names from RGB values
def convert_rgb_to_color_name(rgb_input):
    hexnames = webcolors.css3_hex_to_names
    names = []
    positions = []

    for hex, name in hexnames.items():
        names.append(name)
        positions.append(webcolors.hex_to_rgb(hex))

    spacedb = KDTree(positions)

    querycolor = rgb_input
    dist, index = spacedb.query(querycolor)
    return names[index]

# Convert to gray-scale and reduce noise
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_blur = cv2.medianBlur(gray, 5)

circles = cv2.HoughCircles(img_blur,
                           cv2.HOUGH_GRADIENT,
                           1,
                           img.shape[0]/64,
                           param1=200,
                           param2=10,
                           minRadius=14,
                           maxRadius=15
                          )
# Draw detected circles
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :96]:
        
        # outer circle
        ## cv2.circle(image, center_coordinates, radius, color, thickness)
        cv2.circle(img, (i[0], i[1]), i[2], (0, 0, 0), 2)
        
        # rgb values
        b = img[i[1], i[0], 0]
        g = img[i[1], i[0], 1]
        r = img[i[1], i[0], 2]
        
        color_name = convert_rgb_to_color_name((r, g, b))
        
        mapped_cell = {
            "well_coordinates": (i[0], i[1]),
            "well_color": color_name
        }
        mapped_cells_list.append(mapped_cell)
        
        # inner circle
        cv2.circle(img, (i[0], i[1]), 1, (0, 0, 255), 2)

# Mapping Well names
sorted_outer_list = sorted(mapped_cells_list, key=lambda k: k['well_coordinates'])

for i in range(12):
    sorted_inner_list = sorted(sorted_outer_list[8*i:8*(i+1)], key=lambda k: k['well_coordinates'][1])
    for j in range(len(row_names)):
        sorted_inner_list[j]['well_name'] = row_names[j]+ str(i+1)
        sorted_final_list.append(sorted_inner_list[j])

# print the sorted list
for d in sorted_final_list:
    print(d)

# View image in a window
cv2.imshow('Image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()