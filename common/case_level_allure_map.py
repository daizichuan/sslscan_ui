def get_allure_level(meter_sphere_level):
    res = 'trivial'
    if meter_sphere_level.upper() == 'P0':
        res = 'blocker'
    elif meter_sphere_level.upper() == 'P1':
        res = 'critical'
    elif meter_sphere_level.upper() == 'P2':
        res = 'normal'
    elif meter_sphere_level.upper() == 'P3':
        res = 'minor'

    return res
