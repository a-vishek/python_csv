def csv_dict(file_name, delimiter=','):
    """
    Import data from csv file and created a dict in the format of 
    {subjid: {landmark:[ox,oy,oz,mx,my,mz], landmark2:[ox,oy,oz,mx,my,m]},
    subjid2....}
    """
    with open(file_name, 'r') as file:
        data_frame = {}
        headers = file.readline().upper().strip('\n').split(delimiter)

        # geting index of the header
        (SUBJID, LANDMARK, OX, OY, OZ, MX, MY, MZ) = (
            headers.index('SUBJID'), headers.index('LANDMARK'),
            headers.index('OX'), headers.index('OY'),
            headers.index('OZ'), headers.index('MX'),
            headers.index('MY'), headers.index('MZ'))

        # storing the index of the header in the required format
        csv_header_order = (SUBJID, LANDMARK, OX, OY, OZ, MX, MY, MZ)
        for line in file:
            line_data = line.upper().strip('\n').split(delimiter)
            # cheking if subj has mising values. If missing other function will return None for this subj_id
            if "" in line_data:
                continue
            row = []
            for col in csv_header_order:
                if col < len(line_data):
                    row.append(line_data[col])
                else:
                    row.append(None)
            subj_id = row[0]
            landmark = row[1]
            # taking the coordinates and converting them to float
            coordinates = list(map(float, row[2:]))
            # not taking rows having coordinates value out of the range (-200, 200)
            if min(coordinates) > -200 and max(coordinates) < 200:
                if subj_id in data_frame:
                    data_frame[subj_id].update(
                        {landmark: coordinates})
                else:
                    data_frame[subj_id] = {landmark: coordinates}
        return data_frame


def main(file_name, subj_ids):
    """Returns 3d asymetry, euclidean distance,
       subj_id list of 5 lowest total asymetry
       and the cosine similarity of the give subj_ids
    """
    try:
        data_dict = csv_dict(file_name)
        subj_ids = [i.upper() for i in subj_ids]
        asymetry = asymetry_calc(data_dict, subj_ids)
        euclidean_distance = euclidean_calc(data_dict, subj_ids)
        lowest_asymmetries = get_lowest_asymmetries(data_dict)
        cosine_similarity = cosine_similarity_calc(euclidean_distance)
        return asymetry, euclidean_distance, lowest_asymmetries, cosine_similarity
    # Error handling errors in the csv
    except FileNotFoundError:
        print(f"The file {file_name} is not found")
        return None, None, None, None
    except (AttributeError, IndexError, NameError, ValueError, KeyError):
        print("Please Enter the correct subj_id or check your csv file")
        return None, None, None, None


def asymetry_calc(data_dict, subj_ids, rounded=True):
    """
    format => data_dict = {}, subj_ids = ['10AB','21AB'], rounded=True
    Takes to ids and a dict and returns the 3d assymetric values
    of the landmarks. T
    """
    asy_values = []
    for subj in subj_ids:
        landmarks = {}
        # checking if the subject has all the landmarks
        if len(data_dict[subj]) == 7:
            for key in data_dict[subj]:
                coordinates = [i for i in data_dict[subj][key]]
                ox, oy, oz, mx, my, mz = coordinates

                # calculating 3d assymetric and rounding to 4 decimal place
                if rounded:
                    calculation = round(
                        ((mx-ox)**2+(my-oy)**2+(mz-oz)**2)**0.5, 4)
                else:
                    calculation = ((mx-ox)**2+(my-oy)**2+(mz-oz)**2)**0.5

                if key == 'PRN' and calculation == 0:
                    continue
                elif key == 'PRN' and calculation != 0:
                    return None
                landmarks[key] = calculation
        else:
            landmarks = None

        asy_values.append(landmarks)
    return asy_values


