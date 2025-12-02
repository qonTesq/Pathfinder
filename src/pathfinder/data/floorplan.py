"""Floorplan data for Pathfinder.

This module contains the hard-coded hospital floorplan matrix used by the Pathfinder system.
The floorplan is a 40x40 grid matrix representing hospital wards and obstacles for path planning.

Ward Codes:
- AD: Admissions
- GW: General Ward
- EM: Emergency
- MT: Maternity
- SU: Surgical
- ON: Oncology
- IC: ICU
- IW: Isolation Ward
- PD: Pediatric
- BU: Burn Unit
- HE: Hematology
- MD: Medical
"""

# fmt: off
FLOORPLAN = [
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'MT', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 'MT', 0, 0, 'MT', 'MT', 'MT', 'GW', 'GW', 'MT', 'MT', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'IW', 'IW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 'IW', 'IW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'IW', 'IW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 'IW', 'IW', 'IW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'IW', 'IW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 'IW', 'IW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'IW', 'IW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'EM', 'EM', 'IW', 'IW', 'IW', 0, 0, 'EM', 'EM', 'EM', 'EM', 'EM', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'EM', 'EM', 'IW', 'IW', 'IW', 0, 0, 'IC', 'IC', 'AD', 'AD', 'AD', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'GW', 'GW', 'GW', 'GW', 'GW', 'BU', 'BU', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'EM', 'EM', 'ON', 'EM', 'EM', 0, 0, 'IC', 'IC', 'AD', 'AD', 'AD', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'GW', 'GW', 'GW', 'GW', 'GW', 'BU', 'BU', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'EM', 'EM', 'ON', 'EM', 'EM', 0, 0, 'IC', 'IC', 'AD', 'AD', 'AD', 'AD', 'AD', 1],
    [1, 0, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'GW', 'GW', 'GW', 'GW', 'GW', 'BU', 'BU', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'GW', 'EM', 'EM', 'ON', 'EM', 'EM', 0, 0, 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 1],
    [1, 0, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'GW', 'GW', 'GW', 'GW', 'GW', 'EM', 'EM', 'ON', 'ON', 'ON', 0, 0, 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 1],
    [1, 0, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'GW', 'GW', 'GW', 'GW', 'GW', 'IW', 'IW', 'ON', 'ON', 'ON', 0, 0, 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 1],
    [1, 0, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'BU', 'GW', 'GW', 'GW', 'GW', 'GW', 0, 0, 'IW', 'IW', 'ON', 'ON', 'ON', 0, 0, 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'IC', 'IC', 'IC', 'IC', 'IC', 'IC', 1],
    [1, 1, 1, 0, 0, 0, 0, 'IW', 'ON', 0, 0, 'AD', 'AD', 'AD', 'AD', 'AD', 0, 0, 'HE', 'HE', 'HE', 'HE', 'HE', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 1, 1, 1],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'AD', 'AD', 'AD', 'AD', 'AD', 'HE', 'HE', 'HE', 'HE', 'HE', 'HE', 'HE', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'AD', 'AD', 'AD', 'HE', 'HE', 'HE', 'HE', 'HE', 'HE', 'HE', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'PD', 'PD', 'HE', 'HE', 'HE', 'HE', 'HE', 'HE', 'PD', 'PD', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'PD', 'PD', 'HE', 'HE', 'HE', 'HE', 'HE', 'HE', 'PD', 'PD', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'ON', 'ON', 'ON', 'ON', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 0, 0, 'SU', 'SU', 'SU', 'SU', 'ON', 'ON', 'ON', 'SU', 'SU', 'SU', 'ON', 'ON', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 0, 0, 'ON', 'ON', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'SU', 'SU', 'SU', 'MD', 'SU', 'MD', 'MD', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 0, 0, 'ON', 'ON', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'SU', 'SU', 'SU', 'MD', 'MD', 'MD', 'MD', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'SU', 'SU', 'SU', 'MD', 'MD', 'MD', 'MD', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 'IW', 'IW', 'IW', 'IW', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'SU', 'SU', 'SU', 'MD', 'MD', 'MD', 'MD', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 'IW', 'IW', 'IW', 'IW', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'PD', 'SU', 'SU', 'SU', 'MD', 'MD', 'MD', 'MD', 'SU', 'SU', 'SU', 'SU', 'SU', 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
]
# fmt: on