def euclidean_calc(data_dict, subj_ids):
    """takes a list of subj_ids and return their euclidean distance"""
    euc_distance = []
    # list of first point
    lm1 = ['EX', 'EN', 'AL', 'FT', 'SBAL', 'CH']
    # list of second point
    lm2 = ['EN', 'AL', 'EX', 'SBAL', 'CH', 'FT']
    try:
        for subj in subj_ids:
            facial_distance = {}
            if len(data_dict[subj]) == 7:
                for i, j in zip(lm1, lm2):
                    x1, y1, z1 = [i for i in data_dict[subj][i][:3]]
                    x2, y2, z2 = [i for i in data_dict[subj][j][:3]]
                    calculate = round(
                        ((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)**0.5, 4)
                    # combining corresponding values from each list to create a key
                    key = f'{i}{j}'
                    facial_distance[key] = calculate
            else:
                facial_distance = None
            euc_distance.append(facial_distance)
        return euc_distance
    except KeyError:
        return euc_distance


def get_lowest_asymmetries(data_dict):
    """
    Return a list of tuples with the subj_id
    and its total facial asymmetry
    """
    subj_ids = [i for i in data_dict]
    subj_asymetric_list = asymetry_calc(data_dict, subj_ids, rounded=False)
    total_asymetry = []
    for i, j in enumerate(subj_asymetric_list):
        if j is None:
            continue
        else:
            # geting the subj_id and the sum of the asymetry values
            subj_total = (subj_ids[i], round(sum(j.values()), 4))
            total_asymetry.append(subj_total)
    total_asymetry.sort(key=lambda x: x[1])
    return total_asymetry[:5]


def cosine_similarity_calc(euclidean_list):
    """
    return The cosine_similarity from
    a list of two dictionary {{},{}}
    """
    if None in euclidean_list:
        return None
    euc_a = [i for i in euclidean_list[0].values()]
    euc_b = [i for i in euclidean_list[1].values()]
    # kepping simple variable names for readability
    (a, b, c, d, e, f) = (euc_a[0], euc_a[1], euc_a[2],
                          euc_a[3], euc_a[4], euc_a[5])
    (a2, b2, c2, d2, e2, f2) = (euc_b[0], euc_b[1], euc_b[2],
                                euc_b[3], euc_b[4], euc_b[5])
    # Calculating similarity(A,B)
    similarity = (a*a2 + b*b2 + c*c2 + d*d2+e*e2+f*f2)/(
        (a**2 + b**2 + c**2 + d**2 + e**2 + f**2)**0.5 *
        (a2**2 + b2**2 + c2**2 + d2**2 + e2**2 + f2**2)**0.5
    )
    # rounding to 4 decimal place
    return round(similarity, 4)


OP1, OP2, OP3, OP4 = main('SampleData.csv', ['B7033', 'C1283'])
OP1_ref = [{'FT': 1.9198, 'EX': 1.8028, 'EN': 1.6555, 'AL': 2.5577, 'SBAL': 0.9023, 'CH': 1.7901}, {
    'FT': 1.807, 'EX': 2.2892, 'EN': 0.9371, 'AL': 1.9393, 'SBAL': 1.1624, 'CH': 2.7713}]

flag = True
if len(OP1) != 2:
    flag = False
for idx in range(2):
    for ditem in OP1_ref[idx]:
        if OP1_ref[idx][ditem] != OP1[idx][ditem]:
            flag = False
print(flag)

# Testing Output 2
OP1, OP2, OP3, OP4 = main('SampleData.csv', ['B7033', 'C1283'])
OP2_ref = [{'EXEN': 33.092, 'ENAL': 34.6946, 'ALEX': 50.1037, 'FTSBAL': 91.5324, 'SBALCH': 33.7109, 'CHFT': 98.1642}, {
    'EXEN': 34.4401, 'ENAL': 37.7494, 'ALEX': 54.0952, 'FTSBAL': 90.3202, 'SBALCH': 38.4123, 'CHFT': 104.8566}]

flag = True
if len(OP2) != 2:
    flag = False
for idx in range(2):
    for ditem in OP2_ref[idx]:
        if OP2_ref[idx][ditem] != OP2[idx][ditem]:
            flag = False
print(flag)

# Testing Output 3
OP1, OP2, OP3, OP4 = main('SampleData.csv', ['B7033', 'C1283'])
OP3_ref = [('E4996', 8.3254), ('H1178', 9.1597), ('F7831', 9.3268),
           ('J6687', 9.3878), ('K6431', 9.6359)]

flag = True
if len(OP3) != 5:
    flag = False
for idx in range(5):
    if OP3_ref[idx][0] != OP3[idx][0] or OP3_ref[idx][1] != OP3[idx][1]:
        flag = False
print(flag)

# Testing Output 4
OP1, OP2, OP3, OP4 = main('SampleData.csv', ['B7033', 'C1283'])
OP4_ref = 0.9991

flag = True
if OP4 != OP4_ref:
    flag = False
print(flag)
